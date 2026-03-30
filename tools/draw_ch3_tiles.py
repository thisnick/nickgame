#!/usr/bin/env /opt/homebrew/bin/python3
"""
Generate Chapter 3 background art — three stages of 160x144 (20x18 tiles).

STRICT GBC constraints: max 4 colors per 8x8 tile, max 8 palettes per image.
We work tile-by-tile, assigning each tile to a palette and only using those 4 colors.
"""

import os
from PIL import Image

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'chapter3')

TILE = 8
W, H = 160, 144
COLS, ROWS = W // TILE, H // TILE  # 20 x 18


def fill_tile(img, tx, ty, color):
    """Fill an entire 8x8 tile with a single color."""
    for py in range(ty * 8, ty * 8 + 8):
        for px in range(tx * 8, tx * 8 + 8):
            img.putpixel((px, py), color)


def fill_tile_pattern(img, tx, ty, c1, c2, pattern='checker'):
    """Fill tile with a 2-color pattern."""
    x0, y0 = tx * 8, ty * 8
    for dy in range(8):
        for dx in range(8):
            if pattern == 'checker':
                c = c1 if (dx + dy) % 2 == 0 else c2
            elif pattern == 'hstripe':
                c = c1 if dy % 2 == 0 else c2
            elif pattern == 'vstripe':
                c = c1 if dx % 2 == 0 else c2
            elif pattern == 'top_half':
                c = c1 if dy < 4 else c2
            elif pattern == 'left_half':
                c = c1 if dx < 4 else c2
            elif pattern == 'border':
                c = c1 if dx == 0 or dx == 7 or dy == 0 or dy == 7 else c2
            else:
                c = c1
            img.putpixel((x0 + dx, y0 + dy), c)


def fill_tile_4color(img, tx, ty, colors, pixel_data):
    """Fill tile from a list of 4 colors and an 8x8 array of indices (0-3)."""
    x0, y0 = tx * 8, ty * 8
    for dy in range(8):
        for dx in range(8):
            idx = pixel_data[dy][dx] if dy < len(pixel_data) and dx < len(pixel_data[dy]) else 0
            img.putpixel((x0 + dx, y0 + dy), colors[idx])


# ====================================================================
# Stage 1: Airport Terminal (cold grey-blue)
# ====================================================================
# 8 palettes:
# P0: Floor      = (floor_light, floor_mid, floor_dark, floor_line)
# P1: Wall       = (wall_dark, wall_mid, wall_light, wall_white)
# P2: Sign       = (sign_dark, sign_mid, sign_light, sign_white)
# P3: Belt       = (belt_dark, belt_mid, belt_tan, belt_gray)
# P4: Door       = (door_dark, door_green, door_frame, door_high)
# P5: Seat       = (seat_dkblue, seat_blue, seat_gray, seat_white)
# P6: Rail       = (rail_dark, rail_mid, rail_light, floor_light)
# P7: NPC marker = (npc_dark, npc_red, npc_mid, floor_light)

