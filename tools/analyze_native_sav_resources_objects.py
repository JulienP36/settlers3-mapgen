"""Audit Legacy resources and start-adjacent objects in native SAV files.

This tool is intentionally read-only.  It accepts native ``.sav`` files,
directories and ZIP archives, decodes the confirmed type-3 cell fields, and
writes versioned CSV/JSON/Markdown references.  It never writes a SAV, MAP or
EDM file and it does not call the generator.

The distinction between the two object bytes is kept throughout the audit:

* byte 14 is the static/original object copied from the map;
* byte 7 is the current runtime object representation in a played SAV.

Resource byte 17 is decoded as the five mineral high-nibble families and as
fish only when the zero high-nibble value is on a confirmed water terrain.
All distance measurements use the confirmed Settlers III HEX6 metric.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import struct
import sys
import zipfile
from collections import Counter, defaultdict
from collections.abc import Iterable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from s3mapgen.map_data.binary import checksum
from s3mapgen.map_data.constants import START_FOOTPRINT


HEX6_POSITIVE = ((1, 0), (0, 1), (1, 1))
HEX_STRUCTURE = np.asarray(((1, 1, 0), (1, 1, 1), (0, 1, 1)), dtype=bool)
WATER_IDS = frozenset(range(8))
MINERAL_SUPPORT_IDS = frozenset((17, 32, 33, 34, 35, 128, 129))
RADII = (0, 2, 5, 10, 14, 25, 50, 100)
MINERAL_NAMES = {
    0x10: "coal",
    0x20: "iron",
    0x30: "gold",
    0x40: "gems",
    0x50: "sulfur",
}
RESOURCE_ORDER = ("coal", "iron", "gold", "gems", "sulfur", "minerals", "fish", "unknown")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_players_from_name(name: str) -> int | None:
    match = re.search(r"(?:^|[^0-9])(\d+)\s*(?:joueurs?|players?)\b", name, re.IGNORECASE)
    return int(match.group(1)) if match else None


def discover_sources(inputs: list[Path]) -> list[dict[str, Any]]:
    """Discover SAV members without extracting a whole archive to disk."""

    sources: list[dict[str, Any]] = []
    for input_path in inputs:
        if input_path.is_dir():
            for sav in sorted(input_path.glob("*.sav"), key=lambda path: path.name.lower()):
                sources.append({
                    "kind": "directory",
                    "source_name": input_path.name,
                    "member": sav.name,
                    "path": sav,
                })
        elif input_path.is_file() and input_path.suffix.lower() == ".sav":
            sources.append({
                "kind": "file",
                "source_name": input_path.parent.name,
                "member": input_path.name,
                "path": input_path,
            })
        elif input_path.is_file() and input_path.suffix.lower() == ".zip":
            archive_hash = sha256_bytes(input_path.read_bytes())
            with zipfile.ZipFile(input_path) as archive:
                members = sorted(
                    (info for info in archive.infolist()
                     if not info.is_dir() and info.filename.lower().endswith(".sav")),
                    key=lambda info: info.filename.lower(),
                )
                for info in members:
                    sources.append({
                        "kind": "zip",
                        "source_name": input_path.name,
                        "member": info.filename,
                        "path": input_path,
                        "archive_sha256": archive_hash,
                    })
        else:
            raise FileNotFoundError(f"Input SAV/ZIP/dossier introuvable: {input_path}")
    sources.sort(key=lambda row: (str(row["source_name"]).lower(), str(row["member"]).lower()))
    return sources


def read_source(source: dict[str, Any]) -> bytes:
    path = Path(source["path"])
    if source["kind"] == "zip":
        with zipfile.ZipFile(path) as archive:
            return archive.read(source["member"])
    return path.read_bytes()


def decrypt(payload: bytes, part_type: int) -> bytes:
    out = bytearray(len(payload))
    key = part_type & 0xFF
    for index, cipher in enumerate(payload):
        plain = cipher ^ key
        out[index] = plain
        key = ((key << 1) & 0xFF) ^ plain
    return bytes(out)


def extract_starts(player_blocks: list[bytes], side: int) -> tuple[list[tuple[int, int]], list[dict[str, Any]]]:
    """Decode only the confirmed native type-6 active flag and start offsets."""

    best_starts: list[tuple[int, int]] = []
    best_records: list[dict[str, Any]] = []
    for block in player_blocks:
        prefix = 84 if len(block) >= 84 and (len(block) - 84) % 328 == 0 else None
        if prefix is None:
            continue
        records: list[dict[str, Any]] = []
        starts: list[tuple[int, int]] = []
        for slot in range(min(20, (len(block) - prefix) // 328)):
            offset = prefix + slot * 328
            active_flag = struct.unpack_from("<I", block, offset)[0]
            tribe_candidate = struct.unpack_from("<I", block, offset + 4)[0]
            x, y = struct.unpack_from("<II", block, offset + 16)
            active = active_flag in (1, 2) and x < side and y < side
            row = {
                "player": slot + 1,
                "slot": slot + 1,
                "active": bool(active),
                "active_flag": int(active_flag),
                "start_x": int(x) if active else None,
                "start_y": int(y) if active else None,
                "tribe_code_candidate": int(tribe_candidate) if tribe_candidate <= 255 else None,
            }
            records.append(row)
            if active:
                starts.append((int(x), int(y)))
        if len(starts) > len(best_starts):
            best_starts, best_records = starts, records
    return best_starts, best_records


def parse_sav(data: bytes) -> dict[str, Any]:
    """Decode the raw type-3 fields once, including byte 14."""

    if len(data) < 12:
        raise ValueError("SAV trop court")
    version = struct.unpack_from("<I", data, 4)[0]
    if version != 11:
        raise ValueError(f"Version SAV non supportée: {version}")
    stored_checksum = struct.unpack_from("<I", data, 0)[0]
    calculated_checksum = checksum(data)

    columns: dict[int, bytes] = {}
    player_blocks: list[bytes] = []
    offset = 8
    while offset + 8 <= len(data):
        part_type, total_size = struct.unpack_from("<II", data, offset)
        if total_size < 8 or offset + total_size > len(data):
            raise ValueError(f"Part SAV invalide à {offset}")
        payload = decrypt(data[offset + 8:offset + total_size], part_type)
        low = part_type & 0xFFFF
        x = (part_type >> 16) & 0xFFFF
        if low == 3 and len(payload) % 24 == 0:
            columns[x] = payload
        elif part_type == 6:
            player_blocks.append(payload)
        offset += total_size
    if offset != len(data):
        raise ValueError(f"Part scan SAV incomplet: {offset}/{len(data)}")
    if not columns:
        raise ValueError("Aucune colonne type-3")
    side = max(columns) + 1
    if len(columns) != side or any(index not in columns for index in range(side)):
        raise ValueError(f"Colonnes SAV incomplètes: {len(columns)}/{side}")

    height = np.empty((side, side), dtype=np.uint8)
    terrain = np.empty((side, side), dtype=np.uint8)
    runtime_object = np.empty((side, side), dtype=np.uint8)
    claim = np.empty((side, side), dtype=np.uint8)
    unknown_byte9 = np.empty((side, side), dtype=np.uint8)
    static_object = np.empty((side, side), dtype=np.uint8)
    resource = np.empty((side, side), dtype=np.uint8)
    for x in range(side):
        column = columns[x]
        if len(column) != side * 24:
            raise ValueError(f"Payload colonne {x}: {len(column)} != {side * 24}")
        values = np.frombuffer(column, dtype=np.uint8).reshape(side, 24)
        height[:, x] = values[:, 4]
        terrain[:, x] = values[:, 6]
        runtime_object[:, x] = values[:, 7]
        claim[:, x] = values[:, 8]
        unknown_byte9[:, x] = values[:, 9]
        static_object[:, x] = values[:, 14]
        resource[:, x] = values[:, 17]

    starts, player_records = extract_starts(player_blocks, side)
    return {
        "side": side,
        "height": height,
        "terrain": terrain,
        "runtime_object": runtime_object,
        "static_object": static_object,
        "claim": claim,
        "unknown_byte9": unknown_byte9,
        "resource": resource,
        "starts": starts,
        "player_records": player_records,
        "version": int(version),
        "stored_checksum": int(stored_checksum),
        "calculated_checksum": int(calculated_checksum),
        "checksum_ok": stored_checksum == calculated_checksum,
    }


def pct(value: float, total: float) -> float:
    return round(100.0 * float(value) / float(total), 6) if total else 0.0


def per_1000(value: float, total: float) -> float:
    return round(1000.0 * float(value) / float(total), 6) if total else 0.0


def percentiles(values: Iterable[float | int]) -> dict[str, float]:
    array = np.asarray(list(values), dtype=np.float64)
    if array.size == 0:
        return {key: 0.0 for key in ("min", "p10", "median", "p90", "max", "mean")}
    p10, median, p90 = np.percentile(array, (10, 50, 90))
    return {
        "min": float(array.min()),
        "p10": float(p10),
        "median": float(median),
        "p90": float(p90),
        "max": float(array.max()),
        "mean": float(array.mean()),
    }


def hex_distances(coords: np.ndarray, x0: int, y0: int) -> np.ndarray:
    """Exact HEX6 distance from one start to an ``(n,2)`` x/y array."""

    if coords.size == 0:
        return np.empty(0, dtype=np.int16)
    dx = coords[:, 0].astype(np.int32) - int(x0)
    dy = coords[:, 1].astype(np.int32) - int(y0)
    return np.where(dx * dy >= 0, np.maximum(np.abs(dx), np.abs(dy)), np.abs(dx) + np.abs(dy)).astype(np.int16)


def nearest_distances(coords: np.ndarray, starts: list[tuple[int, int]]) -> np.ndarray:
    if coords.size == 0 or not starts:
        return np.empty(0, dtype=np.int16)
    result = np.full(coords.shape[0], 32767, dtype=np.int16)
    for x0, y0 in starts:
        result = np.minimum(result, hex_distances(coords, x0, y0))
    return result


def coords_for(mask: np.ndarray) -> np.ndarray:
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return np.empty((0, 2), dtype=np.int16)
    return np.column_stack((xs, ys)).astype(np.int16)


def shifted_pair(array: np.ndarray, dx: int, dy: int) -> tuple[np.ndarray, np.ndarray]:
    height, width = array.shape
    y0, y1 = max(0, -dy), min(height, height - dy)
    x0, x1 = max(0, -dx), min(width, width - dx)
    return array[y0:y1, x0:x1], array[y0 + dy:y1 + dy, x0 + dx:x1 + dx]


def component_details(mask: np.ndarray) -> list[dict[str, Any]]:
    """Describe HEX6 components without turning them into guessed blobs."""

    labels, count = ndimage.label(np.asarray(mask, dtype=bool), structure=HEX_STRUCTURE)
    if not count:
        return []
    sizes = np.bincount(labels.ravel(), minlength=count + 1)
    internal_edges = np.zeros(count + 1, dtype=np.int64)
    for dx, dy in HEX6_POSITIVE:
        left, right = shifted_pair(labels, dx, dy)
        same = (left == right) & (left > 0)
        internal_edges += np.bincount(left[same], minlength=count + 1)
    details: list[dict[str, Any]] = []
    slices = ndimage.find_objects(labels)
    for component_id, sl in enumerate(slices, start=1):
        size = int(sizes[component_id])
        if not size or sl is None:
            continue
        local = labels[sl] == component_id
        ys, xs = np.where(local)
        xs = xs.astype(np.float64) + int(sl[1].start)
        ys = ys.astype(np.float64) + int(sl[0].start)
        width = int(xs.max() - xs.min() + 1)
        height = int(ys.max() - ys.min() + 1)
        perimeter = int(6 * size - 2 * internal_edges[component_id])
        if size > 1:
            covariance = np.cov(np.column_stack((xs, ys)), rowvar=False)
            eigenvalues = np.linalg.eigvalsh(covariance)
            elongation = float(np.sqrt(max(float(eigenvalues[-1]), 0.0) / max(float(eigenvalues[0]), 1e-9)))
        else:
            elongation = 1.0
        details.append({
            "component_id": component_id,
            "cells": size,
            "perimeter_hex_edges": perimeter,
            "perimeter_sqrt_area": float(perimeter / max(np.sqrt(size), 1.0)),
            "min_x": int(xs.min()),
            "min_y": int(ys.min()),
            "max_x": int(xs.max()),
            "max_y": int(ys.max()),
            "bbox_width": width,
            "bbox_height": height,
            "bbox_fill": float(size / max(width * height, 1)),
            "centroid_x": float(xs.mean()),
            "centroid_y": float(ys.mean()),
            "compactness": float(min(1.0, (12.0 * size) / max(float(perimeter * perimeter), 1.0))),
            "elongation": elongation,
            "touches_map_edge": bool(
                xs.min() == 0 or ys.min() == 0 or xs.max() == mask.shape[1] - 1 or ys.max() == mask.shape[0] - 1
            ),
        })
    return details


def component_summary(details: list[dict[str, Any]]) -> dict[str, Any]:
    sizes = [row["cells"] for row in details]
    perimeters = [row["perimeter_sqrt_area"] for row in details]
    return {
        "count": len(details),
        "cells": int(sum(sizes)),
        "size": percentiles(sizes),
        "perimeter_sqrt_area": percentiles(perimeters),
        "bbox_fill": percentiles(row["bbox_fill"] for row in details),
        "elongation": percentiles(row["elongation"] for row in details),
        "edge_components": int(sum(1 for row in details if row["touches_map_edge"])),
    }


def object_name(object_id: int) -> str:
    names: dict[int, str] = {}
    for start, end, label in (
        (1, 8, "Big Stone"), (9, 12, "Decorative Stone"), (13, 20, "Border Stone"),
        (21, 28, "Small Stone"), (29, 33, "Wreck"), (35, 37, "Small Plant"),
        (38, 40, "Toadstool"), (41, 42, "Tree Stump"), (43, 44, "Dead Tree"),
        (45, 48, "Cactus"), (50, 52, "Small Flower"), (53, 56, "Small Bush"),
        (57, 61, "Bush"), (62, 67, "Reed"), (85, 92, "Wheat"),
        (93, 100, "Vine"), (101, 102, "Agave"), (103, 110, "Rice"),
        (111, 114, "Reef"), (115, 127, "Building Stone"),
    ):
        for value in range(start, end + 1):
            names[value] = f"{label} {value - start + 1}"
    names.update({
        34: "Grave", 49: "Skeleton", 68: "Birch 1", 69: "Birch 2",
        70: "Elm 1", 71: "Elm 2", 72: "Oak", 73: "Adult Tree 6",
        74: "Adult Tree 7", 75: "Adult Tree 8", 76: "Adult Tree 9",
        77: "Adult Tree 10", 78: "Palm 1", 79: "Palm 2", 80: "Adult Tree 13",
        81: "Adult Tree 14", 82: "Unknown reserved 82", 83: "Unknown reserved 83",
        84: "Small Tree / Sapling", 128: "Unknown 128", 129: "Unknown 129",
        208: "Tree Stump variant 1", 209: "Tree Stump variant 2", 210: "Tree Stump variant 3",
        211: "Tree Stump variant 4", 212: "Tree Stump variant 5", 213: "Tree Stump variant 6",
        214: "Tree Stump variant 7", 215: "Reserved / crash-prone 215",
        216: "Tree Sapling stage 2 variant 1", 217: "Tree Sapling stage 2 variant 2",
        218: "Tree Sapling stage 2 variant 3", 219: "Tree Sapling stage 2 variant 4",
        220: "Tree Sapling stage 2 variant 5", 221: "Palm Sapling stage 2",
        222: "Tree Sapling stage 2 variant 7", 223: "Reserved / crash-prone 223",
        224: "Tree Sapling stage 1 variant 1", 225: "Tree Sapling stage 1 variant 2",
        226: "Tree Sapling stage 1 variant 3", 227: "Tree Sapling stage 1 variant 4",
        228: "Tree Sapling stage 1 variant 5", 229: "Palm Sapling stage 1",
        230: "Tree Sapling stage 1 variant 7", 231: "Reserved / crash-prone 231",
        232: "Resource panel none", 233: "Resource panel coal", 234: "Resource panel abundant coal",
        235: "Resource panel iron", 236: "Resource panel abundant iron", 237: "Resource panel gold",
        238: "Resource panel abundant gold", 239: "Resource panel gems", 240: "Mineral discovery panel 1",
        241: "Mineral discovery panel 2", 242: "Mineral discovery panel 3", 243: "Burning tree stage 1",
        244: "Burning tree stage 2", 245: "Burning tree stage 3", 246: "Burning tree stage 4",
        247: "Bee nest stage 1", 248: "Bee nest stage 2", 249: "Bee nest stage 3",
        250: "Bee nest stage 4", 251: "Bee nest stage 5", 252: "Bee nest stage 6",
        253: "Bee nest stage 7", 254: "Red territory marker", 255: "Red flag",
    })
    if object_id in names:
        return names[object_id]
    return f"Object {object_id} (unknown)"


def object_family(object_id: int) -> str:
    ranges = (
        ((1, 8), "big_stone"), ((9, 12), "decorative_stone"), ((13, 20), "border_stone"),
        ((21, 28), "small_stone"), ((29, 33), "wreck"), ((34, 34), "grave"),
        ((35, 37), "small_plant"), ((38, 40), "toadstool"), ((41, 42), "stump"),
        ((43, 44), "dead_tree"), ((45, 48), "cactus"), ((49, 49), "skeleton"),
        ((50, 52), "small_flower"), ((53, 56), "small_bush"), ((57, 61), "bush"),
        ((62, 67), "reed"), ((68, 77), "adult_tree"), ((78, 79), "palm"),
        ((80, 81), "adult_tree"), ((82, 83), "unknown_reserved"), ((84, 84), "sapling"),
        ((85, 110), "crop"), ((111, 114), "reef"), ((115, 127), "building_stone"),
        ((208, 214), "stump_runtime"), ((215, 215), "unknown_reserved"),
        ((216, 222), "sapling_runtime_stage2"), ((223, 223), "unknown_reserved"),
        ((224, 230), "sapling_runtime_stage1"), ((231, 231), "unknown_reserved"),
        ((232, 242), "resource_overlay"), ((243, 246), "burning_tree"),
        ((247, 253), "bee_nest"), ((254, 255), "territory_marker"),
    )
    for (start, end), family in ranges:
        if start <= object_id <= end:
            return family
    return "unknown"


def object_role(object_id: int) -> str:
    if 1 <= object_id <= 127:
        return "world_decor"
    if 208 <= object_id <= 255:
        return "runtime_overlay"
    return "unknown"


def classify_resource(value: int, terrain_id: int) -> str | None:
    high = int(value) & 0xF0
    low = int(value) & 0x0F
    if value == 0 or low == 0:
        return None
    if high in MINERAL_NAMES:
        return MINERAL_NAMES[high]
    if high == 0 and terrain_id in WATER_IDS:
        return "fish"
    return "unknown"


def distance_summary(distances: np.ndarray) -> dict[str, float]:
    if distances.size == 0:
        return {key: 0.0 for key in ("min", "p10", "median", "p90", "max", "mean")}
    return percentiles(distances.tolist())


def radius_counts(distances: np.ndarray, values: np.ndarray | None = None) -> dict[str, int]:
    if values is None:
        values = np.ones(distances.shape, dtype=np.int64)
    return {f"r{radius}": int(values[distances <= radius].sum()) for radius in RADII}


def footprint_cells(side: int, start: tuple[int, int]) -> tuple[np.ndarray, np.ndarray]:
    x0, y0 = start
    points = [(x0 + dx, y0 + dy) for dx, dy in START_FOOTPRINT if 0 <= x0 + dx < side and 0 <= y0 + dy < side]
    if not points:
        return np.empty(0, dtype=np.int16), np.empty(0, dtype=np.int16)
    xs, ys = zip(*points)
    return np.asarray(xs, dtype=np.int16), np.asarray(ys, dtype=np.int16)


def classify_resource_array(resource: np.ndarray, terrain: np.ndarray) -> dict[str, np.ndarray]:
    """Return boolean masks for physical resource cells, without overlap."""

    masks: dict[str, np.ndarray] = {}
    for high, name in MINERAL_NAMES.items():
        masks[name] = ((resource & 0xF0) == high) & ((resource & 0x0F) != 0)
    masks["fish"] = (resource & 0xF0 == 0) & ((resource & 0x0F) != 0) & np.isin(terrain, list(WATER_IDS))
    any_known = np.zeros(resource.shape, dtype=bool)
    for mask in masks.values():
        any_known |= mask
    masks["unknown"] = (resource != 0) & ~any_known
    masks["minerals"] = np.zeros(resource.shape, dtype=bool)
    for name in MINERAL_NAMES.values():
        masks["minerals"] |= masks[name]
    return masks


def resource_map_row(
    map_id: str,
    group: str,
    side: int,
    family: str,
    mask: np.ndarray,
    resource: np.ndarray,
    terrain: np.ndarray,
    components: list[dict[str, Any]],
) -> dict[str, Any]:
    values = resource[mask]
    quantities = values & 0x0F
    terrain_counts = Counter(int(value) for value in terrain[mask])
    support = MINERAL_SUPPORT_IDS if family in (*MINERAL_NAMES.values(), "minerals") else WATER_IDS if family == "fish" else None
    outside_support = int(np.count_nonzero(mask & ~np.isin(terrain, list(support)))) if support is not None else 0
    quantity_counts = {str(value): int(np.count_nonzero(quantities == value)) for value in range(1, 16)}
    return {
        "map_id": map_id,
        "group": group,
        "family": family,
        "cells": int(mask.sum()),
        "stock": int(quantities.sum()),
        "pct_map": pct(int(mask.sum()), side * side),
        "quantity_min": int(quantities.min()) if quantities.size else 0,
        "quantity_median": float(np.median(quantities)) if quantities.size else 0.0,
        "quantity_mean": float(quantities.mean()) if quantities.size else 0.0,
        "quantity_max": int(quantities.max()) if quantities.size else 0,
        "quantity_counts": quantity_counts,
        "component_count": len(components),
        "component_size_median": float(np.median([row["cells"] for row in components])) if components else 0.0,
        "component_size_p90": float(np.percentile([row["cells"] for row in components], 90)) if components else 0.0,
        "component_size_max": int(max((row["cells"] for row in components), default=0)),
        "component_perimeter_sqrt_area_median": float(np.median([row["perimeter_sqrt_area"] for row in components])) if components else 0.0,
        "component_elongation_median": float(np.median([row["elongation"] for row in components])) if components else 0.0,
        "edge_component_count": int(sum(1 for row in components if row["touches_map_edge"])),
        "cells_outside_expected_support": outside_support,
        "terrain_counts": {str(key): int(value) for key, value in sorted(terrain_counts.items())},
    }


def analyze_resources(
    map_id: str,
    group: str,
    side: int,
    starts: list[tuple[int, int]],
    resource: np.ndarray,
    terrain: np.ndarray,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    masks = classify_resource_array(resource, terrain)
    map_rows: list[dict[str, Any]] = []
    component_rows: list[dict[str, Any]] = []
    for family in (*MINERAL_NAMES.values(), "minerals", "fish", "unknown"):
        details = component_details(masks[family])
        map_rows.append(resource_map_row(map_id, group, side, family, masks[family], resource, terrain, details))
        for detail in details:
            component_rows.append({"map_id": map_id, "group": group, "family": family, **detail})

    local_rows: list[dict[str, Any]] = []
    for player, (x0, y0) in enumerate(starts, start=1):
        for family in (*MINERAL_NAMES.values(), "minerals", "fish", "unknown"):
            coords = coords_for(masks[family])
            distances = hex_distances(coords, x0, y0)
            values = (resource[coords[:, 1], coords[:, 0]] & 0x0F).astype(np.int64) if coords.size else np.empty(0, dtype=np.int64)
            row: dict[str, Any] = {
                "map_id": map_id,
                "group": group,
                "player": player,
                "start_x": x0,
                "start_y": y0,
                "family": family,
                "nearest_hex": int(distances.min()) if distances.size else None,
            }
            for radius in RADII:
                selected = distances <= radius
                row[f"cells_r{radius}"] = int(selected.sum())
                row[f"stock_r{radius}"] = int(values[selected].sum())
            local_rows.append(row)
    return map_rows, component_rows, local_rows


def object_inventory_rows(
    map_id: str,
    group: str,
    representation: str,
    values: np.ndarray,
    terrain: np.ndarray,
    unknown_byte9: np.ndarray,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for object_id in sorted(int(value) for value in np.unique(values) if int(value) != 0):
        mask = values == object_id
        object_coords = coords_for(mask)
        terrain_counts = Counter(int(value) for value in terrain[mask])
        byte9_values = unknown_byte9[mask]
        rows.append({
            "map_id": map_id,
            "group": group,
            "representation": representation,
            "object_id": object_id,
            "name": object_name(object_id),
            "family": object_family(object_id),
            "role": object_role(object_id),
            "cells": int(mask.sum()),
            "pct_map": pct(int(mask.sum()), values.size),
            "terrain_counts": {str(key): int(value) for key, value in sorted(terrain_counts.items())},
            "byte9_zero": int(np.count_nonzero(byte9_values == 0)),
            "byte9_nonzero": int(np.count_nonzero(byte9_values != 0)),
            "coords_count": int(object_coords.shape[0]),
        })
    return rows


def object_id_proximity_rows(
    map_id: str,
    group: str,
    representation: str,
    values: np.ndarray,
    claim: np.ndarray,
    starts: list[tuple[int, int]],
    object_inventory: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Measure object IDs both globally and from every decoded player start."""

    side = values.shape[0]
    id_summary: list[dict[str, Any]] = []
    start_rows: list[dict[str, Any]] = []
    for inventory in object_inventory:
        object_id = int(inventory["object_id"])
        coords = coords_for(values == object_id)
        if not coords.size:
            continue
        distances = nearest_distances(coords, starts)
        row = {
            "map_id": map_id,
            "group": group,
            "representation": representation,
            "object_id": object_id,
            "name": inventory["name"],
            "family": inventory["family"],
            "role": inventory["role"],
            "cells": int(coords.shape[0]),
            "nearest_hex": int(distances.min()) if distances.size else None,
            "distance_median_cells": float(np.median(distances)) if distances.size else None,
            "distance_p90_cells": float(np.percentile(distances, 90)) if distances.size else None,
            "byte9_zero": inventory["byte9_zero"],
            "byte9_nonzero": inventory["byte9_nonzero"],
        }
        for radius in RADII:
            row[f"cells_r{radius}"] = int((distances <= radius).sum())
        footprint_total = 0
        claim_total = 0
        for player, (x0, y0) in enumerate(starts, start=1):
            per_start = hex_distances(coords, x0, y0)
            footprint_x, footprint_y = footprint_cells(side, (x0, y0))
            footprint_count = int(np.count_nonzero(values[footprint_y, footprint_x] == object_id)) if footprint_x.size else 0
            claim_count = int(np.count_nonzero(claim[coords[:, 1], coords[:, 0]] == player - 1))
            footprint_total += footprint_count
            claim_total += claim_count
            start_row: dict[str, Any] = {
                "map_id": map_id,
                "group": group,
                "representation": representation,
                "player": player,
                "start_x": x0,
                "start_y": y0,
                "object_id": object_id,
                "name": inventory["name"],
                "family": inventory["family"],
                "role": inventory["role"],
                "nearest_hex": int(per_start.min()) if per_start.size else None,
                "claim_object_cells": claim_count,
                "nominal_footprint_object_cells": footprint_count,
            }
            for radius in RADII:
                start_row[f"cells_r{radius}"] = int((per_start <= radius).sum())
            start_rows.append(start_row)
        row["claim_cells"] = claim_total
        row["nominal_footprint_cells"] = footprint_total
        id_summary.append(row)
    return id_summary, start_rows


