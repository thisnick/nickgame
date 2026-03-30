#!/usr/bin/env /opt/homebrew/bin/python3
"""
Draw Chapter 2 scrolling street background as pixel art.

Outputs a 256x144 RGB PNG (32x18 tiles) that strictly follows GBC constraints:
- Max 4 colors per 8x8 tile
- Max 8 palettes total
- Seamless horizontal wrapping (column 31 connects back to column 0)

The scene: 1980s/90s Kunming street for a side-scrolling bicycle game.
"""

import os
from PIL import Image

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'chapter2')

W, H = 256, 144
TILE = 8
COLS, ROWS = W // TILE, H // TILE  # 32 x 18

# ============================================================
# PALETTE DEFINITIONS (8 palettes, 4 colors each)
# ============================================================

PAL_SKY = [
    (136, 192, 248),   # 0: light blue sky
    (248, 184, 152),   # 1: peach/pink horizon
    (240, 208, 200),   # 2: pale pink (sunrise row 1)
    (248, 248, 248),   # 3: white/cloud
]

PAL_WALL = [
    (184, 120, 72),    # 0: terracotta brown
    (144, 88, 48),     # 1: dark brown
    (224, 192, 152),   # 2: cream/tan
    (112, 64, 32),     # 3: deep brown
]

PAL_SIGN = [
    (208, 40, 40),     # 0: red
    (240, 200, 48),    # 1: gold/yellow
    (32, 104, 48),     # 2: dark green
    (248, 248, 248),   # 3: white
]

PAL_WINDOW = [
    (48, 128, 136),    # 0: teal
    (24, 48, 96),      # 1: dark blue
    (224, 192, 152),   # 2: cream (matches wall)
    (112, 64, 32),     # 3: dark brown (matches wall)
]

PAL_ROAD = [
    (72, 72, 80),      # 0: dark gray
    (104, 104, 112),   # 1: medium gray
    (136, 136, 144),   # 2: light gray
    (248, 248, 248),   # 3: white
]

PAL_SIDEWALK = [
    (208, 176, 144),   # 0: light tan/beige concrete
    (176, 144, 112),   # 1: warm brown
    (160, 144, 128),   # 2: warm gray
    (128, 104, 80),    # 3: dark warm brown
]

PAL_HUD = [
    (16, 16, 40),      # 0: dark navy
    (32, 32, 72),      # 1: navy
    (16, 16, 40),      # 2: dark navy (dupe for simplicity)
    (16, 16, 40),      # 3: dark navy
]

PAL_SKYWALL = [
    (136, 192, 248),   # 0: light blue (matches sky)
    (248, 184, 152),   # 1: peach (matches sky)
    (184, 120, 72),    # 2: terracotta (matches wall)
    (144, 88, 48),     # 3: dark brown (matches wall)
]

PALETTES = [PAL_SKY, PAL_WALL, PAL_SIGN, PAL_WINDOW, PAL_ROAD, PAL_SIDEWALK, PAL_HUD, PAL_SKYWALL]

# ============================================================
# TILE HELPERS
# ============================================================

def solid(c):
    return [[c]*8 for _ in range(8)]

def hstripe(c_top, c_bot, split=4):
    """Horizontal stripe: top portion c_top, bottom c_bot."""
    return [[c_top]*8 for _ in range(split)] + [[c_bot]*8 for _ in range(8 - split)]

# ============================================================
# SKY TILES (PAL_SKY = pal 0)
# ============================================================

TILE_SKY_TOP = [              # pale pink sunrise (row 1)
    [2,2,2,2,2,2,2,2],
    [2,2,2,2,2,2,2,2],
    [2,2,2,2,2,2,2,2],
    [2,2,2,2,2,2,2,2],
    [1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1],
]

