#!/usr/bin/env python3
"""Analyze the color distribution of the title screen source image tiles."""
import numpy as np
from PIL import Image
from collections import Counter
import colorsys

img = Image.open("/Users/nick/code/nickgame/reference/title/title-scaled.png").convert("RGB")
pixels = np.array(img)

# For each tile, get the 4 pre-quantized colors
from sklearn.cluster import KMeans

TY, TX = 18, 20
tile_colors = []

for ty in range(TY):
    for tx in range(TX):
        tile = pixels[ty*8:(ty+1)*8, tx*8:(tx+1)*8]
        flat = tile.reshape(-1, 3)
        unique = set(map(tuple, flat.tolist()))
        if len(unique) <= 4:
            tile_colors.append((ty, tx, unique))
            continue
        from sklearn.cluster import KMeans
        flat_f = flat.astype(np.float64)
        # Simple RGB k-means for quick analysis
        km = KMeans(n_clusters=4, n_init=5, random_state=42)
        labels = km.fit_predict(flat_f)
        colors = set()
        for ci in range(4):
            mask = labels == ci
            if not mask.any():
                continue
            cpx = [tuple(int(v) for v in flat[j]) for j in np.where(mask)[0]]
            rep = Counter(cpx).most_common(1)[0][0]
            colors.add(rep)
        tile_colors.append((ty, tx, colors))

# Classify all unique colors by hue
all_unique = set()
for _, _, cs in tile_colors:
    all_unique.update(cs)

# Group by hue
hue_groups = {"white/near-white": [], "gray": [], "red/orange": [], "brown": [],
              "yellow": [], "green": [], "cyan": [], "blue": [], "purple": [],
              "dark": [], "other": []}

for c in sorted(all_unique):
    r, g, b = c
    h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)

    if v < 0.15:
        hue_groups["dark"].append(c)
    elif s < 0.1 and v > 0.9:
        hue_groups["white/near-white"].append(c)
    elif s < 0.15:
        hue_groups["gray"].append(c)
    elif h < 0.05 or h > 0.95:
        hue_groups["red/orange"].append(c)
    elif h < 0.1:
        hue_groups["brown" if v < 0.6 else "red/orange"].append(c)
    elif h < 0.17:
        hue_groups["brown" if v < 0.5 else "yellow"].append(c)
    elif h < 0.2:
        hue_groups["yellow"].append(c)
    elif h < 0.45:
        hue_groups["green"].append(c)
    elif h < 0.55:
        hue_groups["cyan"].append(c)
    elif h < 0.72:
        hue_groups["blue"].append(c)
    elif h < 0.85:
        hue_groups["purple"].append(c)
    else:
        hue_groups["red/orange"].append(c)

print(f"Total unique tile colors: {len(all_unique)}")
for name, colors in hue_groups.items():
    if colors:
        print(f"\n{name.upper()} ({len(colors)} colors):")
        for c in sorted(colors, key=lambda x: -colorsys.rgb_to_hsv(x[0]/255, x[1]/255, x[2]/255)[2]):
            h, s, v = colorsys.rgb_to_hsv(c[0]/255, c[1]/255, c[2]/255)
            print(f"  RGB{c}  H={h:.2f} S={s:.2f} V={v:.2f}")

# Count how many non-white tiles exist (tiles that aren't pure white)
non_white_tiles = [(ty, tx) for ty, tx, cs in tile_colors
                    if cs != {(255,255,255)} and len(cs) > 1]
print(f"\nNon-trivial tiles (>1 color, not just white): {len(non_white_tiles)}")

# Show which tiles have warm colors (reds, browns, greens, yellows)
warm_hues = set()
for name in ["red/orange", "brown", "yellow", "green"]:
    warm_hues.update(hue_groups.get(name, []))

warm_tiles = []
for ty, tx, cs in tile_colors:
    if cs & warm_hues:
        warm_tiles.append((ty, tx, cs & warm_hues))
print(f"Tiles containing warm/accent colors: {len(warm_tiles)}")
for ty, tx, wc in warm_tiles[:20]:
    print(f"  ({ty},{tx}): {wc}")