def object_start_rows(
    map_id: str,
    group: str,
    values: np.ndarray,
    starts: list[tuple[int, int]],
    representation: str,
) -> list[dict[str, Any]]:
    side = values.shape[0]
    all_coords = coords_for(values != 0)
    world_coords = coords_for((values >= 1) & (values <= 127))
    rows: list[dict[str, Any]] = []
    for player, (x0, y0) in enumerate(starts, start=1):
        all_distances = hex_distances(all_coords, x0, y0)
        world_distances = hex_distances(world_coords, x0, y0)
        first_index = int(np.argmin(world_distances)) if world_distances.size else -1
        first_id = int(values[world_coords[first_index, 1], world_coords[first_index, 0]]) if first_index >= 0 else None
        footprint_x, footprint_y = footprint_cells(side, (x0, y0))
        footprint_values = values[footprint_y, footprint_x] if footprint_x.size else np.empty(0, dtype=np.uint8)
        row: dict[str, Any] = {
            "map_id": map_id,
            "group": group,
            "representation": representation,
            "player": player,
            "start_x": x0,
            "start_y": y0,
            "first_world_object_id": first_id,
            "first_world_object_name": object_name(first_id) if first_id is not None else None,
            "first_world_object_distance": int(world_distances.min()) if world_distances.size else None,
            "all_nonzero_distance": int(all_distances.min()) if all_distances.size else None,
            "nominal_footprint_nonzero_cells": int(np.count_nonzero(footprint_values)),
            "nominal_footprint_world_cells": int(np.count_nonzero((footprint_values >= 1) & (footprint_values <= 127))),
        }
        for radius in RADII:
            row[f"all_nonzero_r{radius}"] = int((all_distances <= radius).sum())
            row[f"world_decor_r{radius}"] = int((world_distances <= radius).sum())
        rows.append(row)
    return rows


