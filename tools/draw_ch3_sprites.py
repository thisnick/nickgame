#!/usr/bin/env /opt/homebrew/bin/python3
"""
Generate Chapter 3 sprites — player character and NPCs.

Player: 16x16, 4 frames (down1, down2, up1, up2) — left/right via H-flip
NPC 1: Airport helper (maple leaf badge) 16x16
NPC 2: Student friend 16x16

GBC constraints: max 3 opaque colors + transparent per sprite (4 total)
"""

import os
from PIL import Image

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'chapter3')

T = (0, 0, 0, 0)  # Transparent

# Player palette: 3 opaque colors only
SKIN  = (232, 190, 150, 255)  # skin/face
DARK  = (40, 40, 56, 255)     # hair, shoes, eyes
BLUE  = (48, 80, 160, 255)    # jacket, pants, backpack

# NPC helper palette: 3 opaque colors only
N_SKIN  = (216, 176, 144, 255)
N_DARK  = (48, 40, 32, 255)    # hat, pants, eyes
N_RED   = (200, 48, 32, 255)   # maple leaf, uniform

# Student NPC palette: 3 opaque colors only
S_SKIN  = (224, 184, 152, 255)
S_DARK  = (40, 48, 40, 255)    # hair, pants, eyes
S_GREEN = (48, 128, 80, 255)   # sweater


def make_image(w, h, pixels):
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    for y, row in enumerate(pixels):
        for x, color in enumerate(row):
            if color != T:
                img.putpixel((x, y), color)
    return img


# ====================================================================
# Player — facing down (front), frame 1
# ====================================================================
def draw_player_down1():
    S = SKIN; D = DARK; B = BLUE; _ = T
    pixels = [
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 0
        [_, _, _, _, _, D, D, D, D, D, _, _, _, _, _, _],  # 1  hair
        [_, _, _, _, D, D, D, D, D, D, D, _, _, _, _, _],  # 2  hair
        [_, _, _, _, D, S, S, S, S, S, D, _, _, _, _, _],  # 3  face
        [_, _, _, _, _, S, D, S, D, S, _, _, _, _, _, _],  # 4  face (eyes)
        [_, _, _, _, _, S, S, S, S, S, _, _, _, _, _, _],  # 5  face
        [_, _, _, _, _, _, S, S, S, _, _, _, _, _, _, _],  # 6  neck
        [_, _, _, _, B, B, B, B, B, B, B, _, _, _, _, _],  # 7  jacket
        [_, _, _, S, B, B, B, B, B, B, B, S, _, _, _, _],  # 8  jacket+arms
        [_, _, _, S, B, B, B, B, B, B, B, S, _, _, _, _],  # 9  jacket
        [_, _, _, _, B, B, B, B, B, B, B, _, _, _, _, _],  # 10 jacket
        [_, _, _, _, _, B, B, _, B, B, _, _, _, _, _, _],  # 11 legs
        [_, _, _, _, _, B, B, _, B, B, _, _, _, _, _, _],  # 12 legs
        [_, _, _, _, _, D, D, _, D, D, _, _, _, _, _, _],  # 13 shoes
        [_, _, _, _, _, D, D, _, D, D, _, _, _, _, _, _],  # 14 shoes
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 15
    ]
    return make_image(16, 16, pixels)


def draw_player_down2():
    """Walking frame 2 — legs shifted."""
    S = SKIN; D = DARK; B = BLUE; _ = T
    pixels = [
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 0
        [_, _, _, _, _, D, D, D, D, D, _, _, _, _, _, _],  # 1
        [_, _, _, _, D, D, D, D, D, D, D, _, _, _, _, _],  # 2
        [_, _, _, _, D, S, S, S, S, S, D, _, _, _, _, _],  # 3
        [_, _, _, _, _, S, D, S, D, S, _, _, _, _, _, _],  # 4
        [_, _, _, _, _, S, S, S, S, S, _, _, _, _, _, _],  # 5
        [_, _, _, _, _, _, S, S, S, _, _, _, _, _, _, _],  # 6
        [_, _, _, _, B, B, B, B, B, B, B, _, _, _, _, _],  # 7
        [_, _, _, S, B, B, B, B, B, B, B, S, _, _, _, _],  # 8
        [_, _, _, S, B, B, B, B, B, B, B, S, _, _, _, _],  # 9
        [_, _, _, _, B, B, B, B, B, B, B, _, _, _, _, _],  # 10
        [_, _, _, _, B, B, _, _, _, B, B, _, _, _, _, _],  # 11 legs apart
        [_, _, _, _, D, _, _, _, _, _, D, _, _, _, _, _],  # 12 shoes wide
        [_, _, _, _, D, D, _, _, _, D, D, _, _, _, _, _],  # 13
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 14
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 15
    ]
    return make_image(16, 16, pixels)


