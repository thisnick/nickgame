#!/usr/bin/env python3
"""
Convert a full-color 160x144 PNG into a Game Boy Color compatible image.

GBC constraints:
- 160x144 pixels (20x18 tiles of 8x8)
- Each 8x8 tile uses at most 4 colors
- Up to 8 palettes of 4 colors each (max 32 distinct colors)
- Uses LAB perceptual color distance for best quality
"""

import sys
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
from collections import Counter
import itertools

SRC = "/Users/nick/code/nickgame/reference/title/title-scaled.png"
DST = "/Users/nick/code/nickgame/assets/title_screen.png"

TILE_W, TILE_H = 8, 8
TILES_X, TILES_Y = 20, 18  # 160/8, 144/8
MAX_PALETTES = 8
COLORS_PER_PALETTE = 4


# --- Color space conversion (sRGB <-> LAB) ---

def srgb_to_linear(c):
    """Convert sRGB [0,255] to linear RGB [0,1]."""
    c = c / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)

def linear_to_srgb(c):
    """Convert linear RGB [0,1] to sRGB [0,255]."""
    c = np.clip(c, 0, 1)
    out = np.where(c <= 0.0031308, c * 12.92, 1.055 * (c ** (1.0/2.4)) - 0.055)
    return np.clip(np.round(out * 255), 0, 255).astype(np.uint8)

def rgb_to_lab(rgb):
    """Convert RGB array (N,3) uint8 to CIELAB (N,3) float."""
    linear = srgb_to_linear(rgb.astype(np.float64))
    # RGB to XYZ (D65)
    M = np.array([
        [0.4124564, 0.3575761, 0.1804375],
        [0.2126729, 0.7151522, 0.0721750],
        [0.0193339, 0.1191920, 0.9503041],
    ])
    xyz = linear @ M.T
    # Normalize by D65 white point
    xyz[:, 0] /= 0.95047
    xyz[:, 1] /= 1.00000
    xyz[:, 2] /= 1.08883
    # XYZ to LAB
    epsilon = 0.008856
    kappa = 903.3
    f = np.where(xyz > epsilon, xyz ** (1.0/3.0), (kappa * xyz + 16.0) / 116.0)
    L = 116.0 * f[:, 1] - 16.0
    a = 500.0 * (f[:, 0] - f[:, 1])
    b = 200.0 * (f[:, 1] - f[:, 2])
    return np.column_stack([L, a, b])


def color_distance_lab(c1_lab, c2_lab):
    """Euclidean distance in LAB space (perceptual)."""
    return np.sqrt(np.sum((c1_lab - c2_lab) ** 2, axis=-1))


def find_nearest_color(pixel_lab, palette_lab):
    """Find index of nearest palette color for each pixel (in LAB)."""
    # pixel_lab: (N, 3), palette_lab: (K, 3)
    dists = np.sqrt(np.sum((pixel_lab[:, np.newaxis, :] - palette_lab[np.newaxis, :, :]) ** 2, axis=2))
    return np.argmin(dists, axis=1)


def extract_tiles(img_array):
    """Extract all 8x8 tiles from image. Returns list of (ty, tx, tile_pixels)."""
    tiles = []
    for ty in range(TILES_Y):
        for tx in range(TILES_X):
            y0, x0 = ty * TILE_H, tx * TILE_W
            tile = img_array[y0:y0+TILE_H, x0:x0+TILE_W].copy()
            tiles.append((ty, tx, tile))
    return tiles


def get_tile_colors(tile):
    """Get unique colors in a tile as set of tuples."""
    pixels = tile.reshape(-1, 3)
    return set(map(tuple, pixels))