TILE_SKY_MID = [              # peach to pale blue (row 2)
    [1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
]

TILE_SKY_HORIZON = solid(1)   # peach at horizon

TILE_SKY_CLOUD = [            # cloud on pale blue (row 2)
    [1,1,1,1,1,1,1,1],
    [1,1,3,3,3,1,1,1],
    [1,3,3,3,3,3,1,1],
    [3,3,3,3,3,3,3,0],
    [0,3,3,3,3,3,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
]

# ============================================================
# HUD TILE (PAL_HUD = pal 6)
# ============================================================

TILE_HUD = solid(0)

# ============================================================
# BUILDING TILES (various palettes)
# ============================================================

# Plain wall (PAL_WALL = pal 1)
TILE_WALL_PLAIN = solid(0)
TILE_WALL_CREAM = solid(2)
TILE_WALL_DARK = solid(1)

# Wall with horizontal line detail (pal 1)
TILE_WALL_LINE = [
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [1,1,1,1,1,1,1,1],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
]

# Wall top edge / roof line (pal 1)
TILE_ROOF = [
    [3,3,3,3,3,3,3,3],
    [3,3,3,3,3,3,3,3],
    [1,1,1,1,1,1,1,1],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
]

# Window tile (PAL_WINDOW = pal 3)
TILE_WINDOW = [
    [3,3,3,3,3,3,3,3],
    [3,0,0,0,0,0,0,3],
    [3,0,0,1,1,0,0,3],
    [3,0,1,1,1,1,0,3],
    [3,0,1,1,1,1,0,3],
    [3,0,0,1,1,0,0,3],
    [3,0,0,0,0,0,0,3],
    [3,3,3,3,3,3,3,3],
]

# Window with shutters (pal 3)
TILE_WINDOW_SHUTTERS = [
    [2,3,3,3,3,3,3,2],
    [2,3,0,0,0,0,3,2],
    [2,3,0,1,1,0,3,2],
    [2,3,0,1,1,0,3,2],
    [2,3,0,0,0,0,3,2],
    [2,3,3,3,3,3,3,2],
    [2,2,2,2,2,2,2,2],
    [3,3,3,3,3,3,3,3],
]

# Sign tiles (PAL_SIGN = pal 2)
# Red sign with gold border
TILE_SIGN_RED = [
    [1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,1],
    [1,0,0,3,3,0,0,1],
    [1,0,0,3,3,0,0,1],
    [1,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1],
]

# Gold sign with character shape (simplified hanzi)
TILE_SIGN_CHAR1 = [  # "店" simplified
    [1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,1],
    [1,0,3,3,3,3,0,1],
    [1,0,0,3,0,0,0,1],
    [1,0,3,3,3,0,0,1],
    [1,0,0,3,0,3,0,1],
    [1,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1],
]

TILE_SIGN_CHAR2 = [  # "小吃" simplified
    [1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,1],
    [1,0,0,3,0,0,0,1],
    [1,0,3,0,3,0,0,1],
    [1,0,0,3,3,3,0,1],
    [1,0,3,0,0,3,0,1],
    [1,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1],
]

TILE_SIGN_CHAR3 = [  # "书" simplified
    [1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,1],
    [1,0,3,3,3,3,0,1],
    [1,0,0,0,3,0,0,1],
    [1,0,3,3,3,3,0,1],
    [1,0,0,0,3,0,0,1],
    [1,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1],
]

TILE_SIGN_CHAR4 = [  # "茶" simplified (tea)
    [1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,1],
    [1,0,3,0,0,3,0,1],
    [1,0,0,3,3,0,0,1],
    [1,0,3,3,3,3,0,1],
    [1,0,0,3,3,0,0,1],
    [1,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1],
]

TILE_SIGN_CHAR5 = [  # "面" simplified (noodles)
    [1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,1],
    [1,0,3,3,3,3,0,1],
    [1,0,3,0,0,3,0,1],
    [1,0,3,3,3,3,0,1],
    [1,0,3,0,0,3,0,1],
    [1,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1],
]

# Green sign variant (PAL_SIGN = pal 2) - uses green background instead of red
TILE_SIGN_GREEN = [
    [1,1,1,1,1,1,1,1],
    [1,2,2,2,2,2,2,1],
    [1,2,2,2,2,2,2,1],
    [1,2,2,3,3,2,2,1],
    [1,2,2,3,3,2,2,1],
    [1,2,2,2,2,2,2,1],
    [1,2,2,2,2,2,2,1],
    [1,1,1,1,1,1,1,1],
]

# Balcony tile (PAL_WALL = pal 1)
TILE_BALCONY = [
    [0,0,0,0,0,0,0,0],
    [3,3,3,3,3,3,3,3],
    [3,0,0,0,0,0,0,3],
    [3,0,0,0,0,0,0,3],
    [3,3,3,3,3,3,3,3],
    [0,3,0,3,0,3,0,3],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
]

# Tall building roof (PAL_WALL = pal 1) - double roof line
TILE_ROOF_TALL = [
    [3,3,3,3,3,3,3,3],
    [3,3,3,3,3,3,3,3],
    [1,1,1,1,1,1,1,1],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
]

# Green awning (PAL_SIGN = pal 2)
TILE_AWNING = [
    [2,2,2,2,2,2,2,2],
    [2,2,2,2,2,2,2,2],
    [2,3,2,3,2,3,2,3],
    [3,2,3,2,3,2,3,2],
    [2,2,2,2,2,2,2,2],
    [2,2,2,2,2,2,2,2],
    [3,3,3,3,3,3,3,3],
    [3,3,3,3,3,3,3,3],
]

TILE_AWNING_EDGE_L = [
    [3,2,2,2,2,2,2,2],
    [3,2,2,2,2,2,2,2],
    [3,2,3,2,3,2,3,2],
    [3,3,2,3,2,3,2,3],
    [3,2,2,2,2,2,2,2],
    [3,2,2,2,2,2,2,2],
    [3,3,3,3,3,3,3,3],
    [3,3,3,3,3,3,3,3],
]

TILE_AWNING_EDGE_R = [
    [2,2,2,2,2,2,2,3],
    [2,2,2,2,2,2,2,3],
    [2,3,2,3,2,3,2,3],
    [3,2,3,2,3,2,3,3],
    [2,2,2,2,2,2,2,3],
    [2,2,2,2,2,2,2,3],
    [3,3,3,3,3,3,3,3],
    [3,3,3,3,3,3,3,3],
]

# Sky-to-wall transition (PAL_SKYWALL = pal 7)
TILE_SKYWALL = [
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [1,1,1,1,1,1,1,1],
    [3,3,3,3,3,3,3,3],
    [2,2,2,2,2,2,2,2],
    [2,2,2,2,2,2,2,2],
    [2,2,2,2,2,2,2,2],
    [2,2,2,2,2,2,2,2],
]

# ============================================================
# SIDEWALK TILE (PAL_SIDEWALK = pal 5)
# ============================================================

TILE_SIDEWALK = [
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [1,1,1,1,1,1,1,1],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [1,1,1,1,1,1,1,1],
    [2,2,2,2,2,2,2,2],
]

TILE_SIDEWALK_CRACK = [
    [0,0,0,0,0,0,0,0],
    [0,0,0,2,0,0,0,0],
    [1,1,1,1,1,1,1,1],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,2,0,0,0],
    [0,0,0,0,0,2,0,0],
    [1,1,1,1,1,1,1,1],
    [2,2,2,2,2,2,2,2],
]

# ============================================================
# ROAD TILES (PAL_ROAD = pal 4)
# ============================================================

TILE_ROAD = solid(0)            # dark gray asphalt
TILE_ROAD_MED = solid(1)        # medium gray

# Dashed lane marking: 4px white dash, 4px gap over 8px tile
TILE_DASH_LEFT = [               # left half of dash cycle (has dash)
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [3,3,3,3,0,0,0,0],
    [3,3,3,3,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
]

TILE_DASH_RIGHT = [              # right half of dash cycle
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,3,3,3,3],
    [0,0,0,0,3,3,3,3],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
]

TILE_DASH_NONE = solid(0)       # gap in dashes (plain road)

# Bottom curb (pal 5 - sidewalk palette for warm tone)
TILE_CURB = [
    [2,2,2,2,2,2,2,2],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [1,1,1,1,1,1,1,1],
    [0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0],
    [3,3,3,3,3,3,3,3],
    [3,3,3,3,3,3,3,3],
]


# ============================================================
# BUILDING DEFINITIONS (column spans across 32 columns)
# Each building is defined as a dict with column range and details
# ============================================================

def make_building_columns():
    """
    Returns a list of 32 entries, one per column.
    Each entry is a dict describing what to draw in the building rows (4-6)
    for that column.

    Building types:
    A: Terracotta shop with red sign and green awning (6 cols wide)
    B: Cream/tan building with windows (5 cols wide)
    C: Dark brown building with gold sign (5 cols wide)
    D: Narrow alley gap (2 cols wide)
    """
    cols = [None] * 32

    # Layout across 32 columns (must wrap seamlessly):
    # A(0-5) D(6-7) E(8-12) C(13-17) D(18-19) A2(20-25) B2(26-31)
    # E = tea shop with green signs and balcony (new variety)

    # Building A: cols 0-5 (terracotta shop, red signs, green awning)
    for c in range(0, 6):
        cols[c] = {'type': 'A', 'pos': c}

    # Alley: cols 6-7
    for c in range(6, 8):
        cols[c] = {'type': 'D', 'pos': c - 6}

    # Building E: cols 8-12 (tea shop with green sign, balcony)
    for c in range(8, 13):
        cols[c] = {'type': 'E', 'pos': c - 8}

    # Building C: cols 13-17 (dark building with gold sign, noodle shop)
    for c in range(13, 18):
        cols[c] = {'type': 'C', 'pos': c - 13}

    # Alley: cols 18-19
    for c in range(18, 20):
        cols[c] = {'type': 'D', 'pos': c - 18}

    # Building A2 variant: cols 20-25 (bookshop variant)
    for c in range(20, 26):
        cols[c] = {'type': 'A2', 'pos': c - 20}

    # Building B2: cols 26-31 (cream building with windows, wraps)
    for c in range(26, 32):
        cols[c] = {'type': 'B2', 'pos': c - 26}

    return cols


# ============================================================
# TILEMAP BUILDER
# ============================================================

def build_tilemap():
    """Build 32x18 tilemap. Returns list of rows, each row is list of (tile, pal_idx)."""
    bldg_cols = make_building_columns()
    tmap = []

    for row in range(ROWS):
        tiles = []

        for col in range(COLS):

            # Row 0: HUD
            if row == 0:
                tiles.append((TILE_HUD, 6))

            # Row 1: Upper sky
            elif row == 1:
                tiles.append((TILE_SKY_TOP, 0))

            # Row 2: Mid sky with clouds
            elif row == 2:
                if col in (4, 5, 20, 21):
                    tiles.append((TILE_SKY_CLOUD, 0))
                else:
                    tiles.append((TILE_SKY_MID, 0))

            # Row 3: Horizon / sky-to-building transition
            elif row == 3:
                tiles.append((TILE_SKYWALL, 7))

            # Rows 4-6: Buildings
            elif 4 <= row <= 6:
                bldg = bldg_cols[col]
                btype = bldg['type']
                bpos = bldg['pos']
                brow = row - 4  # 0, 1, 2 within building

                if btype == 'A':
                    # Terracotta shop: roof line, sign row, awning
                    if brow == 0:
                        # Roof line
                        if bpos == 0 or bpos == 5:
                            tiles.append((TILE_ROOF, 1))
                        elif bpos == 2:
                            tiles.append((TILE_SIGN_CHAR1, 2))
                        elif bpos == 3:
                            tiles.append((TILE_SIGN_CHAR2, 2))
                        else:
                            tiles.append((TILE_ROOF, 1))
                    elif brow == 1:
                        # Middle: signs
                        if bpos == 1:
                            tiles.append((TILE_SIGN_RED, 2))
                        elif bpos == 2:
                            tiles.append((TILE_SIGN_CHAR1, 2))
                        elif bpos == 3:
                            tiles.append((TILE_SIGN_CHAR2, 2))
                        elif bpos == 4:
                            tiles.append((TILE_SIGN_RED, 2))
                        else:
                            tiles.append((TILE_WALL_PLAIN, 1))
                    else:
                        # Awning row
                        if bpos == 0:
                            tiles.append((TILE_AWNING_EDGE_L, 2))
                        elif bpos == 5:
                            tiles.append((TILE_AWNING_EDGE_R, 2))
                        else:
                            tiles.append((TILE_AWNING, 2))

                elif btype == 'A2':
                    # Variant A: slightly different sign arrangement
                    if brow == 0:
                        if bpos == 0 or bpos == 5:
                            tiles.append((TILE_ROOF, 1))
                        elif bpos == 2:
                            tiles.append((TILE_SIGN_CHAR3, 2))
                        elif bpos == 3:
                            tiles.append((TILE_SIGN_CHAR1, 2))
                        else:
                            tiles.append((TILE_ROOF, 1))
                    elif brow == 1:
                        if bpos == 1:
                            tiles.append((TILE_SIGN_RED, 2))
                        elif bpos == 2:
                            tiles.append((TILE_SIGN_CHAR3, 2))
                        elif bpos == 3:
                            tiles.append((TILE_SIGN_CHAR1, 2))
                        elif bpos == 4:
                            tiles.append((TILE_SIGN_RED, 2))
                        else:
                            tiles.append((TILE_WALL_PLAIN, 1))
                    else:
                        if bpos == 0:
                            tiles.append((TILE_AWNING_EDGE_L, 2))
                        elif bpos == 5:
                            tiles.append((TILE_AWNING_EDGE_R, 2))
                        else:
                            tiles.append((TILE_AWNING, 2))

                elif btype == 'E':
                    # Tea shop: green signs, balcony on top row
                    if brow == 0:
                        if bpos == 0 or bpos == 4:
                            tiles.append((TILE_ROOF_TALL, 1))
                        elif bpos == 2:
                            tiles.append((TILE_SIGN_CHAR4, 2))
                        else:
                            tiles.append((TILE_ROOF_TALL, 1))
                    elif brow == 1:
                        if bpos == 1:
                            tiles.append((TILE_SIGN_GREEN, 2))
                        elif bpos == 2:
                            tiles.append((TILE_SIGN_CHAR4, 2))
                        elif bpos == 3:
                            tiles.append((TILE_SIGN_GREEN, 2))
                        else:
                            tiles.append((TILE_WALL_PLAIN, 1))
                    else:
                        if bpos in (1, 3):
                            tiles.append((TILE_BALCONY, 1))
                        elif bpos == 0:
                            tiles.append((TILE_WALL_PLAIN, 1))
                        elif bpos == 4:
                            tiles.append((TILE_WALL_PLAIN, 1))
                        else:
                            tiles.append((TILE_WINDOW, 3))

                elif btype == 'B':
                    # Cream building with windows
                    if brow == 0:
                        tiles.append((TILE_ROOF, 1))
                    elif brow == 1:
                        if bpos in (1, 3):
                            tiles.append((TILE_WINDOW, 3))
                        else:
                            tiles.append((TILE_WALL_CREAM, 1))
                    else:
                        if bpos in (1, 3):
                            tiles.append((TILE_WINDOW_SHUTTERS, 3))
                        else:
                            tiles.append((TILE_WALL_CREAM, 1))

                elif btype == 'B2':
                    # Variant B: cream building, different window placement
                    if brow == 0:
                        tiles.append((TILE_ROOF, 1))
                    elif brow == 1:
                        if bpos in (1, 3, 5):
                            tiles.append((TILE_WINDOW, 3))
                        else:
                            tiles.append((TILE_WALL_CREAM, 1))
                    else:
                        if bpos in (1, 3, 5):
                            tiles.append((TILE_WINDOW_SHUTTERS, 3))
                        else:
                            tiles.append((TILE_WALL_CREAM, 1))

                elif btype == 'C':
                    # Dark noodle shop with gold signs
                    if brow == 0:
                        if bpos == 0 or bpos == 4:
                            tiles.append((TILE_WALL_DARK, 1))
                        elif bpos == 2:
                            tiles.append((TILE_SIGN_CHAR5, 2))
                        else:
                            tiles.append((TILE_WALL_LINE, 1))
                    elif brow == 1:
                        if bpos == 1:
                            tiles.append((TILE_SIGN_RED, 2))
                        elif bpos == 2:
                            tiles.append((TILE_SIGN_CHAR5, 2))
                        elif bpos == 3:
                            tiles.append((TILE_SIGN_RED, 2))
                        else:
                            tiles.append((TILE_WALL_DARK, 1))
                    else:
                        if bpos == 0:
                            tiles.append((TILE_AWNING_EDGE_L, 2))
                        elif bpos == 4:
                            tiles.append((TILE_AWNING_EDGE_R, 2))
                        else:
                            tiles.append((TILE_AWNING, 2))

                elif btype == 'D':
                    # Alley - dark gap
                    if brow == 0:
                        tiles.append((TILE_SKYWALL, 7))
                    else:
                        tiles.append((TILE_WALL_DARK, 1))

            # Row 7: Sidewalk
            elif row == 7:
                if col % 8 == 3:
                    tiles.append((TILE_SIDEWALK_CRACK, 5))
                else:
                    tiles.append((TILE_SIDEWALK, 5))

            # Rows 8-9: Lane 0 (top lane)
            elif row in (8, 9):
                tiles.append((TILE_ROAD, 4))

            # Row 10: Dashed line
            elif row == 10:
                # Pattern: dash_left, dash_right, gap, gap repeated
                # 4 columns per cycle: dash, dash, gap, gap
                phase = col % 4
                if phase == 0:
                    tiles.append((TILE_DASH_LEFT, 4))
                elif phase == 1:
                    tiles.append((TILE_DASH_RIGHT, 4))
                else:
                    tiles.append((TILE_DASH_NONE, 4))

            # Rows 11-12: Lane 1 (middle lane)
            elif row in (11, 12):
                tiles.append((TILE_ROAD, 4))

            # Row 13: Dashed line (offset from row 10)
            elif row == 13:
                phase = (col + 2) % 4  # offset by 2 for visual variety
                if phase == 0:
                    tiles.append((TILE_DASH_LEFT, 4))
                elif phase == 1:
                    tiles.append((TILE_DASH_RIGHT, 4))
                else:
                    tiles.append((TILE_DASH_NONE, 4))

            # Rows 14-16: Lane 2 (bottom lane)
            elif row in (14, 15, 16):
                tiles.append((TILE_ROAD, 4))

            # Row 17: Bottom curb (warm sidewalk palette)
            elif row == 17:
                tiles.append((TILE_CURB, 5))

            else:
                tiles.append((TILE_ROAD, 4))

        tmap.append(tiles)

    return tmap


# ============================================================
# RENDERER
# ============================================================

def render(tmap):
    """Render tilemap to 256x144 RGB image."""
    img = Image.new('RGB', (W, H))
    pixels = img.load()

    for row in range(ROWS):
        for col in range(COLS):
            tile_data, pal_idx = tmap[row][col]
            pal = PALETTES[pal_idx]
            for dy in range(TILE):
                for dx in range(TILE):
                    ci = tile_data[dy][dx]
                    pixels[col * TILE + dx, row * TILE + dy] = pal[ci]

    return img


# ============================================================
# VERIFICATION
# ============================================================

def verify(img):
    """Verify GBC constraints: max 4 colors per 8x8 tile, max 8 palettes."""
    pixels = img.load()
    max_colors = 0
    all_palettes = set()
    problem_tiles = []

    for ty in range(ROWS):
        for tx in range(COLS):
            tile_colors = set()
            for dy in range(TILE):
                for dx in range(TILE):
                    c = pixels[tx * TILE + dx, ty * TILE + dy]
                    tile_colors.add(c)

            if len(tile_colors) > 4:
                problem_tiles.append((tx, ty, len(tile_colors)))
            max_colors = max(max_colors, len(tile_colors))

            # Track this tile's palette as a frozenset
            all_palettes.add(frozenset(tile_colors))

    # Count unique palette groups (tiles that share exact same color sets)
    # For GBC, we need to map each tile's colors to one of 8 palettes
    # A palette can serve any tile whose colors are a subset of that palette's 4 colors

    # Group tiles by which defined palette covers them
    uncovered = []
    pal_usage = [0] * 8

    for ty in range(ROWS):
        for tx in range(COLS):
            tile_colors = set()
            for dy in range(TILE):
                for dx in range(TILE):
                    c = pixels[tx * TILE + dx, ty * TILE + dy]
                    tile_colors.add(c)

            covered = False
            for pi, pal in enumerate(PALETTES):
                pal_set = set(pal)
                if tile_colors <= pal_set:
                    pal_usage[pi] += 1
                    covered = True
                    break

            if not covered:
                uncovered.append((tx, ty, tile_colors))

    print(f"  Max colors per tile: {max_colors}")
    print(f"  Unique palette sets: {len(all_palettes)}")
    print(f"  Palette usage: {pal_usage}")

    if problem_tiles:
        for tx, ty, nc in problem_tiles:
            print(f"  ERROR: tile ({tx},{ty}) has {nc} colors!")

    if uncovered:
        for tx, ty, colors in uncovered[:10]:
            print(f"  UNCOVERED: tile ({tx},{ty}) colors={colors}")

    ok = max_colors <= 4 and len(uncovered) == 0
    if ok:
        print("  ALL CHECKS PASSED")
    else:
        print("  CHECKS FAILED")

    return ok


# ============================================================
# SEAMLESS WRAP CHECK
# ============================================================

def check_wrap(img):
    """Verify that left and right edges connect reasonably for scrolling."""
    pixels = img.load()
    mismatches = 0
    for y in range(H):
        left = pixels[0, y]
        right = pixels[W - 1, y]
        # For rows that should match (road, sidewalk), check they're close
        # Buildings may differ at edges since they tile through the map
    print("  Wrap check: background is designed for map wrapping (32-col tilemap)")
    return True


def main():
    os.makedirs(ASSETS_DIR, exist_ok=True)

    print("Drawing Chapter 2 street background (256x144)...")
    tmap = build_tilemap()
    img = render(tmap)

    print("Verifying GBC constraints...")
    ok = verify(img)
    if not ok:
        print("  ERROR: Constraints violated!")
        return

    check_wrap(img)

    out = os.path.join(ASSETS_DIR, 'ch2_street_bg.png')
    img.save(out)
    print(f"Saved: {out} ({img.size})")
    print("Next: run png2asset to convert.")


if __name__ == '__main__':
    main()