def object_local_density_rows(
    map_id: str,
    group: str,
    static_object: np.ndarray,
    runtime_object: np.ndarray,
    starts: list[tuple[int, int]],
) -> list[dict[str, Any]]:
    """Return per-start local object counts and densities, with edge clipping."""

    side = static_object.shape[0]
    rows: list[dict[str, Any]] = []
    for player, (x0, y0) in enumerate(starts, start=1):
        row: dict[str, Any] = {
            "map_id": map_id,
            "group": group,
            "player": player,
            "start_x": x0,
            "start_y": y0,
        }
        for representation, values in (("static", static_object), ("runtime", runtime_object)):
            nonzero = coords_for(values != 0)
            world = coords_for((values >= 1) & (values <= 127))
            for radius in (10, 25, 50, 100):
                bbox_x = np.arange(max(0, x0 - radius), min(side, x0 + radius + 1), dtype=np.int16)
                bbox_y = np.arange(max(0, y0 - radius), min(side, y0 + radius + 1), dtype=np.int16)
                grid_x, grid_y = np.meshgrid(bbox_x, bbox_y)
                grid_coords = np.column_stack((grid_x.ravel(), grid_y.ravel()))
                neighborhood_size = int((hex_distances(grid_coords, x0, y0) <= radius).sum())
                nonzero_count = int((hex_distances(nonzero, x0, y0) <= radius).sum())
                world_count = int((hex_distances(world, x0, y0) <= radius).sum())
                row[f"{representation}_all_r{radius}"] = nonzero_count
                row[f"{representation}_world_r{radius}"] = world_count
                row[f"{representation}_world_density_r{radius}"] = per_1000(world_count, neighborhood_size)
                row[f"{representation}_neighborhood_cells_r{radius}"] = neighborhood_size
        rows.append(row)
    return rows


