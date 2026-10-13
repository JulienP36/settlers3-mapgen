"""User PNG catalogue, bounded image decoding and portable drawing state."""
from __future__ import annotations

import os
import re
import tempfile
import warnings
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

from ...generation.archetypes.profiles import MASK_LAYER_MANUAL_GRID_SIDES

MASK_SIDES = MASK_LAYER_MANUAL_GRID_SIDES
MAX_IMAGE_SIDE = 2048
MAX_IMAGE_BYTES = 32 * 1024 * 1024


class MaskImageError(ValueError):
    """A readable reason code, translated by the editor."""


def user_masks_directory() -> Path:
    return Path(os.environ.get('APPDATA') or Path.home()) / 'Settlers3MapGen' / 'masks'


def read_mask_image(path: Path, *, png_only: bool = False) -> Image.Image:
    """Fully decode bounded still images, flattening transparency onto black."""
    path = Path(path)
    try:
        if path.stat().st_size > MAX_IMAGE_BYTES:
            raise MaskImageError('too_large')
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(path) as source:
                if png_only and source.format != 'PNG':
                    raise MaskImageError('not_png')
                if getattr(source, 'n_frames', 1) != 1:
                    raise MaskImageError('animated')
                if min(source.size) < 1 or max(source.size) > MAX_IMAGE_SIDE:
                    raise MaskImageError('too_large')
                source.load()
                image = ImageOps.exif_transpose(source).convert('RGBA')
                background = Image.new('RGBA', image.size, (0, 0, 0, 255))
                return Image.alpha_composite(background, image).convert('L')
    except MaskImageError:
        raise
    except (OSError, ValueError, SyntaxError, Image.DecompressionBombError,
            Image.DecompressionBombWarning) as exc:
        raise MaskImageError('unreadable') from exc


def fit_mask(image: Image.Image, side: int, framing: str = 'pad') -> np.ndarray:
    if side not in MASK_SIDES:
        raise MaskImageError('resolution')
    gray = image.convert('L')
    size = (side, side)
    if framing == 'pad':
        result = ImageOps.pad(gray, size, method=Image.Resampling.LANCZOS, color=0)
    elif framing == 'crop':
        result = ImageOps.fit(gray, size, method=Image.Resampling.LANCZOS)
    elif framing == 'stretch':
        result = gray.resize(size, Image.Resampling.LANCZOS)
    else:
        raise MaskImageError('framing')
    return np.asarray(result, dtype=np.uint8).copy()


def square_resolution(image: Image.Image) -> int:
    return next((side for side in MASK_SIDES if side >= max(image.size)), MASK_SIDES[-1])


@dataclass
class CatalogueEntry:
    path: Path
    grid: np.ndarray | None
    original_size: tuple[int, int] | None
    issue: str | None = None


class MaskCatalogue:
    def __init__(self, directory: Path | None = None):
        self.directory = Path(directory) if directory is not None else user_masks_directory()
        self._cache: dict[Path, tuple[tuple[int, int, int], CatalogueEntry]] = {}

    def paths(self) -> list[Path]:
        self.directory.mkdir(parents=True, exist_ok=True)
        paths = sorted((p for p in self.directory.iterdir()
                        if p.is_file() and p.suffix.lower() == '.png'), key=lambda p: p.name.casefold())
        self._cache = {p: v for p, v in self._cache.items() if p in paths}
        return paths

    def entry(self, path: Path) -> CatalogueEntry:
        path = Path(path)
        try:
            stat = path.stat()
            signature = (stat.st_mtime_ns, stat.st_ctime_ns, stat.st_size)
            cached = self._cache.get(path)
            if cached and cached[0] == signature:
                return cached[1]
            image = read_mask_image(path, png_only=True)
            if image.width != image.height:
                entry = CatalogueEntry(path, None, image.size, 'rectangular')
            else:
                grid = fit_mask(image, square_resolution(image))
                issue = 'uniform' if grid.min() == grid.max() else None
                entry = CatalogueEntry(path, grid, image.size, issue)
        except (OSError, MaskImageError) as exc:
            return CatalogueEntry(path, None, None, str(exc) if isinstance(exc, MaskImageError) else 'unreadable')
        if len(self._cache) >= 128:
            self._cache.pop(next(iter(self._cache)))
        self._cache[path] = (signature, entry)
        return entry

    def _owned_path(self, path: Path) -> Path:
        path = Path(path)
        if path.parent.resolve() != self.directory.resolve() or path.is_symlink() or path.suffix.lower() != '.png':
            raise MaskImageError('protected')
        return path

    def save(self, name: str, grid: np.ndarray, *, overwrite: bool = False) -> Path:
        # Keep names portable and refuse path traversal/reserved Windows basenames.
        name = name.strip()
        if name.lower().endswith('.png'):
            name = name[:-4].strip()
        reserved = {'CON', 'PRN', 'AUX', 'NUL', *(f'COM{i}' for i in range(1, 10)), *(f'LPT{i}' for i in range(1, 10))}
        if not name or len(name) > 100 or re.search(r'[<>:"/\\|?*\x00-\x1f]', name) or name.endswith(('.', ' ')) or name.split('.')[0].upper() in reserved:
            raise MaskImageError('name')
        if grid.ndim != 2 or grid.shape[0] != grid.shape[1] or grid.shape[0] not in MASK_SIDES:
            raise MaskImageError('resolution')
        self.directory.mkdir(parents=True, exist_ok=True)
        path = self._owned_path(self.directory / (name + '.png'))
        if path.exists() and not overwrite:
            raise FileExistsError(path.name)
        fd, temporary = tempfile.mkstemp(prefix='.mask-', suffix='.tmp', dir=self.directory)
        try:
            with os.fdopen(fd, 'wb') as handle:
                Image.fromarray(grid.astype(np.uint8)).save(handle, format='PNG')
            if not overwrite and path.exists():
                raise FileExistsError(path.name)
            os.replace(temporary, path)
        finally:
            Path(temporary).unlink(missing_ok=True)
        self._cache.pop(path, None)
        return path

    def delete(self, path: Path) -> None:
        path = self._owned_path(path)
        path.unlink()
        self._cache.pop(path, None)


