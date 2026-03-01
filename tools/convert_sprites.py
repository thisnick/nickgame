#!/usr/bin/env python3
"""
Convert generated sprite images to NES CHR tile data.

Loads PNG sprites, downscales to NES tile sizes (8x8, 16x16, 32x32),
quantizes to 4 colors per sprite, and outputs CHR data.

Tile layout (sprite pattern table at $1000):
  $00-$03: Bike rider 2x2 metasprite (TL,TR,BL,BR)
  $04: Pothole 8x8
  $05: Baozi 8x8
  $06-$09: Dog 2x2 (32x16 → 2 cols x 2 rows... 16x16 mapped as 2x2)
  $0A-$0D: Vendor cart 2x2
  $0E: Crash star (keep existing)
  $0F-$12: Bus 2x2 metasprite (new)
  $13-$16: Barrier 2x1 metasprite (32x16 → 2x2 tiles, only top 2 matter)
  $17-$1A: School gate 2x2
"""

import sys
import os
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Installing Pillow...")
    os.system("uv pip install pillow 2>/dev/null || pip install pillow")
    from PIL import Image

import numpy as np

SPRITES_DIR = Path(__file__).parent.parent / "sprites"
CHR_DIR = Path(__file__).parent.parent / "chr"
TOOLS_DIR = Path(__file__).parent

# NES palette - map colors to 4 shades (0-3)
def quantize_to_4(img, size):
    """
    Resize img to `size` (w,h), then quantize to 4 colors.
    Returns a 2D array of color indices 0-3.
    Also returns (w, h) of output.
    """
    w, h = size
    img = img.convert("RGBA")
    img = img.resize((w, h), Image.NEAREST)
    
    # Get pixel data
    pixels = np.array(img)  # (h, w, 4)
    rgba = pixels.reshape(-1, 4)
    
    # Identify transparent pixels (alpha < 128) → color 0
    alpha_mask = rgba[:, 3] < 128
    
    # Convert to grayscale for quantization
    rgb = rgba[:, :3].astype(float)
    gray = 0.299 * rgb[:, 0] + 0.587 * rgb[:, 1] + 0.114 * rgb[:, 2]
    
    # Separate opaque pixels for quantization
    opaque_gray = gray[~alpha_mask]
    
    if len(opaque_gray) == 0:
        return np.zeros((h, w), dtype=np.uint8), (w, h)
    
    # Find 3 quantization boundaries (for colors 1, 2, 3)
    # Use percentiles to define 3 color bands among opaque pixels
    p33 = np.percentile(opaque_gray, 33)
    p66 = np.percentile(opaque_gray, 66)
    
    # Assign color indices
    indices = np.zeros(len(rgba), dtype=np.uint8)
    
    for i, (g, is_transparent) in enumerate(zip(gray, alpha_mask)):
        if is_transparent:
            indices[i] = 0  # transparent = color 0
        elif g <= p33:
            indices[i] = 1  # darkest opaque = color 1
        elif g <= p66:
            indices[i] = 2  # medium = color 2
        else:
            indices[i] = 3  # lightest = color 3
    
    return indices.reshape(h, w), (w, h)


def make_tile_from_array(color_2d, row_start, col_start):
    """
    Extract an 8x8 tile from a 2D color index array.
    Returns 16 bytes (plane0 then plane1) in NES CHR format.
    """
    plane0 = []
    plane1 = []
    for row in range(8):
        p0 = 0
        p1 = 0
        for col in range(8):
            r = row_start + row
            c = col_start + col
            if r < color_2d.shape[0] and c < color_2d.shape[1]:
                idx = color_2d[r, c]
            else:
                idx = 0
            bit = 7 - col
            if idx & 1:
                p0 |= (1 << bit)
            if idx & 2:
                p1 |= (1 << bit)
        plane0.append(p0)
        plane1.append(p1)
    return bytes(plane0 + plane1)