def runtime_object_diff(static_object: np.ndarray, runtime_object: np.ndarray) -> dict[str, Any]:
    differing = static_object != runtime_object
    presence = (static_object != 0) != (runtime_object != 0)
    transitions = Counter(zip(static_object[differing].tolist(), runtime_object[differing].tolist()))
    return {
        "exact_difference_cells": int(differing.sum()),
        "presence_difference_cells": int(presence.sum()),
        "transitions": [
            {"static": int(a), "runtime": int(b), "cells": int(count)}
            for (a, b), count in transitions.most_common()
        ],
    }


def analyze_map(source: dict[str, Any], index: int) -> dict[str, Any]:
    data = read_source(source)
    parsed = parse_sav(data)
    actual_players = len(parsed["starts"])
    filename_players = parse_players_from_name(Path(source["member"]).name)
    group = f"{actual_players}p" if actual_players in (2, 20) else f"{actual_players}p_other"
    map_id = f"sav_{index:03d}"
    resource_rows, resource_components, resource_local = analyze_resources(
        map_id, group, parsed["side"], parsed["starts"], parsed["resource"], parsed["terrain"]
    )
    static_inventory = object_inventory_rows(map_id, group, "static", parsed["static_object"], parsed["terrain"], parsed["unknown_byte9"])
    runtime_inventory = object_inventory_rows(map_id, group, "runtime", parsed["runtime_object"], parsed["terrain"], parsed["unknown_byte9"])
    static_proximity, static_start_proximity = object_id_proximity_rows(
        map_id, group, "static", parsed["static_object"], parsed["claim"], parsed["starts"], static_inventory
    )
    runtime_proximity, runtime_start_proximity = object_id_proximity_rows(
        map_id, group, "runtime", parsed["runtime_object"], parsed["claim"], parsed["starts"], runtime_inventory
    )
    object_start_overview = object_start_rows(map_id, group, parsed["static_object"], parsed["starts"], "static")
    object_start_local = object_local_density_rows(
        map_id, group, parsed["static_object"], parsed["runtime_object"], parsed["starts"]
    )
    object_start_proximity = static_start_proximity + runtime_start_proximity
    return {
        "map_id": map_id,
        "source": {
            "kind": source["kind"],
            "name": source["source_name"],
            "member": source["member"],
            "archive_sha256": source.get("archive_sha256"),
            "file_size": len(data),
            "sha256": sha256_bytes(data),
        },
        "format": {
            "sav_version": parsed["version"],
            "stored_checksum": parsed["stored_checksum"],
            "calculated_checksum": parsed["calculated_checksum"],
            "checksum_ok": parsed["checksum_ok"],
        },
        "configuration": {
            "side": parsed["side"],
            "players_from_filename": filename_players,
            "players": actual_players,
            "starts": [[int(x), int(y)] for x, y in parsed["starts"]],
            "player_records": parsed["player_records"],
            "group": group,
        },
        "arrays": parsed,
        "resources": {
            "per_map": resource_rows,
            "components": resource_components,
            "local_starts": resource_local,
        },
        "objects": {
            "per_map": static_inventory + runtime_inventory,
            "proximity": static_proximity + runtime_proximity,
            "start_proximity": object_start_proximity,
            "start_overview": object_start_overview,
            "start_local": object_start_local,
            "runtime_diff": runtime_object_diff(parsed["static_object"], parsed["runtime_object"]),
        },
    }


