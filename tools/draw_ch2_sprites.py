#!/usr/bin/env /opt/homebrew/bin/python3
"""
Generate all Chapter 2 (Bicycle Dash) sprites as pixel art PNGs.

Sprites are drawn pixel-by-pixel for Game Boy Color constraints:
- Max 4 colors per sprite (3 opaque + transparent)
- Dimensions are multiples of 8
- RGBA PNGs with alpha=0 for empty pixels
"""

import os
from PIL import Image

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'chapter2')

# Color palettes (R, G, B, A)
T = (0, 0, 0, 0)  # Transparent

# Palette 0: Bicycle/Rider
SKIN   = (232, 190, 150, 255)
BLUE   = (48, 80, 160, 255)     # School uniform
RED    = (192, 48, 48, 255)     # Backpack
DARK   = (40, 40, 48, 255)     # Bike frame, hair, wheels
HAIR   = DARK

# Palette 1: Warm obstacles (dog, vendor)
BROWN  = (160, 96, 48, 255)
TAN    = (216, 168, 112, 255)
DKBROWN= (80, 48, 24, 255)

# Palette 2: Cool obstacles (bus, pothole, puddle)
GREEN  = (48, 144, 112, 255)   # Bus body
TEAL   = (80, 192, 160, 255)   # Bus highlight
DKGRAY = (48, 48, 48, 255)
GRAY   = (128, 128, 128, 255)
LTGRAY = (176, 176, 176, 255)
DKBLUE = (32, 64, 128, 255)    # Puddle dark
LTBLUE = (96, 160, 224, 255)   # Puddle light
MEDBLUE= (64, 112, 176, 255)   # Puddle mid

# Palette 3: Collectibles
GOLD   = (240, 200, 64, 255)
WHITE  = (248, 248, 240, 255)
CREAM  = (240, 224, 176, 255)
CBLUE  = (64, 96, 176, 255)    # Textbook blue


def make_image(w, h, pixels):
    """Create RGBA image from 2D pixel array."""
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    for y, row in enumerate(pixels):
        for x, color in enumerate(row):
            if color != T:
                img.putpixel((x, y), color)
    return img


def draw_bike_frame1():
    """Bicycle + rider frame 1: right pedal UP. 16x16."""
    # 3 opaque colors: SKIN, BLUE, RED (backpack + bike/hair share RED-dark)
    S = SKIN
    B = BLUE
    R = RED    # backpack, hair, bike frame all use this
    _ = T

    pixels = [
        #0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 0
        [_, _, _, _, _, R, R, R, _, _, _, _, _, _, _, _],  # 1  hair
        [_, _, _, _, R, R, R, R, R, _, _, _, _, _, _, _],  # 2  hair
        [_, _, _, _, R, S, S, S, R, _, _, _, _, _, _, _],  # 3  face
        [_, _, _, _, _, S, S, S, _, _, _, _, _, _, _, _],  # 4  face
        [_, _, _, _, _, _, S, _, _, _, _, _, _, _, _, _],  # 5  neck
        [_, _, _, _, R, R, B, B, B, _, _, _, _, _, _, _],  # 6  backpack+torso
        [_, _, _, _, R, R, B, B, B, _, _, _, _, _, _, _],  # 7  backpack+torso
        [_, _, _, _, R, _, B, B, S, _, _, _, _, _, _, _],  # 8  backpack, arms, hand
        [_, _, _, _, _, _, B, B, _, R, _, _, _, _, _, _],  # 9  waist, handlebar
        [_, _, _, _, _, _, B, _, R, R, R, _, _, _, _, _],  # 10 leg up, bike frame
        [_, _, _, _, _, R, R, R, R, _, R, R, _, _, _, _],  # 11 bike frame
        [_, _, _, R, R, _, R, _, _, R, _, _, R, R, _, _],  # 12 wheels + frame
        [_, _, R, R, R, R, B, _, _, _, R, R, R, R, R, _],  # 13 wheel, pedal leg down
        [_, _, _, R, R, _, _, _, _, _, _, R, R, R, _, _],  # 14 wheels
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 15
    ]
    return make_image(16, 16, pixels)


