#!/usr/bin/env /opt/homebrew/bin/python3
"""
Draw Chapter 1 background as pixel art.

Outputs a 160x144 RGB PNG that strictly follows GBC constraints:
- Max 4 colors per 8x8 tile
- Max 8 palettes total

The scene: A blue room with a back window/opening and a green tiled floor.
Baby sits on the floor during the Zhuazhou tradition scene.
"""

import os
from PIL import Image

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'chapter1')

W, H = 160, 144
TILE = 8
COLS, ROWS = W // TILE, H // TILE  # 20 x 18

# --- Palettes (GBC 5-bit: all values multiples of 8) ---

PAL_WALL = [
    (16, 24, 72),     # 0: dark navy
    (48, 80, 144),    # 1: medium blue
    (96, 136, 192),   # 2: light blue
    (176, 200, 232),  # 3: very light blue
]

PAL_WINDOW = [
    (240, 232, 192),  # 0: cream
    (216, 208, 168),  # 1: pale yellow
    (184, 192, 168),  # 2: sage
    (248, 248, 240),  # 3: near white
]

PAL_FLOOR = [
    (24, 56, 24),     # 0: dark green
    (48, 104, 40),    # 1: medium green
    (80, 144, 64),    # 2: light green
    (120, 176, 96),   # 3: pale green
]

PAL_TRANS = [
    (16, 24, 72),     # 0: dark navy (matches wall 0)
    (40, 56, 96),     # 1: gray-blue
    (48, 104, 40),    # 2: medium green (matches floor 1)
    (24, 56, 24),     # 3: dark green (matches floor 0)
]

# --- Tile definitions (8x8 grids of palette indices 0-3) ---

def solid(c):
    return [[c]*8 for _ in range(8)]

# Wall tiles (palette 0)
TILE_DARK = solid(0)       # dark navy
TILE_WALL = solid(1)       # medium blue
TILE_WALL_LIGHT = solid(2) # light blue

# Left angle: dark top-left, wall bottom-right (perspective wall)
TILE_ANGLE_L = [
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,1],
    [0,0,0,0,0,0,1,1],
    [0,0,0,0,0,1,1,1],
    [0,0,0,0,1,1,1,1],
    [0,0,0,1,1,1,1,1],
    [0,0,1,1,1,1,1,1],
    [0,1,1,1,1,1,1,1],
]

# Right angle: mirror
TILE_ANGLE_R = [row[::-1] for row in TILE_ANGLE_L]

# Lower angle tiles (more gradual, for rows further from ceiling)
TILE_ANGLE_L2 = [
    [0,0,0,1,1,1,1,1],
    [0,0,1,1,1,1,1,1],
    [0,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1],
]

TILE_ANGLE_R2 = [row[::-1] for row in TILE_ANGLE_L2]

# Window tiles (palette 1)
TILE_WIN_BRIGHT = [
    [3,3,3,3,3,3,3,3],
    [3,3,0,0,0,0,3,3],
    [3,0,0,0,0,0,0,3],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
]

TILE_WIN_MID = solid(0)  # cream fill

TILE_WIN_LOW = [
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1],
    [2,2,2,2,2,2,2,2],
    [2,2,2,2,2,2,2,2],
    [2,2,2,2,2,2,2,2],
    [2,2,2,2,2,2,2,2],
]

# Window side edges (palette 0 — wall with light edge)
TILE_WIN_EDGE_L = [
    [1,1,1,1,1,1,2,3],
    [1,1,1,1,1,1,2,3],
    [1,1,1,1,1,1,2,3],
    [1,1,1,1,1,1,2,3],
    [1,1,1,1,1,1,2,3],
    [1,1,1,1,1,1,2,3],
    [1,1,1,1,1,1,2,3],
    [1,1,1,1,1,1,2,3],
]

TILE_WIN_EDGE_R = [row[::-1] for row in TILE_WIN_EDGE_L]

