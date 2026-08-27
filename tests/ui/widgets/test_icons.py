import hashlib

from PIL import Image

from s3mapgen.application.ui.widgets.icons import _thumbnail_with_magnifier, selector_icon_image


SELECTOR_HASHES = {
    ("starts", "#cd1e10", 18): "1ebfa6ae348aad56eea76ce8208305a0643b7f74ba8d08ed59b8a97d6996444e",
    ("cross", "#e04444", 14): "fbbcfe338464e3d9d55869ca7b0077c2334664623f64f69c6c3d202df8dc2699",
    ("status_on", "#34a853", 18): "81601770598dd497dba49a4957f5887e6c3c16271221cf2108d283adaadd5982",
    ("status_off", "#7f858d", 18): "3f9cd3aa852b0c93febb1ae64ccd8ef5e3c71e34003e33877abf72f03790608c",
    ("warning", "#f2b84b", 20): "442351ff9626a4ac4223c30ea6eb25e783a2a0d80a1c8c34e41544101a9848b9",
}


def _pixel_hash(image):
    return hashlib.sha256(image.tobytes()).hexdigest()


def test_selector_drawings_keep_the_validated_pixel_signatures():
    for (kind, color, size), expected in SELECTOR_HASHES.items():
        assert _pixel_hash(selector_icon_image(color, kind, size)) == expected


def test_magnifier_states_remain_visually_distinct_and_transparent_at_edges():
    base = Image.new("RGBA", (180, 120), (31, 73, 109, 255))
    images = {
        state: _thumbnail_with_magnifier(base, state)
        for state in ("idle", "hover", "active", "preview_hover", "close_hover")
    }
    assert len({_pixel_hash(image) for image in images.values()}) == len(images)
    for image in images.values():
        assert image.getpixel((0, 0)) == base.getpixel((0, 0))
        assert image.getpixel((179, 119)) == base.getpixel((179, 119))
