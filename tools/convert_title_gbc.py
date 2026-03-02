#!/usr/bin/env python3
"""
Convert a full-color 160x144 PNG to Game Boy Color format.

GBC: 160x144, 8x8 tiles, max 4 colors/tile, max 8 palettes of 4 colors each.

Approach: iterative palette assignment + refinement with hue-balanced master palette.
1. Pre-quantize tiles to 4 colors, snap near-whites to pure white
2. Build 32-color master: 1 white + 31 from hue-balanced clustering of all tile colors
3. Remap tiles to master, enforce <=4
4. Iterative: assign each tile to lowest-error palette, update palettes from assignments
5. Final remap
"""

import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
from collections import Counter
import colorsys


def rgb_to_lab(rgb):
    rgb = np.asarray(rgb, dtype=np.float64)
    srgb = rgb / 255.0
    linear = np.where(srgb > 0.04045, ((srgb + 0.055) / 1.055) ** 2.4, srgb / 12.92)
    r, g, b = linear[..., 0], linear[..., 1], linear[..., 2]
    x = (0.4124564*r + 0.3575761*g + 0.1804375*b) / 0.95047
    y = 0.2126729*r + 0.7151522*g + 0.0721750*b
    z = (0.0193339*r + 0.1191920*g + 0.9503041*b) / 1.08883
    def f(t):
        d = 6.0/29.0
        return np.where(t > d**3, t**(1.0/3.0), t/(3*d**2) + 4.0/29.0)
    fx, fy, fz = f(x), f(y), f(z)
    return np.stack([116*fy - 16, 500*(fx - fy), 200*(fy - fz)], axis=-1)


def classify_hue(c):
    r, g, b = c
    h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
    if v < 0.15: return "dark"
    if s < 0.10 and v > 0.85: return "white"
    if s < 0.10: return "gray"
    if h < 0.05 or h > 0.92: return "red"
    if h < 0.12: return "warm" if v < 0.55 else "skin"
    if h < 0.20: return "yellow"
    if h < 0.45: return "green"
    if h < 0.55: return "cyan"
    if h < 0.72: return "blue"
    return "purple"


def quantize_tile(tile, n=4):
    flat = tile.reshape(-1, 3)
    unique = set(map(tuple, flat.tolist()))
    if len(unique) <= n:
        return tile.copy(), unique
    flat_lab = rgb_to_lab(flat.astype(np.float64))
    km = KMeans(n_clusters=n, n_init=10, random_state=42)
    labels = km.fit_predict(flat_lab)
    new_tile = tile.copy()
    colors = set()
    for ci in range(n):
        mask = labels == ci
        if not mask.any(): continue
        cpx = [tuple(int(v) for v in flat[j]) for j in np.where(mask)[0]]
        rep = Counter(cpx).most_common(1)[0][0]
        colors.add(rep)
        for j in np.where(mask)[0]:
            py, px = divmod(j, 8)
            new_tile[py, px] = rep
    return new_tile, colors


def snap_near_whites(tile, cset, threshold=8.0):
    """Replace near-white colors with pure white."""
    WHITE = (255, 255, 255)
    white_lab = rgb_to_lab(np.array([255, 255, 255], dtype=np.float64))
    new_cset = set()
    remap = {}
    for c in cset:
        c_lab = rgb_to_lab(np.array(c, dtype=np.float64))
        d = float(np.sqrt(np.sum((c_lab - white_lab)**2)))
        if d < threshold and c != WHITE:
            remap[c] = WHITE
            new_cset.add(WHITE)
        else:
            new_cset.add(c)

    if not remap:
        return tile, cset

    new_tile = tile.copy()
    for py in range(8):
        for px in range(8):
            c = tuple(int(v) for v in tile[py, px])
            if c in remap:
                new_tile[py, px] = remap[c]
    return new_tile, new_cset


def tile_error(tile_lab, pal_lab):
    diffs = tile_lab[:, None, :] - pal_lab[None, :, :]
    dists = np.sqrt(np.sum(diffs**2, axis=-1))
    return float(np.sum(np.min(dists, axis=1)))