def load_sprite_tiles(filename, target_w, target_h, tiles_x, tiles_y):
    """
    Load a sprite, resize to target dimensions, quantize to 4 colors,
    and return a list of 16-byte CHR tiles in row-major order (TL→TR→BL→BR).
    """
    path = SPRITES_DIR / filename
    if not path.exists():
        print(f"  WARNING: {filename} not found, using blank tiles")
        return [bytes(16)] * (tiles_x * tiles_y)
    
    img = Image.open(path)
    colors, (w, h) = quantize_to_4(img, (target_w, target_h))
    
    tiles = []
    for ty in range(tiles_y):
        for tx in range(tiles_x):
            tile = make_tile_from_array(colors, ty * 8, tx * 8)
            tiles.append(tile)
    
    return tiles


def make_blank_tile():
    return bytes(16)


def make_crash_star():
    """Keep the existing crash star tile."""
    def make_tile(art):
        plane0 = []
        plane1 = []
        for row in art[:8]:
            row = row.ljust(8)[:8]
            p0 = 0
            p1 = 0
            for col in range(8):
                ch = row[col]
                bit = 7 - col
                if ch in ('1', '3'):
                    p0 |= (1 << bit)
                if ch in ('2', '3'):
                    p1 |= (1 << bit)
            plane0.append(p0)
            plane1.append(p1)
        return bytes(plane0 + plane1)
    
    return make_tile([
        '3  3  3 ',
        ' 3 3 3  ',
        '  333   ',
        '333333  ',
        '  333   ',
        ' 3 3 3  ',
        '3  3  3 ',
        '        ',
    ])


def build_sprite_chr():
    """
    Build the sprite pattern table (4KB at $1000 offset).
    Returns 4096 bytes.
    """
    sprite_chr = bytearray(4096)
    
    def set_sprite_tile(index, data):
        offset = index * 16
        sprite_chr[offset:offset+16] = data
    
    def set_sprite_tiles(start_index, tiles):
        for i, tile in enumerate(tiles):
            set_sprite_tile(start_index + i, tile)
    
    print("Loading bike rider (32x32 → 4 tiles)...")
    bike_tiles = load_sprite_tiles("bike_rider.png", 32, 32, 4, 4)
    # Use top 2x2 tiles for compact representation (tiles 0-3 = row0col0, row0col1, row1col0, row1col1)
    # Actually we want TL=0, TR=1, BL=2, BR=3 in NES layout
    # from 4x4 tiles, use the top-left 2x2 block
    tl = bike_tiles[0]   # row0, col0
    tr = bike_tiles[1]   # row0, col1
    bl = bike_tiles[4]   # row1, col0
    br = bike_tiles[5]   # row1, col1
    set_sprite_tile(0x00, tl)
    set_sprite_tile(0x01, tr)
    set_sprite_tile(0x02, bl)
    set_sprite_tile(0x03, br)
    
    print("Loading pothole (16x16 → 1 tile)...")
    pothole_tiles = load_sprite_tiles("pothole.png", 8, 8, 1, 1)
    set_sprite_tile(0x04, pothole_tiles[0])
    
    print("Loading baozi (16x16 → 1 tile)...")
    baozi_tiles = load_sprite_tiles("baozi.png", 8, 8, 1, 1)
    set_sprite_tile(0x05, baozi_tiles[0])
    
    print("Loading dog (32x16 → 2x2 tiles)...")
    # Dog is 32x16, which is 4 tiles wide, 2 tiles tall
    dog_tiles = load_sprite_tiles("dog.png", 32, 16, 4, 2)
    # Use left 2 cols: TL=dog[0], TR=dog[1], BL=dog[4], BR=dog[5]
    set_sprite_tile(0x06, dog_tiles[0])
    set_sprite_tile(0x07, dog_tiles[1])
    set_sprite_tile(0x08, dog_tiles[4])
    set_sprite_tile(0x09, dog_tiles[5])
    
    print("Loading vendor cart (32x32 → 2x2 tiles)...")
    vendor_tiles = load_sprite_tiles("vendor_cart.png", 32, 32, 4, 4)
    set_sprite_tile(0x0A, vendor_tiles[0])
    set_sprite_tile(0x0B, vendor_tiles[1])
    set_sprite_tile(0x0C, vendor_tiles[4])
    set_sprite_tile(0x0D, vendor_tiles[5])
    
    print("Keeping crash star tile at $0E...")
    set_sprite_tile(0x0E, make_crash_star())
    
    print("Loading school gate (32x32 → 2x2 tiles)...")
    gate_tiles = load_sprite_tiles("school_gate.png", 32, 32, 4, 4)
    set_sprite_tile(0x0F, gate_tiles[0])
    set_sprite_tile(0x10, gate_tiles[1])
    set_sprite_tile(0x11, gate_tiles[4])
    set_sprite_tile(0x12, gate_tiles[5])
    
    print("Loading bus (32x32 → 2x2 tiles)...")
    bus_tiles = load_sprite_tiles("bus.png", 32, 32, 4, 4)
    set_sprite_tile(0x13, bus_tiles[0])
    set_sprite_tile(0x14, bus_tiles[1])
    set_sprite_tile(0x15, bus_tiles[4])
    set_sprite_tile(0x16, bus_tiles[5])
    
    print("Loading barrier (32x16 → 2x2 tiles)...")
    barrier_tiles = load_sprite_tiles("barrier.png", 32, 16, 4, 2)
    set_sprite_tile(0x17, barrier_tiles[0])
    set_sprite_tile(0x18, barrier_tiles[1])
    set_sprite_tile(0x19, barrier_tiles[4])
    set_sprite_tile(0x1A, barrier_tiles[5])
    
    return bytes(sprite_chr)