def draw_bike_frame2():
    """Bicycle + rider frame 2: right pedal DOWN. 16x16."""
    S = SKIN
    B = BLUE
    R = RED    # backpack, hair, bike frame all use this
    _ = T

    pixels = [
        #0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 0
        [_, _, _, _, _, R, R, R, _, _, _, _, _, _, _, _],  # 1  hair
        [_, _, _, _, R, R, R, R, R, _, _, _, _, _, _, _],  # 2  hair
        [_, _, _, _, R, S, S, S, R, _, _, _, _, _, _, _],  # 3  face
        [_, _, _, _, _, S, S, S, _, _, _, _, _, _, _, _],  # 4  face
        [_, _, _, _, _, _, S, _, _, _, _, _, _, _, _, _],  # 5  neck
        [_, _, _, _, R, R, B, B, B, _, _, _, _, _, _, _],  # 6  backpack+torso
        [_, _, _, _, R, R, B, B, B, _, _, _, _, _, _, _],  # 7  backpack+torso
        [_, _, _, _, R, _, B, B, S, _, _, _, _, _, _, _],  # 8  backpack, arms
        [_, _, _, _, _, _, B, B, _, R, _, _, _, _, _, _],  # 9  waist, handlebar
        [_, _, _, _, _, _, _, B, R, R, R, _, _, _, _, _],  # 10 bike frame, leg down
        [_, _, _, _, _, R, R, R, R, _, R, R, _, _, _, _],  # 11 bike frame
        [_, _, _, R, R, _, R, B, _, R, _, _, R, R, _, _],  # 12 wheels, pedal leg
        [_, _, R, R, R, R, _, _, _, _, R, R, R, R, R, _],  # 13 wheel
        [_, _, _, R, R, _, _, _, _, _, _, R, R, R, _, _],  # 14 wheels
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 15
    ]
    return make_image(16, 16, pixels)


def draw_pothole():
    """Pothole obstacle. 8x8. Colors: DKGRAY, GRAY, LTGRAY.
    Irregular crack/hole shape — dark center, gray edges, crack lines."""
    D = DKGRAY
    G = GRAY
    L = LTGRAY
    _ = T

    pixels = [
        [_, _, _, _, _, _, _, _],
        [_, _, _, L, _, _, _, _],
        [_, _, L, G, G, _, _, _],
        [_, L, G, D, D, G, L, _],
        [_, _, G, D, D, D, G, _],
        [_, _, L, G, D, G, _, _],
        [_, _, _, _, L, _, L, _],
        [_, _, _, _, _, _, _, _],
    ]
    return make_image(8, 8, pixels)


def draw_puddle():
    """Puddle obstacle. 8x8. Colors: DKBLUE, MEDBLUE, LTBLUE.
    Oval water reflection shape — light blue center, darker edges."""
    D = DKBLUE
    M = MEDBLUE
    L = LTBLUE
    _ = T

    pixels = [
        [_, _, _, _, _, _, _, _],
        [_, _, _, M, M, _, _, _],
        [_, _, M, L, L, M, _, _],
        [_, M, L, L, L, L, M, _],
        [_, M, D, L, L, D, M, _],
        [_, _, M, D, D, M, _, _],
        [_, _, _, M, M, _, _, _],
        [_, _, _, _, _, _, _, _],
    ]
    return make_image(8, 8, pixels)


def draw_dog_frame1():
    """Stray dog frame 1: legs forward. 16x8, facing LEFT."""
    B = BROWN
    N = TAN
    D = DKBROWN
    _ = T

    pixels = [
        #0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
        [_, _, _, _, _, _, _, _, _, _, _, _, D, D, _, _],  # 0  ear
        [_, _, _, _, _, _, _, _, _, _, _, D, N, D, D, _],  # 1  head
        [_, _, _, _, _, B, B, B, B, B, B, D, N, D, _, _],  # 2  body + snout
        [_, _, _, _, B, B, B, B, B, B, B, B, D, _, _, _],  # 3  body
        [_, _, _, _, B, B, B, B, B, B, B, B, _, _, _, _],  # 4  body
        [_, _, _, _, _, B, _, _, _, _, B, _, _, _, _, _],  # 5  legs
        [_, _, _, _, B, _, _, _, _, _, _, B, _, _, _, _],  # 6  legs forward
        [_, _, _, D, _, _, _, _, _, _, _, _, D, _, _, _],  # 7  paws
    ]
    return make_image(16, 8, pixels)


