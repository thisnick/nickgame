#!/usr/bin/env python3
"""
Generate 8KB CHR ROM for nickgame Chapter 2: Bicycle Dash
Tile layout:
  Background pattern table ($0000-$0FFF):
    $00: Blank
    $01: Sky (solid)
    $02: Road (solid)
    $03: Lane marker
    $04: Curb
    $05: Grass
    $06: Building top
    $07: Building window
    $10-$19: Digits 0-9
    $1A: Colon ':'
    $1B: 'T'
    $1C: 'I'
    $1D: 'M'
    $1E: 'E'
    $1F: 'S'
  Sprite pattern table ($1000-$1FFF):
    $00-$03: Bike 2x2 metasprite (TL,TR,BL,BR)
    $04: Pothole
    $05: Baozi (bun)
    $06-$09: Dog 2x2
    $0A-$0D: Vendor cart 2x2
    $0E: Crash star
    $0F: School gate top
    $10: School gate bottom
"""

def make_tile(art):
    """
    art: list of 8 strings, each 8 chars
    ' ' or '0' = color 0 (transparent)
    '1' = color 1
    '2' = color 2
    '3' = color 3
    Returns 16 bytes (plane0 then plane1)
    """
    if len(art) < 8:
        art = art + [' ' * 8] * (8 - len(art))
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

def blank():
    return make_tile(['        '] * 8)

# --- Build CHR ROM ---
chr_rom = bytearray(8192)

def set_tile(index, art, table=0):
    """table=0: BG table at $0000, table=1: sprite table at $1000"""
    offset = table * 0x1000 + index * 16
    data = make_tile(art)
    chr_rom[offset:offset+16] = data

# ==== BACKGROUND TABLE ($0000-$0FFF) ====

# Tile $00: Blank
set_tile(0x00, ['        '] * 8, 0)

# Tile $01: Sky (solid color 1)
set_tile(0x01, ['11111111'] * 8, 0)

# Tile $02: Road (solid color 2)
set_tile(0x02, ['22222222'] * 8, 0)

# Tile $03: Lane marker (white dashes on road)
set_tile(0x03, [
    '22222222',
    '22222222',
    '33333333',
    '33333333',
    '33333333',
    '22222222',
    '22222222',
    '22222222',
], 0)

# Tile $04: Curb (alternating blocks)
set_tile(0x04, [
    '33113311',
    '33113311',
    '11331133',
    '11331133',
    '33113311',
    '33113311',
    '11331133',
    '11331133',
], 0)

# Tile $05: Grass (solid color 1, green via palette)
set_tile(0x05, ['11111111'] * 8, 0)

# Tile $06: Building side
set_tile(0x06, [
    '22222222',
    '21111112',
    '21221122',
    '21221122',
    '21221122',
    '21221122',
    '21111112',
    '22222222',
], 0)

# Tile $07: Building window (lit)
set_tile(0x07, [
    '33333333',
    '31111113',
    '31331313',
    '31111113',
    '31331313',
    '31111113',
    '31331313',
    '33333333',
], 0)

# ---- Digits $10-$19 ----
DIGITS_ART = [
    # 0
    [' 11111 ',
     '1     1',
     '1     1',
     '1     1',
     '1     1',
     '1     1',
     ' 11111 ',
     '       '],
    # 1
    ['  111  ',
     '   1   ',
     '   1   ',
     '   1   ',
     '   1   ',
     '   1   ',
     ' 11111 ',
     '       '],
    # 2
    [' 11111 ',
     '     1 ',
     '     1 ',
     ' 11111 ',
     '1      ',
     '1      ',
     ' 11111 ',
     '       '],
    # 3
    [' 11111 ',
     '     1 ',
     '     1 ',
     ' 11111 ',
     '     1 ',
     '     1 ',
     ' 11111 ',
     '       '],
    # 4
    ['1     1',
     '1     1',
     '1     1',
     ' 111111',
     '      1',
     '      1',
     '      1',
     '       '],
    # 5
    [' 11111 ',
     '1      ',
     '1      ',
     ' 11111 ',
     '     1 ',
     '     1 ',
     ' 11111 ',
     '       '],
    # 6
    [' 11111 ',
     '1      ',
     '1      ',
     '111111 ',
     '1     1',
     '1     1',
     ' 11111 ',
     '       '],
    # 7
    [' 11111 ',
     '     1 ',
     '    1  ',
     '   1   ',
     '  1    ',
     '  1    ',
     '  1    ',
     '       '],
    # 8
    [' 11111 ',
     '1     1',
     '1     1',
     ' 11111 ',
     '1     1',
     '1     1',
     ' 11111 ',
     '       '],
    # 9
    [' 11111 ',
     '1     1',
     '1     1',
     ' 111111',
     '      1',
     '      1',
     ' 11111 ',
     '       '],
]

for i, art in enumerate(DIGITS_ART):
    set_tile(0x10 + i, art, 0)

# Colon ':'
set_tile(0x1A, [
    '       ',
    '  111  ',
    '  111  ',
    '       ',
    '  111  ',
    '  111  ',
    '       ',
    '       '], 0)

# 'T'
set_tile(0x1B, [
    '1111111',
    '  111  ',
    '  111  ',
    '  111  ',
    '  111  ',
    '  111  ',
    '  111  ',
    '       '], 0)

# 'I'
set_tile(0x1C, [
    '1111111',
    '  111  ',
    '  111  ',
    '  111  ',
    '  111  ',
    '  111  ',
    '1111111',
    '       '], 0)

# 'M'
set_tile(0x1D, [
    '1     1',
    '11   11',
    '1 1 1 1',
    '1  1  1',
    '1     1',
    '1     1',
    '1     1',
    '       '], 0)