def build_bg_chr():
    """
    Import the background CHR from the existing make_chr.py logic.
    Returns 4096 bytes.
    """
    # Run make_chr.py to regenerate the CHR, then extract the BG portion
    import subprocess
    import tempfile
    import shutil
    
    tools_dir = Path(__file__).parent
    original_chr = CHR_DIR / "tiles.chr"
    
    # Run original make_chr.py to get a fresh BG table
    result = subprocess.run(
        ["python3", str(tools_dir / "make_chr.py")],
        capture_output=True,
        cwd=str(tools_dir.parent)
    )
    
    if result.returncode != 0:
        print(f"  WARNING: make_chr.py failed: {result.stderr.decode()}")
        # Return blank
        return bytes(4096)
    
    # Read the generated CHR and extract BG portion (first 4KB)
    with open(original_chr, "rb") as f:
        data = f.read()
    
    return data[:4096]


def main():
    print("=== NES Sprite Converter ===")
    print(f"Sprites dir: {SPRITES_DIR}")
    print(f"CHR dir: {CHR_DIR}")
    print()
    
    # Build BG CHR (first 4KB) from existing make_chr.py
    print("Building background CHR from make_chr.py...")
    bg_chr = build_bg_chr()
    print(f"  BG CHR: {len(bg_chr)} bytes")
    
    # Build sprite CHR (second 4KB) from image sprites
    print()
    print("Building sprite CHR from images...")
    sprite_chr = build_sprite_chr()
    print(f"  Sprite CHR: {len(sprite_chr)} bytes")
    
    # Combine into 8KB CHR ROM
    full_chr = bg_chr + sprite_chr
    assert len(full_chr) == 8192, f"Expected 8192 bytes, got {len(full_chr)}"
    
    # Write to file
    output_path = CHR_DIR / "tiles.chr"
    with open(output_path, "wb") as f:
        f.write(full_chr)
    
    print()
    print(f"✓ Written {len(full_chr)} bytes to {output_path}")
    print()
    print("Sprite tile map:")
    print("  $00-$03: Bike rider (2x2)")
    print("  $04:     Pothole")
    print("  $05:     Baozi")
    print("  $06-$09: Dog (2x2)")
    print("  $0A-$0D: Vendor cart (2x2)")
    print("  $0E:     Crash star")
    print("  $0F-$12: School gate (2x2)")
    print("  $13-$16: Bus (2x2)")
    print("  $17-$1A: Barrier (2x2)")


if __name__ == "__main__":
    main()