def prequantize_tiles(img_array, max_colors=4):
    """
    Pre-quantize each 8x8 tile to at most max_colors using k-means in LAB space.
    Returns the modified image array.
    """
    result = img_array.copy()
    for ty in range(TILES_Y):
        for tx in range(TILES_X):
            y0, x0 = ty * TILE_H, tx * TILE_W
            tile = result[y0:y0+TILE_H, x0:x0+TILE_W]
            pixels = tile.reshape(-1, 3)
            unique_colors = np.unique(pixels, axis=0)

            if len(unique_colors) <= max_colors:
                continue  # Already within limit

            # Convert to LAB for perceptual clustering
            pixels_lab = rgb_to_lab(pixels)
            unique_lab = rgb_to_lab(unique_colors)

            # K-means in LAB space
            km = KMeans(n_clusters=max_colors, n_init=10, random_state=42)
            km.fit(pixels_lab)
            labels = km.labels_

            # For each cluster, find the nearest original color to the centroid
            # (to avoid introducing colors that weren't in the image)
            centroids_lab = km.cluster_centers_
            new_pixels = np.zeros_like(pixels)
            for ci in range(max_colors):
                mask = labels == ci
                if not np.any(mask):
                    continue
                cluster_pixels = pixels[mask]
                cluster_unique = np.unique(cluster_pixels, axis=0)
                cluster_unique_lab = rgb_to_lab(cluster_unique)
                # Find original color nearest to centroid
                dists = np.sqrt(np.sum((cluster_unique_lab - centroids_lab[ci:ci+1]) ** 2, axis=1))
                best_idx = np.argmin(dists)
                new_pixels[mask] = cluster_unique[best_idx]

            result[y0:y0+TILE_H, x0:x0+TILE_W] = new_pixels.reshape(TILE_H, TILE_W, 3)

    return result


def build_palettes(img_array, n_palettes=MAX_PALETTES):
    """
    Build optimal palettes by clustering tiles based on their color needs.
    Returns list of palettes, each a list of RGB tuples.
    """
    tiles = extract_tiles(img_array)

    # Collect color sets per tile
    tile_color_sets = []
    for ty, tx, tile in tiles:
        colors = get_tile_colors(tile)
        tile_color_sets.append(colors)

    # Collect all unique colors across the image
    all_colors = set()
    for cs in tile_color_sets:
        all_colors.update(cs)
    all_colors = sorted(all_colors)
    color_to_idx = {c: i for i, c in enumerate(all_colors)}
    n_colors = len(all_colors)

    print(f"After pre-quantization: {n_colors} unique colors across all tiles")

    # Build feature vector per tile: binary vector of which colors it uses
    n_tiles = len(tiles)
    features = np.zeros((n_tiles, n_colors), dtype=np.float32)
    for i, cs in enumerate(tile_color_sets):
        for c in cs:
            features[i, color_to_idx[c]] = 1.0

    # If we have few enough unique color sets, no need for clustering
    unique_sets = list(set(frozenset(cs) for cs in tile_color_sets))
    print(f"Unique tile color sets: {len(unique_sets)}")

    if len(unique_sets) <= n_palettes:
        # Each unique color set becomes a palette (pad to 4 colors)
        palettes = []
        for cs in unique_sets:
            pal = list(cs)
            while len(pal) < COLORS_PER_PALETTE:
                pal.append(pal[0])  # Pad with first color
            palettes.append(pal[:COLORS_PER_PALETTE])
        return palettes

    # Cluster tiles into n_palettes groups using k-means on color feature vectors
    # Weight by LAB similarity
    all_colors_arr = np.array(all_colors, dtype=np.uint8)
    all_colors_lab = rgb_to_lab(all_colors_arr)

    # Use color presence features weighted by perceptual importance
    km = KMeans(n_clusters=n_palettes, n_init=20, random_state=42)
    km.fit(features)
    tile_labels = km.labels_

    # For each cluster of tiles, collect all colors used, then pick the best 4
    palettes = []
    for ci in range(n_palettes):
        cluster_mask = tile_labels == ci
        cluster_tiles_idx = np.where(cluster_mask)[0]

        if len(cluster_tiles_idx) == 0:
            palettes.append([(255, 255, 255)] * COLORS_PER_PALETTE)
            continue

        # Collect all colors used by tiles in this cluster, with frequency
        color_freq = Counter()
        for ti in cluster_tiles_idx:
            for c in tile_color_sets[ti]:
                color_freq[c] += 1

        cluster_colors = list(color_freq.keys())

        if len(cluster_colors) <= COLORS_PER_PALETTE:
            pal = cluster_colors[:]
            while len(pal) < COLORS_PER_PALETTE:
                pal.append(pal[0])
            palettes.append(pal)
            continue

        # Need to reduce to 4 colors using k-means in LAB space, weighted by frequency
        cc_arr = np.array(cluster_colors, dtype=np.uint8)
        cc_lab = rgb_to_lab(cc_arr)

        # Weight by sqrt of frequency for balanced clustering
        weights = np.array([color_freq[c] for c in cluster_colors], dtype=np.float64)
        weights = np.sqrt(weights)

        # Expand samples by weight for weighted k-means
        expanded_lab = np.repeat(cc_lab, np.maximum(1, (weights * 3).astype(int)), axis=0)
        expanded_rgb = np.repeat(cc_arr, np.maximum(1, (weights * 3).astype(int)), axis=0)

        n_cl = min(COLORS_PER_PALETTE, len(cc_arr))
        km2 = KMeans(n_clusters=n_cl, n_init=10, random_state=42)
        km2.fit(expanded_lab)

        # For each centroid, find the nearest actual color
        pal = []
        for centroid in km2.cluster_centers_:
            dists = np.sqrt(np.sum((cc_lab - centroid[np.newaxis, :]) ** 2, axis=1))
            best = np.argmin(dists)
            pal.append(cluster_colors[best])

        while len(pal) < COLORS_PER_PALETTE:
            pal.append(pal[0])
        palettes.append(pal)

    return palettes