# 'E'
set_tile(0x1E, [
    '1111111',
    '1      ',
    '1      ',
    '111111 ',
    '1      ',
    '1      ',
    '1111111',
    '       '], 0)

# 'S'
set_tile(0x1F, [
    ' 11111 ',
    '1      ',
    '1      ',
    ' 11111 ',
    '      1',
    '      1',
    ' 11111 ',
    '       '], 0)

# 'C'
set_tile(0x20, [
    ' 11111 ',
    '1      ',
    '1      ',
    '1      ',
    '1      ',
    '1      ',
    ' 11111 ',
    '       '], 0)

# 'O'
set_tile(0x21, [
    ' 11111 ',
    '1     1',
    '1     1',
    '1     1',
    '1     1',
    '1     1',
    ' 11111 ',
    '       '], 0)

# 'R'
set_tile(0x22, [
    '111111 ',
    '1     1',
    '1     1',
    '111111 ',
    '1  1   ',
    '1   1  ',
    '1    11',
    '       '], 0)

# ==== SPRITE TABLE ($1000-$1FFF) ====
# Tile $00: Bike top-left (rider head/torso)
set_tile(0x00, [
    '  1111  ',
    ' 111111 ',
    '  1111  ',
    '  1221  ',
    ' 112211 ',
    ' 111111 ',
    '  2112  ',
    ' 211112 ',
], 1)

# Tile $01: Bike top-right (handlebars)
set_tile(0x01, [
    '        ',
    ' 333333 ',
    '3       ',
    '33      ',
    '2       ',
    '        ',
    '        ',
    '        ',
], 1)

# Tile $02: Bike bottom-left (frame + left wheel)
set_tile(0x02, [
    ' 222222 ',
    '2      2',
    '       2',
    ' 333333 ',
    '3      3',
    ' 333333 ',
    '   22   ',
    '  2222  ',
], 1)

# Tile $03: Bike bottom-right (right wheel)
set_tile(0x03, [
    '  1111  ',
    ' 1    1 ',
    '1      1',
    '1  11  1',
    '1  11  1',
    '1      1',
    ' 1    1 ',
    '  1111  ',
], 1)

# Tile $04: Pothole (dark oval on road)
set_tile(0x04, [
    '        ',
    ' 333333 ',
    '33    33',
    '3      3',
    '33    33',
    ' 333333 ',
    '        ',
    '        ',
], 1)

# Tile $05: Baozi bun
set_tile(0x05, [
    '  1111  ',
    ' 133331 ',
    '1333331 ',
    '1333331 ',
    '13333 1 ',
    '1 111 1 ',
    ' 11111  ',
    '        ',
], 1)

# Tile $06: Dog top-left
set_tile(0x06, [
    '   1    ',
    ' 11111  ',
    ' 12221  ',
    '1122211 ',
    ' 12221  ',
    '3111113 ',
    '3      3',
    ' 333333 ',
], 1)

# Tile $07: Dog top-right
set_tile(0x07, [
    '  11    ',
    '  1     ',
    '        ',
    '        ',
    '     1  ',
    '     1  ',
    '        ',
    '        ',
], 1)

# Tile $08: Dog bottom-left
set_tile(0x08, [
    ' 333333 ',
    '3      3',
    '3      3',
    '33    33',
    ' 3    3 ',
    ' 3    3 ',
    '33    33',
    '        ',
], 1)

# Tile $09: Dog bottom-right
set_tile(0x09, [
    '        ',
    '        ',
    '        ',
    '      33',
    '     3  ',
    '     3  ',
    '      33',
    '        ',
], 1)

# Tile $0A: Vendor cart top-left
set_tile(0x0A, [
    '33333333',
    '3111111 ',
    '31222213',
    '31222213',
    '3111111 ',
    '33333333',
    '   2    ',
    '   2    ',
], 1)

# Tile $0B: Vendor cart top-right
set_tile(0x0B, [
    '33333333',
    ' 1111113',
    '31222213',
    '31222213',
    ' 1111113',
    '33333333',
    '    2   ',
    '    2   ',
], 1)

# Tile $0C: Vendor cart bottom-left
set_tile(0x0C, [
    '   2    ',
    '   2    ',
    '222222  ',
    '2      2',
    '2  22  2',
    '2      2',
    '222222  ',
    '        ',
], 1)

# Tile $0D: Vendor cart bottom-right
set_tile(0x0D, [
    '    2   ',
    '    2   ',
    '  222222',
    '2      2',
    '2  22  2',
    '2      2',
    '  222222',
    '        ',
], 1)

# Tile $0E: Crash star
set_tile(0x0E, [
    '3  3  3 ',
    ' 3 3 3  ',
    '  333   ',
    '333333  ',
    '  333   ',
    ' 3 3 3  ',
    '3  3  3 ',
    '        ',
], 1)

# Tile $0F: Finish flag / school gate top
set_tile(0x0F, [
    '31313131',
    '13131313',
    '31313131',
    '13131313',
    '31313131',
    '13131313',
    '31313131',
    '13131313',
], 1)

# Tile $10: Gate pillar
set_tile(0x10, [
    '333  333',
    '3 1  1 3',
    '3 1  1 3',
    '3 1  1 3',
    '3 1  1 3',
    '3 1  1 3',
    '3 1  1 3',
    '3333333 ',
], 1)

with open('chr/tiles.chr', 'wb') as f:
    f.write(chr_rom)

print(f"CHR ROM written: {len(chr_rom)} bytes")
print(f"Tiles defined:")
print(f"  BG table:     sky, road, lane marker, curb, grass, digits 0-9, letters")
print(f"  Sprite table: bike, pothole, baozi, dog, vendor cart, crash star, gate")
