"""Pack Julien's two pixel-art drawings into a Windows multi-resolution ICO."""
from __future__ import annotations

import argparse
from io import BytesIO
from pathlib import Path
import struct

from PIL import Image


SIZES = (16, 20, 24, 32, 40, 48, 64, 128, 256)
ROOT = Path(__file__).resolve().parents[2]


def icon_bytes(assets: Path) -> bytes:
    with Image.open(assets/'Settlers3MapGen.png') as image:
        small = image.convert('RGBA')
    with Image.open(assets/'Settlers3MapGen_64.png') as image:
        large = image.convert('RGBA')
    if small.size != (16, 16) or large.size != (64, 64):
        raise ValueError('Expected the supplied 16×16 and 64×64 drawings.')
    payloads = []
    for size in SIZES:
        source = small if size <= 24 else large
        frame = source.resize((size, size), Image.Resampling.NEAREST)
        stream = BytesIO()
        frame.save(stream, format='PNG')
        payloads.append(stream.getvalue())
    offset = 6 + 16*len(SIZES)
    entries = []
    for size, payload in zip(SIZES, payloads):
        entries.append(struct.pack('<BBBBHHII', size % 256, size % 256, 0, 0,
                                   1, 32, len(payload), offset))
        offset += len(payload)
    return struct.pack('<HHH', 0, 1, len(SIZES)) + b''.join(entries + payloads)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    target = ROOT/'assets/Settlers3MapGen.ico'
    expected = icon_bytes(ROOT/'assets')
    if args.check:
        # Compare decoded pixels: PNG compression can differ between the
        # Windows and Linux zlib builds without changing the drawings.
        with Image.open(target) as actual, Image.open(BytesIO(expected)) as reference:
            valid = actual.ico.sizes() == reference.ico.sizes()
            if valid:
                valid = all(actual.ico.getimage((size, size)).convert('RGBA').tobytes()
                            == reference.ico.getimage((size, size)).convert('RGBA').tobytes()
                            for size in SIZES)
        if not valid:
            raise SystemExit('ICO pixels differ from the two source drawings; regenerate it.')
        print('PASS: application ICO matches both supplied drawings.')
    else:
        target.write_bytes(expected)
        print(target)


if __name__ == '__main__':
    main()
