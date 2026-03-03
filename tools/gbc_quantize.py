#!/usr/bin/env /opt/homebrew/bin/python3
"""
GBC Image Quantizer — converts an image to Game Boy Color constraints.

Input:  any image (JPG, PNG, etc.)
Output: 160x144 indexed PNG with max 4 colors per 8x8 tile, max 8 palettes.

Usage: python3 tools/gbc_quantize.py input.jpg output.png [--max-palettes 8]
"""

import sys
import math
from collections import Counter
from PIL import Image

MAX_PALETTES = 8
COLORS_PER_PAL = 4
TILE_W, TILE_H = 8, 8
SCREEN_W, SCREEN_H = 160, 144
TILES_X = SCREEN_W // TILE_W   # 20
TILES_Y = SCREEN_H // TILE_H   # 18

def rgb15(r, g, b):
    """Snap RGB to GBC 5-bit per channel (32 levels)."""
    return ((r >> 3) << 3, (g >> 3) << 3, (b >> 3) << 3)

def color_distance(c1, c2):
    """Weighted Euclidean distance (human perception)."""
    dr = c1[0] - c2[0]
    dg = c1[1] - c2[1]
    db = c1[2] - c2[2]
    return 2*dr*dr + 4*dg*dg + 3*db*db

def best_4_colors(pixels):
    """Pick the best 4 representative colors from a list of pixels using median cut."""
    if len(set(pixels)) <= 4:
        return list(set(pixels))

    def median_cut(box, depth):
        if depth == 0 or len(box) <= 1:
            # Average the box
            r = sum(p[0] for p in box) // len(box)
            g = sum(p[1] for p in box) // len(box)
            b = sum(p[2] for p in box) // len(box)
            return [rgb15(r, g, b)]

        # Find channel with greatest range
        ranges = []
        for ch in range(3):
            vals = [p[ch] for p in box]
            ranges.append(max(vals) - min(vals))
        split_ch = ranges.index(max(ranges))

        box.sort(key=lambda p: p[split_ch])
        mid = len(box) // 2
        return median_cut(box[:mid], depth-1) + median_cut(box[mid:], depth-1)

    result = median_cut(list(pixels), 2)  # 2 splits = 4 buckets
    # Deduplicate
    seen = set()
    unique = []
    for c in result:
        if c not in seen:
            seen.add(c)
            unique.append(c)
    return unique[:4]

def nearest_color(pixel, palette):
    """Find the closest palette color to a pixel."""
    best = palette[0]
    best_d = color_distance(pixel, best)
    for c in palette[1:]:
        d = color_distance(pixel, c)
        if d < best_d:
            best_d = d
            best = c
    return best

def palette_error(tile_pixels, palette):
    """Total quantization error for a tile with a given palette."""
    error = 0
    for p in tile_pixels:
        best_d = min(color_distance(p, c) for c in palette)
        error += best_d
    return error

def merge_palettes(palettes, max_palettes):
    """Merge closest palettes until we have <= max_palettes."""
    while len(palettes) > max_palettes:
        # Find the two most similar palettes
        best_i, best_j = 0, 1
        best_dist = float('inf')
        for i in range(len(palettes)):
            for j in range(i+1, len(palettes)):
                # Distance = sum of min distances between all colors
                d = 0
                for c1 in palettes[i]:
                    d += min(color_distance(c1, c2) for c2 in palettes[j])
                for c2 in palettes[j]:
                    d += min(color_distance(c2, c1) for c1 in palettes[i])
                if d < best_dist:
                    best_dist = d
                    best_i, best_j = i, j

        # Merge: combine all colors, re-pick best 4
        combined = list(palettes[best_i]) + list(palettes[best_j])
        merged = best_4_colors(combined)
        palettes[best_i] = tuple(merged)
        palettes.pop(best_j)

    return palettes