def main():
    src_path = "/Users/nick/code/nickgame/reference/title/title-scaled.png"
    dst_path = "/Users/nick/code/nickgame/assets/title_screen.png"

    img = Image.open(src_path).convert("RGB")
    w, h = img.size
    print(f"Source: {w}x{h}")
    assert (w, h) == (160, 144)
    pixels = np.array(img)
    TY, TX = h//8, w//8
    NT = TY * TX

    # ================================================================
    # 1. Pre-quantize + snap near-whites
    # ================================================================
    print("1. Pre-quantizing + snapping near-whites...")
    tiles = []
    tile_csets = []
    for ty in range(TY):
        for tx in range(TX):
            raw = pixels[ty*8:(ty+1)*8, tx*8:(tx+1)*8]
            qt, cs = quantize_tile(raw, 4)
            qt, cs = snap_near_whites(qt, cs, threshold=12.0)
            tiles.append(qt)
            tile_csets.append(cs)

    # Precompute LAB
    tiles_lab = [rgb_to_lab(t.reshape(-1, 3).astype(np.float64)) for t in tiles]

    # ================================================================
    # 2. Hue-balanced 32-color master palette
    # ================================================================
    print("2. Building master palette...")
    WHITE = (255, 255, 255)
    all_colors = sorted(set().union(*tile_csets) - {WHITE})
    print(f"   Non-white unique colors: {len(all_colors)}")

    if len(all_colors) <= 31:
        master = [WHITE] + list(all_colors)
    else:
        # Group by hue sector, filtering out near-whites that got snapped
        hue_buckets = {}
        for c in all_colors:
            s = classify_hue(c)
            if s == "white":
                continue  # already have pure white
            hue_buckets.setdefault(s, []).append(c)

        # Count tile usage per sector (how many tiles contain at least one color from this sector)
        sector_tiles = Counter()
        for cs in tile_csets:
            seen = set()
            for c in cs:
                s = classify_hue(c)
                if s != "white" and s not in seen:
                    sector_tiles[s] += 1
                    seen.add(s)

        # Allocate slots: use sqrt(tile_count) to boost rare sectors
        raw_alloc = {}
        for s in hue_buckets:
            raw_alloc[s] = max(1, sector_tiles.get(s, 1) ** 0.6)
        total_raw = sum(raw_alloc.values())

        sector_slots = {}
        for s in hue_buckets:
            sector_slots[s] = max(1, round(31 * raw_alloc[s] / total_raw))

        # Normalize to exactly 31
        total = sum(sector_slots.values())
        while total > 31:
            for s in sorted(sector_slots, key=lambda x: -sector_slots[x]):
                if total <= 31: break
                if sector_slots[s] > 1:
                    sector_slots[s] -= 1
                    total -= 1
        while total < 31:
            for s in sorted(sector_slots, key=lambda x: -sector_tiles.get(x, 0)):
                if total >= 31: break
                sector_slots[s] += 1
                total += 1

        print("   Slot allocation:")
        for s in sorted(sector_slots):
            print(f"     {s:8s}: {sector_slots[s]:2d} slots ({len(hue_buckets[s]):3d} colors, {sector_tiles.get(s,0):3d} tiles)")

        # Cluster within each sector
        master = [WHITE]
        used = {WHITE}
        for sector, colors in sorted(hue_buckets.items()):
            n_slots = min(sector_slots.get(sector, 1), len(colors))
            if n_slots == 0: continue

            if len(colors) <= n_slots:
                for c in colors:
                    if c not in used:
                        master.append(c)
                        used.add(c)
                continue

            colors_arr = np.array(colors, dtype=np.float64)
            colors_lab = rgb_to_lab(colors_arr)
            weights = np.array([sum(1 for cs in tile_csets if c in cs) for c in colors], dtype=np.float64)
            weights = np.maximum(weights, 1.0)

            km = KMeans(n_clusters=n_slots, n_init=30, random_state=42)
            km.fit(colors_lab, sample_weight=weights)

            for centroid in km.cluster_centers_:
                dists = np.sqrt(np.sum((colors_lab - centroid)**2, axis=-1))
                for si in np.argsort(dists):
                    c = colors[si]
                    if c not in used:
                        master.append(c)
                        used.add(c)
                        break

    master = master[:32]
    M = len(master)
    master_arr = np.array(master, dtype=np.float64)
    master_lab = rgb_to_lab(master_arr)

    print(f"   Master palette ({M} colors):")
    for i, c in enumerate(master):
        print(f"     [{i:2d}] RGB{c}  {classify_hue(c)}")

    # ================================================================
    # 3. Remap tiles to master palette
    # ================================================================
    print("\n3. Remapping tiles to master...")
    tile_midx = []
    for ti in range(NT):
        flat_lab = tiles_lab[ti]
        diffs = flat_lab[:, None, :] - master_lab[None, :, :]
        dists = np.sqrt(np.sum(diffs**2, axis=-1))
        nearest = np.argmin(dists, axis=1)

        used_set = set(nearest.tolist())
        if len(used_set) > 4:
            counts = Counter(nearest.tolist())
            keep = sorted(c for c, _ in counts.most_common(4))
            keep_lab = master_lab[keep]
            for j in range(64):
                d = np.sqrt(np.sum((flat_lab[j] - keep_lab)**2, axis=-1))
                nearest[j] = keep[np.argmin(d)]
            used_set = set(nearest.tolist())

        tile_midx.append(used_set)
        tile = tiles[ti]
        for j in range(64):
            py, px = divmod(j, 8)
            tile[py, px] = master[nearest[j]]
        tiles[ti] = tile

    # Update LAB cache
    tiles_lab = [rgb_to_lab(t.reshape(-1, 3).astype(np.float64)) for t in tiles]

    # ================================================================
    # 4. Iterative palette refinement
    # ================================================================
    print("4. Iterative palette optimization...")

    # Initialize: group the 32 master colors into 8 palettes of 4
    # Use k-means on master_lab to get 8 groups
    km8 = KMeans(n_clusters=8, n_init=50, random_state=42)
    color_labels = km8.fit_predict(master_lab)

    palettes = [[] for _ in range(8)]
    for ci, label in enumerate(color_labels):
        palettes[label].append(ci)

    # Trim/pad to exactly 4
    for pi in range(8):
        if len(palettes[pi]) > 4:
            # Keep 4 most widely used
            usage = {ci: sum(1 for cs in tile_csets if master[ci] in cs) for ci in palettes[pi]}
            palettes[pi] = sorted(palettes[pi], key=lambda ci: -usage.get(ci, 0))[:4]
        while len(palettes[pi]) < 4:
            # Add nearest unused color
            pal_lab = master_lab[palettes[pi]]
            center = pal_lab.mean(axis=0)
            dists = np.sqrt(np.sum((master_lab - center)**2, axis=-1))
            for si in np.argsort(dists):
                if int(si) not in palettes[pi]:
                    palettes[pi].append(int(si))
                    break

    def assign_all():
        tp = np.zeros(NT, dtype=int)
        for ti in range(NT):
            best_pi, best_err = 0, float('inf')
            for pi in range(8):
                pal_lab = master_lab[palettes[pi]]
                err = tile_error(tiles_lab[ti], pal_lab)
                if err < best_err:
                    best_err = err
                    best_pi = pi
            tp[ti] = best_pi
        return tp

    def update_all(tp):
        new_pals = []
        for pi in range(8):
            assigned = np.where(tp == pi)[0]
            if len(assigned) == 0:
                new_pals.append(list(palettes[pi]))
                continue

            group_lab = np.vstack([tiles_lab[ti] for ti in assigned])
            n_cl = min(4, len(group_lab))
            km = KMeans(n_clusters=n_cl, n_init=10, random_state=42)
            km.fit(group_lab)

            pal = []
            used_ci = set()
            for cent in km.cluster_centers_:
                dists = np.sqrt(np.sum((master_lab - cent)**2, axis=-1))
                for si in np.argsort(dists):
                    if int(si) not in used_ci:
                        pal.append(int(si))
                        used_ci.add(int(si))
                        break
            while len(pal) < 4:
                for ci in range(M):
                    if ci not in used_ci:
                        pal.append(ci)
                        used_ci.add(ci)
                        break
            new_pals.append(pal[:4])
        return new_pals

    def total_err(tp):
        return sum(tile_error(tiles_lab[ti], master_lab[palettes[tp[ti]]]) for ti in range(NT))

    for it in range(20):
        tp = assign_all()
        palettes = update_all(tp)
        err = total_err(tp)
        if it % 4 == 0 or it == 19:
            print(f"   Iter {it:2d}: error = {err:.0f}")

    tp = assign_all()

    print("\n   Final palettes:")
    for pi in range(8):
        cs = [master[ci] for ci in palettes[pi]]
        n = int(np.sum(tp == pi))
        sectors = [classify_hue(c) for c in cs]
        print(f"     Pal {pi}: {cs} ({n} tiles) {sectors}")

    # ================================================================
    # 5. Final remap
    # ================================================================
    print("\n5. Final remap...")
    output = np.zeros_like(pixels)
    for ti in range(NT):
        ty, tx = ti // TX, ti % TX
        pi = int(tp[ti])
        pal_idx = palettes[pi]
        pal_lab = master_lab[pal_idx]
        flat_lab = tiles_lab[ti]
        diffs = flat_lab[:, None, :] - pal_lab[None, :, :]
        dists = np.sqrt(np.sum(diffs**2, axis=-1))
        nearest = np.argmin(dists, axis=1)
        for j in range(64):
            py, px = divmod(j, 8)
            output[ty*8+py, tx*8+px] = master[pal_idx[nearest[j]]]

    Image.fromarray(output.astype(np.uint8), "RGB").save(dst_path)
    print(f"\nSaved: {dst_path}")

    # ================================================================
    # Verify
    # ================================================================
    print("\n--- Verification ---")
    vp = np.array(Image.open(dst_path).convert("RGB"))
    all_c = set()
    max_tc = 0
    for ty in range(TY):
        for tx in range(TX):
            t = vp[ty*8:(ty+1)*8, tx*8:(tx+1)*8]
            cs = set(tuple(int(v) for v in t[py, px]) for py in range(8) for px in range(8))
            all_c.update(cs)
            nc = len(cs)
            if nc > max_tc: max_tc = nc
            if nc > 4:
                print(f"   WARN: tile ({ty},{tx}): {nc} colors")

    print(f"Size: {vp.shape[1]}x{vp.shape[0]}")
    print(f"Total unique colors: {len(all_c)}")
    print(f"Max colors/tile: {max_tc}")
    print(f"{'PASS' if max_tc <= 4 else 'FAIL'}: per-tile limit")
    print(f"{'PASS' if len(all_c) <= 32 else 'FAIL'}: total colors <= 32")

    print(f"\nFinal 8 palettes:")
    for i in range(8):
        cs = [master[ci] for ci in palettes[i]]
        while len(cs) < 4: cs.append(None)
        print(f"  Palette {i}: {cs}")

    print(f"\nAll {len(all_c)} output colors:")
    for c in sorted(all_c):
        print(f"  RGB{c}  [{classify_hue(c)}]")


if __name__ == "__main__":
    main()
