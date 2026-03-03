#!/usr/bin/env python3
"""Extend the green checkered floor in the gameplay background image.

The floor currently only covers tile rows 15-17 (y=120-143).
The baby crawls at y~136, so the floor needs to extend higher to be visible behind it.
We'll extend the floor up to tile row 10 (y=80).
"""

from PIL import Image

img = Image.open("assets/chapter1/ch1_gameplay_bg.png").convert("RGB")
w, h = img.size
print(f"Image size: {w}x{h}")

# Floor is at rows 15-17 (y=120-143) — green checkered pattern
# Colors: (80,144,64), (32,96,40), (32,72,120)
# The floor pattern repeats every 16px (2 tile rows)

# Grab 16px of floor pattern (rows 15-16, y=120-135)
floor_strip = img.crop((0, 120, w, 136))

# Grab the baseboard/transition row (row 14, y=112-119)
baseboard = img.crop((0, 112, w, 120))

# New layout:
# Rows 0-9 (y=0-79): wall + window (keep as-is)
# Row 10 (y=80-87): baseboard transition
# Rows 11-17 (y=88-143): green checkered floor

# Paste baseboard at row 10
img.paste(baseboard, (0, 80))

# Fill rows 11-17 with floor pattern
for y in range(88, 144, 16):
    remaining = min(16, 144 - y)
    strip = floor_strip.crop((0, 0, w, remaining))
    img.paste(strip, (0, y))

out_path = "assets/chapter1/ch1_gameplay_bg.png"
img.save(out_path)
print(f"Saved to {out_path}")
print("Floor now extends from y=88 to y=143 (tile rows 11-17)")