def draw_airport():
    P0 = [(176,184,192), (144,152,160), (112,120,128), (96,104,112)]  # floor
    P1 = [(64,72,88), (96,104,120), (144,152,168), (200,208,216)]      # wall
    P2 = [(48,56,72), (80,88,104), (160,168,184), (200,208,216)]       # sign
    P3 = [(72,64,56), (120,104,80), (160,144,112), (128,128,128)]      # belt
    P4 = [(40,64,48), (72,112,80), (88,96,104), (128,168,136)]         # door
    P5 = [(48,56,88), (72,88,128), (128,136,144), (200,208,216)]       # seat
    P6 = [(80,88,96), (128,136,144), (168,176,184), (176,184,192)]     # rail
    P7 = [(72,56,48), (160,64,48), (128,112,96), (176,184,192)]        # npc marker

    img = Image.new('RGB', (W, H), P0[0])

    # Row 0 (ty=0): wall dark top
    for tx in range(20):
        fill_tile(img, tx, 0, P1[0])

    # Row 1 (ty=1): wall mid
    for tx in range(20):
        fill_tile(img, tx, 1, P1[1])

    # Row 2 (ty=2): wall light/white transition
    for tx in range(20):
        fill_tile_pattern(img, tx, 2, P1[2], P1[3], 'top_half')

    # Luggage belt area (ty=1, tx=2-7) - overlay on wall
    for tx in range(2, 8):
        fill_tile_4color(img, tx, 1, P3, [
            [0,0,0,0,0,0,0,0],
            [0,1,1,1,1,1,1,0],
            [0,1,2,2,2,2,1,0],
            [0,1,2,2,2,2,1,0],
            [0,1,2,3,2,3,1,0],
            [0,1,1,1,1,1,1,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
        ])

    # Signs on wall row 1 (garbled text)
    # Sign 1 at tx=8,9,10 ty=1
    for tx in [8, 9, 10, 11]:
        fill_tile_4color(img, tx, 1, P2, [
            [0,0,0,0,0,0,0,0],
            [0,1,1,1,1,1,1,0],
            [0,1,3,1,3,1,1,0],
            [0,1,1,3,1,3,1,0],
            [0,1,3,3,1,1,1,0],
            [0,1,1,1,1,1,1,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
        ])

    # Sign 2 at tx=13,14,15,16 ty=1
    for tx in [13, 14, 15, 16]:
        fill_tile_4color(img, tx, 1, P2, [
            [0,0,0,0,0,0,0,0],
            [0,1,1,1,1,1,1,0],
            [0,1,3,1,1,3,1,0],
            [0,1,1,3,3,1,1,0],
            [0,1,3,1,1,3,1,0],
            [0,1,1,1,1,1,1,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
        ])

    # Left wall column (tx=0) rows 3-17
    for ty in range(3, 18):
        fill_tile_pattern(img, 0, ty, P1[0], P1[1], 'left_half')

    # Right wall column (tx=19) rows 3-17
    for ty in range(3, 18):
        fill_tile_pattern(img, 19, ty, P1[1], P1[0], 'left_half')

    # Floor tiles (tx=1-18, ty=3-17) — checkerboard
    for ty in range(3, 18):
        for tx in range(1, 19):
            if (tx + ty) % 2 == 0:
                fill_tile_pattern(img, tx, ty, P0[0], P0[3], 'border')
            else:
                fill_tile_pattern(img, tx, ty, P0[1], P0[3], 'border')

    # Seats left side (tx=1, ty=6,7,8)
    for ty in [6, 7, 8]:
        fill_tile_4color(img, 1, ty, P5, [
            [0,0,1,1,1,1,0,0],
            [0,1,1,1,1,1,1,0],
            [0,1,1,1,1,1,1,0],
            [0,1,1,2,2,1,1,0],
            [0,0,2,2,2,2,0,0],
            [0,0,2,2,2,2,0,0],
            [0,0,0,2,2,0,0,0],
            [0,0,0,0,0,0,0,0],
        ])

    # Seats right side (tx=18, ty=6,7,8)
    for ty in [6, 7, 8]:
        fill_tile_4color(img, 18, ty, P5, [
            [0,0,1,1,1,1,0,0],
            [0,1,1,1,1,1,1,0],
            [0,1,1,1,1,1,1,0],
            [0,1,1,2,2,1,1,0],
            [0,0,2,2,2,2,0,0],
            [0,0,2,2,2,2,0,0],
            [0,0,0,2,2,0,0,0],
            [0,0,0,0,0,0,0,0],
        ])

    # Railing barrier (ty=10, tx=3-16)
    for tx in range(3, 17):
        fill_tile_4color(img, tx, 10, P6, [
            [3,3,3,3,3,3,3,3],
            [3,3,3,3,3,3,3,3],
            [0,3,3,3,3,3,3,0],
            [0,1,3,3,3,3,1,0],
            [0,1,3,3,3,3,1,0],
            [0,0,0,0,0,0,0,0],
            [0,0,1,1,1,1,0,0],
            [3,3,3,3,3,3,3,3],
        ])

    # NPC marker (tx=10, ty=7) — red spot on floor
    fill_tile_4color(img, 10, 7, P7, [
        [3,3,3,3,3,3,3,3],
        [3,3,3,1,1,3,3,3],
        [3,3,1,1,1,1,3,3],
        [3,1,1,1,1,1,1,3],
        [3,1,1,1,1,1,1,3],
        [3,3,1,1,1,1,3,3],
        [3,3,3,1,1,3,3,3],
        [3,3,3,3,3,3,3,3],
    ])

    # Exit door (ty=16-17, tx=9,10)
    for tx in [9, 10]:
        fill_tile_4color(img, tx, 16, P4, [
            [2,2,2,2,2,2,2,2],
            [2,0,0,0,0,0,0,2],
            [2,0,1,1,1,1,0,2],
            [2,0,1,3,3,1,0,2],
            [2,0,1,3,3,1,0,2],
            [2,0,1,1,1,1,0,2],
            [2,0,0,0,0,0,0,2],
            [2,2,2,2,2,2,2,2],
        ])
        fill_tile_4color(img, tx, 17, P4, [
            [2,0,0,0,0,0,0,2],
            [2,0,1,1,1,1,0,2],
            [2,0,1,3,3,1,0,2],
            [2,0,1,3,3,1,0,2],
            [2,0,1,1,1,1,0,2],
            [2,0,0,0,0,0,0,2],
            [2,2,2,2,2,2,2,2],
            [2,2,2,2,2,2,2,2],
        ])

    # Sign above exit (ty=15, tx=9,10)
    for tx in [9, 10]:
        fill_tile_4color(img, tx, 15, P2, [
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,1,1,1,1,1,1,0],
            [0,1,3,1,3,1,1,0],
            [0,1,1,3,1,3,1,0],
            [0,1,1,1,1,1,1,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
        ])

    return img


# ====================================================================
# Stage 2: City Street / Bus Stop (warming palette)
# ====================================================================
# P0: Sky        = (sky_light, sky_mid, sky_warm, sky_white)
# P1: Brick      = (brick_dark, brick_mid, brick_light, brick_line)
# P2: Window     = (win_dark, win_glass, win_frame, brick_mid)
# P3: Shop       = (shop_dark, shop_wood, shop_cream, shop_sign)
# P4: Sidewalk   = (side_light, side_mid, side_dark, side_line)
# P5: Road       = (road_dark, road_mid, road_line, road_light)
# P6: Bus stop   = (bus_dark, bus_blue, bus_white, bus_pole)
# P7: Tree       = (tree_dark, tree_mid, tree_light, tree_trunk)

def draw_city():
    P0 = [(176,192,216), (152,168,200), (200,192,184), (224,228,232)]  # sky
    P1 = [(128,72,48), (168,96,64), (192,128,88), (104,56,32)]         # brick
    P2 = [(40,48,56), (96,120,144), (160,144,120), (168,96,64)]        # window
    P3 = [(96,72,40), (160,128,80), (224,216,192), (192,160,96)]       # shop
    P4 = [(200,192,176), (176,168,152), (144,136,120), (128,120,104)]  # sidewalk
    P5 = [(80,80,72), (104,104,96), (200,192,160), (120,120,112)]      # road
    P6 = [(40,56,80), (64,96,144), (216,224,232), (96,96,96)]          # bus stop
    P7 = [(56,88,48), (80,128,64), (112,160,96), (96,72,48)]           # tree

    img = Image.new('RGB', (W, H), P4[1])

    # Sky (ty=0,1)
    for tx in range(20):
        fill_tile(img, tx, 0, P0[0])
        fill_tile_pattern(img, tx, 1, P0[1], P0[0], 'top_half')
    # Clouds
    fill_tile_4color(img, 5, 0, P0, [
        [0,0,0,3,3,3,0,0],
        [0,0,3,3,3,3,3,0],
        [0,3,3,3,3,3,3,0],
        [0,0,3,3,3,3,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
    ])
    fill_tile_4color(img, 13, 0, P0, [
        [0,0,0,0,3,3,0,0],
        [0,0,3,3,3,3,3,0],
        [0,3,3,3,3,3,3,3],
        [0,0,3,3,3,3,3,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
    ])

    # Buildings (ty=2-7)
    # Left building (tx=0-8)
    for ty in range(2, 8):
        for tx in range(0, 9):
            fill_tile_pattern(img, tx, ty, P1[1], P1[3], 'hstripe')

    # Windows on left building (using P2)
    for ty in [3, 5]:
        for tx in [1, 3, 5, 7]:
            fill_tile_4color(img, tx, ty, P2, [
                [3,3,3,3,3,3,3,3],
                [3,0,0,2,0,0,0,3],
                [3,0,1,2,1,0,0,3],
                [3,0,1,2,1,0,0,3],
                [3,2,2,2,2,2,2,3],
                [3,0,1,2,1,0,0,3],
                [3,0,0,2,0,0,0,3],
                [3,3,3,3,3,3,3,3],
            ])

    # Right building (tx=12-19)
    for ty in range(2, 8):
        for tx in range(12, 20):
            fill_tile_pattern(img, tx, ty, P1[0], P1[3], 'hstripe')

    # Windows on right building
    for ty in [3, 5]:
        for tx in [13, 15, 17]:
            fill_tile_4color(img, tx, ty, P2, [
                [3,3,3,3,3,3,3,3],
                [3,0,0,2,0,0,0,3],
                [3,0,1,2,1,0,0,3],
                [3,0,1,2,1,0,0,3],
                [3,2,2,2,2,2,2,3],
                [3,0,1,2,1,0,0,3],
                [3,0,0,2,0,0,0,3],
                [3,3,3,3,3,3,3,3],
            ])

    # Tree (tx=9,10,11, ty=4-7)
    for ty in [4, 5]:
        for tx in [9, 10, 11]:
            fill_tile_4color(img, tx, ty, P7, [
                [0,0,1,2,2,1,0,0],
                [0,1,2,2,2,2,1,0],
                [1,2,2,2,2,2,2,1],
                [1,2,2,2,2,2,2,1],
                [0,1,2,2,2,2,1,0],
                [0,1,1,2,2,1,1,0],
                [0,0,1,1,1,1,0,0],
                [0,0,0,1,1,0,0,0],
            ])
    # Trunk
    fill_tile_4color(img, 10, 6, P7, [
        [0,0,0,3,3,0,0,0],
        [0,0,0,3,3,0,0,0],
        [0,0,0,3,3,0,0,0],
        [0,0,0,3,3,0,0,0],
        [0,0,0,3,3,0,0,0],
        [0,0,0,3,3,0,0,0],
        [0,0,0,3,3,0,0,0],
        [0,0,0,3,3,0,0,0],
    ])
    fill_tile_4color(img, 10, 7, P7, [
        [0,0,0,3,3,0,0,0],
        [0,0,0,3,3,0,0,0],
        [0,0,3,3,3,3,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
    ])

    # Shop (tx=0-6, ty=7-10)
    for ty in [7, 8, 9, 10]:
        for tx in range(0, 7):
            fill_tile(img, tx, ty, P3[2])
    # Shop sign area (ty=7)
    for tx in range(0, 7):
        fill_tile_pattern(img, tx, 7, P3[1], P3[3], 'top_half')
    # Shop door
    fill_tile_4color(img, 3, 9, P3, [
        [2,2,0,0,0,0,2,2],
        [2,0,0,1,1,0,0,2],
        [2,0,0,1,1,0,0,2],
        [2,0,0,1,1,0,0,2],
        [2,0,0,1,1,0,0,2],
        [2,0,0,1,1,0,0,2],
        [2,0,0,1,1,0,0,2],
        [2,2,0,0,0,0,2,2],
    ])
    fill_tile_4color(img, 3, 10, P3, [
        [2,0,0,1,1,0,0,2],
        [2,0,0,1,1,0,0,2],
        [2,0,0,1,1,0,0,2],
        [2,0,0,1,1,0,0,2],
        [2,0,0,0,0,0,0,2],
        [2,2,2,2,2,2,2,2],
        [2,2,2,2,2,2,2,2],
        [2,2,2,2,2,2,2,2],
    ])

    # Bus stop sign (tx=16, ty=7,8)
    fill_tile_4color(img, 16, 7, P6, [
        [0,0,0,0,0,0,0,0],
        [0,1,1,1,1,1,1,0],
        [0,1,2,2,2,2,1,0],
        [0,1,2,0,0,2,1,0],
        [0,1,2,2,2,2,1,0],
        [0,1,1,1,1,1,1,0],
        [0,0,0,3,3,0,0,0],
        [0,0,0,3,3,0,0,0],
    ])
    fill_tile_4color(img, 16, 8, P6, [
        [0,0,0,3,3,0,0,0],
        [0,0,0,3,3,0,0,0],
        [0,0,0,3,3,0,0,0],
        [0,0,0,3,3,0,0,0],
        [0,0,0,3,3,0,0,0],
        [0,0,0,3,3,0,0,0],
        [0,0,0,3,3,0,0,0],
        [0,0,0,3,3,0,0,0],
    ])

    # Sidewalk (ty=11,12)
    for tx in range(20):
        fill_tile_pattern(img, tx, 11, P4[0], P4[3], 'border')
        fill_tile_pattern(img, tx, 12, P4[1], P4[3], 'border')

    # Road (ty=13-16)
    for ty in range(13, 17):
        for tx in range(20):
            fill_tile(img, tx, ty, P5[0])
    # Road center line (ty=14,15)
    for tx in range(0, 20, 2):
        fill_tile_pattern(img, tx, 14, P5[0], P5[2], 'hstripe')

    # Bottom curb (ty=17)
    for tx in range(20):
        fill_tile_pattern(img, tx, 17, P4[2], P4[1], 'top_half')

    return img


# ====================================================================
# Stage 3: UBC Campus (vibrant palette)
# ====================================================================
# P0: Sky       = (sky_light, sky_mid, sky_white, sky_warm)
# P1: Grass     = (grass_dark, grass_mid, grass_light, grass_line)
# P2: Path      = (path_dark, path_mid, path_light, path_line)
# P3: Building  = (bldg_dark, bldg_mid, bldg_light, bldg_roof)
# P4: Tree      = (tree_dark, tree_mid, tree_light, tree_trunk)
# P5: Sign      = (sign_dark, sign_bg, sign_white, sign_frame)
# P6: Flower    = (flower_red, flower_yell, flower_green, grass_mid)
# P7: Water     = (water_dark, water_mid, water_light, water_white)

def draw_campus():
    P0 = [(128,192,248), (96,160,232), (232,240,248), (176,208,240)]   # sky
    P1 = [(24,96,32), (64,176,80), (96,208,112), (48,144,56)]          # grass
    P2 = [(160,144,112), (192,176,144), (216,200,168), (144,128,96)]   # path
    P3 = [(96,72,56), (160,128,96), (200,176,144), (128,96,64)]        # building
    P4 = [(24,96,32), (48,144,56), (80,192,96), (96,64,32)]            # tree
    P5 = [(32,32,48), (64,48,40), (248,248,240), (128,112,96)]         # sign
    P6 = [(224,64,64), (240,208,64), (64,160,80), (64,176,80)]         # flower
    P7 = [(48,96,176), (80,144,216), (128,192,240), (200,224,248)]     # water

    img = Image.new('RGB', (W, H), P1[1])

    # Sky (ty=0,1,2)
    for tx in range(20):
        fill_tile(img, tx, 0, P0[0])
        fill_tile(img, tx, 1, P0[1])
        fill_tile_pattern(img, tx, 2, P0[1], P0[3], 'top_half')
    # Clouds
    fill_tile_4color(img, 4, 0, P0, [
        [0,0,2,2,2,0,0,0],
        [0,2,2,2,2,2,0,0],
        [0,2,2,2,2,2,2,0],
        [0,0,2,2,2,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
    ])
    fill_tile_4color(img, 14, 0, P0, [
        [0,0,0,2,2,0,0,0],
        [0,0,2,2,2,2,0,0],
        [0,2,2,2,2,2,2,0],
        [0,0,2,2,2,2,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0],
    ])

    # Trees at top (ty=2,3, various tx)
    for tx in [0, 1, 2, 15, 16, 17, 18, 19]:
        fill_tile_4color(img, tx, 2, P4, [
            [0,0,1,2,2,1,0,0],
            [0,1,2,2,2,2,1,0],
            [1,2,2,2,2,2,2,1],
            [1,1,2,2,2,2,1,1],
            [0,1,1,2,2,1,1,0],
            [0,0,1,1,1,1,0,0],
            [0,0,0,3,3,0,0,0],
            [0,0,0,3,3,0,0,0],
        ])
    for tx in [0, 1, 2, 15, 16, 17, 18, 19]:
        fill_tile_4color(img, tx, 3, P4, [
            [0,0,0,3,3,0,0,0],
            [0,0,0,3,3,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
        ])

    # Main building: Student Center (tx=5-14, ty=3-8)
    for ty in range(3, 9):
        for tx in range(5, 15):
            fill_tile(img, tx, ty, P3[1])
    # Roof (ty=3)
    for tx in range(5, 15):
        fill_tile_pattern(img, tx, 3, P3[3], P3[1], 'top_half')
    # Windows (ty=4,5,6)
    for ty in [5, 6]:
        for tx in [6, 8, 10, 12]:
            fill_tile_4color(img, tx, ty, P3, [
                [1,1,1,1,1,1,1,1],
                [1,0,0,2,0,0,0,1],
                [1,0,0,2,0,0,0,1],
                [1,0,0,2,0,0,0,1],
                [1,2,2,2,2,2,2,1],
                [1,0,0,2,0,0,0,1],
                [1,0,0,2,0,0,0,1],
                [1,1,1,1,1,1,1,1],
            ])

    # Sign on building (tx=7-12, ty=4)
    for tx in [7, 8, 9, 10, 11, 12]:
        fill_tile_4color(img, tx, 4, P5, [
            [3,3,3,3,3,3,3,3],
            [3,1,1,1,1,1,1,3],
            [3,1,2,0,2,0,1,3],
            [3,1,0,2,0,2,1,3],
            [3,1,2,0,2,0,1,3],
            [3,1,1,1,1,1,1,3],
            [3,3,3,3,3,3,3,3],
            [3,3,3,3,3,3,3,3],
        ])

    # Door (tx=9,10, ty=7,8)
    for tx in [9, 10]:
        fill_tile_4color(img, tx, 7, P3, [
            [1,1,0,0,0,0,1,1],
            [1,0,0,2,2,0,0,1],
            [1,0,0,2,2,0,0,1],
            [1,0,0,2,2,0,0,1],
            [1,0,0,2,2,0,0,1],
            [1,0,0,2,2,0,0,1],
            [1,0,0,2,2,0,0,1],
            [1,1,0,0,0,0,1,1],
        ])
        fill_tile_4color(img, tx, 8, P3, [
            [1,0,0,2,2,0,0,1],
            [1,0,0,2,2,0,0,1],
            [1,0,0,2,2,0,0,1],
            [1,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1],
            [1,1,1,1,1,1,1,1],
            [1,1,1,1,1,1,1,1],
            [1,1,1,1,1,1,1,1],
        ])

    # Grass (ty=9,10,11)
    for ty in [9, 10, 11]:
        for tx in range(20):
            if (tx + ty) % 3 == 0:
                fill_tile_pattern(img, tx, ty, P1[1], P1[2], 'checker')
            elif (tx + ty) % 3 == 1:
                fill_tile_pattern(img, tx, ty, P1[1], P1[0], 'checker')
            else:
                fill_tile(img, tx, ty, P1[1])

    # Flower patches (using P6)
    for tx in [1, 3, 16, 18]:
        fill_tile_4color(img, tx, 10, P6, [
            [3,3,3,3,3,3,3,3],
            [3,3,0,3,3,1,3,3],
            [3,0,0,0,1,1,1,3],
            [3,3,0,3,3,1,3,3],
            [3,3,2,3,3,2,3,3],
            [3,3,2,3,3,2,3,3],
            [3,3,3,3,3,3,3,3],
            [3,3,3,3,3,3,3,3],
        ])

    # Stone path (ty=12,13,14,15)
    for ty in range(12, 16):
        for tx in range(20):
            fill_tile_pattern(img, tx, ty, P2[2], P2[3], 'border')

    # Fountain (tx=7-12, ty=12-14)
    for ty in [12, 13, 14]:
        for tx in [7, 8, 9, 10, 11, 12]:
            fill_tile_4color(img, tx, ty, P7, [
                [0,0,1,1,1,1,0,0],
                [0,1,2,2,2,2,1,0],
                [1,2,3,3,3,3,2,1],
                [1,2,3,3,3,3,2,1],
                [1,2,3,3,3,3,2,1],
                [1,2,2,2,2,2,2,1],
                [0,1,1,1,1,1,1,0],
                [0,0,0,0,0,0,0,0],
            ])

    # Bottom grass (ty=16,17)
    for ty in [16, 17]:
        for tx in range(20):
            fill_tile_pattern(img, tx, ty, P1[1], P1[3], 'checker')

    # Side trees on path (tx=0,1,18,19 ty=12,13)
    for tx in [0, 1, 18, 19]:
        fill_tile_4color(img, tx, 12, P4, [
            [0,1,2,2,2,2,1,0],
            [1,2,2,2,2,2,2,1],
            [1,2,2,2,2,2,2,1],
            [0,1,2,2,2,2,1,0],
            [0,0,1,1,1,1,0,0],
            [0,0,0,3,3,0,0,0],
            [0,0,0,3,3,0,0,0],
            [0,0,0,3,3,0,0,0],
        ])

    return img


# ====================================================================
# Main
# ====================================================================

def main():
    os.makedirs(ASSETS_DIR, exist_ok=True)

    airport = draw_airport()
    airport_path = os.path.join(ASSETS_DIR, 'ch3_airport.png')
    airport.save(airport_path)
    print(f"Saved {airport_path}")

    city = draw_city()
    city_path = os.path.join(ASSETS_DIR, 'ch3_city.png')
    city.save(city_path)
    print(f"Saved {city_path}")

    campus = draw_campus()
    campus_path = os.path.join(ASSETS_DIR, 'ch3_campus.png')
    campus.save(campus_path)
    print(f"Saved {campus_path}")

    # Verify: check that every tile has <= 4 colors
    for name, img_obj in [("airport", airport), ("city", city), ("campus", campus)]:
        bad = 0
        for ty in range(ROWS):
            for tx in range(COLS):
                colors = set()
                for dy in range(8):
                    for dx in range(8):
                        colors.add(img_obj.getpixel((tx*8+dx, ty*8+dy)))
                if len(colors) > 4:
                    print(f"WARNING: {name} tile ({tx},{ty}) has {len(colors)} colors!")
                    bad += 1
        if bad == 0:
            print(f"  {name}: all tiles OK (<=4 colors each)")

    print("\nDone! Next: run png2asset to convert.")


if __name__ == '__main__':
    main()