def draw_player_up1():
    """Facing up (back), frame 1."""
    S = SKIN; D = DARK; B = BLUE; _ = T
    pixels = [
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 0
        [_, _, _, _, _, D, D, D, D, D, _, _, _, _, _, _],  # 1  hair
        [_, _, _, _, D, D, D, D, D, D, D, _, _, _, _, _],  # 2  hair
        [_, _, _, _, D, D, D, D, D, D, D, _, _, _, _, _],  # 3  back of head
        [_, _, _, _, _, D, D, D, D, D, _, _, _, _, _, _],  # 4
        [_, _, _, _, _, _, S, S, S, _, _, _, _, _, _, _],  # 5  neck
        [_, _, _, _, _, _, S, S, S, _, _, _, _, _, _, _],  # 6
        [_, _, _, _, B, B, B, B, B, B, B, _, _, _, _, _],  # 7  jacket
        [_, _, _, S, B, B, B, B, B, B, B, S, _, _, _, _],  # 8  backpack
        [_, _, _, S, B, B, B, B, B, B, B, S, _, _, _, _],  # 9  backpack
        [_, _, _, _, B, B, B, B, B, B, B, _, _, _, _, _],  # 10
        [_, _, _, _, _, B, B, _, B, B, _, _, _, _, _, _],  # 11
        [_, _, _, _, _, B, B, _, B, B, _, _, _, _, _, _],  # 12
        [_, _, _, _, _, D, D, _, D, D, _, _, _, _, _, _],  # 13
        [_, _, _, _, _, D, D, _, D, D, _, _, _, _, _, _],  # 14
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 15
    ]
    return make_image(16, 16, pixels)


def draw_player_up2():
    """Facing up (back), frame 2 — legs shifted."""
    S = SKIN; D = DARK; B = BLUE; _ = T
    pixels = [
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 0
        [_, _, _, _, _, D, D, D, D, D, _, _, _, _, _, _],  # 1
        [_, _, _, _, D, D, D, D, D, D, D, _, _, _, _, _],  # 2
        [_, _, _, _, D, D, D, D, D, D, D, _, _, _, _, _],  # 3
        [_, _, _, _, _, D, D, D, D, D, _, _, _, _, _, _],  # 4
        [_, _, _, _, _, _, S, S, S, _, _, _, _, _, _, _],  # 5
        [_, _, _, _, _, _, S, S, S, _, _, _, _, _, _, _],  # 6
        [_, _, _, _, B, B, B, B, B, B, B, _, _, _, _, _],  # 7
        [_, _, _, S, B, B, B, B, B, B, B, S, _, _, _, _],  # 8
        [_, _, _, S, B, B, B, B, B, B, B, S, _, _, _, _],  # 9
        [_, _, _, _, B, B, B, B, B, B, B, _, _, _, _, _],  # 10
        [_, _, _, _, B, B, _, _, _, B, B, _, _, _, _, _],  # 11
        [_, _, _, _, D, _, _, _, _, _, D, _, _, _, _, _],  # 12
        [_, _, _, _, D, D, _, _, _, D, D, _, _, _, _, _],  # 13
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 14
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 15
    ]
    return make_image(16, 16, pixels)


