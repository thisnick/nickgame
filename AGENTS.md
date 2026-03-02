# nickgame — Agent Guide

> **Note:** `CLAUDE.md` is a symlink to this file (`AGENTS.md`). Edit `AGENTS.md` only.

Game Boy game built with **GBDK-2020** (C language). Chapter-based biographical RPG — see `GAME_DESIGN.md` for full design.

## Toolchain

- **GBDK-2020 v4.5.0** — installed at `~/gbdk/`
- **Build:** `make` produces `nickgame.gb`
- **Test:** `make web && make serve` → browser at localhost:8080

## Project Layout

```
Makefile                # build targets
src/main.c              # game code (C)
web/index.html          # EmulatorJS browser emulator
reference/              # reference art
GAME_DESIGN.md          # game design document
```

## Key Commands

```
make            # build nickgame.gb
make serve      # build + local web server at :8080
make clean      # clean build artifacts
```

## GBDK Quick Reference

- **Entry point:** `void main(void)` — standard C main
- **Game loop:** `while(1) { ... vsync(); }` — vsync() waits for vblank
- **Input:** `joypad()` returns bitmask — `J_UP`, `J_DOWN`, `J_LEFT`, `J_RIGHT`, `J_A`, `J_B`, `J_START`, `J_SELECT`
- **Background:** `set_bkg_data()` loads tiles, `set_bkg_tiles()` sets tilemap, `SHOW_BKG` enables
- **Sprites:** `set_sprite_data()` loads tiles, `set_sprite_tile()` assigns, `move_sprite()` positions, `SHOW_SPRITES` enables
- **Text:** `#include <stdio.h>` then `printf()` writes to background layer
- **Scrolling:** `scroll_bkg()` or `move_bkg()` for background scrolling
- **Asset conversion:** `~/gbdk/bin/png2asset` converts PNGs to C source (tiles + maps)

## GBDK Docs & Examples

- **Examples:** `~/gbdk/examples/gb/` — template_minimal, template_subfolders, galaxy, etc.
- **Manual:** `~/gbdk/gbdk_manual.pdf`
- **GitHub:** https://github.com/gbdk-2020/gbdk-2020

## Game Boy Constraints

- 160x144 resolution, 40 sprites max, 10 per scanline
- 4 BG palettes of 4 colors, 4 sprite palettes (DMG) — 8 each for GBC color mode
- 8x8 or 8x16 sprite mode
- 192 unique BG tiles (monochrome) or 384 (GBC color-only mode)
- Background map is 32x32 tiles (256x256 pixels), wraps around
- OAM is 160 bytes = 40 sprite entries
