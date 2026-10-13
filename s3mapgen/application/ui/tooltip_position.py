"""Position tooltips beside a screen-coordinate anchor without covering it."""


def tooltip_position(x, y, width, height, screen_width, screen_height):
    left, top = int(x) + 12, int(y) + 18
    if left + width + 6 > screen_width:
        left = int(x) - width - 12
    if top + height + 6 > screen_height:
        top = int(y) - height - 12
    return (max(6, min(left, max(6, screen_width - width - 6))),
            max(6, min(top, max(6, screen_height - height - 6))))
