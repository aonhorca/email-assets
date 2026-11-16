"""Bake a drop shadow into 2x PNG exports, since most email clients ignore CSS box-shadow.

Matches `box-shadow: 0 2px 3px rgba(0,0,0,0.2)` at 1x. Output keeps the input width,
so the card shrinks slightly to leave room for the shadow.

Usage: python3 scripts/add_shadow.py <input.png> <output.png>
"""

import sys

from PIL import Image, ImageFilter

SCALE = 2
OFFSET_Y = 2 * SCALE
BLUR_SIGMA = 1.5 * SCALE
OPACITY = 0.2
PAD_X, PAD_TOP, PAD_BOTTOM = 4 * SCALE, 3 * SCALE, 6 * SCALE


def add_shadow(src: str, dst: str) -> None:
    card = Image.open(src).convert("RGBA")
    width = card.width
    card_w = width - 2 * PAD_X
    card_h = round(card.height * card_w / card.width)
    card = card.resize((card_w, card_h), Image.LANCZOS)

    canvas = Image.new("RGBA", (width, PAD_TOP + card_h + PAD_BOTTOM), (0, 0, 0, 0))

    alpha = card.getchannel("A").point(lambda a: round(a * OPACITY))
    shadow = Image.new("RGBA", card.size, (0, 0, 0, 255))
    shadow.putalpha(alpha)
    shadow_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    shadow_layer.paste(shadow, (PAD_X, PAD_TOP + OFFSET_Y))
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(BLUR_SIGMA))

    canvas.alpha_composite(shadow_layer)
    canvas.alpha_composite(card, (PAD_X, PAD_TOP))
    canvas.save(dst, optimize=True)
    print(f"{dst}: {canvas.width}x{canvas.height}")


if __name__ == "__main__":
    add_shadow(sys.argv[1], sys.argv[2])
