#!/usr/bin/env /opt/homebrew/bin/python3
"""
Generate all Chapter 2 (Bicycle Dash) sprites as pixel art PNGs.

Sprites are drawn pixel-by-pixel for Game Boy Color constraints:
- Max 4 colors per sprite (3 opaque + transparent)
- Dimensions are multiples of 8
- RGBA PNGs with alpha=0 for empty pixels

v2: All sprites doubled in size for better visibility on 160x144 screen.
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

# Palette 2: Cool obstacles (bus, pothole, puddle, cyclist)
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
    """Bicycle + rider frame 1: right pedal UP. 32x32.
    Rider with backpack on bike, detailed at 2x scale.
    Colors: SKIN, BLUE (uniform), DARK (hair/bike/wheels)."""
    S = SKIN
    B = BLUE
    D = DARK
    _ = T

    pixels = [
        #0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 0
        [_, _, _, _, _, _, _, _, _, _, D, D, D, D, D, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 1  hair top
        [_, _, _, _, _, _, _, _, _, D, D, D, D, D, D, D, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 2  hair
        [_, _, _, _, _, _, _, _, D, D, D, D, D, D, D, D, D, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 3  hair
        [_, _, _, _, _, _, _, _, D, D, D, D, D, D, D, D, D, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 4  hair
        [_, _, _, _, _, _, _, _, D, D, S, S, S, S, S, D, D, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 5  face
        [_, _, _, _, _, _, _, _, D, D, S, S, S, S, S, D, D, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 6  face
        [_, _, _, _, _, _, _, _, _, _, S, S, S, S, S, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 7  face lower
        [_, _, _, _, _, _, _, _, _, _, _, S, S, S, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 8  neck
        [_, _, _, _, _, _, _, _, _, _, _, S, S, S, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 9  neck
        [_, _, _, _, _, _, _, _, D, D, B, B, B, B, B, B, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 10 backpack+torso
        [_, _, _, _, _, _, _, _, D, D, B, B, B, B, B, B, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 11 backpack+torso
        [_, _, _, _, _, _, _, _, D, D, B, B, B, B, B, B, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 12 backpack+torso
        [_, _, _, _, _, _, _, _, D, D, B, B, B, B, B, B, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 13 backpack+torso
        [_, _, _, _, _, _, _, _, D, D, _, B, B, B, S, S, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 14 backpack, arm, hand
        [_, _, _, _, _, _, _, _, D, D, _, B, B, B, S, S, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 15 backpack, arm, hand
        [_, _, _, _, _, _, _, _, _, _, _, B, B, B, _, _, D, D, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 16 waist, handlebar
        [_, _, _, _, _, _, _, _, _, _, _, B, B, B, _, _, D, D, D, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 17 waist, handlebar
        [_, _, _, _, _, _, _, _, _, _, _, B, B, _, D, D, D, D, D, D, _, _, _, _, _, _, _, _, _, _, _, _],  # 18 leg up, frame
        [_, _, _, _, _, _, _, _, _, _, _, B, B, _, D, D, D, D, D, D, _, _, _, _, _, _, _, _, _, _, _, _],  # 19 leg up, frame
        [_, _, _, _, _, _, _, _, _, D, D, D, D, D, D, D, _, _, D, D, D, D, _, _, _, _, _, _, _, _, _, _],  # 20 bike frame
        [_, _, _, _, _, _, _, _, _, D, D, D, D, D, D, D, _, _, D, D, D, D, _, _, _, _, _, _, _, _, _, _],  # 21 bike frame
        [_, _, _, _, _, _, D, D, D, _, _, D, D, _, _, D, D, _, _, _, _, D, D, D, D, _, _, _, _, _, _, _],  # 22 wheels + frame
        [_, _, _, _, _, _, D, D, D, _, _, D, D, _, _, _, D, D, _, _, _, D, D, D, D, _, _, _, _, _, _, _],  # 23 wheels + frame
        [_, _, _, _, D, D, D, D, D, D, _, _, B, B, _, _, _, D, D, D, D, D, D, D, D, D, _, _, _, _, _, _],  # 24 wheel, pedal down
        [_, _, _, _, D, D, D, D, D, D, _, _, B, B, _, _, _, D, D, D, D, D, D, D, D, D, _, _, _, _, _, _],  # 25 wheel, pedal down
        [_, _, _, _, D, D, D, D, D, D, D, _, _, _, _, _, _, _, D, D, D, D, D, D, D, D, _, _, _, _, _, _],  # 26 wheels
        [_, _, _, _, D, D, D, D, D, D, D, _, _, _, _, _, _, _, D, D, D, D, D, D, D, D, _, _, _, _, _, _],  # 27 wheels
        [_, _, _, _, _, D, D, D, D, D, _, _, _, _, _, _, _, _, _, D, D, D, D, D, _, _, _, _, _, _, _, _],  # 28 wheels lower
        [_, _, _, _, _, _, D, D, D, _, _, _, _, _, _, _, _, _, _, _, D, D, D, _, _, _, _, _, _, _, _, _],  # 29 wheels bottom
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 30
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 31
    ]
    return make_image(32, 32, pixels)


def draw_bike_frame2():
    """Bicycle + rider frame 2: right pedal DOWN. 32x32.
    Colors: SKIN, BLUE (uniform), DARK (hair/bike/wheels)."""
    S = SKIN
    B = BLUE
    D = DARK
    _ = T

    pixels = [
        #0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 0
        [_, _, _, _, _, _, _, _, _, _, D, D, D, D, D, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 1  hair top
        [_, _, _, _, _, _, _, _, _, D, D, D, D, D, D, D, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 2  hair
        [_, _, _, _, _, _, _, _, D, D, D, D, D, D, D, D, D, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 3  hair
        [_, _, _, _, _, _, _, _, D, D, D, D, D, D, D, D, D, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 4  hair
        [_, _, _, _, _, _, _, _, D, D, S, S, S, S, S, D, D, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 5  face
        [_, _, _, _, _, _, _, _, D, D, S, S, S, S, S, D, D, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 6  face
        [_, _, _, _, _, _, _, _, _, _, S, S, S, S, S, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 7  face lower
        [_, _, _, _, _, _, _, _, _, _, _, S, S, S, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 8  neck
        [_, _, _, _, _, _, _, _, _, _, _, S, S, S, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 9  neck
        [_, _, _, _, _, _, _, _, D, D, B, B, B, B, B, B, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 10 backpack+torso
        [_, _, _, _, _, _, _, _, D, D, B, B, B, B, B, B, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 11 backpack+torso
        [_, _, _, _, _, _, _, _, D, D, B, B, B, B, B, B, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 12 backpack+torso
        [_, _, _, _, _, _, _, _, D, D, B, B, B, B, B, B, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 13 backpack+torso
        [_, _, _, _, _, _, _, _, D, D, _, B, B, B, S, S, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 14 backpack, arm
        [_, _, _, _, _, _, _, _, D, D, _, B, B, B, S, S, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 15 backpack, arm
        [_, _, _, _, _, _, _, _, _, _, _, B, B, B, _, _, D, D, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 16 waist, handlebar
        [_, _, _, _, _, _, _, _, _, _, _, B, B, B, _, _, D, D, D, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 17 waist, handlebar
        [_, _, _, _, _, _, _, _, _, _, _, _, B, B, D, D, D, D, D, D, _, _, _, _, _, _, _, _, _, _, _, _],  # 18 frame, leg down
        [_, _, _, _, _, _, _, _, _, _, _, _, B, B, D, D, D, D, D, D, _, _, _, _, _, _, _, _, _, _, _, _],  # 19 frame, leg down
        [_, _, _, _, _, _, _, _, _, D, D, D, D, D, D, D, _, _, D, D, D, D, _, _, _, _, _, _, _, _, _, _],  # 20 bike frame
        [_, _, _, _, _, _, _, _, _, D, D, D, D, D, D, D, _, _, D, D, D, D, _, _, _, _, _, _, _, _, _, _],  # 21 bike frame
        [_, _, _, _, _, _, D, D, D, _, _, D, D, B, B, D, D, _, _, _, _, D, D, D, D, _, _, _, _, _, _, _],  # 22 wheels, pedal
        [_, _, _, _, _, _, D, D, D, _, _, D, D, B, B, _, D, D, _, _, _, D, D, D, D, _, _, _, _, _, _, _],  # 23 wheels, pedal
        [_, _, _, _, D, D, D, D, D, D, _, _, _, _, _, _, _, D, D, D, D, D, D, D, D, D, _, _, _, _, _, _],  # 24 wheel
        [_, _, _, _, D, D, D, D, D, D, _, _, _, _, _, _, _, D, D, D, D, D, D, D, D, D, _, _, _, _, _, _],  # 25 wheel
        [_, _, _, _, D, D, D, D, D, D, D, _, _, _, _, _, _, _, D, D, D, D, D, D, D, D, _, _, _, _, _, _],  # 26 wheels
        [_, _, _, _, D, D, D, D, D, D, D, _, _, _, _, _, _, _, D, D, D, D, D, D, D, D, _, _, _, _, _, _],  # 27 wheels
        [_, _, _, _, _, D, D, D, D, D, _, _, _, _, _, _, _, _, _, D, D, D, D, D, _, _, _, _, _, _, _, _],  # 28 wheels lower
        [_, _, _, _, _, _, D, D, D, _, _, _, _, _, _, _, _, _, _, _, D, D, D, _, _, _, _, _, _, _, _, _],  # 29 wheels bottom
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 30
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 31
    ]
    return make_image(32, 32, pixels)


def draw_pothole():
    """Pothole obstacle. 16x16. Dark crack/hole pattern.
    Colors: DKGRAY, GRAY, LTGRAY."""
    D = DKGRAY
    G = GRAY
    L = LTGRAY
    _ = T

    pixels = [
        #0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 0
        [_, _, _, _, _, _, _, L, _, _, _, _, _, _, _, _],  # 1
        [_, _, _, _, _, _, L, L, L, _, _, _, _, _, _, _],  # 2
        [_, _, _, _, _, L, G, G, G, L, _, _, _, _, _, _],  # 3
        [_, _, _, _, L, G, G, D, D, G, L, _, _, _, _, _],  # 4
        [_, _, _, L, G, G, D, D, D, D, G, L, _, _, _, _],  # 5
        [_, _, L, G, G, D, D, D, D, D, D, G, L, _, _, _],  # 6
        [_, _, L, G, D, D, D, D, D, D, D, G, L, _, _, _],  # 7
        [_, _, _, G, D, D, D, D, D, D, D, D, G, _, _, _],  # 8
        [_, _, _, G, G, D, D, D, D, D, G, G, _, _, _, _],  # 9
        [_, _, _, _, L, G, G, D, D, G, G, L, _, _, _, _],  # 10
        [_, _, _, _, _, L, G, G, G, L, _, _, _, _, _, _],  # 11
        [_, _, _, _, _, _, L, L, _, _, L, _, _, _, _, _],  # 12  crack line
        [_, _, _, _, _, _, _, _, _, _, _, L, _, _, _, _],  # 13  crack extends
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 14
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 15
    ]
    return make_image(16, 16, pixels)


def draw_puddle():
    """Puddle obstacle. 16x16. Blue oval water reflection.
    Colors: DKBLUE, MEDBLUE, LTBLUE."""
    D = DKBLUE
    M = MEDBLUE
    L = LTBLUE
    _ = T

    pixels = [
        #0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 0
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 1
        [_, _, _, _, _, _, M, M, M, M, _, _, _, _, _, _],  # 2
        [_, _, _, _, M, M, L, L, L, L, M, M, _, _, _, _],  # 3
        [_, _, _, M, L, L, L, L, L, L, L, L, M, _, _, _],  # 4
        [_, _, M, L, L, L, L, L, L, L, L, L, L, M, _, _],  # 5
        [_, _, M, L, L, L, L, L, L, L, L, L, L, M, _, _],  # 6
        [_, _, M, M, L, L, L, L, L, L, L, L, M, M, _, _],  # 7
        [_, _, M, M, D, L, L, L, L, L, L, D, M, M, _, _],  # 8
        [_, _, M, D, D, D, L, L, L, L, D, D, D, M, _, _],  # 9
        [_, _, _, M, D, D, D, D, D, D, D, D, M, _, _, _],  # 10
        [_, _, _, _, M, M, D, D, D, D, M, M, _, _, _, _],  # 11
        [_, _, _, _, _, _, M, M, M, M, _, _, _, _, _, _],  # 12
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 13
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 14
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 15
    ]
    return make_image(16, 16, pixels)


def draw_dog_frame1():
    """Stray dog frame 1: legs extended. 32x16, facing LEFT.
    Colors: BROWN, TAN, DKBROWN."""
    B = BROWN
    N = TAN
    D = DKBROWN
    _ = T

    pixels = [
        #0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, D, D, _, _, _, _, _, _, _],  # 0  ear tip
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, D, D, D, D, _, _, _, _, _, _],  # 1  ear
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, D, D, N, N, D, D, _, _, _, _, _],  # 2  head
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, D, D, N, N, D, D, D, _, _, _, _],  # 3  head+snout
        [_, _, _, _, _, _, _, _, _, _, B, B, B, B, B, B, B, B, B, B, B, D, D, N, D, D, _, _, _, _, _, _],  # 4  body + head
        [_, _, _, _, _, _, _, _, _, B, B, B, B, B, B, B, B, B, B, B, B, B, D, D, D, _, _, _, _, _, _, _],  # 5  body
        [_, _, _, _, _, _, _, _, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, D, _, _, _, _, _, _, _, _],  # 6  body
        [_, _, _, _, _, _, _, _, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, _, _, _, _, _, _, _, _, _],  # 7  body
        [_, _, _, _, _, _, _, _, B, B, B, B, B, B, B, B, B, B, B, B, B, B, _, _, _, _, _, _, _, _, _, _],  # 8  body
        [_, _, _, _, _, _, _, _, B, B, B, B, B, B, B, B, B, B, B, B, B, B, _, _, _, _, _, _, _, _, _, _],  # 9  body lower
        [_, _, _, _, _, _, _, _, _, _, B, B, _, _, _, _, _, _, _, B, B, _, _, _, _, _, _, _, _, _, _, _],  # 10 legs
        [_, _, _, _, _, _, _, _, _, B, B, _, _, _, _, _, _, _, _, _, B, B, _, _, _, _, _, _, _, _, _, _],  # 11 legs
        [_, _, _, _, _, _, _, _, B, B, _, _, _, _, _, _, _, _, _, _, _, B, B, _, _, _, _, _, _, _, _, _],  # 12 legs extended
        [_, _, _, _, _, _, _, D, D, _, _, _, _, _, _, _, _, _, _, _, _, _, D, D, _, _, _, _, _, _, _, _],  # 13 paws
        [_, _, _, _, _, _, _, D, D, _, _, _, _, _, _, _, _, _, _, _, _, _, D, D, _, _, _, _, _, _, _, _],  # 14 paws
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 15
    ]
    return make_image(32, 16, pixels)


def draw_dog_frame2():
    """Stray dog frame 2: legs together. 32x16, facing LEFT.
    Colors: BROWN, TAN, DKBROWN."""
    B = BROWN
    N = TAN
    D = DKBROWN
    _ = T

    pixels = [
        #0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, D, D, _, _, _, _, _, _, _],  # 0  ear tip
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, D, D, D, D, _, _, _, _, _, _],  # 1  ear
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, D, D, N, N, D, D, _, _, _, _, _],  # 2  head
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, D, D, N, N, D, D, D, _, _, _, _],  # 3  head+snout
        [_, _, _, _, _, _, _, _, _, _, B, B, B, B, B, B, B, B, B, B, B, D, D, N, D, D, _, _, _, _, _, _],  # 4  body + head
        [_, _, _, _, _, _, _, _, _, B, B, B, B, B, B, B, B, B, B, B, B, B, D, D, D, _, _, _, _, _, _, _],  # 5  body
        [_, _, _, _, _, _, _, _, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, D, _, _, _, _, _, _, _, _],  # 6  body
        [_, _, _, _, _, _, _, _, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, _, _, _, _, _, _, _, _, _],  # 7  body
        [_, _, _, _, _, _, _, _, B, B, B, B, B, B, B, B, B, B, B, B, B, B, _, _, _, _, _, _, _, _, _, _],  # 8  body
        [_, _, _, _, _, _, _, _, B, B, B, B, B, B, B, B, B, B, B, B, B, B, _, _, _, _, _, _, _, _, _, _],  # 9  body lower
        [_, _, _, _, _, _, _, _, _, _, _, _, B, B, _, _, _, B, B, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 10 legs
        [_, _, _, _, _, _, _, _, _, _, _, _, _, B, B, _, B, B, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 11 legs together
        [_, _, _, _, _, _, _, _, _, _, _, _, _, B, B, B, B, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 12 legs crossed
        [_, _, _, _, _, _, _, _, _, _, _, _, D, D, _, _, D, D, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 13 paws
        [_, _, _, _, _, _, _, _, _, _, _, _, D, D, _, _, D, D, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 14 paws
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 15
    ]
    return make_image(32, 16, pixels)


def draw_vendor():
    """Vendor stall (BBQ cart 烧烤摊). 32x32. Canopy, grill, smoke wisps.
    Colors: BROWN, TAN, DKBROWN."""
    B = BROWN
    N = TAN
    D = DKBROWN
    _ = T

    pixels = [
        #0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31
        [_, _, _, _, _, _, _, _, _, _, _, N, _, _, _, _, _, _, _, N, _, _, _, _, _, _, _, _, _, _, _, _],  # 0  smoke
        [_, _, _, _, _, _, _, _, _, _, N, _, _, _, _, _, _, _, _, _, N, _, _, _, _, _, _, _, _, _, _, _],  # 1  smoke
        [_, _, _, _, _, _, _, _, _, _, _, N, _, _, N, _, _, N, _, N, _, _, _, _, _, _, _, _, _, _, _, _],  # 2  smoke
        [_, _, _, _, _, _, _, _, _, _, _, _, N, _, _, _, _, _, N, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 3  smoke
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 4
        [_, _, _, _, _, _, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, _, _, _, _, _, _],  # 5  roof top
        [_, _, _, _, _, _, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, _, _, _, _, _, _],  # 6  roof
        [_, _, _, _, _, _, D, N, N, N, N, N, N, N, N, N, N, N, N, N, N, N, N, N, N, D, _, _, _, _, _, _],  # 7  awning
        [_, _, _, _, _, _, D, N, N, N, N, N, N, N, N, N, N, N, N, N, N, N, N, N, N, D, _, _, _, _, _, _],  # 8  awning
        [_, _, _, _, _, _, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, _, _, _, _, _, _],  # 9  awning bottom
        [_, _, _, _, _, _, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, _, _, _, _, _, _],  # 10 awning bottom
        [_, _, _, _, _, _, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, _, _, _, _, _, _],  # 11 cart body
        [_, _, _, _, _, _, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, _, _, _, _, _, _],  # 12 cart body
        [_, _, _, _, _, _, B, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, B, _, _, _, _, _, _],  # 13 grill area
        [_, _, _, _, _, _, B, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, B, _, _, _, _, _, _],  # 14 grill
        [_, _, _, _, _, _, B, D, N, D, N, D, N, D, N, D, N, D, N, D, N, D, N, D, N, B, _, _, _, _, _, _],  # 15 food on grill
        [_, _, _, _, _, _, B, D, N, D, N, D, N, D, N, D, N, D, N, D, N, D, N, D, N, B, _, _, _, _, _, _],  # 16 food on grill
        [_, _, _, _, _, _, B, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, B, _, _, _, _, _, _],  # 17 grill
        [_, _, _, _, _, _, B, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, B, _, _, _, _, _, _],  # 18 grill
        [_, _, _, _, _, _, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, _, _, _, _, _, _],  # 19 cart body
        [_, _, _, _, _, _, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, _, _, _, _, _, _],  # 20 cart body
        [_, _, _, _, _, _, B, B, N, N, N, N, N, N, N, N, N, N, N, N, N, N, N, N, B, B, _, _, _, _, _, _],  # 21 sign area
        [_, _, _, _, _, _, B, B, N, N, N, N, N, N, N, N, N, N, N, N, N, N, N, N, B, B, _, _, _, _, _, _],  # 22 sign area
        [_, _, _, _, _, _, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, _, _, _, _, _, _],  # 23 cart bottom
        [_, _, _, _, _, _, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, B, _, _, _, _, _, _],  # 24 cart bottom
        [_, _, _, _, _, _, _, _, B, B, _, _, _, _, _, _, _, _, _, _, _, _, B, B, _, _, _, _, _, _, _, _],  # 25 legs
        [_, _, _, _, _, _, _, _, B, B, _, _, _, _, _, _, _, _, _, _, _, _, B, B, _, _, _, _, _, _, _, _],  # 26 legs
        [_, _, _, _, _, _, _, D, D, D, D, _, _, _, _, _, _, _, _, _, _, D, D, D, D, _, _, _, _, _, _, _],  # 27 wheels
        [_, _, _, _, _, _, _, D, D, D, D, _, _, _, _, _, _, _, _, _, _, D, D, D, D, _, _, _, _, _, _, _],  # 28 wheels
        [_, _, _, _, _, _, _, _, D, D, _, _, _, _, _, _, _, _, _, _, _, _, D, D, _, _, _, _, _, _, _, _],  # 29 wheel bottom
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 30
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 31
    ]
    return make_image(32, 32, pixels)


def draw_bus():
    """City bus. 32x32, facing LEFT. Bright red body with cream windows.
    Colors: BUS_RED, BUS_CREAM, DARK."""
    R = (208, 48, 48, 255)     # bright red bus body
    C = (240, 224, 192, 255)   # cream/white windows
    D = DARK                    # dark outline, wheels
    _ = T

    pixels = [
        #0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 0
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 1
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 2
        [_, _, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, _, _, _],  # 3  roof
        [_, _, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, _, _, _],  # 4  roof
        [_, _, D, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, D, _, _, _],  # 5  body top
        [_, _, D, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, D, _, _, _],  # 6  body
        [_, _, D, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, D, _, _, _],  # 7  body
        [_, _, D, C, C, C, D, D, C, C, C, D, D, C, C, C, D, D, C, C, C, D, D, C, C, C, R, R, D, _, _, _],  # 8  windows
        [_, _, D, C, C, C, D, D, C, C, C, D, D, C, C, C, D, D, C, C, C, D, D, C, C, C, R, R, D, _, _, _],  # 9  windows
        [_, _, D, C, C, C, D, D, C, C, C, D, D, C, C, C, D, D, C, C, C, D, D, C, C, C, R, R, D, _, _, _],  # 10 windows
        [_, _, D, C, C, C, D, D, C, C, C, D, D, C, C, C, D, D, C, C, C, D, D, C, C, C, R, R, D, _, _, _],  # 11 windows
        [_, _, D, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, D, _, _, _],  # 12 body mid
        [_, _, D, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, D, _, _, _],  # 13 body
        [_, _, D, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, D, _, _, _],  # 14 body
        [_, _, D, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, D, _, _, _],  # 15 body
        [_, _, D, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, D, _, _, _],  # 16 body
        [_, _, D, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, D, _, _, _],  # 17 body
        [_, _, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, _, _, _],  # 18 stripe
        [_, _, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, _, _, _],  # 19 stripe
        [_, _, D, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, D, _, _, _],  # 20 lower body
        [_, _, D, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, R, D, _, _, _],  # 21 lower
        [_, _, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, _, _, _],  # 22 undercarriage
        [_, _, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, D, _, _, _],  # 23 undercarriage
        [_, _, _, _, _, D, D, D, D, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, D, D, D, D, _, _, _, _],  # 24 wheels
        [_, _, _, _, D, D, D, D, D, D, _, _, _, _, _, _, _, _, _, _, _, _, _, D, D, D, D, D, D, _, _, _],  # 25 wheels
        [_, _, _, _, D, D, D, D, D, D, _, _, _, _, _, _, _, _, _, _, _, _, _, D, D, D, D, D, D, _, _, _],  # 26 wheels
        [_, _, _, _, D, D, D, D, D, D, _, _, _, _, _, _, _, _, _, _, _, _, _, D, D, D, D, D, D, _, _, _],  # 27 wheels
        [_, _, _, _, _, D, D, D, D, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, D, D, D, D, _, _, _, _],  # 28 wheels
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 29
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 30
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 31
    ]
    return make_image(32, 32, pixels)


def draw_cyclist():
    """Oncoming cyclist. 16x32, facing LEFT.
    Colors: SKIN, DARK, GRAY."""
    S = SKIN
    D = DARK
    G = GRAY
    _ = T

    pixels = [
        #0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 0
        [_, _, _, _, _, _, D, D, D, D, _, _, _, _, _, _],  # 1  helmet
        [_, _, _, _, _, D, D, D, D, D, D, _, _, _, _, _],  # 2  helmet
        [_, _, _, _, _, D, D, D, D, D, D, _, _, _, _, _],  # 3  helmet
        [_, _, _, _, _, D, D, D, D, D, D, _, _, _, _, _],  # 4  hair
        [_, _, _, _, _, D, S, S, S, S, D, _, _, _, _, _],  # 5  face
        [_, _, _, _, _, D, S, S, S, S, D, _, _, _, _, _],  # 6  face
        [_, _, _, _, _, _, S, S, S, S, _, _, _, _, _, _],  # 7  face lower
        [_, _, _, _, _, _, _, S, S, _, _, _, _, _, _, _],  # 8  neck
        [_, _, _, _, _, _, _, S, S, _, _, _, _, _, _, _],  # 9  neck
        [_, _, _, _, _, G, G, G, G, G, G, _, _, _, _, _],  # 10 torso
        [_, _, _, _, _, G, G, G, G, G, G, _, _, _, _, _],  # 11 torso
        [_, _, _, _, _, G, G, G, G, G, G, _, _, _, _, _],  # 12 torso
        [_, _, _, _, _, G, G, G, G, G, G, _, _, _, _, _],  # 13 torso
        [_, _, _, _, S, G, G, G, G, G, G, S, _, _, _, _],  # 14 arms out
        [_, _, _, _, S, G, G, G, G, G, G, S, _, _, _, _],  # 15 arms
        [_, _, _, _, _, _, G, G, G, G, _, _, _, _, _, _],  # 16 waist
        [_, _, _, _, _, _, G, G, G, G, _, _, _, _, _, _],  # 17 waist
        [_, _, _, _, _, G, G, _, _, G, G, _, _, _, _, _],  # 18 legs
        [_, _, _, _, _, G, G, _, _, G, G, _, _, _, _, _],  # 19 legs
        [_, _, _, _, _, _, D, D, D, D, _, _, _, _, _, _],  # 20 bike frame
        [_, _, _, _, _, _, D, D, D, D, _, _, _, _, _, _],  # 21 bike frame
        [_, _, _, _, _, D, D, D, D, D, D, _, _, _, _, _],  # 22 bike frame
        [_, _, _, _, _, D, D, D, D, D, D, _, _, _, _, _],  # 23 bike frame
        [_, _, _, _, D, D, D, _, _, D, D, D, _, _, _, _],  # 24 wheels
        [_, _, _, D, D, D, _, _, _, _, D, D, D, _, _, _],  # 25 wheels
        [_, _, _, D, D, D, _, _, _, _, D, D, D, _, _, _],  # 26 wheels
        [_, _, _, D, D, D, _, _, _, _, D, D, D, _, _, _],  # 27 wheels
        [_, _, _, _, D, D, D, _, _, D, D, D, _, _, _, _],  # 28 wheels
        [_, _, _, _, _, D, D, _, _, D, D, _, _, _, _, _],  # 29 wheel bottom
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 30
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 31
    ]
    return make_image(16, 32, pixels)


def draw_baozi():
    """Steamed bun collectible. 16x16.
    Colors: WHITE, CREAM, GOLD."""
    W = WHITE
    C = CREAM
    G = GOLD
    _ = T

    pixels = [
        #0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 0
        [_, _, _, _, _, _, G, G, G, G, _, _, _, _, _, _],  # 1  pleated top
        [_, _, _, _, _, G, G, G, G, G, G, _, _, _, _, _],  # 2  pleated top
        [_, _, _, _, G, G, W, W, W, W, G, G, _, _, _, _],  # 3  top
        [_, _, _, G, W, W, W, W, W, W, W, W, G, _, _, _],  # 4  body
        [_, _, G, W, W, W, W, W, W, W, W, W, W, G, _, _],  # 5  body
        [_, _, W, W, W, W, W, W, W, W, W, W, W, W, _, _],  # 6  body
        [_, _, W, W, W, W, W, W, W, W, W, W, W, W, _, _],  # 7  body
        [_, _, W, W, W, W, W, W, W, W, W, W, W, W, _, _],  # 8  body
        [_, _, W, W, W, W, W, W, W, W, W, W, W, W, _, _],  # 9  body
        [_, _, C, W, W, W, W, W, W, W, W, W, W, C, _, _],  # 10 body bottom
        [_, _, C, C, W, W, W, W, W, W, W, W, C, C, _, _],  # 11 bottom shadow
        [_, _, _, C, C, C, C, C, C, C, C, C, C, _, _, _],  # 12 bottom
        [_, _, _, _, C, C, C, C, C, C, C, C, _, _, _, _],  # 13 shadow
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 14
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 15
    ]
    return make_image(16, 16, pixels)


def draw_textbook():
    """Textbook collectible. 16x16.
    Colors: CBLUE, DARK, WHITE."""
    B = CBLUE
    D = DARK
    W = WHITE
    _ = T

    pixels = [
        #0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 0
        [_, _, _, D, D, D, D, D, D, D, D, D, D, _, _, _],  # 1  top edge
        [_, _, _, D, D, D, D, D, D, D, D, D, D, _, _, _],  # 2  top edge
        [_, _, _, D, B, B, B, B, B, B, B, B, D, _, _, _],  # 3  cover
        [_, _, _, D, B, B, B, B, B, B, B, B, D, _, _, _],  # 4  cover
        [_, _, _, D, B, B, W, W, W, W, B, B, D, _, _, _],  # 5  title area
        [_, _, _, D, B, B, W, W, W, W, B, B, D, _, _, _],  # 6  title
        [_, _, _, D, B, B, W, W, W, W, B, B, D, _, _, _],  # 7  title
        [_, _, _, D, B, B, W, W, W, W, B, B, D, _, _, _],  # 8  title
        [_, _, _, D, B, B, B, B, B, B, B, B, D, _, _, _],  # 9  cover
        [_, _, _, D, B, B, B, B, B, B, B, B, D, _, _, _],  # 10 cover
        [_, _, _, D, B, B, B, B, B, B, B, B, D, _, _, _],  # 11 cover
        [_, _, _, D, B, B, B, B, B, B, B, B, D, _, _, _],  # 12 cover
        [_, _, _, D, D, D, D, D, D, D, D, D, D, _, _, _],  # 13 bottom edge
        [_, _, _, D, D, D, D, D, D, D, D, D, D, _, _, _],  # 14 bottom edge
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 15
    ]
    return make_image(16, 16, pixels)


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
