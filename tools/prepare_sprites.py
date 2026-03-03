#!/usr/bin/env /opt/homebrew/bin/python3
"""
Prepare Chapter 1 sprite/background assets from reference JPGs.

Handles:
- Fake checkerboard transparency removal
- Tight cropping to content
- Splitting multi-sprite sheets
- Resizing to target Game Boy sizes
- GBC background quantization
"""

import sys
import os
from PIL import Image
import math

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'chapter1')
REF_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reference', 'chapter-1')

def is_checker_pixel(r, g, b, checker_colors, tolerance=30):
    """Check if a pixel matches one of the checkerboard colors."""
    for cr, cg, cb in checker_colors:
        if abs(r-cr) < tolerance and abs(g-cg) < tolerance and abs(b-cb) < tolerance:
            return True
    return False

def detect_checker_colors(img):
    """Sample corners to detect the two checkerboard colors."""
    pixels = img.load()
    w, h = img.size
    # Sample from corners (should be checkerboard)
    samples = []
    for x in [0, 1, 2, 3, w-4, w-3, w-2, w-1]:
        for y in [0, 1, 2, 3, h-4, h-3, h-2, h-1]:
            samples.append(pixels[x, y][:3])

    # Find the two most common colors
    from collections import Counter
    # Group similar colors
    groups = []
    for s in samples:
        found = False
        for g in groups:
            if all(abs(s[i] - g[0][i]) < 20 for i in range(3)):
                g.append(s)
                found = True
                break
        if not found:
            groups.append([s])

    groups.sort(key=len, reverse=True)
    colors = []
    for g in groups[:2]:
        avg = tuple(sum(c[i] for c in g) // len(g) for i in range(3))
        colors.append(avg)

    print(f"  Detected checker colors: {colors}")
    return colors

def remove_checkerboard(img, tolerance=35):
    """Remove checkerboard background, return RGBA image."""
    img = img.convert('RGBA')
    rgb = img.convert('RGB')
    checker_colors = detect_checker_colors(rgb)

    pixels = img.load()
    rgb_pixels = rgb.load()
    w, h = img.size

    for y in range(h):
        for x in range(w):
            r, g, b = rgb_pixels[x, y]
            if is_checker_pixel(r, g, b, checker_colors, tolerance):
                pixels[x, y] = (0, 0, 0, 0)

    return img

def crop_to_content(img):
    """Crop RGBA image to non-transparent bounding box."""
    bbox = img.getbbox()
    if bbox:
        return img.crop(bbox), bbox
    return img, (0, 0, img.size[0], img.size[1])

def split_vertical(img, n):
    """Split image into n equal vertical sections."""
    w, h = img.size
    section_h = h // n
    sections = []
    for i in range(n):
        section = img.crop((0, i * section_h, w, (i + 1) * section_h))
        sections.append(section)
    return sections

def split_horizontal(img, n):
    """Split image into n equal horizontal sections."""
    w, h = img.size
    section_w = w // n
    sections = []
    for i in range(n):
        section = img.crop((i * section_w, 0, (i + 1) * section_w, h))
        sections.append(section)
    return sections

def resize_nearest(img, target_w, target_h):
    """Resize using nearest-neighbor (best for pixel art)."""
    return img.resize((target_w, target_h), Image.NEAREST)

def resize_fit(img, target_w, target_h):
    """Resize to fit within target, maintaining aspect ratio, then center on transparent canvas."""
    w, h = img.size
    scale = min(target_w / w, target_h / h)
    new_w = max(1, int(w * scale))
    new_h = max(1, int(h * scale))
    resized = img.resize((new_w, new_h), Image.LANCZOS)

    # Threshold alpha to binary (GBC needs fully opaque or fully transparent)
    pixels = resized.load()
    for y in range(new_h):
        for x in range(new_w):
            r, g, b, a = pixels[x, y]
            if a < 128:
                pixels[x, y] = (0, 0, 0, 0)
            else:
                pixels[x, y] = (r, g, b, 255)

    canvas = Image.new('RGBA', (target_w, target_h), (0, 0, 0, 0))
    paste_x = (target_w - new_w) // 2
    paste_y = (target_h - new_h) // 2
    canvas.paste(resized, (paste_x, paste_y))
    return canvas

def snap_to_tile_size(w, h, tile=8):
    """Round up to nearest multiple of tile size."""
    return ((w + tile - 1) // tile) * tile, ((h + tile - 1) // tile) * tile

def color_dist(c1, c2):
    """Weighted color distance for perceptual similarity."""
    dr = c1[0] - c2[0]
    dg = c1[1] - c2[1]
    db = c1[2] - c2[2]
    return 2*dr*dr + 4*dg*dg + 3*db*db

def quantize_sprite(img, max_palettes=4, colors_per_pal=3):
    """Quantize an RGBA sprite for GBC: max_palettes tile palettes,
    each with colors_per_pal opaque colors + transparent.
    1. Snap to 5-bit RGB
    2. Find per-tile best colors
    3. Merge tile palettes to fit max_palettes
    4. Remap all pixels
    """
    from collections import Counter

    pixels = img.load()
    w, h = img.size

    # Step 1: snap all opaque pixels to 5-bit RGB
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if a < 128:
                pixels[x, y] = (0, 0, 0, 0)
            else:
                pixels[x, y] = ((r >> 3) << 3, (g >> 3) << 3, (b >> 3) << 3, 255)

    # Step 2: collect per-tile opaque colors and find best palette per tile
    tiles = []  # list of (tx, ty, pixel_list, palette)
    for ty in range(0, h, 8):
        for tx in range(0, w, 8):
            opaque = []
            for dy in range(8):
                for dx in range(8):
                    x, y = tx + dx, ty + dy
                    if x < w and y < h:
                        r, g, b, a = pixels[x, y]
                        if a > 0:
                            opaque.append((r, g, b))
            if not opaque:
                tiles.append((tx, ty, opaque, ()))
                continue
            # Pick best colors for this tile
            unique = list(set(opaque))
            if len(unique) <= colors_per_pal:
                pal = tuple(sorted(unique))
            else:
                counts = Counter(opaque)
                pal = tuple(sorted([c for c, _ in counts.most_common(colors_per_pal)]))
            tiles.append((tx, ty, opaque, pal))

    # Step 3: collect unique non-empty palettes and merge down
    unique_pals = list(set(t[3] for t in tiles if t[3]))
    print(f"    {len(unique_pals)} unique tile palettes, merging to {max_palettes}")

    while len(unique_pals) > max_palettes:
        # Find two closest palettes to merge
        best_i, best_j, best_dist = 0, 1, float('inf')
        for i in range(len(unique_pals)):
            for j in range(i+1, len(unique_pals)):
                d = 0
                for c1 in unique_pals[i]:
                    d += min(color_dist(c1, c2) for c2 in unique_pals[j])
                for c2 in unique_pals[j]:
                    d += min(color_dist(c2, c1) for c1 in unique_pals[i])
                if d < best_dist:
                    best_dist = d
                    best_i, best_j = i, j
        # Merge: combine colors, pick top by coverage
        combined = list(unique_pals[best_i]) + list(unique_pals[best_j])
        counts = Counter(combined)
        merged = tuple(sorted([c for c, _ in counts.most_common(colors_per_pal)]))
        unique_pals[best_i] = merged
        unique_pals.pop(best_j)

    final_pals = unique_pals
    print(f"    Final palettes: {len(final_pals)}")

    # Step 4: assign each tile to best palette and remap pixels
    def pal_error(tile_pixels, pal):
        return sum(min(color_dist(p, c) for c in pal) for p in tile_pixels)

    for tx, ty, opaque, _ in tiles:
        if not opaque:
            continue
        # Find best palette
        best_p = min(final_pals, key=lambda p: pal_error(opaque, p))
        # Remap pixels
        for dy in range(8):
            for dx in range(8):
                x, y = tx + dx, ty + dy
                if x < w and y < h:
                    r, g, b, a = pixels[x, y]
                    if a > 0:
                        best_c = min(best_p, key=lambda c: color_dist((r, g, b), c))
                        pixels[x, y] = (best_c[0], best_c[1], best_c[2], 255)

    return img

def process_background():
    """Process background: resize to 160x144."""
    print("\n=== Background ===")
    path = os.path.join(REF_DIR, 'background.jpg')
    if not os.path.exists(path):
        # Try PNG
        path = os.path.join(REF_DIR, 'background.png')
    img = Image.open(path).convert('RGB')
    print(f"  Source: {img.size}")

    img = img.resize((160, 144), Image.LANCZOS)
    out = os.path.join(ASSETS_DIR, 'ch1_bg.png')
    img.save(out)
    print(f"  Saved: {out} ({img.size})")
    return out

def process_baby():
    """Process baby: remove checkerboard, split into 2 poses, crop, resize."""
    print("\n=== Baby ===")
    path = os.path.join(REF_DIR, 'baby.jpg')
    if not os.path.exists(path):
        path = os.path.join(REF_DIR, 'baby.png')
    img = Image.open(path)
    print(f"  Source: {img.size}")

    # Remove checkerboard
    img = remove_checkerboard(img)

    # Split into 2 poses (top = sitting, bottom = with calculator)
    poses = split_vertical(img, 2)

    results = []
    names = ['baby_sitting', 'baby_calculator']
    for i, (pose, name) in enumerate(zip(poses, names)):
        cropped, bbox = crop_to_content(pose)
        print(f"  {name}: cropped to {cropped.size} from bbox {bbox}")

        # Determine target size: snap to 8px grid, fit within reasonable sprite bounds
        cw, ch = cropped.size
        # Scale to fit roughly 32x40 max (4x5 tiles), preserving aspect
        max_w, max_h = 32, 40
        scale = min(max_w / cw, max_h / ch)
        if scale < 1:
            new_w = max(8, int(cw * scale))
            new_h = max(8, int(ch * scale))
        else:
            new_w, new_h = cw, ch

        tw, th = snap_to_tile_size(new_w, new_h)
        resized = resize_fit(cropped, tw, th)
        resized = quantize_sprite(resized, max_palettes=4, colors_per_pal=3)

        out = os.path.join(ASSETS_DIR, f'{name}.png')
        resized.save(out)
        print(f"  Saved: {out} ({resized.size})")
        results.append(out)

    return results

def process_objects():
    """Process objects: remove checkerboard, split into 3, crop, resize to 16x16."""
    print("\n=== Objects ===")
    path = os.path.join(REF_DIR, 'objects.jpg')
    if not os.path.exists(path):
        path = os.path.join(REF_DIR, 'objects.png')
    img = Image.open(path)
    print(f"  Source: {img.size}")

    # Remove checkerboard
    img = remove_checkerboard(img)

    # Split into 3 objects horizontally
    objects = split_horizontal(img, 3)

    results = []
    names = ['obj_calculator', 'obj_book', 'obj_ball']
    for obj, name in zip(objects, names):
        cropped, bbox = crop_to_content(obj)
        print(f"  {name}: cropped to {cropped.size} from bbox {bbox}")

        # Resize to 16x16
        resized = resize_fit(cropped, 16, 16)
        resized = quantize_sprite(resized, max_palettes=1, colors_per_pal=3)

        out = os.path.join(ASSETS_DIR, f'{name}.png')
        resized.save(out)
        print(f"  Saved: {out} ({resized.size})")
        results.append(out)

    return results

def main():
    os.makedirs(ASSETS_DIR, exist_ok=True)

    bg = process_background()
    babies = process_baby()
    objects = process_objects()

    print("\n=== Summary ===")
    print(f"Background: {bg}")
    for b in babies:
        print(f"Sprite: {b}")
    for o in objects:
        print(f"Sprite: {o}")
    print("\nNext: run gbc_quantize.py on the background, then png2asset on everything.")

if __name__ == '__main__':
    main()
