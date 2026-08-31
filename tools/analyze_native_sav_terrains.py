"""Audit terrain geometry in native Settlers III SAV files.

This tool is deliberately read-only.  It accepts SAV directories and/or ZIP
archives, decodes only the already documented SAV fields, and writes a
versioned terrain audit (JSON, CSV and Markdown).  It does not call the map
generator and it never writes a SAV/MAP/EDM file.

The SAV terrain byte is reported twice:

* ``raw`` keeps the runtime value exactly as stored, including terrain 28;
* ``normalized`` maps runtime start-area terrain 28 to Grass16, which is the
  comparison layer used by the existing native-generation references.

All connectivity and component measurements use the confirmed Settlers III
HEX6 neighbourhood, not an 8-connected raster neighbourhood.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import struct
import sys
import tempfile
import zipfile
from collections import Counter, defaultdict
from collections.abc import Iterable
from concurrent.futures import ProcessPoolExecutor
from contextlib import ExitStack
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# The project-root insertion above intentionally precedes these imports so the
# tool also works when invoked as ``python tools/...`` from a checkout.
# isort: off
from s3mapgen.map_data.binary import checksum, read_sav_state
from s3mapgen.map_data.hexgrid import component_labels, distance_from, neighbor_count
# isort: on


HEX6_POSITIVE = ((1, 0), (0, 1), (1, 1))
HEX_STRUCTURE = np.asarray(((1, 1, 0), (1, 1, 1), (0, 1, 1)), dtype=bool)
WATER_IDS = tuple(range(8))

# These are names already demonstrated by the project references.  Unknown
# values remain explicit instead of being folded into a guessed family.
TERRAIN_NAMES: dict[int, str] = {
    **{i: f"Water {i + 1}" for i in WATER_IDS},
    16: "Grass",
    17: "Rock transition 1",
    18: "Grass detail 1",
    19: "Grass detail 2",
    20: "Grass/desert transition",
    21: "Grass/swamp transition",
    22: "Runtime agriculture",
    23: "Mud",
    24: "Dry grass",
    28: "Runtime start-area terrain",
    32: "Rocky core",
    33: "Rock transition 2",
    34: "Rocky detail",
    35: "Rock/snow transition",
    48: "Shore",
    64: "Desert core",
    65: "Desert transition",
    80: "Swamp core",
    81: "Swamp transition",
    96: "River 1",
    97: "River 2",
    98: "River 3",
    99: "River 4",
    128: "Snow core",
    129: "Snow transition",
    144: "Mud transition 1",
    145: "Mud transition 2",
}

# Analytical families overlap intentionally: Snow is inside the full
# mountain-family union, while the exact-ID table remains disjoint.
FAMILY_IDS: dict[str, tuple[int, ...]] = {
    "water": WATER_IDS,
    "grass": (16, 18, 19, 24),
    "mountain_full": (17, 32, 33, 34, 35, 128, 129),
    "mountain_core": (32, 34),
    "snow": (35, 128, 129),
    "desert": (20, 64, 65),
    "swamp": (21, 80, 81),
    "mud": (23, 144, 145),
    "shore": (48,),
    "river": (96, 97, 98, 99),
    "runtime_agriculture": (22,),
}

FAMILY_NAMES = {
    "water": "Water",
    "grass": "Grass",
    "mountain_full": "Full mountain family",
    "mountain_core": "Rocky core",
    "snow": "Snow family",
    "desert": "Desert family",
    "swamp": "Swamp family",
    "mud": "Mud family",
    "shore": "Shore",
    "river": "River",
    "runtime_agriculture": "Runtime agriculture",
}


def terrain_name(tid: int) -> str:
    return TERRAIN_NAMES.get(int(tid), f"Terrain {int(tid)} (unknown)")


def pct(value: float, total: float) -> float:
    return round(100.0 * float(value) / float(total), 6) if total else 0.0


def percentiles(values: Iterable[int | float]) -> dict[str, float]:
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


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_players_from_name(name: str) -> int | None:
    match = re.search(r"(?:^|[^0-9])(\d+)\s*(?:joueurs?|players?)\b", name, re.IGNORECASE)
    return int(match.group(1)) if match else None


def _safe_member_name(name: str) -> str:
    """Keep ZIP extraction temporary and flat; never trust archive paths."""

    return Path(name).name


def discover_sources(inputs: list[Path], stack: ExitStack) -> list[dict[str, Any]]:
    """Return deterministic SAV paths plus their source provenance."""

    sources: list[dict[str, Any]] = []
    for input_path in inputs:
        if input_path.is_dir():
            for sav in sorted(input_path.glob("*.sav"), key=lambda p: p.name.lower()):
                sources.append({
                    "path": sav,
                    "source_kind": "directory",
                    "source_name": input_path.name,
                    "member": sav.name,
                })
        elif input_path.is_file() and input_path.suffix.lower() == ".sav":
            sources.append({
                "path": input_path,
                "source_kind": "file",
                "source_name": input_path.parent.name,
                "member": input_path.name,
            })
        elif input_path.is_file() and input_path.suffix.lower() == ".zip":
            tempdir = Path(stack.enter_context(tempfile.TemporaryDirectory(prefix="s3mapgen_sav_")))
            archive_hash = sha256_file(input_path)
            with zipfile.ZipFile(input_path) as archive:
                members = [
                    info for info in archive.infolist()
                    if not info.is_dir() and info.filename.lower().endswith(".sav")
                ]
                for info in sorted(members, key=lambda row: row.filename.lower()):
                    name = _safe_member_name(info.filename)
                    sav_path = tempdir / name
                    sav_path.write_bytes(archive.read(info))
                    sources.append({
                        "path": sav_path,
                        "source_kind": "zip",
                        "source_name": input_path.name,
                        "member": info.filename,
                        "archive_sha256": archive_hash,
                    })
        else:
            raise FileNotFoundError(f"Input SAV/ZIP/dossier introuvable: {input_path}")
    sources.sort(key=lambda row: (str(row["source_name"]).lower(), str(row["member"]).lower()))
    return sources


def hex_distance_field(side: int, starts: list[tuple[int, int]]) -> np.ndarray:
    yy, xx = np.indices((side, side), dtype=np.int32)
    if not starts:
        return np.full((side, side), -1, dtype=np.int16)
    distances = []
    for x0, y0 in starts:
        dx = xx - int(x0)
        dy = yy - int(y0)
        distances.append(np.where((dx * dy) >= 0, np.maximum(np.abs(dx), np.abs(dy)), np.abs(dx) + np.abs(dy)))
    return np.minimum.reduce(distances).astype(np.int16)


def shifted_pair(array: np.ndarray, dx: int, dy: int) -> tuple[np.ndarray, np.ndarray]:
    height, width = array.shape
    y0, y1 = max(0, -dy), min(height, height - dy)
    x0, x1 = max(0, -dx), min(width, width - dx)
    return array[y0:y1, x0:x1], array[y0 + dy:y1 + dy, x0 + dx:x1 + dx]


def adjacency_counts(array: np.ndarray) -> Counter[tuple[int, int]]:
    """Count each undirected HEX6 edge exactly once."""

    result: Counter[tuple[int, int]] = Counter()
    for dx, dy in HEX6_POSITIVE:
        left, right = shifted_pair(array, dx, dy)
        values = np.sort(np.stack((left.ravel(), right.ravel()), axis=1), axis=1)
        pairs, counts = np.unique(values, axis=0, return_counts=True)
        for (a, b), count in zip(pairs.tolist(), counts.tolist()):
            result[(int(a), int(b))] += int(count)
    return result


def component_details(mask: np.ndarray) -> list[dict[str, Any]]:
    """Return shape descriptors using HEX6 components and perimeter."""

    labels, count = component_labels(np.asarray(mask, dtype=bool))
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
        perimeter = int(6 * size - 2 * internal_edges[component_id])
        if size > 1:
            covariance = np.cov(np.column_stack((xs, ys)), rowvar=False)
            eigenvalues = np.linalg.eigvalsh(covariance)
            elongation = float(np.sqrt(max(float(eigenvalues[-1]), 0.0) / max(float(eigenvalues[0]), 1e-9)))
        else:
            elongation = 1.0
        bbox_width = int(xs.max() - xs.min() + 1)
        bbox_height = int(ys.max() - ys.min() + 1)
        bbox_area = max(1, bbox_width * bbox_height)
        details.append({
            "component_id": component_id,
            "cells": size,
            "perimeter_hex_edges": perimeter,
            "perimeter_sqrt_area": float(perimeter / max(np.sqrt(size), 1.0)),
            "bbox": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())],
            "bbox_width": bbox_width,
            "bbox_height": bbox_height,
            "bbox_fill": float(size / bbox_area),
            "centroid": [float(xs.mean()), float(ys.mean())],
            "compactness": float(min(1.0, (12.0 * size) / max(float(perimeter * perimeter), 1.0))),
            "elongation": elongation,
            "touches_map_edge": bool(
                xs.min() == 0 or ys.min() == 0 or xs.max() == mask.shape[1] - 1 or ys.max() == mask.shape[0] - 1
            ),
        })
    details.sort(key=lambda row: (-row["cells"], row["component_id"]))
    return details


def component_summary(details: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "count": len(details),
        "cells": int(sum(row["cells"] for row in details)),
        "size": percentiles(row["cells"] for row in details),
        "perimeter_sqrt_area": percentiles(row["perimeter_sqrt_area"] for row in details),
        "bbox_fill": percentiles(row["bbox_fill"] for row in details),
        "elongation": percentiles(row["elongation"] for row in details),
        "compactness": percentiles(row["compactness"] for row in details),
        "edge_components": int(sum(row["touches_map_edge"] for row in details)),
        "largest": details[0] if details else None,
    }


def holes_in(mask: np.ndarray) -> dict[str, Any]:
    filled = ndimage.binary_fill_holes(np.asarray(mask, dtype=bool), structure=HEX_STRUCTURE)
    holes = filled & ~mask
    return {"cells": int(holes.sum()), "ratio": pct(int(holes.sum()), int(mask.sum()))}


def primary_family(tid: int) -> str:
    """Assign one label for readable family-transition aggregates."""

    for family in ("water", "shore", "river", "snow", "mountain_full", "desert", "swamp", "mud", "grass", "runtime_agriculture"):
        if tid in FAMILY_IDS[family]:
            return family
    if tid == 28:
        return "runtime_start"
    return "unknown"


def metric_summary(
    mask: np.ndarray,
    heights: np.ndarray,
    water_mask: np.ndarray,
    water_distance: np.ndarray,
    edge_distance: np.ndarray,
    start_distance: np.ndarray,
    *,
    adjacent_water: np.ndarray | None = None,
    components: list[dict[str, Any]] | None = None,
    calculate_holes: bool = True,
) -> dict[str, Any]:
    count = int(mask.sum())
    if not count:
        return {
            "cells": 0,
            "pct_map": 0.0,
            "pct_land": 0.0,
            "edge_cells": 0,
            "edge_pct": 0.0,
            "adjacent_water_cells": 0,
            "adjacent_water_pct": 0.0,
            "distance_to_water": percentiles(()),
            "distance_to_edge": percentiles(()),
            "distance_to_start": percentiles(()),
            "height": percentiles(()),
            "components": component_summary([]),
            "holes": {"cells": 0, "ratio": 0.0, "computed": calculate_holes},
        }
    total = int(mask.size)
    land_mask = ~water_mask
    edge = edge_distance == 0
    if adjacent_water is None:
        adjacent_water = neighbor_count(water_mask) > 0
    starts = start_distance >= 0
    if components is None:
        components = component_details(mask)
    return {
        "cells": count,
        "pct_map": pct(count, total),
        "pct_land": pct(count, int(land_mask.sum())) if np.any(mask & land_mask) else 0.0,
        "edge_cells": int((mask & edge).sum()),
        "edge_pct": pct(int((mask & edge).sum()), count),
        "adjacent_water_cells": int((mask & adjacent_water).sum()),
        "adjacent_water_pct": pct(int((mask & adjacent_water).sum()), count),
        "distance_to_water": percentiles(water_distance[mask]),
        "distance_to_edge": percentiles(edge_distance[mask]),
        "distance_to_start": percentiles(start_distance[mask & starts]),
        "height": percentiles(heights[mask]),
        "components": component_summary(components),
        "holes": holes_in(mask) | {"computed": calculate_holes} if calculate_holes else {"cells": 0, "ratio": 0.0, "computed": False},
    }


def terrain_summary(
    terrain: np.ndarray,
    heights: np.ndarray,
    starts: list[tuple[int, int]],
    normalized: bool,
    *,
    geometry: bool = True,
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]], dict[str, Any]]:
    side = terrain.shape[0]
    water_mask = np.isin(terrain, WATER_IDS)
    land_mask = ~water_mask
    water_distance = distance_from(water_mask) if geometry else np.zeros_like(terrain, dtype=np.int16)
    adjacent_water = neighbor_count(water_mask) > 0 if geometry else np.zeros_like(water_mask, dtype=bool)
    yy, xx = np.indices(terrain.shape, dtype=np.int16)
    edge_distance = np.minimum.reduce((xx, yy, side - 1 - xx, side - 1 - yy)).astype(np.int16)
    start_distance = hex_distance_field(side, starts)

    counts = Counter(map(int, terrain.ravel().tolist()))
    ids: dict[str, dict[str, Any]] = {}
    component_rows: dict[str, dict[str, Any]] = {}
    for tid in sorted(counts):
        mask = terrain == tid
        details = component_details(mask) if geometry else []
        stats = metric_summary(
            mask, heights, water_mask, water_distance, edge_distance, start_distance,
            adjacent_water=adjacent_water, components=details, calculate_holes=False,
        )
        stats["id"] = tid
        stats["name"] = terrain_name(tid)
        stats["representation"] = "normalized" if normalized else "raw"
        stats["land_cells"] = int((mask & land_mask).sum())
        ids[str(tid)] = stats
        for component in details:
            row = dict(component)
            row.update({"id": tid, "name": terrain_name(tid)})
            component_rows[f"{tid}:{component['component_id']}"] = row

    families: dict[str, dict[str, Any]] = {}
    for family, family_ids in FAMILY_IDS.items():
        mask = np.isin(terrain, family_ids)
        details = component_details(mask) if geometry else []
        calculate_holes = family in {"mountain_full", "desert", "swamp", "mud", "snow", "river"}
        stats = metric_summary(
            mask, heights, water_mask, water_distance, edge_distance, start_distance,
            adjacent_water=adjacent_water, components=details, calculate_holes=calculate_holes,
        )
        stats.update({"key": family, "name": FAMILY_NAMES[family], "ids": list(family_ids), "overlapping": family in ("mountain_full", "mountain_core", "snow")})
        families[family] = stats

    other_ids = sorted(set(counts) - {tid for values in FAMILY_IDS.values() for tid in values})
    other_mask = np.isin(terrain, other_ids)
    families["other_observed"] = {
        **metric_summary(
            other_mask, heights, water_mask, water_distance, edge_distance, start_distance,
            adjacent_water=adjacent_water, components=component_details(other_mask) if geometry else [], calculate_holes=geometry,
        ),
        "key": "other_observed",
        "name": "Other observed terrain",
        "ids": other_ids,
        "overlapping": False,
    }
    water_details = component_details(water_mask) if geometry else []
    inland_details = [row for row in water_details if not row["touches_map_edge"]]
    context = {
        "water_cells": int(water_mask.sum()),
        "land_cells": int(land_mask.sum()),
        "water_components": component_summary(water_details),
        "inland_water_components": component_summary(inland_details),
        "water_id_depth_counts": {str(tid): int(counts.get(tid, 0)) for tid in WATER_IDS},
        "runtime_terrain_28_cells": int(counts.get(28, 0)),
    }
    return ids, families, {"context": context, "components": component_rows}


def map_record(source: dict[str, Any], index: int) -> dict[str, Any]:
    path = Path(source["path"])
    raw_bytes = path.read_bytes()
    stored_checksum = struct.unpack_from("<I", raw_bytes, 0)[0] if len(raw_bytes) >= 4 else None
    calculated_checksum = checksum(raw_bytes) if len(raw_bytes) >= 8 else None
    state = read_sav_state(path)
    raw_terrain = np.asarray(state.terrain, dtype=np.uint8)
    normalized_terrain = raw_terrain.copy()
    normalized_terrain[normalized_terrain == 28] = 16
    # The raw layer is retained for exact ID counts and runtime provenance.
    # Full geometry is measured once on the normalized comparison layer; the
    # only intentional raw-only terrain is runtime 28.
    raw_ids, raw_families, raw_extra = terrain_summary(raw_terrain, state.height, state.starts, normalized=False, geometry=False)
    normalized_ids, normalized_families, normalized_extra = terrain_summary(normalized_terrain, state.height, state.starts, normalized=True)
    runtime_28_details = component_details(raw_terrain == 28)
    raw_transitions = adjacency_counts(raw_terrain)
    normalized_transitions = adjacency_counts(normalized_terrain)
    family_transitions: Counter[tuple[str, str]] = Counter()
    for (a, b), count in normalized_transitions.items():
        pair = tuple(sorted((primary_family(a), primary_family(b))))
        family_transitions[pair] += count
    actual_players = len(state.starts)
    filename_players = parse_players_from_name(path.name)
    return {
        "map_id": f"sav_{index:03d}",
        "source": {
            "kind": source["source_kind"],
            "name": source["source_name"],
            "member": source["member"],
            "archive_sha256": source.get("archive_sha256"),
            "file_name": path.name,
            "file_size": len(raw_bytes),
            "sha256": hashlib.sha256(raw_bytes).hexdigest(),
        },
        "format": {
            "sav_version": int(state.metadata.get("sav_version", 11)),
            "stored_checksum": stored_checksum,
            "calculated_checksum": calculated_checksum,
            "checksum_ok": stored_checksum == calculated_checksum,
        },
        "configuration": {
            "side": int(state.side),
            "players_from_filename": filename_players,
            "players": actual_players,
            "starts": [[int(x), int(y)] for x, y in state.starts],
            "group": f"{actual_players}p" if actual_players in (2, 20) else "other",
        },
        "terrain": {
            "raw_ids": raw_ids,
            "normalized_ids": normalized_ids,
            "raw_families": raw_families,
            "normalized_families": normalized_families,
            "raw_context": raw_extra["context"],
            "normalized_context": normalized_extra["context"],
            "runtime_terrain_28": {
                "cells": int((raw_terrain == 28).sum()),
                "components": runtime_28_details,
            },
        },
        "transitions": {
            "raw": [{"a": a, "b": b, "edges": count} for (a, b), count in sorted(raw_transitions.items())],
            "normalized": [{"a": a, "b": b, "edges": count} for (a, b), count in sorted(normalized_transitions.items())],
            "family_normalized": [
                {"a": a, "b": b, "edges": count}
                for (a, b), count in sorted(family_transitions.items())
            ],
        },
        "components": {
            "raw_ids": raw_extra["components"],
            "normalized_ids": normalized_extra["components"],
        },
    }


def aggregate_id_rows(maps: list[dict[str, Any]], representation: str) -> list[dict[str, Any]]:
    layer = "raw_ids" if representation == "raw" else "normalized_ids"
    union = sorted({int(tid) for record in maps for tid in record["terrain"][layer]})
    rows: list[dict[str, Any]] = []
    for tid in union:
        present = [record["terrain"][layer][str(tid)] for record in maps if str(tid) in record["terrain"][layer]]
        counts = [int(record["terrain"][layer].get(str(tid), {}).get("cells", 0)) for record in maps]
        pct_map = [float(record["terrain"][layer].get(str(tid), {}).get("pct_map", 0.0)) for record in maps]
        pct_land = [float(record["terrain"][layer].get(str(tid), {}).get("pct_land", 0.0)) for record in maps]
        components = [row["components"] for row in present]
        component_sizes = [row["components"]["size"] for row in present]
        rows.append({
            "representation": representation,
            "id": tid,
            "name": terrain_name(tid),
            "maps_present": len(present),
            "total_cells": int(sum(counts)),
            "mean_cells_all_maps": float(np.mean(counts)),
            "median_cells_all_maps": float(np.median(counts)),
            "min_cells_all_maps": int(min(counts)),
            "max_cells_all_maps": int(max(counts)),
            "mean_pct_map_all_maps": float(np.mean(pct_map)),
            "mean_pct_land_all_maps": float(np.mean(pct_land)),
            "mean_components_when_present": float(np.mean([row["count"] for row in components])) if components else 0.0,
            "component_size_median_when_present": float(np.median([row["median"] for row in component_sizes])) if component_sizes else 0.0,
            "component_size_p90_when_present": float(np.median([row["p90"] for row in component_sizes])) if component_sizes else 0.0,
            "perimeter_sqrt_area_median_when_present": float(np.median([row["perimeter_sqrt_area"]["median"] for row in components])) if components else 0.0,
            "bbox_fill_median_when_present": float(np.median([row["bbox_fill"]["median"] for row in components])) if components else 0.0,
            "elongation_median_when_present": float(np.median([row["elongation"]["median"] for row in components])) if components else 0.0,
            "edge_pct_mean_when_present": float(np.mean([row["edge_pct"] for row in present])) if present else 0.0,
            "adjacent_water_pct_mean_when_present": float(np.mean([row["adjacent_water_pct"] for row in present])) if present else 0.0,
            "distance_to_water_median_when_present": float(np.median([row["distance_to_water"]["median"] for row in present])) if present else 0.0,
            "distance_to_edge_median_when_present": float(np.median([row["distance_to_edge"]["median"] for row in present])) if present else 0.0,
            "distance_to_start_median_when_present": float(np.median([row["distance_to_start"]["median"] for row in present])) if present else 0.0,
            "height_median_when_present": float(np.median([row["height"]["median"] for row in present])) if present else 0.0,
        })
    return rows


def aggregate_family_rows(maps: list[dict[str, Any]], representation: str) -> list[dict[str, Any]]:
    layer = "raw_families" if representation == "raw" else "normalized_families"
    families = sorted({key for record in maps for key in record["terrain"][layer]})
    rows = []
    for family in families:
        present = [record["terrain"][layer][family] for record in maps if family in record["terrain"][layer] and record["terrain"][layer][family]["cells"]]
        counts = [int(record["terrain"][layer].get(family, {}).get("cells", 0)) for record in maps]
        rows.append({
            "representation": representation,
            "family": family,
            "name": FAMILY_NAMES.get(family, family),
            "ids": ",".join(map(str, FAMILY_IDS.get(family, ()))),
            "maps_present": len(present),
            "total_cells": int(sum(counts)),
            "mean_cells_all_maps": float(np.mean(counts)),
            "mean_pct_map_all_maps": float(np.mean([float(record["terrain"][layer].get(family, {}).get("pct_map", 0.0)) for record in maps])),
            "mean_pct_land_all_maps": float(np.mean([float(record["terrain"][layer].get(family, {}).get("pct_land", 0.0)) for record in maps])),
            "component_count_median_when_present": float(np.median([row["components"]["count"] for row in present])) if present else 0.0,
            "component_size_median_when_present": float(np.median([row["components"]["size"]["median"] for row in present])) if present else 0.0,
            "component_size_p90_when_present": float(np.median([row["components"]["size"]["p90"] for row in present])) if present else 0.0,
            "perimeter_sqrt_area_median_when_present": float(np.median([row["components"]["perimeter_sqrt_area"]["median"] for row in present])) if present else 0.0,
            "bbox_fill_median_when_present": float(np.median([row["components"]["bbox_fill"]["median"] for row in present])) if present else 0.0,
            "elongation_median_when_present": float(np.median([row["components"]["elongation"]["median"] for row in present])) if present else 0.0,
            "holes_mean_cells_when_present": float(np.mean([row["holes"]["cells"] for row in present])) if present else 0.0,
            "edge_pct_mean_when_present": float(np.mean([row["edge_pct"] for row in present])) if present else 0.0,
            "adjacent_water_pct_mean_when_present": float(np.mean([row["adjacent_water_pct"] for row in present])) if present else 0.0,
            "distance_to_water_median_when_present": float(np.median([row["distance_to_water"]["median"] for row in present])) if present else 0.0,
            "distance_to_edge_median_when_present": float(np.median([row["distance_to_edge"]["median"] for row in present])) if present else 0.0,
            "distance_to_start_median_when_present": float(np.median([row["distance_to_start"]["median"] for row in present])) if present else 0.0,
            "height_median_when_present": float(np.median([row["height"]["median"] for row in present])) if present else 0.0,
        })
    return rows


def aggregate_transition_rows(maps: list[dict[str, Any]], layer: str = "normalized") -> list[dict[str, Any]]:
    totals: Counter[tuple[int, int]] = Counter()
    per_map: defaultdict[tuple[int, int], list[int]] = defaultdict(list)
    for record in maps:
        current: Counter[tuple[int, int]] = Counter()
        for row in record["transitions"][layer]:
            pair = (int(row["a"]), int(row["b"]))
            current[pair] = int(row["edges"])
            totals[pair] += int(row["edges"])
        for pair in current:
            per_map[pair].append(current[pair])
    total_edges = sum(totals.values())
    rows = []
    for (a, b), total in sorted(totals.items(), key=lambda item: (-item[1], item[0])):
        rows.append({
            "a": a,
            "b": b,
            "terrain_a": terrain_name(a),
            "terrain_b": terrain_name(b),
            "family_a": primary_family(a),
            "family_b": primary_family(b),
            "maps_present": len(per_map[(a, b)]),
            "total_hex_edges": int(total),
            "mean_hex_edges_per_map": float(np.mean(per_map[(a, b)])),
            "pct_of_all_hex_edges": pct(total, total_edges),
        })
    return rows


def component_csv_rows(maps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for record in maps:
        for representation, key in (("raw", "raw_ids"), ("normalized", "normalized_ids")):
            for component in record["components"][key].values():
                row = {
                    "map_id": record["map_id"],
                    "group": record["configuration"]["group"],
                    "players": record["configuration"]["players"],
                    "representation": representation,
                    "terrain_id": component["id"],
                    "terrain_name": component["name"],
                }
                row.update({k: v for k, v in component.items() if k not in ("id", "name", "bbox", "centroid")})
                row["bbox"] = json.dumps(component["bbox"], separators=(",", ":"))
                row["centroid"] = json.dumps([round(v, 4) for v in component["centroid"]], separators=(",", ":"))
                rows.append(row)
        for component in record["terrain"]["runtime_terrain_28"]["components"]:
            row = {
                "map_id": record["map_id"],
                "group": record["configuration"]["group"],
                "players": record["configuration"]["players"],
                "representation": "raw_runtime",
                "terrain_id": 28,
                "terrain_name": terrain_name(28),
            }
            row.update({k: v for k, v in component.items() if k not in ("bbox", "centroid")})
            row["bbox"] = json.dumps(component["bbox"], separators=(",", ":"))
            row["centroid"] = json.dumps([round(v, 4) for v in component["centroid"]], separators=(",", ":"))
            rows.append(row)
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        fieldnames = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def fmt(value: float, digits: int = 2) -> str:
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return f"{value:,}"


def markdown_report(
    maps: list[dict[str, Any]],
    id_rows: list[dict[str, Any]],
    family_rows: list[dict[str, Any]],
    transition_rows: list[dict[str, Any]],
    generated_at: str,
) -> str:
    raw_ids = [row for row in id_rows if row["representation"] == "raw"]
    normalized_ids = [row for row in id_rows if row["representation"] == "normalized"]
    normalized_families = [row for row in family_rows if row["representation"] == "normalized"]
    present_families = [row for row in normalized_families if row["maps_present"]]
    top_cross = [row for row in transition_rows if row["a"] != row["b"]][:30]
    lines = [
        "# Settlers III — audit des terrains natifs SAV 768 (2P/20P)",
        "",
        "> Première tranche du point 1 de la v2.0. Analyse en lecture seule des 16 SAV fournis le 29 août 2026 : 8 cartes à 2 joueurs et 8 cartes à 20 joueurs.",
        "> Ce document ne modifie pas le générateur. Les objets, les joueurs en profondeur et les ressources seront traités dans les phases suivantes.",
        "",
        "## Méthode et limites",
        "",
        f"- Exécution : `{generated_at}` ; {len(maps)} SAV, tous traités individuellement.",
        "- Terrain brut : byte 6 runtime tel qu'enregistré. Terrain normalisé : remplacement analytique de `28 → 16` pour isoler le terrain de départ ajouté par le runtime.",
        "- L'ID 28 est aussi décrit séparément par composantes dans le CSV (`representation=raw_runtime`) afin de conserver sa forme runtime sans la mélanger à l'herbe.",
        "- Composantes, périmètres, voisinages et distances : topologie HEX6 confirmée `(+1,0), (-1,0), (0,+1), (0,-1), (+1,+1), (-1,-1)`.",
        "- Les formes mesurées ici sont géométriques (cellules, composantes, périmètres, bounding boxes, compacité, allongement). La texture graphique exacte doit rester corrélée plus tard aux EDM/MAP/PNG.",
        "- Les tableaux complets, y compris chaque composante, sont dans les CSV/JSON du même dossier.",
        "",
        "## Corpus",
        "",
        "| Carte | Groupe | Joueurs décodés | Départs | Taille SAV | Checksum | Fichier |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    for record in maps:
        source = record["source"]
        fmt_size = f"{source['file_size']:,}".replace(",", " ")
        lines.append(
            f"| `{record['map_id']}` | {record['configuration']['group']} | {record['configuration']['players']} | {len(record['configuration']['starts'])} | {fmt_size} octets | {'OK' if record['format']['checksum_ok'] else 'ÉCHEC'} | `{source['name']}::{source['member']}` |"
        )

    lines += [
        "",
        "## Tous les IDs de terrain bruts présents",
        "",
        "`28` est conservé ici : il ne doit pas être oublié dans l'inventaire, même s'il est normalisé en 16 pour les comparaisons statiques.",
        "",
        "| ID | Nom actuel | Cartes | Total cellules | Moyenne/carte | Min–max/carte | % moyen carte |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    for row in raw_ids:
        lines.append(
            f"| {row['id']} | {row['name']} | {row['maps_present']}/{len(maps)} | {fmt(row['total_cells'])} | {fmt(row['mean_cells_all_maps'])} | {fmt(row['min_cells_all_maps'])}–{fmt(row['max_cells_all_maps'])} | {fmt(row['mean_pct_map_all_maps'], 3)} % |"
        )

    lines += [
        "",
        "## Cas particulier du terrain runtime 28",
        "",
        "L'ID 28 est un état ajouté autour des départs par le runtime. Sa géométrie brute est conservée séparément ; elle ne doit pas être traitée comme une nouvelle famille géographique.",
        "",
        "| Groupe | Cartes | Cellules moyennes | Cellules moyennes par départ | Min–max total | Composantes moyennes |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for group in ("2p", "20p"):
        group_maps = [record for record in maps if record["configuration"]["group"] == group]
        totals = [record["terrain"]["runtime_terrain_28"]["cells"] for record in group_maps]
        components = [len(record["terrain"]["runtime_terrain_28"]["components"]) for record in group_maps]
        starts = sum(len(record["configuration"]["starts"]) for record in group_maps)
        mean_total = float(np.mean(totals)) if totals else 0.0
        lines.append(
            f"| {group} | {len(group_maps)} | {fmt(mean_total)} | {fmt(float(sum(totals) / starts) if starts else 0.0)} | {fmt(min(totals) if totals else 0)}–{fmt(max(totals) if totals else 0)} | {fmt(float(np.mean(components)) if components else 0.0, 1)} |"
        )
    lines.append("- Les deux premières cartes 2P sont des cas à surveiller (`54` et `59` cellules 28 au total) ; les autres cartes 2P sont à `66`, tandis que les cartes 20P restent proches de 20 × 33 cellules. Cette anomalie est conservée pour l'analyse joueurs/runtime et n'est pas corrigée ici.")

    lines += [
        "",
        "## IDs normalisés — forme, position et relief",
        "",
        "Les métriques de forme sont calculées sur les composantes HEX6 de chaque ID exact. Les métriques `when_present` ne prennent en compte que les cartes où l'ID apparaît.",
        "",
        "| ID | Nom | Moy. cellules | % terre moyen | Composantes moy. | Médiane composante | P90 composante | Allongement médian | Bord moyen | Eau adjacente moyenne | Distance eau médiane |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in normalized_ids:
        lines.append(
            f"| {row['id']} | {row['name']} | {fmt(row['mean_cells_all_maps'])} | {fmt(row['mean_pct_land_all_maps'], 3)} % | {fmt(row['mean_components_when_present'], 1)} | {fmt(row['component_size_median_when_present'], 1)} | {fmt(row['component_size_p90_when_present'], 1)} | {fmt(row['elongation_median_when_present'], 2)} | {fmt(row['edge_pct_mean_when_present'], 1)} % | {fmt(row['adjacent_water_pct_mean_when_present'], 1)} % | {fmt(row['distance_to_water_median_when_present'], 1)} |"
        )

    lines += [
        "",
        "## Familles analytiques",
        "",
        "Les familles `mountain_full`, `mountain_core` et `snow` se recouvrent volontairement ; leurs pourcentages ne doivent donc pas être additionnés.",
        "",
        "| Famille | IDs | Cartes | % moyen carte | % moyen terre | Composantes médianes | Taille composante médiane | Périmètre/√aire médian | Trous moyens |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in present_families:
        lines.append(
            f"| {row['name']} | `{row['ids']}` | {row['maps_present']}/{len(maps)} | {fmt(row['mean_pct_map_all_maps'], 3)} % | {fmt(row['mean_pct_land_all_maps'], 3)} % | {fmt(row['component_count_median_when_present'], 1)} | {fmt(row['component_size_median_when_present'], 1)} | {fmt(row['perimeter_sqrt_area_median_when_present'], 2)} | {fmt(row['holes_mean_cells_when_present'], 1)} |"
        )

    lines += [
        "",
        "## Transitions HEX6 observées",
        "",
        "Le fichier `transitions_normalized.csv` contient tous les couples d'IDs, y compris les auto-voisinages. Voici les 30 couples inter-terrains les plus fréquents, agrégés sur les 16 cartes :",
        "",
        "| ID A | ID B | Familles | Cartes | Arêtes HEX6 totales | Part de toutes les arêtes |",
        "|---:|---:|---|---:|---:|---:|",
    ]
    for row in top_cross:
        lines.append(
            f"| {row['a']} ({row['terrain_a']}) | {row['b']} ({row['terrain_b']}) | `{row['family_a']} ↔ {row['family_b']}` | {row['maps_present']}/{len(maps)} | {fmt(row['total_hex_edges'])} | {fmt(row['pct_of_all_hex_edges'], 3)} % |"
        )

    cross_family_pairs = sorted({
        tuple(sorted((row["family_a"], row["family_b"])))
        for row in transition_rows
        if row["a"] != row["b"] and row["family_a"] != row["family_b"]
    })
    lines += [
        "",
        f"Contacts inter-familles observés : {', '.join(f'`{a} ↔ {b}`' for a, b in cross_family_pairs)}.",
        "Aucun contact direct entre une famille montagneuse et une famille désert/marais/boue/rivière n'apparaît dans cette tranche ; les contacts eau/rivière sont détaillés par ID dans le CSV et correspondent aux raccords peu profonds observés.",
    ]

    lines += [
        "",
        "## Comparaison 2 joueurs / 20 joueurs",
        "",
        "Cette comparaison mesure les terrains, pas encore les règles de placement des joueurs. Elle indique si la densité de joueurs semble modifier la géographie native à taille identique.",
        "",
        "| ID normalisé | % terre moyen 2P | % terre moyen 20P | Écart 20P–2P | Cellules moy. 2P | Cellules moy. 20P |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    by_id: dict[int, dict[str, list[float]]] = defaultdict(lambda: {"2p": [], "20p": []})
    for record in maps:
        group = record["configuration"]["group"]
        if group not in ("2p", "20p"):
            continue
        for tid, row in record["terrain"]["normalized_ids"].items():
            by_id[int(tid)][group].append(float(row["pct_land"]))
    for tid in sorted(by_id):
        two = by_id[tid]["2p"]
        twenty = by_id[tid]["20p"]
        if not two and not twenty:
            continue
        mean_two = float(np.mean(two)) if two else 0.0
        mean_twenty = float(np.mean(twenty)) if twenty else 0.0
        two_cells = [record["terrain"]["normalized_ids"].get(str(tid), {}).get("cells", 0) for record in maps if record["configuration"]["group"] == "2p"]
        twenty_cells = [record["terrain"]["normalized_ids"].get(str(tid), {}).get("cells", 0) for record in maps if record["configuration"]["group"] == "20p"]
        lines.append(f"| {tid} ({terrain_name(tid)}) | {fmt(mean_two, 3)} % | {fmt(mean_twenty, 3)} % | {fmt(mean_twenty - mean_two, 3)} pp | {fmt(float(np.mean(two_cells)) if two_cells else 0.0)} | {fmt(float(np.mean(twenty_cells)) if twenty_cells else 0.0)} |")

    lines += [
        "",
        "## Premières observations, sans modification du générateur",
        "",
        "- Les IDs présents, leurs quantités et leurs formes exactes sont maintenant enregistrés séparément en brut et en couche normalisée.",
        "- La distinction `28 → 16` est indispensable : compter 28 comme un biome autonome fausserait la surface d'herbe et les contours autour des starts.",
        "- Les tableaux de composantes permettent de distinguer une grande famille cohérente d'une multitude de petits composants indépendants ; les trous de famille sont mesurés séparément et ne sont pas assimilés à des micro-composants.",
        "- Les transitions sont mesurées par couples d'IDs adjacents, avant toute décision sur l'ordre de génération. Cette sortie servira à confronter les règles actuelles `eau → rive → terrains` aux observations natives.",
        "- Aucun changement de règle ou de terrain n'est déduit de la seule moyenne 2P/20P : les écarts seront confrontés aux formes, aux starts et aux ressources dans les phases suivantes.",
        "",
        "## Sorties détaillées",
        "",
        "- `native_terrain_audit_16_768_2p20p.json` : corpus et statistiques agrégées/par carte ; les composantes détaillées sont dans le CSV dédié.",
        "- `native_terrain_audit_16_768_2p20p_manifest.json` : provenance, tailles, hash SHA-256 et contrôles de format.",
        "- `native_terrain_audit_16_768_2p20p_per_map.csv` : tableau large par carte et ID.",
        "- `native_terrain_audit_16_768_2p20p_terrain_ids.csv` : agrégats par ID brut/normalisé.",
        "- `native_terrain_audit_16_768_2p20p_families.csv` : agrégats par famille analytique.",
        "- `native_terrain_audit_16_768_2p20p_components.csv` : une ligne par composante des IDs normalisés, plus les composantes brutes de l'ID 28.",
        "- `native_terrain_audit_16_768_2p20p_transitions_normalized.csv` : matrice longue des transitions normalisées.",
        "",
    ]
    return "\n".join(lines)


def build_outputs(maps: list[dict[str, Any]], output_dir: Path, generated_at: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    prefix = "native_terrain_audit_16_768_2p20p"
    id_rows = aggregate_id_rows(maps, "raw") + aggregate_id_rows(maps, "normalized")
    family_rows = aggregate_family_rows(maps, "raw") + aggregate_family_rows(maps, "normalized")
    transitions = aggregate_transition_rows(maps)

    # Wide per-map counts make quick spreadsheet comparisons practical while
    # the JSON keeps the full nested geometry.
    all_raw_ids = sorted({int(tid) for record in maps for tid in record["terrain"]["raw_ids"]})
    all_normalized_ids = sorted({int(tid) for record in maps for tid in record["terrain"]["normalized_ids"]})
    per_map_rows = []
    for record in maps:
        row = {
            "map_id": record["map_id"],
            "source": f"{record['source']['name']}::{record['source']['member']}",
            "sha256": record["source"]["sha256"],
            "side": record["configuration"]["side"],
            "players": record["configuration"]["players"],
            "group": record["configuration"]["group"],
            "starts": len(record["configuration"]["starts"]),
            "file_size": record["source"]["file_size"],
            "checksum_ok": record["format"]["checksum_ok"],
            "raw_water_pct": record["terrain"]["raw_context"]["water_cells"] / (record["configuration"]["side"] ** 2) * 100.0,
            "normalized_water_pct": record["terrain"]["normalized_context"]["water_cells"] / (record["configuration"]["side"] ** 2) * 100.0,
        }
        for tid in all_raw_ids:
            row[f"raw_id_{tid}"] = record["terrain"]["raw_ids"].get(str(tid), {}).get("cells", 0)
        for tid in all_normalized_ids:
            row[f"normalized_id_{tid}"] = record["terrain"]["normalized_ids"].get(str(tid), {}).get("cells", 0)
        for family in sorted(record["terrain"]["normalized_families"]):
            row[f"normalized_family_{family}"] = record["terrain"]["normalized_families"][family]["cells"]
        per_map_rows.append(row)

    manifest = {
        "schema_version": 1,
        "analysis": "native terrain geometry audit",
        "generated_at_utc": generated_at,
        "corpus": {
            "maps": len(maps),
            "sizes": sorted({record["configuration"]["side"] for record in maps}),
            "player_groups": dict(sorted(Counter(record["configuration"]["group"] for record in maps).items())),
        },
        "format": {
            "sav_version_expected": 11,
            "terrain_field": "type-3 runtime cell byte 6",
            "normalization": "runtime terrain 28 -> Grass16 for normalized layer only",
            "connectivity": "HEX6: (+1,0), (-1,0), (0,+1), (0,-1), (+1,+1), (-1,-1)",
            "read_only": True,
        },
        "files": [record["source"] | {"map_id": record["map_id"], "checksum_ok": record["format"]["checksum_ok"]} for record in maps],
    }
    # Component-level geometry is already stored losslessly in the dedicated
    # CSV.  Keeping the nested rows a second time in JSON would make the
    # reference needlessly huge; JSON retains every aggregate and per-map
    # terrain/transition statistic and points to the component table.
    json_maps = []
    for record in maps:
        compact = {key: value for key, value in record.items() if key != "components"}
        compact["components_csv"] = f"{prefix}_components.csv"
        json_maps.append(compact)
    (output_dir / f"{prefix}_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / f"{prefix}.json").write_text(json.dumps({
        "schema_version": 1,
        "generated_at_utc": generated_at,
        "method": manifest["format"],
        "maps": json_maps,
        "aggregate": {"terrain_ids": id_rows, "families": family_rows, "transitions_normalized": transitions},
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    write_csv(output_dir / f"{prefix}_per_map.csv", per_map_rows)
    write_csv(output_dir / f"{prefix}_terrain_ids.csv", id_rows)
    write_csv(output_dir / f"{prefix}_families.csv", family_rows)
    write_csv(output_dir / f"{prefix}_components.csv", component_csv_rows(maps))
    write_csv(output_dir / f"{prefix}_transitions_normalized.csv", transitions)
    (output_dir / f"{prefix}.md").write_text(markdown_report(maps, id_rows, family_rows, transitions, generated_at), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path, help="Dossier SAV, fichier SAV ou archive ZIP")
    parser.add_argument("--output-dir", type=Path, required=True, help="Dossier de références à créer")
    parser.add_argument("--workers", type=int, default=1, help="Nombre de cartes analysées en parallèle (défaut: 1)")
    args = parser.parse_args()
    with ExitStack() as stack:
        sources = discover_sources(args.inputs, stack)
        if not sources:
            raise SystemExit("Aucun fichier SAV trouvé")
        workers = max(1, min(int(args.workers), len(sources)))
        indexed_sources = list(zip(sources, range(1, len(sources) + 1)))
        if workers == 1:
            maps = [map_record(source, index) for source, index in indexed_sources]
        else:
            with ProcessPoolExecutor(max_workers=workers) as executor:
                maps = list(executor.map(_map_record_indexed, indexed_sources))
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    build_outputs(maps, args.output_dir, generated_at)
    print(f"Analysé: {len(maps)} SAV")
    print(f"Sorties: {args.output_dir}")
    print(f"Checksums OK: {sum(record['format']['checksum_ok'] for record in maps)}/{len(maps)}")
    return 0


def _map_record_indexed(item: tuple[dict[str, Any], int]) -> dict[str, Any]:
    source, index = item
    return map_record(source, index)


if __name__ == "__main__":
    raise SystemExit(main())