def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} input.jpg output.png [--max-palettes N]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    max_pals = MAX_PALETTES
    if '--max-palettes' in sys.argv:
        idx = sys.argv.index('--max-palettes')
        max_pals = int(sys.argv[idx + 1])

    print(f"Loading {input_path}...")
    img = Image.open(input_path).convert('RGB')

    # Resize to 160x144
    img = img.resize((SCREEN_W, SCREEN_H), Image.LANCZOS)

    # Snap all pixels to GBC 5-bit color space
    pixels = img.load()
    for y in range(SCREEN_H):
        for x in range(SCREEN_W):
            r, g, b = pixels[x, y]
            pixels[x, y] = rgb15(r, g, b)

    print("Extracting tile palettes...")
    # Step 1: For each 8x8 tile, find its best 4-color palette
    tile_palettes = []
    tile_pixels = []
    for ty in range(TILES_Y):
        for tx in range(TILES_X):
            tile_pxs = []
            for dy in range(TILE_H):
                for dx in range(TILE_W):
                    tile_pxs.append(pixels[tx*TILE_W + dx, ty*TILE_H + dy])
            tile_pixels.append(tile_pxs)
            pal = best_4_colors(tile_pxs)
            # Pad to exactly 4 if fewer
            while len(pal) < 4:
                pal.append(pal[-1])
            tile_palettes.append(tuple(pal))

    print(f"Found {len(set(tile_palettes))} unique tile palettes, merging to {max_pals}...")

    # Step 2: Cluster tile palettes down to max_pals
    unique_pals = list(set(tile_palettes))
    if len(unique_pals) > max_pals:
        unique_pals = merge_palettes(unique_pals, max_pals)

    # Pad each palette to 4 colors
    final_palettes = []
    for pal in unique_pals:
        p = list(pal)
        while len(p) < 4:
            p.append(p[-1])
        final_palettes.append(tuple(p[:4]))

    print(f"Final palettes: {len(final_palettes)}")
    for i, pal in enumerate(final_palettes):
        print(f"  Pal {i}: {pal}")

    # Step 3: Assign each tile to its best palette
    tile_pal_idx = []
    for i in range(len(tile_pixels)):
        best_p = 0
        best_err = palette_error(tile_pixels[i], final_palettes[0])
        for p in range(1, len(final_palettes)):
            err = palette_error(tile_pixels[i], final_palettes[p])
            if err < best_err:
                best_err = err
                best_p = p
        tile_pal_idx.append(best_p)

    # Step 4: Remap all pixels to their tile's assigned palette
    print("Remapping pixels...")
    for ty in range(TILES_Y):
        for tx in range(TILES_X):
            tidx = ty * TILES_X + tx
            pal = final_palettes[tile_pal_idx[tidx]]
            for dy in range(TILE_H):
                for dx in range(TILE_W):
                    x = tx * TILE_W + dx
                    y = ty * TILE_H + dy
                    pixels[x, y] = nearest_color(pixels[x, y], pal)

    # Build a global palette (all colors from all palettes, ordered)
    global_palette = []
    for pal in final_palettes:
        for c in pal:
            if c not in global_palette:
                global_palette.append(c)

    # Verify: count colors per tile
    max_tile_colors = 0
    for ty in range(TILES_Y):
        for tx in range(TILES_X):
            colors = set()
            for dy in range(TILE_H):
                for dx in range(TILE_W):
                    colors.add(pixels[tx*TILE_W + dx, ty*TILE_H + dy])
            max_tile_colors = max(max_tile_colors, len(colors))
    print(f"Max colors in any tile: {max_tile_colors}")
    print(f"Total unique colors: {len(global_palette)}")

    # Save as indexed PNG
    # Create palette image
    pal_img = Image.new('P', (SCREEN_W, SCREEN_H))
    # Build flat palette (R,G,B,R,G,B,...)
    flat_pal = []
    for c in global_palette:
        flat_pal.extend(c)
    # Pad to 256 entries
    while len(flat_pal) < 768:
        flat_pal.extend([0, 0, 0])
    pal_img.putpalette(flat_pal)

    # Map pixels to palette indices
    color_to_idx = {c: i for i, c in enumerate(global_palette)}
    pal_pixels = pal_img.load()
    for y in range(SCREEN_H):
        for x in range(SCREEN_W):
            pal_pixels[x, y] = color_to_idx[pixels[x, y]]

    pal_img.save(output_path)
    print(f"Saved to {output_path}")

if __name__ == '__main__':
    main()