def draw_dog_frame2():
    """Stray dog frame 2: legs back. 16x8, facing LEFT."""
    B = BROWN
    N = TAN
    D = DKBROWN
    _ = T

    pixels = [
        #0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
        [_, _, _, _, _, _, _, _, _, _, _, _, D, D, _, _],  # 0  ear
        [_, _, _, _, _, _, _, _, _, _, _, D, N, D, D, _],  # 1  head
        [_, _, _, _, _, B, B, B, B, B, B, D, N, D, _, _],  # 2  body + snout
        [_, _, _, _, B, B, B, B, B, B, B, B, D, _, _, _],  # 3  body
        [_, _, _, _, B, B, B, B, B, B, B, B, _, _, _, _],  # 4  body
        [_, _, _, _, _, _, B, _, _, B, _, _, _, _, _, _],  # 5  legs
        [_, _, _, _, _, _, _, B, B, _, _, _, _, _, _, _],  # 6  legs back
        [_, _, _, _, _, _, D, _, _, D, _, _, _, _, _, _],  # 7  paws
    ]
    return make_image(16, 8, pixels)


def draw_vendor():
    """Vendor stall (BBQ cart). 16x16. Colors: BROWN, TAN, DKBROWN."""
    B = BROWN
    N = TAN
    D = DKBROWN
    _ = T

    pixels = [
        #0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
        [_, _, _, _, _, _, N, _, _, N, _, _, _, _, _, _],  # 0  smoke wisps
        [_, _, _, _, _, N, _, _, _, _, N, _, _, _, _, _],  # 1  smoke
        [_, _, _, _, _, _, N, _, N, _, _, _, _, _, _, _],  # 2  smoke
        [_, _, _, D, D, D, D, D, D, D, D, D, D, _, _, _],  # 3  roof top
        [_, _, _, D, N, N, N, N, N, N, N, N, D, _, _, _],  # 4  awning
        [_, _, _, D, D, D, D, D, D, D, D, D, D, _, _, _],  # 5  awning bottom
        [_, _, _, B, B, B, B, B, B, B, B, B, B, _, _, _],  # 6  cart body
        [_, _, _, B, D, D, D, D, D, D, D, D, B, _, _, _],  # 7  grill area
        [_, _, _, B, D, N, D, N, D, N, D, N, B, _, _, _],  # 8  food on grill
        [_, _, _, B, D, D, D, D, D, D, D, D, B, _, _, _],  # 9  grill
        [_, _, _, B, B, B, B, B, B, B, B, B, B, _, _, _],  # 10 cart body
        [_, _, _, B, B, N, N, N, N, N, N, B, B, _, _, _],  # 11 sign area
        [_, _, _, B, B, B, B, B, B, B, B, B, B, _, _, _],  # 12 cart bottom
        [_, _, _, _, B, _, _, _, _, _, _, B, _, _, _, _],  # 13 legs
        [_, _, _, D, D, D, _, _, _, _, D, D, D, _, _, _],  # 14 wheels
        [_, _, _, _, D, _, _, _, _, _, _, D, _, _, _, _],  # 15
    ]
    return make_image(16, 16, pixels)


def draw_bus():
    """City bus. 24x16, facing LEFT. Bright red body with cream windows.
    Colors: BUS_RED, BUS_CREAM, DARK (3 opaque + transparent)."""
    R = (208, 48, 48, 255)     # bright red bus body
    C = (240, 224, 192, 255)   # cream/white windows
    D = DARK                    # dark outline, wheels, undercarriage
    _ = T

    pixels = [
        #0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16 17 18 19 20 21 22 23
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 0
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 1
        [_, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, _],  # 2  roof
        [_, D, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, D, _],  # 3  body top
        [_, D, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, D, _],  # 4  body
        [_, D, C, C, D, C, C, D, C, C, D, C, C, D, C, C, D, C, C, D, R, R, D, _],  # 5  windows
        [_, D, C, C, D, C, C, D, C, C, D, C, C, D, C, C, D, C, C, D, R, R, D, _],  # 6  windows
        [_, D, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, D, _],  # 7  body mid
        [_, D, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, D, _],  # 8  body
        [_, D, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, D, _],  # 9  body
        [_, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, _],  # 10 stripe
        [_, D, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, D, _],  # 11 lower
        [_, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, _],  # 12 undercarriage
        [_, _, _, D, D, D, _, _, _, _, _, _, _, _, _, _, _, _, _, D, D, D, _, _],  # 13 wheels
        [_, _, D, D, D, D, D, _, _, _, _, _, _, _, _, _, _, _, D, D, D, D, D, _],  # 14 wheels
        [_, _, _, D, D, D, _, _, _, _, _, _, _, _, _, _, _, _, _, D, D, D, _, _],  # 15
    ]
    return make_image(24, 16, pixels)