# ====================================================================
# NPC 1: Airport Helper (maple leaf badge on uniform)
# ====================================================================
def draw_npc_helper():
    S = N_SKIN; D = N_DARK; R = N_RED; _ = T
    pixels = [
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 0
        [_, _, _, _, _, D, D, D, D, D, _, _, _, _, _, _],  # 1  hat
        [_, _, _, _, D, D, D, D, D, D, D, _, _, _, _, _],  # 2  hat
        [_, _, _, _, _, S, S, S, S, S, _, _, _, _, _, _],  # 3  face
        [_, _, _, _, _, S, D, S, D, S, _, _, _, _, _, _],  # 4  face (eyes)
        [_, _, _, _, _, S, S, S, S, S, _, _, _, _, _, _],  # 5  face (smile)
        [_, _, _, _, _, _, S, S, S, _, _, _, _, _, _, _],  # 6  neck
        [_, _, _, _, R, R, R, R, R, R, R, _, _, _, _, _],  # 7  uniform
        [_, _, _, S, R, R, R, D, R, R, R, S, _, _, _, _],  # 8  uniform + maple leaf
        [_, _, _, S, R, R, D, D, D, R, R, S, _, _, _, _],  # 9  maple leaf bigger
        [_, _, _, _, R, R, R, D, R, R, R, _, _, _, _, _],  # 10 uniform
        [_, _, _, _, _, D, D, _, D, D, _, _, _, _, _, _],  # 11 pants
        [_, _, _, _, _, D, D, _, D, D, _, _, _, _, _, _],  # 12
        [_, _, _, _, _, D, D, _, D, D, _, _, _, _, _, _],  # 13
        [_, _, _, _, _, D, D, _, D, D, _, _, _, _, _, _],  # 14
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 15
    ]
    return make_image(16, 16, pixels)


# ====================================================================
# NPC 2: Student Friend
# ====================================================================
def draw_npc_student():
    S = S_SKIN; D = S_DARK; G = S_GREEN; _ = T
    pixels = [
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 0
        [_, _, _, _, _, D, D, D, D, D, _, _, _, _, _, _],  # 1  hair
        [_, _, _, _, D, D, D, D, D, D, D, _, _, _, _, _],  # 2
        [_, _, _, _, D, S, S, S, S, S, D, _, _, _, _, _],  # 3  face
        [_, _, _, _, _, S, D, S, D, S, _, _, _, _, _, _],  # 4  eyes
        [_, _, _, _, _, S, S, S, S, S, _, _, _, _, _, _],  # 5
        [_, _, _, _, _, _, S, S, S, _, _, _, _, _, _, _],  # 6  neck
        [_, _, _, _, G, G, G, G, G, G, G, _, _, _, _, _],  # 7  sweater
        [_, _, _, S, G, G, G, G, G, G, G, S, _, _, _, _],  # 8
        [_, _, _, S, G, G, G, G, G, G, G, S, _, _, _, _],  # 9
        [_, _, _, _, G, G, G, G, G, G, G, _, _, _, _, _],  # 10
        [_, _, _, _, _, D, D, _, D, D, _, _, _, _, _, _],  # 11
        [_, _, _, _, _, D, D, _, D, D, _, _, _, _, _, _],  # 12
        [_, _, _, _, _, D, D, _, D, D, _, _, _, _, _, _],  # 13
        [_, _, _, _, _, D, D, _, D, D, _, _, _, _, _, _],  # 14
        [_, _, _, _, _, _, _, _, _, _, _, _, _, _, _, _],  # 15
    ]
    return make_image(16, 16, pixels)


# ====================================================================
# Main
# ====================================================================

def main():
    os.makedirs(ASSETS_DIR, exist_ok=True)

    sprites = [
        (draw_player_down1, 'ch3_player_down1.png'),
        (draw_player_down2, 'ch3_player_down2.png'),
        (draw_player_up1,   'ch3_player_up1.png'),
        (draw_player_up2,   'ch3_player_up2.png'),
        (draw_npc_helper,   'ch3_npc_helper.png'),
        (draw_npc_student,  'ch3_npc_student.png'),
    ]

    for func, name in sprites:
        img = func()
        path = os.path.join(ASSETS_DIR, name)
        img.save(path)
        print(f"Saved {path}")

        # Verify colors per 8x8 tile
        for ty in range(img.height // 8):
            for tx in range(img.width // 8):
                colors = set()
                for dy in range(8):
                    for dx in range(8):
                        colors.add(img.getpixel((tx*8+dx, ty*8+dy)))
                if len(colors) > 4:
                    print(f"  WARNING: {name} tile ({tx},{ty}) has {len(colors)} colors!")

    print("\nDone! Next: run png2asset to convert sprites.")


if __name__ == '__main__':
    main()