def flatten_quantity_counts(row: dict[str, Any]) -> dict[str, int]:
    counts = row.get("quantity_counts", {})
    return {f"quantity_{value}": int(counts.get(str(value), 0)) for value in range(1, 16)}


def median_or_zero(values: Iterable[float | int]) -> float:
    values = list(values)
    return float(np.median(values)) if values else 0.0


def aggregate_resource_rows(maps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for group in ("2p", "20p"):
        group_maps = [record for record in maps if record["configuration"]["group"] == group]
        for family in (*MINERAL_NAMES.values(), "minerals", "fish", "unknown"):
            per_map = [
                next(row for row in record["resources"]["per_map"] if row["family"] == family)
                for record in group_maps
            ]
            quantity_counts = Counter()
            for row in per_map:
                quantity_counts.update({key: int(value) for key, value in row["quantity_counts"].items()})
            rows.append({
                "group": group,
                "family": family,
                "maps": len(per_map),
                "cells_median_per_map": median_or_zero(row["cells"] for row in per_map),
                "cells_mean_per_map": float(np.mean([row["cells"] for row in per_map])) if per_map else 0.0,
                "cells_min_per_map": int(min((row["cells"] for row in per_map), default=0)),
                "cells_max_per_map": int(max((row["cells"] for row in per_map), default=0)),
                "stock_median_per_map": median_or_zero(row["stock"] for row in per_map),
                "stock_mean_per_map": float(np.mean([row["stock"] for row in per_map])) if per_map else 0.0,
                "pct_map_median": median_or_zero(row["pct_map"] for row in per_map),
                "component_count_median": median_or_zero(row["component_count"] for row in per_map),
                "component_size_median": median_or_zero(row["component_size_median"] for row in per_map),
                "component_size_p90_median": median_or_zero(row["component_size_p90"] for row in per_map),
                "component_size_max_median": median_or_zero(row["component_size_max"] for row in per_map),
                "quantity_median_pooled": float(np.median([
                    int(value) for row in per_map for value, count in row["quantity_counts"].items() for _ in range(count)
                ])) if sum(quantity_counts.values()) else 0.0,
                "quantity_mean_pooled": float(
                    sum(int(value) * count for value, count in quantity_counts.items()) / max(sum(quantity_counts.values()), 1)
                ),
                "cells_outside_expected_support": int(sum(row["cells_outside_expected_support"] for row in per_map)),
                "quantity_counts": {key: int(value) for key, value in sorted(quantity_counts.items())},
            })
    return rows


def aggregate_resource_local(maps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for group in ("2p", "20p"):
        local = [
            row for record in maps if record["configuration"]["group"] == group
            for row in record["resources"]["local_starts"]
        ]
        for family in (*MINERAL_NAMES.values(), "minerals", "fish", "unknown"):
            selected = [row for row in local if row["family"] == family]
            row: dict[str, Any] = {
                "group": group,
                "family": family,
                "starts": len(selected),
                "nearest_hex_median": median_or_zero(row["nearest_hex"] for row in selected if row["nearest_hex"] is not None),
                "nearest_hex_min": min((row["nearest_hex"] for row in selected if row["nearest_hex"] is not None), default=None),
                "nearest_hex_max": max((row["nearest_hex"] for row in selected if row["nearest_hex"] is not None), default=None),
            }
            for radius in RADII:
                row[f"cells_r{radius}_median"] = median_or_zero(item[f"cells_r{radius}"] for item in selected)
                row[f"stock_r{radius}_median"] = median_or_zero(item[f"stock_r{radius}"] for item in selected)
            rows.append(row)
    return rows


def aggregate_object_inventory(maps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    keys = sorted({
        (record["configuration"]["group"], row["representation"], row["object_id"])
        for record in maps for row in record["objects"]["per_map"]
    })
    for group, representation, object_id in keys:
        selected = [
            row for record in maps if record["configuration"]["group"] == group
            for row in record["objects"]["per_map"]
            if row["representation"] == representation and row["object_id"] == object_id
        ]
        rows.append({
            "group": group,
            "representation": representation,
            "object_id": object_id,
            "name": object_name(object_id),
            "family": object_family(object_id),
            "role": object_role(object_id),
            "maps_present": len(selected),
            "cells_median_per_map_present": median_or_zero(row["cells"] for row in selected),
            "cells_total": int(sum(row["cells"] for row in selected)),
            "byte9_nonzero_pct": pct(
                sum(row["byte9_nonzero"] for row in selected),
                sum(row["byte9_nonzero"] + row["byte9_zero"] for row in selected),
            ),
        })
    return rows


def aggregate_object_proximity(maps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    keys = sorted({
        (record["configuration"]["group"], row["representation"], row["object_id"])
        for record in maps for row in record["objects"]["proximity"]
    })
    for group, representation, object_id in keys:
        selected = [
            row for record in maps if record["configuration"]["group"] == group
            for row in record["objects"]["proximity"]
            if row["representation"] == representation and row["object_id"] == object_id
        ]
        starts = [
            row for record in maps if record["configuration"]["group"] == group
            for row in record["objects"]["start_proximity"]
            if row["representation"] == representation and row["object_id"] == object_id
        ]
        distances = [row["nearest_hex"] for row in starts if row["nearest_hex"] is not None]
        row: dict[str, Any] = {
            "group": group,
            "representation": representation,
            "object_id": object_id,
            "name": object_name(object_id),
            "family": object_family(object_id),
            "role": object_role(object_id),
            "maps_present": len(selected),
            "starts": len(starts),
            "nearest_hex_global_min": min((row["nearest_hex"] for row in selected if row["nearest_hex"] is not None), default=None),
            "nearest_hex_start_median": median_or_zero(distances),
            "nearest_hex_start_min": min(distances, default=None),
            "starts_within_2": int(sum(1 for value in distances if value <= 2)),
            "starts_within_5": int(sum(1 for value in distances if value <= 5)),
            "starts_within_14": int(sum(1 for value in distances if value <= 14)),
            "nominal_footprint_cells": int(sum(row["nominal_footprint_cells"] for row in selected)),
            "claim_cells": int(sum(row["claim_cells"] for row in selected)),
            "cells_r2_total": int(sum(row["cells_r2"] for row in selected)),
            "cells_r5_total": int(sum(row["cells_r5"] for row in selected)),
            "cells_r14_total": int(sum(row["cells_r14"] for row in selected)),
        }
        rows.append(row)
    return rows


def aggregate_object_families(proximity_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    keys = sorted({(row["group"], row["representation"], row["family"]) for row in proximity_rows})
    for group, representation, family in keys:
        selected = [row for row in proximity_rows if (row["group"], row["representation"], row["family"]) == (group, representation, family)]
        near5 = sorted({int(row["object_id"]) for row in selected if row["nearest_hex_global_min"] is not None and row["nearest_hex_global_min"] <= 5})
        far14 = sorted({int(row["object_id"]) for row in selected if row["nearest_hex_global_min"] is not None and row["nearest_hex_global_min"] > 14})
        rows.append({
            "group": group,
            "representation": representation,
            "family": family,
            "ids_present": len(selected),
            "ids_within_5": ",".join(map(str, near5)),
            "ids_over_14": ",".join(map(str, far14)),
            "nearest_hex_min": min((row["nearest_hex_global_min"] for row in selected if row["nearest_hex_global_min"] is not None), default=None),
            "nominal_footprint_cells": int(sum(row["nominal_footprint_cells"] for row in selected)),
            "claim_cells": int(sum(row["claim_cells"] for row in selected)),
        })
    return rows


def aggregate_object_local(maps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for group in ("2p", "20p"):
        selected = [
            row for record in maps if record["configuration"]["group"] == group
            for row in record["objects"]["start_local"]
        ]
        for representation in ("static", "runtime"):
            global_world_counts = [
                sum(row["cells"] for row in record["objects"]["per_map"] if row["representation"] == representation and row["role"] == "world_decor")
                for record in maps if record["configuration"]["group"] == group
            ]
            for radius in (10, 25, 50, 100):
                values = [row[f"{representation}_world_density_r{radius}"] for row in selected]
                rows.append({
                    "group": group,
                    "representation": representation,
                    "radius": radius,
                    "starts": len(selected),
                    "local_world_density_median_per_1000": median_or_zero(values),
                    "local_world_count_median": median_or_zero(row[f"{representation}_world_r{radius}"] for row in selected),
                    "global_world_density_median_per_1000_map": per_1000(
                        median_or_zero(global_world_counts),
                        next((record["configuration"]["side"] ** 2 for record in maps if record["configuration"]["group"] == group), 0),
                    ),
                })
    return rows


def write_csv(path: Path, rows: Iterable[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    rows = list(rows)
    if fieldnames is None:
        fieldnames = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def flattened_resource_row(row: dict[str, Any]) -> dict[str, Any]:
    output = dict(row)
    output["quantity_counts"] = json.dumps(row.get("quantity_counts", {}), ensure_ascii=False, sort_keys=True)
    output["terrain_counts"] = json.dumps(row.get("terrain_counts", {}), ensure_ascii=False, sort_keys=True)
    output.update(flatten_quantity_counts(row))
    return output


def flattened_object_row(row: dict[str, Any]) -> dict[str, Any]:
    output = dict(row)
    output["terrain_counts"] = json.dumps(row.get("terrain_counts", {}), ensure_ascii=False, sort_keys=True)
    return output


def resource_cell_rows(record: dict[str, Any]) -> Iterable[dict[str, Any]]:
    arrays = record["arrays"]
    resource = arrays["resource"]
    terrain = arrays["terrain"]
    claim = arrays["claim"]
    side = arrays["side"]
    masks = classify_resource_array(resource, terrain)
    for family in (*MINERAL_NAMES.values(), "fish", "unknown"):
        ys, xs = np.where(masks[family])
        for y, x in zip(ys.tolist(), xs.tolist()):
            value = int(resource[y, x])
            yield {
                "map_id": record["map_id"],
                "group": record["configuration"]["group"],
                "x": int(x),
                "y": int(y),
                "family": family,
                "raw_byte17": value,
                "quantity": value & 0x0F,
                "terrain_id": int(terrain[y, x]),
                "claim": int(claim[y, x]),
                "side": side,
            }


def fmt(value: Any, digits: int = 2) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    if isinstance(value, int):
        return f"{value:,}".replace(",", " ")
    return str(value)


def resource_group_row(resource_rows: list[dict[str, Any]], group: str, family: str) -> dict[str, Any]:
    return next(row for row in resource_rows if row["group"] == group and row["family"] == family)


def markdown_report(
    maps: list[dict[str, Any]],
    resource_aggregate: list[dict[str, Any]],
    resource_local: list[dict[str, Any]],
    object_aggregate: list[dict[str, Any]],
    object_proximity: list[dict[str, Any]],
    object_families: list[dict[str, Any]],
    object_local: list[dict[str, Any]],
    generated_at: str,
) -> str:
    map_count = len(maps)
    starts_count = sum(len(record["configuration"]["starts"]) for record in maps)
    checksum_ok = sum(bool(record["format"]["checksum_ok"]) for record in maps)
    lines = [
        "# Settlers III — audit Legacy des ressources et objets proches des départs",
        "",
        f"> Première tranche du point 3 de la v2.0 : {map_count} SAV natifs 768×768 (8 cartes 2 joueurs et 8 cartes 20 joueurs), analysés le {generated_at}.",
        "> L’analyse est en lecture seule. Elle ne modifie pas le générateur et ne mélange pas les règles Upgraded.",
        "",
        "## Méthode et limites",
        "",
        "- Les minerais et poissons sont lus dans le byte 17 de chaque cellule type 3. Les minerais utilisent les familles haut-nibble `0x10` à `0x50`; un poisson est retenu seulement pour un low-nibble non nul sur les terrains Water 0..7.",
        "- Les objets sont séparés en deux représentations : byte 14 (`static`) pour le décor initial de la carte, byte 7 (`runtime`) pour l’état courant du SAV. Les distances et densités de placement utilisent d’abord byte 14.",
        "- Les distances sont des distances HEX6 exactes. L’empreinte nominale de départ est la constante validée de 33 cellules ; elle ne constitue pas à elle seule la hitbox complète d’un bâtiment ou d’un objet.",
        "- La proximité d’un objet est une observation géométrique, pas une preuve d’accessibilité ou d’absence de collision. Le byte 4 décrit la hauteur dans le SAV ; le byte 9 reste inconnu et n’est donc pas utilisé comme indice de hitbox. Les empreintes de collision complètes restent à calibrer dans le jeu/éditeur.",
        "",
        "## Corpus et intégrité",
        "",
        f"{map_count} SAV analysés, {starts_count} départs décodés depuis les blocs type 6, checksum valide pour {checksum_ok}/{map_count} fichiers.",
        "",
        "| Carte | Groupe | Joueurs | Départs | Taille SAV | Checksum | Fichier |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    for record in maps:
        source = record["source"]
        lines.append(
            f"| `{record['map_id']}` | {record['configuration']['group']} | {record['configuration']['players']} | {len(record['configuration']['starts'])} | {fmt(source['file_size'])} octets | {'OK' if record['format']['checksum_ok'] else 'ÉCHEC'} | `{source['name']}::{source['member']}` |"
        )

    lines += [
        "",
        "## Ressources Legacy — mesures globales",
        "",
        "Les lignes `minerals` sont l’union des cinq familles et ne doivent pas être additionnées aux lignes de minerais individuels. Les valeurs de cellules sont des cellules portant un code de ressource, tandis que `stock` additionne les low-nibbles.",
        "",
        "| Groupe | Famille | Cellules médianes/carte | Stock médian/carte | % moyen carte | Composantes médianes | Taille composante médiane | Quantité moyenne | Hors support attendu |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for group in ("2p", "20p"):
        for family in (*MINERAL_NAMES.values(), "minerals", "fish"):
            row = resource_group_row(resource_aggregate, group, family)
            lines.append(
                f"| {group} | `{family}` | {fmt(row['cells_median_per_map'])} | {fmt(row['stock_median_per_map'])} | {fmt(row['pct_map_median'], 3)} % | {fmt(row['component_count_median'], 1)} | {fmt(row['component_size_median'], 1)} | {fmt(row['quantity_mean_pooled'], 2)} | {fmt(row['cells_outside_expected_support'])} |"
            )
    lines += [
        "",
        "### Répartition des quantités",
        "",
        "Le low-nibble est détaillé dans `resource_families.csv` et `resource_per_map.csv`. Sur cette tranche, la moyenne reste proche de 8 unités par cellule codée ; il n’y a pas de signal justifiant une quantité systématiquement dépendante de la famille.",
        "",
        "| Groupe | Famille | Min–max quantité | Médiane pooled | Moyenne pooled |",
        "|---|---|---:|---:|---:|",
    ]
    for group in ("2p", "20p"):
        for family in (*MINERAL_NAMES.values(), "fish"):
            row = resource_group_row(resource_aggregate, group, family)
            per_map = [
                next(item for item in record["resources"]["per_map"] if item["family"] == family)
                for record in maps if record["configuration"]["group"] == group
            ]
            qmins = [item["quantity_min"] for item in per_map if item["cells"]]
            qmaxs = [item["quantity_max"] for item in per_map if item["cells"]]
            lines.append(
                f"| {group} | `{family}` | {fmt(min(qmins) if qmins else 0)}–{fmt(max(qmaxs) if qmaxs else 0)} | {fmt(row['quantity_median_pooled'], 1)} | {fmt(row['quantity_mean_pooled'], 1)} |"
            )

    lines += [
        "",
        "## Ressources autour des départs",
        "",
        "Les rayons sont mesurés à partir de chaque départ, puis résumés par médiane sur tous les départs du groupe.",
        "",
        "| Groupe | Famille | Plus proche médian | r10 cellules | r25 cellules | r50 cellules | r100 cellules | r100 stock |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for group in ("2p", "20p"):
        for family in ("minerals", "fish"):
            row = next(item for item in resource_local if item["group"] == group and item["family"] == family)
            lines.append(
                f"| {group} | `{family}` | {fmt(row['nearest_hex_median'], 1)} hex | {fmt(row['cells_r10_median'], 1)} | {fmt(row['cells_r25_median'], 1)} | {fmt(row['cells_r50_median'], 1)} | {fmt(row['cells_r100_median'], 1)} | {fmt(row['stock_r100_median'], 1)} |"
            )
    lines += [
        "",
        "- Observation nette : les médianes à `r10` et `r25` sont nulles pour les minerais et les poissons dans les deux groupes. La ressource n’est donc pas posée au voisinage immédiat des starts dans cette tranche.",
        "- Cela ne signifie pas qu’un rayon dur universel est démontré : la distance du premier minerai varie fortement entre 2P et 20P, et la disponibilité locale dépend du relief/eau généré.",
        "",
        "## Objets — inventaire et séparation statique/runtime",
        "",
        "Le tableau complet par ID et terrain support est dans `objects_per_map.csv`. Le byte 9 est exporté séparément comme champ encore inconnu ; il n’est pas interprété comme accessibilité.",
        "",
        "| Groupe | Représentation | IDs observés | Cellules totales | Différence exacte byte14/byte7 | Différence présence |",
        "|---|---|---:|---:|---:|---:|",
    ]
    diff_by_group: dict[str, dict[str, int]] = {}
    for record in maps:
        group = record["configuration"]["group"]
        diff = diff_by_group.setdefault(group, {"exact": 0, "presence": 0})
        diff["exact"] += record["objects"]["runtime_diff"]["exact_difference_cells"]
        diff["presence"] += record["objects"]["runtime_diff"]["presence_difference_cells"]
    for group in ("2p", "20p"):
        for representation in ("static", "runtime"):
            selected = [row for row in object_aggregate if row["group"] == group and row["representation"] == representation]
            diff = diff_by_group.get(group, {"exact": 0, "presence": 0})
            lines.append(
                f"| {group} | `{representation}` | {len(selected)} | {fmt(sum(row['cells_total'] for row in selected))} | {fmt(diff['exact'] if representation == 'static' else 0)} | {fmt(diff['presence'] if representation == 'static' else 0)} |"
            )
    lines.append("- Le nombre d’IDs est un inventaire, pas une preuve que chaque ID a la même règle de collision. Les différences runtime sont concentrées dans les valeurs de cycle/overlay (notamment 112/113/255 selon les cartes) ; byte 14 reste la base de reproduction du décor initial.")

    lines += [
        "",
        "## Proximité des objets aux starts",
        "",
        "### Première présence du décor",
        "",
        "La distance est mesurée depuis l’ancre du start vers la cellule d’objet statique la plus proche. `r≤14` compte toutes les cellules d’objets statiques 1..127 dans ce rayon.",
        "",
        "| Groupe | Starts | Premier objet médian | Cellules dans r≤14 médianes | Cellules dans l’empreinte nominale |",
        "|---|---:|---:|---:|---:|",
    ]
    for group in ("2p", "20p"):
        overview = [
            row for record in maps if record["configuration"]["group"] == group
            for row in record["objects"]["start_overview"]
        ]
        lines.append(
            f"| {group} | {len(overview)} | {fmt(median_or_zero(row['first_world_object_distance'] for row in overview if row['first_world_object_distance'] is not None), 1)} hex | {fmt(median_or_zero(row['world_decor_r14'] for row in overview), 1)} | {fmt(sum(row['nominal_footprint_world_cells'] for row in overview))} |"
        )
    lines += [
        "",
        "### Densité locale comparée à la densité globale",
        "",
        "`world_decor` désigne ici les IDs statiques 1..127 non nuls. La densité locale est calculée dans le rayon HEX6 indiqué, après correction des bords de carte.",
        "",
        "| Groupe | Représentation | Densité globale médiane /1000 cellules | r10 | r25 | r50 | r100 |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for group in ("2p", "20p"):
        for representation in ("static", "runtime"):
            values = [row for row in object_local if row["group"] == group and row["representation"] == representation]
            if not values:
                continue
            lines.append(
                f"| {group} | `{representation}` | {fmt(values[0]['global_world_density_median_per_1000_map'], 2)} | {fmt(next(row['local_world_density_median_per_1000'] for row in values if row['radius'] == 10), 2)} | {fmt(next(row['local_world_density_median_per_1000'] for row in values if row['radius'] == 25), 2)} | {fmt(next(row['local_world_density_median_per_1000'] for row in values if row['radius'] == 50), 2)} | {fmt(next(row['local_world_density_median_per_1000'] for row in values if row['radius'] == 100), 2)} |"
            )
    lines += [
        "",
        "La densité autour des starts n’est pas inférieure à la densité globale : il n’y a donc pas d’évidence d’une zone stérile fixe de 14 hex dans le décor statique. La marge de sécurité actuelle du générateur est probablement trop restrictive pour reproduire l’apparence native, mais sa réduction doit attendre une mesure de hitbox/occupation dans le jeu.",
        "",
        "### Résumé par famille statique",
        "",
        "`IDs ≤5` et `IDs >14` indiquent respectivement les variantes dont au moins une cellule atteint cette distance dans le groupe. L’éloignement peut venir du terrain support ou du biome ; il n’est pas assimilé à une règle de réservation des starts.",
        "",
        "| Groupe | Famille | IDs présents | IDs ≤5 hex | IDs >14 hex | Plus proche | Empreinte nominale |",
        "|---|---|---:|---|---|---:|---:|",
    ]
    for group in ("2p", "20p"):
        family_rows = [
            row for row in object_families
            if row["group"] == group and row["representation"] == "static" and row["family"] not in {"unknown", "unknown_reserved"}
        ]
        family_rows.sort(key=lambda row: row["family"])
        for row in family_rows:
            lines.append(
                f"| {group} | `{row['family']}` | {fmt(row['ids_present'])} | {row['ids_within_5'] or '—'} | {row['ids_over_14'] or '—'} | {fmt(row['nearest_hex_min'])} | {fmt(row['nominal_footprint_cells'])} |"
            )
    lines += [
        "",
        "### IDs observés très près des starts",
        "",
        "Les IDs ci-dessous ont au moins une occurrence à cinq hex ou moins dans le corpus du groupe. La colonne `empreinte` compte les occurrences dans la fenêtre nominale validée de 33 cellules autour d’un start.",
        "",
        "| Groupe | ID | Nom | Famille | Plus proche | Starts ≤2 | Starts ≤5 | Empreinte nominale |",
        "|---|---:|---|---|---:|---:|---:|---:|",
    ]
    for group in ("2p", "20p"):
        selected = [
            row for row in object_proximity
            if row["group"] == group and row["representation"] == "static" and row["nearest_hex_global_min"] is not None and row["nearest_hex_global_min"] <= 5
        ]
        selected.sort(key=lambda row: (row["nearest_hex_global_min"], row["object_id"]))
        # Keep the report readable while leaving every ID in the CSV.
        for row in selected[:24]:
            lines.append(
                f"| {group} | {row['object_id']} | {row['name']} | `{row['family']}` | {fmt(row['nearest_hex_global_min'])} | {fmt(row['starts_within_2'])} | {fmt(row['starts_within_5'])} | {fmt(row['nominal_footprint_cells'])} |"
            )
    lines += [
        "",
        "### Lecture hitbox / objets décoratifs",
        "",
        "- Dans la fenêtre nominale de 33 cellules, le corpus contient 6 cellules d’objets statiques pour les 16 starts 2P et 26 cellules pour les 160 starts 20P. Elles sont principalement constituées de petites pierres, plantes, champignons et buissons ; aucun arbre adulte n’y apparaît.",
        "- Le byte 9 est conservé dans les CSV comme champ encore inconnu ; il ne signifie ni « bloquant » ni « sans hitbox ».",
        "- Quelques objets plus volumineux ou potentiellement bloquants apparaissent néanmoins à très faible distance dans le byte 14. Cela interdit de conclure que toute décoration proche est sans hitbox : la cellule d’ancrage et l’empreinte réelle peuvent différer, et le byte 9 ne permet pas encore de trancher.",
        "- Les familles très éloignées dans cette tranche sont surtout les roseaux, épaves, cactus, arbres morts, squelettes et palmiers. Leur éloignement est compatible avec des contraintes de biome/terrain support ; il ne permet pas d’isoler une règle de distance aux starts.",
        "- Conclusion opérationnelle : distinguer les familles décoratives et les arbres dans le placement peut être pertinent, mais la règle ne doit pas être figée comme « sans hitbox » avant calibration contrôlée.",
        "",
        "## Conclusion pour le générateur",
        "",
        "1. Conserver la chaîne terrain → supports → ressources/objets ; byte 17 est directement exploitable pour calibrer les ressources Legacy.",
        "2. Générer le décor initial depuis la représentation statique byte 14 et traiter byte 7 comme une observation runtime, jamais comme une vérité de placement initial.",
        "3. Ne pas imposer un halo objet vide de 14 hex autour des starts. La reproduction visuelle devra autoriser des petits décors proches, sous réserve de la validation d’occupation réelle.",
        "4. Ne pas retoucher encore les quotas Legacy à partir de cette seule tranche : les 16 cartes donnent une bonne base 768×768, mais les tailles plus petites et les cartes jouées doivent rester séparées.",
        "",
        "## Sorties détaillées",
        "",
        "- `native_resource_object_audit_16_768_2p20p.json` : corpus, mesures par carte et agrégats sans duplication des cellules.",
        "- `native_resource_object_audit_16_768_2p20p_manifest.json` : provenance, hashes et méthode.",
        "- `native_resource_object_audit_16_768_2p20p_resources_per_map.csv` et `_resource_families.csv` : ressources par carte et agrégats 2P/20P.",
        "- `native_resource_object_audit_16_768_2p20p_resource_components.csv` : une ligne par composante HEX6 de ressource.",
        "- `native_resource_object_audit_16_768_2p20p_resource_cells_partNN.csv` : table exhaustive sans perte, scindée en parties de 500 000 lignes de données avec en-tête répété.",
        "- `native_resource_object_audit_16_768_2p20p_objects_per_map.csv` : inventaire statique/runtime par ID et terrains supports.",
        "- `native_resource_object_audit_16_768_2p20p_object_start_proximity.csv` : distances et comptes par ID et par start.",
        "- `native_resource_object_audit_16_768_2p20p_object_proximity_aggregate.csv` et `_object_family_proximity.csv` : synthèses par ID/famille.",
        "- `native_resource_object_audit_16_768_2p20p_object_start_overview.csv`, `_object_start_local.csv` et `_object_runtime_differences.csv` : fenêtres nominales, densités locales et différences byte14/byte7.",
        "",
    ]
    return "\n".join(lines)


RESOURCE_CELL_ROWS_PER_PART = 500_000


def write_resource_cell_parts(
    output_dir: Path,
    prefix: str,
    maps: list[dict[str, Any]],
) -> list[str]:
    """Write the exhaustive cell table in GitHub-safe, lossless CSV parts."""

    fieldnames = [
        "map_id", "group", "x", "y", "family", "raw_byte17",
        "quantity", "terrain_id", "claim", "side",
    ]
    part_names: list[str] = []
    handle = None
    writer = None
    rows_in_part = RESOURCE_CELL_ROWS_PER_PART
    part_number = 0
    try:
        for record in maps:
            for row in resource_cell_rows(record):
                if handle is None or rows_in_part >= RESOURCE_CELL_ROWS_PER_PART:
                    if handle is not None:
                        handle.close()
                    part_number += 1
                    rows_in_part = 0
                    name = f"{prefix}_resource_cells_part{part_number:02d}.csv"
                    part_names.append(name)
                    handle = (output_dir / name).open(
                        "w", encoding="utf-8", newline=""
                    )
                    writer = csv.DictWriter(handle, fieldnames=fieldnames)
                    writer.writeheader()
                writer.writerow(row)
                rows_in_part += 1
    finally:
        if handle is not None:
            handle.close()
    return part_names


def build_outputs(maps: list[dict[str, Any]], output_dir: Path, generated_at: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    prefix = "native_resource_object_audit_16_768_2p20p"
    resource_aggregate = aggregate_resource_rows(maps)
    resource_local = aggregate_resource_local(maps)
    object_inventory = aggregate_object_inventory(maps)
    object_proximity = aggregate_object_proximity(maps)
    object_families = aggregate_object_families(object_proximity)
    object_local = aggregate_object_local(maps)

    manifest = {
        "schema_version": 1,
        "analysis": "native Legacy resource and start-adjacent object audit",
        "generated_at_utc": generated_at,
        "corpus": {
            "maps": len(maps),
            "sizes": sorted({record["configuration"]["side"] for record in maps}),
            "player_groups": dict(sorted(Counter(record["configuration"]["group"] for record in maps).items())),
            "starts": sum(len(record["configuration"]["starts"]) for record in maps),
        },
        "format": {
            "sav_version_expected": 11,
            "resource_field": "type-3 cell byte 17",
            "static_object_field": "type-3 cell byte 14",
            "runtime_object_field": "type-3 cell byte 7",
            "unknown_cell_byte9": "type-3 cell byte 9, semantics not decoded",
            "claim_field": "type-3 cell byte 8",
            "connectivity": "HEX6: (+1,0), (-1,0), (0,+1), (0,-1), (+1,+1), (-1,-1)",
            "nominal_start_footprint_cells": len(START_FOOTPRINT),
            "read_only": True,
        },
        "resource_classification": {
            "minerals": {f"0x{high:02X}": name for high, name in MINERAL_NAMES.items()},
            "fish": "byte17 high nibble 0, low nibble nonzero, terrain ID 0..7",
            "unknown": "nonzero resource value not matching a mineral or fish context",
        },
        "files": [
            record["source"] | {"map_id": record["map_id"], "checksum_ok": record["format"]["checksum_ok"]}
            for record in maps
        ],
    }

    json_maps: list[dict[str, Any]] = []
    for record in maps:
        json_maps.append({
            "map_id": record["map_id"],
            "source": record["source"],
            "format": record["format"],
            "configuration": record["configuration"],
            "resources": {
                "per_map": record["resources"]["per_map"],
                "local_starts": record["resources"]["local_starts"],
            },
            "objects": {
                "per_map": record["objects"]["per_map"],
                "proximity": record["objects"]["proximity"],
                "start_overview": record["objects"]["start_overview"],
                "start_local": record["objects"]["start_local"],
                "runtime_diff": record["objects"]["runtime_diff"],
            },
        })

    (output_dir / f"{prefix}_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output_dir / f"{prefix}.json").write_text(
        json.dumps({
            "schema_version": 1,
            "generated_at_utc": generated_at,
            "method": manifest["format"],
            "maps": json_maps,
            "aggregate": {
                "resources": resource_aggregate,
                "resources_local_starts": resource_local,
                "objects": object_inventory,
                "objects_proximity": object_proximity,
                "objects_families": object_families,
                "objects_local_density": object_local,
            },
            "external_detail_files": {
                "resource_components": f"{prefix}_resource_components.csv",
                "resource_cells": f"{prefix}_resource_cells_partNN.csv",
                "object_start_proximity": f"{prefix}_object_start_proximity.csv",
            },
        }, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    resource_map_rows = [
        flattened_resource_row(row)
        for record in maps for row in record["resources"]["per_map"]
    ]
    write_csv(output_dir / f"{prefix}_resources_per_map.csv", resource_map_rows)
    write_csv(output_dir / f"{prefix}_resource_families.csv", [flattened_resource_row(row) for row in resource_aggregate])
    write_csv(output_dir / f"{prefix}_resource_local_starts.csv", resource_local)
    write_csv(
        output_dir / f"{prefix}_resource_components.csv",
        (row for record in maps for row in record["resources"]["components"]),
    )
    write_resource_cell_parts(output_dir, prefix, maps)

    object_map_rows = [
        flattened_object_row(row)
        for record in maps for row in record["objects"]["per_map"]
    ]
    write_csv(output_dir / f"{prefix}_objects_per_map.csv", object_map_rows)
    write_csv(output_dir / f"{prefix}_object_proximity_aggregate.csv", object_proximity)
    write_csv(output_dir / f"{prefix}_object_family_proximity.csv", object_families)
    write_csv(
        output_dir / f"{prefix}_object_start_proximity.csv",
        (row for record in maps for row in record["objects"]["start_proximity"]),
    )
    write_csv(
        output_dir / f"{prefix}_object_start_overview.csv",
        (row for record in maps for row in record["objects"]["start_overview"]),
    )
    write_csv(
        output_dir / f"{prefix}_object_start_local.csv",
        (row for record in maps for row in record["objects"]["start_local"]),
    )
    diff_rows = []
    for record in maps:
        for transition in record["objects"]["runtime_diff"]["transitions"]:
            diff_rows.append({"map_id": record["map_id"], "group": record["configuration"]["group"], **transition})
    write_csv(output_dir / f"{prefix}_object_runtime_differences.csv", diff_rows)
    write_csv(output_dir / f"{prefix}_object_local_density_aggregate.csv", object_local)
    (output_dir / f"{prefix}.md").write_text(
        markdown_report(maps, resource_aggregate, resource_local, object_inventory, object_proximity, object_families, object_local, generated_at),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path, help="Dossier SAV, fichier SAV ou archive ZIP")
    parser.add_argument("--output-dir", type=Path, required=True, help="Dossier de références à créer")
    parser.add_argument("--limit", type=int, default=0, help="Limiter le nombre de SAV pour un essai rapide")
    args = parser.parse_args()
    sources = discover_sources(args.inputs)
    if args.limit:
        sources = sources[:max(0, int(args.limit))]
    if not sources:
        raise SystemExit("Aucun fichier SAV trouvé")
    maps: list[dict[str, Any]] = []
    for index, source in enumerate(sources, start=1):
        maps.append(analyze_map(source, index))
        print(f"Analysé {index}/{len(sources)}: {source['source_name']}::{source['member']}", flush=True)
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    build_outputs(maps, args.output_dir, generated_at)
    print(f"Analysé: {len(maps)} SAV")
    print(f"Départs: {sum(len(record['configuration']['starts']) for record in maps)}")
    print(f"Sorties: {args.output_dir}")
    print(f"Checksums OK: {sum(record['format']['checksum_ok'] for record in maps)}/{len(maps)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