def draw_cyclist():
    """Oncoming cyclist. 8x16, facing LEFT. Colors: SKIN, DARK, GRAY."""
    S = SKIN
    D = DARK
    G = GRAY
    _ = T

    pixels = [
        #0  1  2  3  4  5  6  7
        [_, _, _, _, _, _, _, _],  # 0
        [_, _, _, D, D, _, _, _],  # 1  hair/helmet
        [_, _, D, D, D, D, _, _],  # 2  hair
        [_, _, D, S, S, D, _, _],  # 3  face
        [_, _, _, S, S, _, _, _],  # 4  face
        [_, _, _, S, _, _, _, _],  # 5  neck
        [_, _, G, G, G, _, _, _],  # 6  torso
        [_, _, G, G, G, _, _, _],  # 7  torso
        [_, S, G, G, G, S, _, _],  # 8  arms out
        [_, _, _, G, _, _, _, _],  # 9  waist
        [_, _, G, _, G, _, _, _],  # 10 legs
        [_, _, _, D, D, _, _, _],  # 11 bike frame
        [_, _, D, D, D, D, _, _],  # 12 bike frame
        [_, D, D, _, _, D, D, _],  # 13 wheels
        [_, D, D, _, _, D, D, _],  # 14 wheels
        [_, _, D, _, _, D, _, _],  # 15
    ]
    return make_image(8, 16, pixels)


def draw_baozi():
    """Steamed bun collectible. 8x8. Colors: WHITE, CREAM, GOLD."""
    W = WHITE
    C = CREAM
    G = GOLD
    _ = T

    pixels = [
        [_, _, _, G, G, _, _, _],  # 0  pleated top
        [_, _, G, W, W, G, _, _],  # 1  top
        [_, G, W, W, W, W, G, _],  # 2  body
        [_, W, W, W, W, W, W, _],  # 3  body
        [_, W, W, W, W, W, W, _],  # 4  body
        [_, C, W, W, W, W, C, _],  # 5  body bottom
        [_, _, C, C, C, C, _, _],  # 6  bottom shadow
        [_, _, _, _, _, _, _, _],  # 7
    ]
    return make_image(8, 8, pixels)


def draw_textbook():
    """Textbook collectible. 8x8. Colors: CBLUE, DARK, WHITE."""
    B = CBLUE
    D = DARK
    W = WHITE
    _ = T

    pixels = [
        [_, _, _, _, _, _, _, _],  # 0
        [_, D, D, D, D, D, D, _],  # 1  top edge
        [_, D, B, B, B, B, D, _],  # 2  cover
        [_, D, B, W, W, B, D, _],  # 3  title area
        [_, D, B, W, W, B, D, _],  # 4  title area
        [_, D, B, B, B, B, D, _],  # 5  cover
        [_, D, D, D, D, D, D, _],  # 6  bottom edge
        [_, _, _, _, _, _, _, _],  # 7
    ]
    return make_image(8, 8, pixels)


def main():
    os.makedirs(ASSETS_DIR, exist_ok=True)

    sprites = [
        ("ch2_bike_frame1.png", draw_bike_frame1),
        ("ch2_bike_frame2.png", draw_bike_frame2),
        ("ch2_pothole.png", draw_pothole),
        ("ch2_puddle.png", draw_puddle),
        ("ch2_dog_frame1.png", draw_dog_frame1),
        ("ch2_dog_frame2.png", draw_dog_frame2),
        ("ch2_vendor.png", draw_vendor),
        ("ch2_bus.png", draw_bus),
        ("ch2_cyclist.png", draw_cyclist),
        ("ch2_baozi.png", draw_baozi),
        ("ch2_textbook.png", draw_textbook),
    ]

    for filename, draw_fn in sprites:
        img = draw_fn()
        path = os.path.join(ASSETS_DIR, filename)
        img.save(path)
        w, h = img.size
        # Count unique opaque colors
        colors = set()
        for y in range(h):
            for x in range(w):
                r, g, b, a = img.getpixel((x, y))
                if a > 0:
                    colors.add((r, g, b))
        print(f"  {filename}: {w}x{h}, {len(colors)} colors: {colors}")

    print(f"\nAll sprites saved to {ASSETS_DIR}")


if __name__ == '__main__':
    main()