class MaskDrawing:
    """Bounded undo history: one snapshot per stroke or transformation."""
    def __init__(self, grid: np.ndarray):
        self.grid = np.asarray(grid, dtype=np.uint8).copy()
        self.undo_stack: list[np.ndarray] = []
        self.redo_stack: list[np.ndarray] = []

    def checkpoint(self):
        self.undo_stack.append(self.grid.copy())
        self.undo_stack = self.undo_stack[-32:]
        self.redo_stack.clear()

    def replace(self, grid: np.ndarray):
        self.checkpoint()
        self.grid = np.asarray(grid, dtype=np.uint8).copy()

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(self.grid.copy())
            self.grid = self.undo_stack.pop()

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(self.grid.copy())
            self.grid = self.redo_stack.pop()

    def fill(self, x: int, y: int, value: int) -> bool:
        """Fill the connected equal-gray region; scan spans, not individual pixels.

        Four-neighbor connectivity keeps diagonally touching regions separate.
        One history entry per click; no entry when the gray is unchanged.
        """
        height, width = self.grid.shape
        if not (0 <= x < width and 0 <= y < height):
            return False
        value = max(0, min(255, int(value)))
        original = int(self.grid[y, x])
        if original == value:
            return False
        self.checkpoint()
        pending = [(x, y)]
        while pending:
            x, y = pending.pop()
            if self.grid[y, x] != original:
                continue
            left = right = x
            while left > 0 and self.grid[y, left-1] == original:
                left -= 1
            while right+1 < width and self.grid[y, right+1] == original:
                right += 1
            self.grid[y, left:right+1] = value
            for row in (y-1, y+1):
                if not 0 <= row < height:
                    continue
                matches = self.grid[row, left:right+1] == original
                starts = matches.copy()
                starts[1:] &= ~matches[:-1]
                pending.extend((left+int(offset), row) for offset in np.flatnonzero(starts))
        return True

    def paint(self, x: float, y: float, radius: float, value: int, softness: float, shape: str = 'round'):
        side = self.grid.shape[0]
        radius = max(1.0, float(radius))
        x0, x1 = max(0, int(x-radius)), min(side, int(x+radius)+2)
        y0, y1 = max(0, int(y-radius)), min(side, int(y+radius)+2)
        rows, cols = np.ogrid[y0:y1, x0:x1]
        if shape == 'square':
            distance = np.maximum(np.abs(rows-y), np.abs(cols-x))
        else:
            distance = np.sqrt((rows-y)**2 + (cols-x)**2)
        inside = distance <= radius
        feather = radius * np.clip(softness, 0.0, 1.0)
        weight = inside.astype(np.float32) if feather == 0 else np.clip((radius-distance)/max(.01, feather), 0, 1)
        region = self.grid[y0:y1, x0:x1]
        region[:] = np.rint(region * (1-weight) + int(value)*weight).astype(np.uint8)

    def stroke(self, start, end, radius: float, value: int, softness: float, shape: str = 'round'):
        # Interpolate between motion events so fast strokes have no gaps.
        distance = float(np.hypot(end[0]-start[0], end[1]-start[1]))
        steps = max(1, int(np.ceil(distance / max(1.0, radius*.35))))
        for amount in np.linspace(0, 1, steps+1):
            self.paint(start[0]+(end[0]-start[0])*amount,
                       start[1]+(end[1]-start[1])*amount, radius, value, softness, shape)
