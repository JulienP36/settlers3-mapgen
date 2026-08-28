"""Deterministic Pillow drawings used by Tk controls and map thumbnails."""

from PIL import Image, ImageDraw, ImageTk


def selector_icon_image(color, kind="dot", size=18):
    """Return the Pillow image behind a selector icon without requiring Tk."""
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = color
    if kind == "global":
        d.ellipse((2, 2, size - 3, size - 3), fill=c, outline="#111111", width=1)
        d.arc((5, 4, size - 6, size - 4), 80, 280, fill="#d7f2ff", width=1)
        d.line((3, size // 2, size - 4, size // 2), fill="#d7f2ff", width=1)
    elif kind == "starts":
        d.ellipse((3, 2, size - 4, size - 5), fill=c, outline="#111111", width=1)
        d.ellipse((7, 6, size - 8, size - 9), fill="#fff2df")
        d.polygon(((size // 2, size - 2), (size // 2 - 3, size - 7), (size // 2 + 3, size - 7)), fill=c, outline="#111111")
    elif kind == "initial_territory":
        d.polygon([(size // 2, 2), (size - 3, 5), (size - 4, size - 5), (size // 2, size - 2), (3, size - 5), (2, 5)], fill=c, outline="#111111")
        d.line((5, 7, 8, 11, 12, 6, 15, 10), fill="#fff1d2", width=2)
    elif kind == "heightmap":
        d.polygon([(2, size - 3), (size // 2, 2), (size - 3, size - 3)], fill=c, outline="#111111")
        d.line((size // 2, 4, size // 2 - 3, 9), fill="#f2eaff", width=2)
    elif kind == "resources":
        d.polygon([(size // 2, 2), (size - 3, size // 2), (size // 2, size - 3), (2, size // 2)], fill=c, outline="#111111")
        d.ellipse((7, 7, 10, 10), fill="#fff0c7")
    elif kind == "territories":
        d.polygon([(size // 2, 2), (size - 3, 5), (size - 4, 12), (size // 2, size - 2), (3, 12), (2, 5)], fill=c, outline="#111111")
        d.line((5, 8, 8, 11, 13, 5), fill="#e8ffe8", width=2)
    elif kind == "paths":
        d.line((2, size - 4, 6, 9, 9, 11, size - 3, 3), fill="#111111", width=5)
        d.line((2, size - 4, 6, 9, 9, 11, size - 3, 3), fill=c, width=3)
    elif kind == "crops":
        d.line((size // 2, size - 3, size // 2, 4), fill="#5a4716", width=2)
        d.ellipse((3, 4, 9, 8), fill=c, outline="#111111")
        d.ellipse((9, 7, 15, 11), fill=c, outline="#111111")
        d.ellipse((4, 10, 10, 14), fill=c, outline="#111111")
    elif kind == "heatmap":
        d.ellipse((2, 2, size - 3, size - 3), fill=c, outline="#111111")
        d.ellipse((5, 5, size - 6, size - 6), outline="#ffd9d9", width=2)
        d.ellipse((8, 8, 10, 10), fill="#ffffff")
    elif kind == "cross":
        d.line((3, 3, size - 4, size - 4), fill="#111111", width=5)
        d.line((size - 4, 3, 3, size - 4), fill="#111111", width=5)
        d.line((3, 3, size - 4, size - 4), fill=c, width=3)
        d.line((size - 4, 3, 3, size - 4), fill=c, width=3)
    elif kind == "flag_fr":
        x0, y0, x1, y1 = 2, 4, size - 3, size - 5
        third = max(1, (x1 - x0 + 1) // 3)
        d.rectangle((x0, y0, x0 + third - 1, y1), fill="#0055a4")
        d.rectangle((x0 + third, y0, x0 + 2 * third - 1, y1), fill="#ffffff")
        d.rectangle((x0 + 2 * third, y0, x1, y1), fill="#ef4135")
        d.rectangle((x0, y0, x1, y1), outline="#111111")
    elif kind == "flag_en":
        x0, y0, x1, y1 = 2, 4, size - 3, size - 5
        d.rectangle((x0, y0, x1, y1), fill="#21468b", outline="#111111")
        d.line((x0, y0, x1, y1), fill="#ffffff", width=4)
        d.line((x0, y1, x1, y0), fill="#ffffff", width=4)
        d.line((x0, y0, x1, y1), fill="#cf142b", width=2)
        d.line((x0, y1, x1, y0), fill="#cf142b", width=2)
        cy, cx = (y0 + y1) // 2, (x0 + x1) // 2
        d.rectangle((x0, cy - 2, x1, cy + 2), fill="#ffffff")
        d.rectangle((cx - 2, y0, cx + 2, y1), fill="#ffffff")
        d.rectangle((x0, cy - 1, x1, cy + 1), fill="#cf142b")
        d.rectangle((cx - 1, y0, cx + 1, y1), fill="#cf142b")
    elif kind == "flag_de":
        x0, y0, x1, y1 = 2, 4, size - 3, size - 5
        third = max(1, (y1 - y0 + 1) // 3)
        d.rectangle((x0, y0, x1, y0 + third - 1), fill="#000000")
        d.rectangle((x0, y0 + third, x1, y0 + 2 * third - 1), fill="#dd0000")
        d.rectangle((x0, y0 + 2 * third, x1, y1), fill="#ffce00")
        d.rectangle((x0, y0, x1, y1), outline="#111111")
    elif kind == "flag_es":
        x0, y0, x1, y1 = 2, 4, size - 3, size - 5
        quarter = max(1, (y1 - y0 + 1) // 4)
        d.rectangle((x0, y0, x1, y0 + quarter - 1), fill="#aa151b")
        d.rectangle((x0, y0 + quarter, x1, y1 - quarter), fill="#f1bf00")
        d.rectangle((x0, y1 - quarter + 1, x1, y1), fill="#aa151b")
        d.rectangle((x0, y0, x1, y1), outline="#111111")
    elif kind == "lock_closed":
        d.rounded_rectangle((4, 8, size - 4, size - 3), radius=2, fill=c, outline="#111111")
        d.arc((5, 2, size - 5, 11), 180, 360, fill=c, width=3)
        d.ellipse((8, 11, 10, 13), fill="#ffffff")
    elif kind == "lock_open":
        d.rounded_rectangle((4, 8, size - 4, size - 3), radius=2, fill=c, outline="#111111")
        d.arc((7, 2, size - 2, 11), 180, 315, fill=c, width=3)
        d.ellipse((8, 11, 10, 13), fill="#ffffff")
    elif kind == "status_on":
        d.ellipse((0, 0, size - 1, size - 1), fill=c, outline="#111111", width=1)
        d.line((size * .23, size * .52, size * .43, size * .71, size * .77, size * .29), fill="#ffffff", width=max(2, size // 6), joint="curve")
    elif kind == "status_off":
        d.ellipse((2, 2, size - 3, size - 3), fill="#ffffff", outline="#111111", width=1)
        d.ellipse((4, 4, size - 5, size - 5), fill=None, outline=c, width=max(2, size // 7))
    elif kind == "warning":
        d.polygon(((size // 2, 1), (size - 2, size - 3), (2, size - 3)), fill=c, outline="#111111")
        d.line((size // 2, 5, size // 2, size - 8), fill="#111111", width=max(2, size // 8))
        d.ellipse((size // 2 - 1, size - 6, size // 2 + 1, size - 4), fill="#111111")
    elif kind == "conflict":
        d.ellipse((1, 1, size - 2, size - 2), fill=c, outline="#111111", width=1)
        d.line((size // 2, 4, size // 2, size - 7), fill="#ffffff", width=max(2, size // 7))
        d.ellipse((size // 2 - 1, size - 5, size // 2 + 1, size - 3), fill="#ffffff")
    elif kind == "pending":
        d.ellipse((1, 1, size - 2, size - 2), fill=c, outline="#111111", width=1)
        cx, cy = size // 2, size // 2
        d.line((cx, 4, cx, cy), fill="#202124", width=max(2, size // 9))
        d.line((cx, cy, size - 5, cy + 3), fill="#202124", width=max(2, size // 9))
        d.ellipse((cx - 1, cy - 1, cx + 1, cy + 1), fill="#202124")
    elif kind == "blank":
        pass
    else:
        d.ellipse((1, 1, size - 2, size - 2), fill="#ffffff", outline="#111111", width=1)
        outline = "#444444" if c.lower() != "#101010" else "#eeeeee"
        d.ellipse((3, 3, size - 4, size - 4), fill=c, outline=outline, width=1)
    return im


def _selector_icon(master, color, kind="dot", size=18):
    """Create a colored Tk icon from the independently testable Pillow image."""
    return ImageTk.PhotoImage(selector_icon_image(color, kind, size), master=master)


def _history_heading_lock_icon(master, width=62, size=18):
    """Center a real lock inside the full History protection heading width."""
    im = Image.new("RGBA", (width, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x, c = (width - size) // 2, "#d84a3a"
    d.rounded_rectangle((x + 4, 8, x + size - 4, size - 3), radius=2, fill=c, outline="#111111")
    d.arc((x + 5, 2, x + size - 5, 11), 180, 360, fill=c, width=3)
    d.ellipse((x + 8, 11, x + 10, 13), fill="#ffffff")
    return ImageTk.PhotoImage(im, master=master)


def _thumbnail_with_magnifier(image, state="idle"):
    """Composite a large translucent magnifier without an opaque backing box."""
    base = image.convert("RGBA")
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    short = max(1, min(base.size))
    radius = max(12, round(short * .17))
    handle = max(10, round(short * .14))
    cx, cy = base.width // 2 - 4, base.height // 2 - 4
    alpha = {"idle": 58, "hover": 205, "active": 238, "preview_hover": 236, "close_hover": 245}.get(state, 58)
    accent = {
        "idle": (245, 248, 252, alpha), "hover": (138, 190, 255, alpha),
        "active": (72, 210, 128, alpha), "preview_hover": (178, 132, 255, alpha),
        "close_hover": (255, 184, 92, alpha),
    }.get(state, (245, 248, 252, alpha))
    shadow = (0, 0, 0, min(170, alpha + 42))
    fill = (12, 20, 28, 22 if state == "idle" else 50)
    box = (cx - radius, cy - radius, cx + radius, cy + radius)
    width = max(3, round(short * .035))
    draw.ellipse((box[0] + 2, box[1] + 2, box[2] + 2, box[3] + 2), fill=(0, 0, 0, 28), outline=shadow, width=width + 2)
    draw.ellipse(box, fill=fill, outline=accent, width=width)
    start = (cx + round(radius * .68), cy + round(radius * .68))
    end = (start[0] + handle, start[1] + handle)
    draw.line((start[0] + 2, start[1] + 2, end[0] + 2, end[1] + 2), fill=shadow, width=width + 3)
    draw.line((*start, *end), fill=accent, width=width, joint="curve")
    if state in ("active", "preview_hover"):
        inner = max(4, radius // 3)
        draw.ellipse((cx - inner, cy - inner, cx + inner, cy + inner), outline=(255, 255, 255, 225), width=max(2, width // 2))
        if state == "preview_hover":
            draw.ellipse((cx - 2, cy - 2, cx + 2, cy + 2), fill=(255, 255, 255, 225))
    elif state == "close_hover":
        inner, cross = max(5, radius // 3), max(3, max(5, radius // 3) // 2)
        draw.line((cx - cross, cy - cross, cx + cross, cy + cross), fill=(255, 255, 255, 235), width=max(2, width // 2))
        draw.line((cx + cross, cy - cross, cx - cross, cy + cross), fill=(255, 255, 255, 235), width=max(2, width // 2))
    return Image.alpha_composite(base, overlay)


def _history_role_icon(master, roles, size=15):
    """Draw compact padlocks for Viewer, comparison and Manual roles."""
    roles = tuple(roles)
    gap = 1
    width = max(1, len(roles) * (size + gap) - gap)
    im = Image.new("RGBA", (width, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    colors = {"V": "#2f7ed8", "A": "#34a853", "B": "#9b59d0", "M": "#d59b28"}
    for index, role in enumerate(roles):
        x = index * (size + gap)
        color = colors.get(role, "#7b8088")
        d.arc((x + 4, 0, x + size - 5, size - 6), 180, 360, fill="#111111", width=4)
        d.arc((x + 4, 0, x + size - 5, size - 6), 180, 360, fill=color, width=2)
        d.rounded_rectangle((x + 1, 6, x + size - 2, size - 1), radius=2, fill=color, outline="#111111", width=1)
        d.text((x + size // 2, 10), role, fill="#ffffff", anchor="mm", stroke_width=1, stroke_fill="#111111")
    return ImageTk.PhotoImage(im, master=master)
