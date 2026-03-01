# nickgame — Agent Guide

NES game built with **NESFab** (not cc65/ca65). Chapter-based biographical RPG — see `GAME_DESIGN.md` for full design. Currently implementing **Chapter 2: Bicycle Dash** (side-scrolling obstacle course).

## Toolchain

- **NESFab v1.8** — purpose-built NES language, compiles `.fab` to 6502. Binary at `/usr/local/bin/nesfab`
- **Build:** `make` produces `nickgame.nes` (40KB NROM). `make web && make serve` for browser testing at localhost:8080
- **Config:** `game.cfg` — NROM mapper, vertical mirroring, 32K PRG, 8K CHR
- **No Python, no cc65, no ca65/ld65** — those were removed
- **If `nesfab` is missing:** rebuild from source (requires boost):
  ```
  brew install boost
  git clone https://github.com/pubby/nesfab.git /tmp/nesfab
  cd /tmp/nesfab && make CXX=clang++ ARCH=ARM64 \
    CXXFLAGS="-I/opt/homebrew/include" \
    LDLIBS="-L/opt/homebrew/lib -lboost_program_options" release
  cp /tmp/nesfab/nesfab /usr/local/bin/nesfab
  ```

## Project Layout

```
game.cfg                # NESFab project config
Makefile                # build/web/clean/serve targets
src/main.fab            # game code (NESFab source)
lib/                    # NESFab standard library (vendored)
lib/nesfab-doc.adoc     # NESFab language reference (6500 lines)
lib/examples/           # NESFab example projects (platformer, scrolling, etc.)
assets/chapter-2/       # 46 PNG source art files (see README.md inside)
reference/chapter-2/    # reference photos
web/index.html          # JSNES browser emulator for testing
GAME_DESIGN.md          # full game design document
```

## NESFab Quick Reference

NESFab is not C and not assembly. Key concepts:

- **`mode`** — a game state (like `main()`, `play_level()`). Entry point is `mode main()`
- **`nmi`** — NMI handler function, runs every vblank. Declared with `: nmi handler_name` on a mode
- **`vars /group`** — variable declarations in a named RAM group
- **`fn`** — regular function. **`ct`** — compile-time constant
- **`struct`** — value types. **Types:** `U` (u8), `UU` (u16), `S` (s8), `SS` (s16), `SF`/`SSF` (fixed-point), `Bool`
- **`{$ADDR}(value)`** — write to hardware register. **`{NAMED}(value)`** for named registers
- **`data /group`** — ROM data (palettes, metasprites, nametables)
- **`chrrom`** — inline CHR data from files: `chrrom : "file.png"`
- **Indentation-based** syntax (like Python), no semicolons or braces
- **`goto mode X()`** — switch game mode. **`: preserves /group`** — keep vars across mode switch

### Standard Library Highlights (in `lib/`)

- `lib/nes.fab` — core NES hardware interface (PPU, OAM, palettes, scrolling, pads)
- `lib/metasprite/` — metasprite system for multi-tile sprites
- `lib/math/rng.fab` — PRNG. `lib/math/base_10.fab` — number display
- `lib/decompress/` — data compression (donut, pbz, rlz)
- `lib/audio/` — APU interface, Puf1 music engine

### NESFab Docs & Examples (READ THESE)

All vendored locally — no network needed:

- **Language reference:** `lib/nesfab-doc.adoc` (~6500 lines). Read sections relevant to your task.
- **Online docs:** https://pubby.games/nesfab/doc.html (same content, formatted)
- **GitHub:** https://github.com/pubby/nesfab

**Examples** in `lib/examples/` — most relevant:
- `lib/examples/platformer/` — scrolling, collision, metasprites, levels (closest to our game)
- `lib/examples/scrolling_8_way/` — scroll engine, metatiles, mapfab integration
- `lib/examples/hello_world/` — minimal NESFab program
- `lib/examples/metasprite/` — sprite animation
- `lib/examples/counter/` — text/number display

## Art Assets

46 PNGs in `assets/chapter-2/` — see `assets/chapter-2/README.md` for the full manifest. Sprites are various sizes (8x8 to 32x32, RGBA). BG tiles are all 8x8.

These PNGs need to be converted to NES CHR format. NESFab handles this natively with `chrrom` declarations — no external Python tools needed.

## Current State

Minimal bootable ROM — just shows a colored screen. Everything from here is greenfield: CHR conversion, sprites, scrolling, gameplay, etc.

## NES Constraints (always keep in mind)

- 256x240 resolution, 64 sprites max, 8 per scanline
- 4 palettes of 4 colors each for BG, 4 palettes of 3+transparent for sprites
- CHR tiles are 8x8. Larger sprites = multiple tiles (metasprites)
- Horizontal scrolling is natural for NROM vertical mirroring
- OAM (sprite RAM) is 256 bytes = 64 sprite entries