# Baseboard tile (palette 3: transition)
TILE_BASEBOARD = [
    [1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [3,3,3,3,3,3,3,3],
    [3,3,3,3,3,3,3,3],
    [2,2,2,2,2,2,2,2],
    [2,2,2,2,2,2,2,2],
]

# Floor tiles (palette 2) — 4 tiles forming a 2x2 diamond pattern
TILE_FLOOR_TL = [
    [0,0,0,0,0,0,0,1],
    [0,0,0,0,0,0,1,1],
    [0,0,0,0,0,1,1,2],
    [0,0,0,0,1,1,2,2],
    [0,0,0,1,1,2,2,2],
    [0,0,1,1,2,2,2,3],
    [0,1,1,2,2,2,3,3],
    [1,1,2,2,2,3,3,3],
]

TILE_FLOOR_TR = [row[::-1] for row in TILE_FLOOR_TL]
TILE_FLOOR_BL = TILE_FLOOR_TL[::-1]
TILE_FLOOR_BR = TILE_FLOOR_TR[::-1]

# --- Tilemap: (tile_data, palette_index) for each position ---

def build_tilemap():
    """Build 20x18 tilemap. Returns list of rows, each row is list of (tile, pal)."""
    tmap = []

    # Perspective: dark columns on each side per row (rows 0-7)
    dark_cols = [4, 3, 2, 1, 0, 0, 0, 0]

    # Window spans (left col inclusive, right col exclusive) per row
    # Window visible in rows 0-4, wider toward bottom
    win_spans = {
        0: (7, 13),   # 6 tiles wide
        1: (6, 14),   # 8 tiles wide
        2: (5, 15),   # 10 tiles wide
        3: (5, 15),   # 10 tiles wide
        4: (6, 14),   # 8 tiles (lower edge, fading into wall)
    }

    for row in range(ROWS):
        tiles = []

        if row <= 4:
            dc = dark_cols[row]
            ws, we = win_spans.get(row, (10, 10))

            for col in range(COLS):
                # Left dark corner
                if dc > 0 and col < dc - 1:
                    tiles.append((TILE_DARK, 0))
                elif dc > 0 and col == dc - 1:
                    tiles.append((TILE_ANGLE_L if row < 2 else TILE_ANGLE_L2, 0))
                # Right dark corner
                elif dc > 0 and col > COLS - dc:
                    tiles.append((TILE_DARK, 0))
                elif dc > 0 and col == COLS - dc:
                    tiles.append((TILE_ANGLE_R if row < 2 else TILE_ANGLE_R2, 0))
                # Window area
                elif ws <= col < we:
                    if col == ws:
                        tiles.append((TILE_WIN_EDGE_L, 0))
                    elif col == we - 1:
                        tiles.append((TILE_WIN_EDGE_R, 0))
                    elif row == 0:
                        tiles.append((TILE_WIN_BRIGHT, 1))
                    elif row <= 3:
                        tiles.append((TILE_WIN_MID, 1))
                    else:
                        tiles.append((TILE_WIN_LOW, 1))
                # Wall
                else:
                    tiles.append((TILE_WALL, 0))

        elif row <= 6:
            for col in range(COLS):
                tiles.append((TILE_WALL, 0))

        elif row == 7:
            for col in range(COLS):
                tiles.append((TILE_BASEBOARD, 3))

        else:
            fr = row - 8
            for col in range(COLS):
                if fr % 2 == 0:
                    tiles.append((TILE_FLOOR_TL if col % 2 == 0 else TILE_FLOOR_TR, 2))
                else:
                    tiles.append((TILE_FLOOR_BL if col % 2 == 0 else TILE_FLOOR_BR, 2))

        tmap.append(tiles)

    return tmap


def render(tmap):
    """Render tilemap to 160x144 RGB image."""
    palettes = [PAL_WALL, PAL_WINDOW, PAL_FLOOR, PAL_TRANS]
    img = Image.new('RGB', (W, H))
    pixels = img.load()

    for row in range(ROWS):
        for col in range(COLS):
            tile_data, pal_idx = tmap[row][col]
            pal = palettes[pal_idx]
            for dy in range(TILE):
                for dx in range(TILE):
                    ci = tile_data[dy][dx]
                    pixels[col * TILE + dx, row * TILE + dy] = pal[ci]

    return img


def verify(img):
    """Verify GBC constraints: max 4 colors per 8x8 tile."""
    pixels = img.load()
    max_colors = 0
    total_unique = set()

    for ty in range(ROWS):
        for tx in range(COLS):
            tile_colors = set()
            for dy in range(TILE):
                for dx in range(TILE):
                    c = pixels[tx * TILE + dx, ty * TILE + dy]
                    tile_colors.add(c)
                    total_unique.add(c)
            if len(tile_colors) > 4:
                print(f"  WARNING: tile ({tx},{ty}) has {len(tile_colors)} colors!")
            max_colors = max(max_colors, len(tile_colors))

    print(f"  Max colors per tile: {max_colors}")
    print(f"  Total unique colors: {len(total_unique)}")
    return max_colors <= 4


def main():
    os.makedirs(ASSETS_DIR, exist_ok=True)

    print("Drawing Chapter 1 background...")
    tmap = build_tilemap()
    img = render(tmap)

    print("Verifying GBC constraints...")
    ok = verify(img)
    if not ok:
        print("  ERROR: Constraints violated!")
        return

    out = os.path.join(ASSETS_DIR, 'ch1_bg.png')
    img.save(out)
    print(f"Saved: {out} ({img.size})")
    print("Next: run png2asset on this file.")


if __name__ == '__main__':
    main()