def assign_tiles_to_palettes(img_array, palettes):
    """
    For each tile, find the palette that minimizes total color error.
    Returns tile_palette_map: (ty, tx) -> palette_index
    """
    # Precompute LAB for each palette
    palettes_lab = []
    for pal in palettes:
        pal_arr = np.array(pal, dtype=np.uint8)
        palettes_lab.append(rgb_to_lab(pal_arr))

    tiles = extract_tiles(img_array)
    tile_palette_map = {}

    for ty, tx, tile in tiles:
        pixels = tile.reshape(-1, 3)
        pixels_lab = rgb_to_lab(pixels)

        best_pal = 0
        best_error = float('inf')

        for pi, pal_lab in enumerate(palettes_lab):
            # For each pixel, find nearest palette color
            indices = find_nearest_color(pixels_lab, pal_lab)
            mapped_lab = pal_lab[indices]
            error = np.sum((pixels_lab - mapped_lab) ** 2)

            if error < best_error:
                best_error = error
                best_pal = pi

        tile_palette_map[(ty, tx)] = best_pal

    return tile_palette_map


def remap_image(img_array, palettes, tile_palette_map):
    """Remap all pixels to their assigned palette colors."""
    result = img_array.copy()

    palettes_lab = []
    palettes_rgb = []
    for pal in palettes:
        pal_arr = np.array(pal, dtype=np.uint8)
        palettes_lab.append(rgb_to_lab(pal_arr))
        palettes_rgb.append(pal_arr)

    for ty in range(TILES_Y):
        for tx in range(TILES_X):
            y0, x0 = ty * TILE_H, tx * TILE_W
            tile = result[y0:y0+TILE_H, x0:x0+TILE_W]
            pixels = tile.reshape(-1, 3)

            pi = tile_palette_map[(ty, tx)]
            pal_lab = palettes_lab[pi]
            pal_rgb = palettes_rgb[pi]

            pixels_lab = rgb_to_lab(pixels)
            indices = find_nearest_color(pixels_lab, pal_lab)
            new_pixels = pal_rgb[indices]

            result[y0:y0+TILE_H, x0:x0+TILE_W] = new_pixels.reshape(TILE_H, TILE_W, 3)

    return result


