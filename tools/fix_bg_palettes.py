#!/usr/bin/env python3
"""Fix gameplay background to use ≤8 GBC palettes.

The image has 11 unique colors across 28 per-tile color sets.
png2asset groups these into 9 GBC palettes (4 colors each), then truncates to 8.
This causes floor tiles to get wrong palette assignments.

Analysis shows the 9th palette exists because 2 tiles in the window frame area
use {(176,216,232), (248,240,200)} together. No existing 4-color GBC palette
can include both colors.

Fix: Replace (176,216,232) with (104,176,216) in those 2 tiles — a subtle
color shift that lets them fit into the main wall palette.
"""

from PIL import Image

img = Image.open("assets/chapter1/ch1_gameplay_bg.png").convert("RGB")
w, h = img.size

# Find tiles that use BOTH (176,216,232) and (248,240,200)
target_old = (176, 216, 232)
target_new = (104, 176, 216)  # similar pale blue, already in wall palette
cream = (248, 240, 200)

fixed_count = 0
for row in range(h // 8):
    for col in range(w // 8):
        colors = set()
        for py in range(8):
            for px in range(8):
                colors.add(img.getpixel((col * 8 + px, row * 8 + py)))

        if target_old in colors and cream in colors:
            # This tile uses both — remap (176,216,232) → (104,176,216)
            print(f"  Fixing tile ({col},{row}): {sorted(colors)}")
            for py in range(8):
                for px in range(8):
                    x, y = col * 8 + px, row * 8 + py
                    if img.getpixel((x, y)) == target_old:
                        img.putpixel((x, y), target_new)
            fixed_count += 1

print(f"\nFixed {fixed_count} tiles")

# Verify: recount GBC palettes needed
tile_pals = set()
for row in range(h // 8):
    for col in range(w // 8):
        colors = set()
        for py in range(8):
            for px in range(8):
                colors.add(img.getpixel((col * 8 + px, row * 8 + py)))
        tile_pals.add(frozenset(colors))

print(f"Per-tile palettes: {len(tile_pals)}")

# Group into GBC palettes (greedy: each GBC palette max 4 colors)
gbc_pals = []
for tp in sorted(tile_pals, key=lambda x: -len(x)):
    placed = False
    for gp in gbc_pals:
        combined = gp | tp
        if len(combined) <= 4:
            gp.update(tp)
            placed = True
            break
    if not placed:
        gbc_pals.append(set(tp))

print(f"GBC palettes needed: {len(gbc_pals)}")
for i, gp in enumerate(gbc_pals):
    print(f"  GBC Pal {i}: {sorted(gp)}")

if len(gbc_pals) > 8:
    print("\nWARNING: Still >8 GBC palettes! Need more fixes.")
else:
    print("\nSUCCESS: ≤8 GBC palettes!")

out_path = "assets/chapter1/ch1_gameplay_bg.png"
img.save(out_path)
print(f"Saved to {out_path}")