def verify_output(img_array, palettes):
    """Verify GBC constraints are met."""
    h, w = img_array.shape[:2]
    print(f"\n=== Verification ===")
    print(f"Dimensions: {w}x{h} {'OK' if w == 160 and h == 144 else 'FAIL'}")

    all_colors = set()
    max_tile_colors = 0
    tiles_over_4 = 0

    for ty in range(TILES_Y):
        for tx in range(TILES_X):
            y0, x0 = ty * TILE_H, tx * TILE_W
            tile = img_array[y0:y0+TILE_H, x0:x0+TILE_W]
            colors = get_tile_colors(tile)
            all_colors.update(colors)
            nc = len(colors)
            if nc > max_tile_colors:
                max_tile_colors = nc
            if nc > 4:
                tiles_over_4 += 1
                print(f"  FAIL: Tile ({tx},{ty}) has {nc} colors")

    print(f"Total unique colors: {len(all_colors)}")
    print(f"Max colors per tile: {max_tile_colors} {'OK' if max_tile_colors <= 4 else 'FAIL'}")
    print(f"Tiles exceeding 4 colors: {tiles_over_4}")

    print(f"\n=== Palettes ({len(palettes)}) ===")
    for i, pal in enumerate(palettes):
        # Deduplicate for display
        unique_pal = list(dict.fromkeys(pal))
        hex_colors = [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in unique_pal]
        print(f"  Palette {i}: {hex_colors}")

    # Count which palettes are actually used
    used_pals = set()
    for ty in range(TILES_Y):
        for tx in range(TILES_X):
            y0, x0 = ty * TILE_H, tx * TILE_W
            tile = img_array[y0:y0+TILE_H, x0:x0+TILE_W]
            colors = get_tile_colors(tile)
            # Find which palette contains all these colors
            for pi, pal in enumerate(palettes):
                pal_set = set(pal)
                if colors.issubset(pal_set):
                    used_pals.add(pi)
                    break

    print(f"\nPalettes actually used: {len(used_pals)}/{len(palettes)}")

    return max_tile_colors <= 4 and len(all_colors) <= 32


def main():
    print("Loading source image...")
    img = Image.open(SRC).convert("RGB")
    w, h = img.size
    print(f"Source: {w}x{h}")

    if w != 160 or h != 144:
        print(f"WARNING: Source is {w}x{h}, expected 160x144. Resizing with nearest neighbor.")
        img = img.resize((160, 144), Image.NEAREST)

    img_array = np.array(img)

    # Step 1: Analyze raw tile color counts
    tiles = extract_tiles(img_array)
    raw_tile_counts = []
    for ty, tx, tile in tiles:
        nc = len(get_tile_colors(tile))
        raw_tile_counts.append(nc)
    print(f"Raw tile color counts: min={min(raw_tile_counts)}, max={max(raw_tile_counts)}, "
          f"mean={np.mean(raw_tile_counts):.1f}")
    print(f"Tiles with >4 colors: {sum(1 for c in raw_tile_counts if c > 4)}/{len(raw_tile_counts)}")

    # Step 2: Pre-quantize each tile to at most 4 colors
    print("\nPre-quantizing tiles to 4 colors each...")
    img_array = prequantize_tiles(img_array, max_colors=COLORS_PER_PALETTE)

    # Step 3: Build 8 optimal palettes
    print("\nBuilding optimal palettes...")
    palettes = build_palettes(img_array, n_palettes=MAX_PALETTES)

    # Step 4: Assign each tile to best palette and remap
    print("Assigning tiles to palettes and remapping...")
    tile_palette_map = assign_tiles_to_palettes(img_array, palettes)
    result = remap_image(img_array, palettes, tile_palette_map)

    # Step 5: Save
    out_img = Image.fromarray(result)
    out_img.save(DST)
    print(f"\nSaved to {DST}")

    # Step 6: Verify
    ok = verify_output(result, palettes)
    if ok:
        print("\nAll GBC constraints satisfied!")
    else:
        print("\nWARNING: Some constraints not met!")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
