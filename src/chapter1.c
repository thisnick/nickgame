#include <gb/gb.h>
#include <gb/cgb.h>
#include <gbdk/font.h>
#include <gbdk/console.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "chapter1.h"
#include "scene.h"
#include "ch1_level.h"
#include "ch1_bg_data.h"
#include "ch1_gameplay_bg_data.h"
#include "ch1_baby_sitting.h"
#include "ch1_baby_calc.h"
#include "ch1_baby_crawl1.h"
#include "ch1_baby_crawl2.h"
#include "ch1_obj_calc.h"
#include "ch1_obj_book.h"
#include "ch1_obj_ball.h"

// --- Constants ---

#define MAX_ARROWS     16
#define TARGET_Y       20
#define SPAWN_Y        124
#define SCROLL_SPEED   0x0180u  // 8.8 fixed-point (~1.5 px/frame)
#define TRAVEL_FRAMES  69

#define PERFECT_WINDOW 3
#define GOOD_WINDOW    8
#define PERFECT_SCORE  100
#define GOOD_SCORE     50

#define FEEDBACK_DURATION 20

#define DIR_LEFT  0
#define DIR_UP    1
#define DIR_DOWN  2
#define DIR_RIGHT 3

#define TARGET_SPRITE_BASE 16   // sprites 16-19: target outlines
#define BABY_SPRITE_BASE   20   // sprites 20+: baby metasprite
#define OUTLINE_TILE_BASE   4   // tiles 4-7: outline arrows
#define BABY_TILE_BASE      8   // tiles 8+: crawl1 tiles
#define CRAWL2_TILE_BASE    28  // tiles 28+: crawl2 tiles (8 + 20)
#define BABY_PAL_BASE       4   // palettes 4-6: baby colors
#define CRAWL_ANIM_PERIOD   15  // frames per crawl pose (~4 fps)

static const uint8_t arrow_x[4] = { 24, 88, 56, 120 };

// --- Data Structures ---

typedef struct {
    uint8_t  active;
    uint8_t  direction;
    uint8_t  sprite_id;
    uint16_t y_pos;       // 8.8 fixed-point
} arrow_t;

// --- Sprite Tile Data (8x8, 2bpp = 16 bytes each) ---
// Bold filled arrows — wide arrowhead end = direction of travel
//
// Left ←:              Right →:
//   ......X.              .X......
//   ....XXX.              .XXX....
//   ..XXXXX.              .XXXXX..
//   XXXXXXX.              .XXXXXXX
//   XXXXXXX.              .XXXXXXX
//   ..XXXXX.              .XXXXX..
//   ....XXX.              .XXX....
//   ......X.              .X......
//
// Up ▲:                Down ▼:
//   ...XX...              XXXXXXXX
//   ...XX...              XXXXXXXX
//   ..XXXX..              .XXXXXX.
//   ..XXXX..              .XXXXXX.
//   .XXXXXX.              ..XXXX..
//   .XXXXXX.              ..XXXX..
//   XXXXXXXX              ...XX...
//   XXXXXXXX              ...XX...

static const unsigned char tile_left[] = {
    0x02,0x02, 0x0E,0x0E, 0x3E,0x3E, 0xFE,0xFE,
    0xFE,0xFE, 0x3E,0x3E, 0x0E,0x0E, 0x02,0x02
};

static const unsigned char tile_up[] = {
    0x18,0x18, 0x18,0x18, 0x3C,0x3C, 0x3C,0x3C,
    0x7E,0x7E, 0x7E,0x7E, 0xFF,0xFF, 0xFF,0xFF
};

static const unsigned char tile_down[] = {
    0xFF,0xFF, 0xFF,0xFF, 0x7E,0x7E, 0x7E,0x7E,
    0x3C,0x3C, 0x3C,0x3C, 0x18,0x18, 0x18,0x18
};

static const unsigned char tile_right[] = {
    0x40,0x40, 0x70,0x70, 0x7C,0x7C, 0x7F,0x7F,
    0x7F,0x7F, 0x7C,0x7C, 0x70,0x70, 0x40,0x40
};

// Hollow outlines for target zone
static const unsigned char outline_left[] = {
    0x02,0x02, 0x0E,0x0E, 0x32,0x32, 0xC2,0xC2,
    0xC2,0xC2, 0x32,0x32, 0x0E,0x0E, 0x02,0x02
};

static const unsigned char outline_up[] = {
    0x18,0x18, 0x18,0x18, 0x24,0x24, 0x24,0x24,
    0x42,0x42, 0x42,0x42, 0x81,0x81, 0xFF,0xFF
};

static const unsigned char outline_down[] = {
    0xFF,0xFF, 0x81,0x81, 0x42,0x42, 0x42,0x42,
    0x24,0x24, 0x24,0x24, 0x18,0x18, 0x18,0x18
};

static const unsigned char outline_right[] = {
    0x40,0x40, 0x70,0x70, 0x4C,0x4C, 0x43,0x43,
    0x43,0x43, 0x4C,0x4C, 0x70,0x70, 0x40,0x40
};

// --- State ---

static arrow_t arrows[MAX_ARROWS];
static uint16_t frame_count;
static uint16_t next_step;
static uint16_t score;
static uint16_t displayed_score;
static uint8_t  combo;
static uint8_t  max_combo;
static uint8_t  feedback_timer;
static uint8_t  shake_timer;
static uint8_t  prev_crawl_frame;
static uint8_t  prev_keys;
static uint16_t total_perfect;
static uint16_t total_good;
static uint16_t total_miss;
static uint16_t music_next_step;
static uint8_t  last_pulse1;
static uint8_t  last_pulse2;
static uint8_t  last_wave;

// --- Helpers ---

static void ch1_wait_release(void) {
    while (joypad()) vsync();
}

static void ch1_wait_frames(uint8_t n) {
    for (uint8_t i = 0; i < n; i++) vsync();
}

static void hide_all_sprites(void) {
    for (uint8_t i = 0; i < 40; i++) {
        move_sprite(i, 0, 0);
    }
}

// --- Sound ---

// Pulse frequency register values for MIDI notes 48-88 (C3 to E6)
// Formula: 2048 - round(131072 / freq_hz)
static const uint16_t pulse_freq[41] = {
    1046,    0, 1155,    0, 1253, 1297,    0, 1379,    0, 1452,  /* C3..A3  (48-57) */
       0,    0,    0,    0, 1602,    0, 1650, 1673,    0, 1714,  /* ..D4..G4 (58-67) */
       0, 1750,    0, 1783, 1798,    0, 1825,    0, 1849, 1860,  /* ..A4..F5 (68-77) */
       0, 1881,    0, 1899,    0, 1915, 1923,    0, 1936,    0,  /* ..G5..D6 (78-87) */
    1949                                                          /* E6      (88) */
};

// Noise channel: NR43 polynomial counter settings per drum type
static const uint8_t noise_poly[4] = {
    0x10,  // 0: hi-hat  (fast, crisp)
    0x77,  // 1: kick    (slow, deep)
    0x44,  // 2: tom     (mid frequency)
    0x2C,  // 3: snare   (metallic, 7-bit width)
};

// Noise channel: NR42 envelope per drum type
static const uint8_t noise_env[4] = {
    0x81,  // 0: hi-hat  (vol=8,  short decay)
    0xF2,  // 1: kick    (vol=15, longer decay)
    0xA1,  // 2: tom     (vol=10, short decay)
    0xC1,  // 3: snare   (vol=12, short decay)
};

static void ch1_init_sound(void) {
    NR52_REG = 0x80;  // Master sound on
    NR50_REG = 0x77;  // Max volume both speakers
    NR51_REG = 0xFF;  // All channels to both speakers

    // Load triangle wave pattern into wave RAM
    NR30_REG = 0x00;  // Wave DAC off while loading
    {
        static const uint8_t triangle[16] = {
            0x01, 0x23, 0x45, 0x67, 0x89, 0xAB, 0xCD, 0xEF,
            0xFE, 0xDC, 0xBA, 0x98, 0x76, 0x54, 0x32, 0x10
        };
        volatile uint8_t *wram = (volatile uint8_t *)0xFF30u;
        for (uint8_t i = 0; i < 16; i++) {
            wram[i] = triangle[i];
        }
    }
    NR30_REG = 0x80;  // Wave DAC on

    music_next_step = 0;
    last_pulse1 = NOTE_REST;
    last_pulse2 = NOTE_REST;
    last_wave = NOTE_REST;
}

static void ch1_update_music(void) {
    uint16_t target_step = (frame_count * 2u) / 15u;
    if (target_step >= LEVEL_STEPS) target_step = LEVEL_STEPS - 1;

    while (music_next_step <= target_step) {
        uint16_t s = music_next_step;

        // Pulse 1 (melody, 50% duty)
        {
            uint8_t note = pulse1_data[s];
            if (note != NOTE_REST && note != last_pulse1) {
                uint16_t freq = pulse_freq[note - 48];
                if (freq) {
                    NR10_REG = 0x00;
                    NR11_REG = 0x80;
                    NR12_REG = 0xF3;
                    NR13_REG = (uint8_t)(freq & 0xFFu);
                    NR14_REG = (uint8_t)(0x80u | ((freq >> 8) & 0x07u));
                }
            }
            last_pulse1 = note;
        }

        // Pulse 2 (harmony, 25% duty)
        {
            uint8_t note = pulse2_data[s];
            if (note != NOTE_REST && note != last_pulse2) {
                uint16_t freq = pulse_freq[note - 48];
                if (freq) {
                    NR21_REG = 0x40;
                    NR22_REG = 0xC3;
                    NR23_REG = (uint8_t)(freq & 0xFFu);
                    NR24_REG = (uint8_t)(0x80u | ((freq >> 8) & 0x07u));
                }
            }
            last_pulse2 = note;
        }

        // Wave (bass)
        {
            uint8_t note = wave_data[s];
            if (note != NOTE_REST && note != last_wave) {
                uint16_t pf = pulse_freq[note - 48];
                if (pf) {
                    uint16_t wf = 2048u - (2048u - pf) / 2u;
                    NR30_REG = 0x80;
                    NR31_REG = 0x00;
                    NR32_REG = 0x20;
                    NR33_REG = (uint8_t)(wf & 0xFFu);
                    NR34_REG = (uint8_t)(0x80u | ((wf >> 8) & 0x07u));
                }
            }
            last_wave = note;
        }

        // Noise (drums)
        {
            uint8_t n = noise_data[s];
            if (n != NOTE_REST) {
                uint8_t idx = n & 0x03;
                NR41_REG = 0x00;
                NR42_REG = noise_env[idx];
                NR43_REG = noise_poly[idx];
                NR44_REG = 0x80;
            }
        }

        music_next_step++;
    }
}

static void ch1_stop_sound(void) {
    NR52_REG = 0x00;  // Master sound off (resets all channels)
}

// --- Scene Background + Sprites ---

static void load_scene_bg(void) {
    // Load map attributes into VRAM bank 1
    VBK_REG = 1;
    set_bkg_tiles(0, 0, 20, 18, ch1_bg_data_map_attributes);

    // Load tiles + map into VRAM bank 0
    VBK_REG = 0;
    set_bkg_data(0, ch1_bg_data_TILE_COUNT, ch1_bg_data_tiles);
    set_bkg_tiles(0, 0, 20, 18, ch1_bg_data_map);

    set_bkg_palette(0, ch1_bg_data_PALETTE_COUNT, ch1_bg_data_palettes);
    move_bkg(0, 0);
}

static void show_intro_image(void) {
    DISPLAY_OFF;
    SPRITES_8x8;

    load_scene_bg();

    // Load baby_sitting sprite tiles at slot 0
    set_sprite_data(0, ch1_baby_sitting_TILE_COUNT, ch1_baby_sitting_tiles);
    set_sprite_palette(0, ch1_baby_sitting_PALETTE_COUNT, ch1_baby_sitting_palettes);

    // Load object tiles after baby tiles
    uint8_t obj_base = ch1_baby_sitting_TILE_COUNT;
    uint8_t obj_pal = ch1_baby_sitting_PALETTE_COUNT;
    set_sprite_data(obj_base, ch1_obj_calc_TILE_COUNT, ch1_obj_calc_tiles);
    set_sprite_palette(obj_pal, ch1_obj_calc_PALETTE_COUNT, ch1_obj_calc_palettes);
    set_sprite_data(obj_base + ch1_obj_calc_TILE_COUNT, ch1_obj_book_TILE_COUNT, ch1_obj_book_tiles);
    set_sprite_palette(obj_pal + 1, ch1_obj_book_PALETTE_COUNT, ch1_obj_book_palettes);
    set_sprite_data(obj_base + ch1_obj_calc_TILE_COUNT + ch1_obj_book_TILE_COUNT,
                    ch1_obj_ball_TILE_COUNT, ch1_obj_ball_tiles);
    set_sprite_palette(obj_pal + 2, ch1_obj_ball_PALETTE_COUNT, ch1_obj_ball_palettes);

    hide_all_sprites();

    // Position baby (center-left of screen)
    // move_metasprite_ex(metasprite, base_tile, base_prop, base_sprite, x, y)
    move_metasprite_ex(ch1_baby_sitting_metasprites[0], 0, 0, 0, 56, 116);

    // Position objects (right side, spaced out on floor)
    uint8_t spr_id = 20;  // start after baby sprites
    move_metasprite_ex(ch1_obj_calc_metasprites[0], obj_base,
                       obj_pal, spr_id, 100, 128);
    spr_id += 4;
    move_metasprite_ex(ch1_obj_book_metasprites[0], obj_base + ch1_obj_calc_TILE_COUNT,
                       (uint8_t)(obj_pal + 1), spr_id, 120, 128);
    spr_id += 4;
    move_metasprite_ex(ch1_obj_ball_metasprites[0],
                       obj_base + ch1_obj_calc_TILE_COUNT + ch1_obj_book_TILE_COUNT,
                       (uint8_t)(obj_pal + 2), spr_id, 140, 128);

    SHOW_BKG;
    SHOW_SPRITES;
    DISPLAY_ON;

    // Wait for button
    while (joypad()) vsync();
    while (!(joypad() & (J_A | J_START))) vsync();
    while (joypad()) vsync();
}

static void show_ending_image(void) {
    DISPLAY_OFF;
    SPRITES_8x8;

    load_scene_bg();

    // Load baby_calc sprite
    set_sprite_data(0, ch1_baby_calc_TILE_COUNT, ch1_baby_calc_tiles);
    set_sprite_palette(0, ch1_baby_calc_PALETTE_COUNT, ch1_baby_calc_palettes);

    hide_all_sprites();

    // Position baby with calculator (center of screen)
    move_metasprite_ex(ch1_baby_calc_metasprites[0], 0, 0, 0, 80, 116);

    SHOW_BKG;
    SHOW_SPRITES;
    DISPLAY_ON;
}

// --- Story Intro (text pages) ---

static const scene_line_t intro_p1[] = {
    { 3, 4, "This is Nick." },
    { 1, 7, "Born in the quiet" },
    { 1, 8, "town of Kunming," },
    { 1, 9, "China." },
};

static const scene_line_t intro_p2[] = {
    { 0, 3, "A long life awaits," },
    { 0, 4, "but first..." },
    { 0, 6, "a tradition." },
    { 0, 8, "Lay objects before" },
    { 0, 9, "the baby." },
    { 0, 11, "What he picks will" },
    { 0, 12, "reveal his future." },
};

static const scene_line_t intro_p3[] = {
    { 3, 6, "Help baby Nick" },
    { 3, 8, "take his first" },
    { 3, 9, "steps!" },
};

static const scene_page_t intro_text[] = {
    { intro_p1, 4, SCENE_WAIT_BUTTON, 0 },
    { intro_p2, 7, SCENE_WAIT_BUTTON, 0 },
    { intro_p3, 3, SCENE_WAIT_BUTTON, 0 },
};

// --- Object Cutscene (text pages) ---

static const scene_line_t obj_p1[] = {
    { 2, 7, "Nick reaches the" },
    { 2, 8, "pile of objects..." },
};

static const scene_line_t obj_p2[] = {
    { 1, 6, "A ball... a book..." },
    { 1, 8, "a paintbrush..." },
};

static const scene_line_t obj_p3[] = {
    { 3, 7, "He reaches out" },
    { 3, 8, "and grabs..." },
};

static const scene_line_t obj_p4[] = {
    { 1, 8, "...the calculator!" },
};

static const scene_line_t obj_p5[] = {
    { 3, 6, "His future is" },
    { 3, 7, "already taking" },
    { 3, 8, "shape." },
};

static const scene_page_t object_text[] = {
    { obj_p1, 2, SCENE_WAIT_TIMED, 180 },
    { obj_p2, 2, SCENE_WAIT_TIMED, 180 },
    { obj_p3, 2, SCENE_WAIT_TIMED, 150 },
    { obj_p4, 1, SCENE_WAIT_TIMED, 180 },
    { obj_p5, 3, SCENE_WAIT_BUTTON, 0 },
};

// --- Init ---

static void ch1_init_display(void) {
    DISPLAY_OFF;
    SPRITES_8x8;

    // Load font FIRST (tiles at 0+), before setting up background
    font_init();
    font_load(font_ibm);

    // Load gameplay background: tiles at 128+, map, attributes, palettes
    // Background tilemap set AFTER font_init to avoid being cleared
    set_bkg_data(ch1_gameplay_bg_data_TILE_ORIGIN,
                 ch1_gameplay_bg_data_TILE_COUNT, ch1_gameplay_bg_data_tiles);
    VBK_REG = 1;
    set_bkg_tiles(0, 0, 20, 18, ch1_gameplay_bg_data_map_attributes);
    VBK_REG = 0;
    set_bkg_tiles(0, 0, 20, 18, ch1_gameplay_bg_data_map);
    set_bkg_palette(0, ch1_gameplay_bg_data_PALETTE_COUNT, ch1_gameplay_bg_data_palettes);

    // Load sprite tiles: 0-3 solid arrows, 4-7 outline arrows
    set_sprite_data(0, 1, tile_left);
    set_sprite_data(1, 1, tile_up);
    set_sprite_data(2, 1, tile_down);
    set_sprite_data(3, 1, tile_right);
    set_sprite_data(OUTLINE_TILE_BASE, 1, outline_left);
    set_sprite_data(OUTLINE_TILE_BASE + 1, 1, outline_up);
    set_sprite_data(OUTLINE_TILE_BASE + 2, 1, outline_down);
    set_sprite_data(OUTLINE_TILE_BASE + 3, 1, outline_right);

    // Load both crawling frame tiles for animation
    set_sprite_data(BABY_TILE_BASE, ch1_baby_crawl1_TILE_COUNT, ch1_baby_crawl1_tiles);
    set_sprite_data(CRAWL2_TILE_BASE, ch1_baby_crawl2_TILE_COUNT, ch1_baby_crawl2_tiles);

    // CGB sprite palettes: 0-3 arrow colors, 4-6 baby colors
    palette_color_t pal_red[4] = {
        RGB8(0,0,0), RGB8(200,0,0), RGB8(255,50,50), RGB8(255,150,150)
    };
    palette_color_t pal_green[4] = {
        RGB8(0,0,0), RGB8(0,180,0), RGB8(50,255,50), RGB8(150,255,150)
    };
    palette_color_t pal_blue[4] = {
        RGB8(0,0,0), RGB8(0,0,200), RGB8(50,50,255), RGB8(150,150,255)
    };
    palette_color_t pal_yellow[4] = {
        RGB8(0,0,0), RGB8(200,200,0), RGB8(255,255,50), RGB8(255,255,150)
    };
    set_sprite_palette(0, 1, pal_red);
    set_sprite_palette(1, 1, pal_green);
    set_sprite_palette(2, 1, pal_blue);
    set_sprite_palette(3, 1, pal_yellow);
    set_sprite_palette(BABY_PAL_BASE, ch1_baby_crawl1_PALETTE_COUNT, ch1_baby_crawl1_palettes);

    hide_all_sprites();

    // Init arrow pool
    for (uint8_t i = 0; i < MAX_ARROWS; i++) {
        arrows[i].active = 0;
        arrows[i].sprite_id = i;
    }

    // Init state
    frame_count = 0;
    next_step = 0;
    score = 0;
    displayed_score = 0xFFFFu;  // force initial draw
    combo = 0;
    max_combo = 0;
    feedback_timer = 0;
    shake_timer = 0;
    prev_crawl_frame = 0xFF;  // force initial draw
    prev_keys = 0xFF;  // suppress ghost presses from menu
    total_perfect = 0;
    total_good = 0;
    total_miss = 0;

    // Init sound
    ch1_init_sound();

    // Draw HUD
    gotoxy(0, 0);
    printf("SCORE:00000");

    // Target zone: hollow arrow outlines as sprites (matching colors)
    for (uint8_t d = 0; d < 4; d++) {
        uint8_t sid = TARGET_SPRITE_BASE + d;
        set_sprite_tile(sid, OUTLINE_TILE_BASE + d);
        set_sprite_prop(sid, d);  // palette matches direction
        move_sprite(sid, (uint8_t)(arrow_x[d] + 8u), (uint8_t)(TARGET_Y + 16u));
    }

    // Baby metasprite — starts at left edge, crawls right during game
    move_metasprite_ex(ch1_baby_crawl1_metasprites[0], BABY_TILE_BASE,
                       BABY_PAL_BASE, BABY_SPRITE_BASE,
                       (uint8_t)(12 + 8), (uint8_t)(136 + 16));

    move_bkg(0, 0);
    SHOW_BKG;
    SHOW_SPRITES;
    DISPLAY_ON;
}

// --- Background Restore ---

static void restore_bg_rect(uint8_t x, uint8_t y, uint8_t w, uint8_t h) {
    for (uint8_t r = 0; r < h; r++) {
        uint16_t off = (uint16_t)(y + r) * 20u + x;
        VBK_REG = 1;
        set_bkg_tiles(x, y + r, w, 1, &ch1_gameplay_bg_data_map_attributes[off]);
        VBK_REG = 0;
        set_bkg_tiles(x, y + r, w, 1, &ch1_gameplay_bg_data_map[off]);
    }
}

// --- Countdown ---

static void ch1_countdown(void) {
    gotoxy(8, 9);
    printf("  3  ");
    ch1_wait_frames(60);

    gotoxy(8, 9);
    printf("  2  ");
    ch1_wait_frames(60);

    gotoxy(8, 9);
    printf("  1  ");
    ch1_wait_frames(60);

    gotoxy(8, 9);
    printf(" GO! ");
    ch1_wait_frames(30);

    restore_bg_rect(8, 9, 5, 1);
}

// --- Arrow Management ---

static void spawn_arrow(uint8_t direction) {
    for (uint8_t i = 0; i < MAX_ARROWS; i++) {
        if (!arrows[i].active) {
            arrows[i].active = 1;
            arrows[i].direction = direction;
            arrows[i].y_pos = (uint16_t)SPAWN_Y << 8;
            set_sprite_tile(i, direction);
            set_sprite_prop(i, direction);  // CGB palette = direction
            move_sprite(i, (uint8_t)(arrow_x[direction] + 8u), (uint8_t)(SPAWN_Y + 16u));
            return;
        }
    }
}

static void show_feedback(const char *text) {
    gotoxy(6, 5);
    printf("%s", text);
    feedback_timer = FEEDBACK_DURATION;
}

static void update_score_display(void) {
    if (score != displayed_score) {
        displayed_score = score;
        // Manual zero-padded 5-digit score
        gotoxy(6, 0);
        printf("%u", (unsigned int)(score / 10000));
        printf("%u", (unsigned int)((score / 1000) % 10));
        printf("%u", (unsigned int)((score / 100) % 10));
        printf("%u", (unsigned int)((score / 10) % 10));
        printf("%u", (unsigned int)(score % 10));
    }
}

// --- Game Loop ---

static void ch1_game_loop(void) {
    while (1) {
        // 1. Spawn arrows from level data (step-based timing)
        // 120 BPM, 8 steps/sec = 7.5 frames/step
        // due_step = which step should have been spawned by now (with travel lead time)
        {
            uint16_t due_step = ((frame_count + TRAVEL_FRAMES) * 2u) / 15u;
            if (due_step >= LEVEL_STEPS) due_step = LEVEL_STEPS - 1;
            while (next_step <= due_step) {
                uint8_t bits = chart_combined[next_step];
                if (bits & 0x01) spawn_arrow(DIR_LEFT);
                if (bits & 0x02) spawn_arrow(DIR_DOWN);
                if (bits & 0x04) spawn_arrow(DIR_UP);
                if (bits & 0x08) spawn_arrow(DIR_RIGHT);
                next_step++;
            }
        }

        // 1b. Update music
        ch1_update_music();

        // 2. Read input (edge-detect)
        uint8_t keys = joypad();
        uint8_t pressed = keys & ~prev_keys;
        prev_keys = keys;

        // 3. Check hits for each direction
        uint8_t dir_buttons[4];
        dir_buttons[DIR_LEFT]  = pressed & J_LEFT;
        dir_buttons[DIR_UP]    = pressed & J_UP;
        dir_buttons[DIR_DOWN]  = pressed & J_DOWN;
        dir_buttons[DIR_RIGHT] = pressed & J_RIGHT;

        for (uint8_t d = 0; d < 4; d++) {
            if (!dir_buttons[d]) continue;

            // Find closest active arrow in this column
            int8_t best = -1;
            uint8_t best_dist = 255;

            for (uint8_t i = 0; i < MAX_ARROWS; i++) {
                if (!arrows[i].active || arrows[i].direction != d) continue;
                uint8_t ay = (uint8_t)(arrows[i].y_pos >> 8);
                uint8_t dist;
                if (ay >= TARGET_Y)
                    dist = ay - TARGET_Y;
                else
                    dist = TARGET_Y - ay;
                if (dist < best_dist) {
                    best_dist = dist;
                    best = (int8_t)i;
                }
            }

            if (best >= 0) {
                if (best_dist <= PERFECT_WINDOW) {
                    score += PERFECT_SCORE;
                    combo++;
                    total_perfect++;
                    show_feedback("PERFECT!");
                } else if (best_dist <= GOOD_WINDOW) {
                    score += GOOD_SCORE;
                    combo++;
                    total_good++;
                    show_feedback(" GOOD!  ");
                } else {
                    continue;  // too far away, ignore
                }
                if (combo > max_combo) max_combo = combo;
                arrows[best].active = 0;
                move_sprite(arrows[best].sprite_id, 0, 0);
            }
        }

        // 4. Move arrows upward, detect misses
        uint8_t active_count = 0;
        for (uint8_t i = 0; i < MAX_ARROWS; i++) {
            if (!arrows[i].active) continue;

            // Prevent underflow
            if (arrows[i].y_pos < SCROLL_SPEED) {
                arrows[i].active = 0;
                move_sprite(i, 0, 0);
                total_miss++;
                combo = 0;
                show_feedback("  MISS  "); shake_timer = 6;
                continue;
            }

            arrows[i].y_pos -= SCROLL_SPEED;
            uint8_t py = (uint8_t)(arrows[i].y_pos >> 8);

            // Past the hit window = miss
            if (py < (TARGET_Y - GOOD_WINDOW - 2)) {
                arrows[i].active = 0;
                move_sprite(i, 0, 0);
                total_miss++;
                combo = 0;
                show_feedback("  MISS  "); shake_timer = 6;
                continue;
            }

            move_sprite(i, arrow_x[arrows[i].direction] + 8, py + 16);
            active_count++;
        }

        // 5. Feedback timer
        if (feedback_timer > 0) {
            feedback_timer--;
            if (feedback_timer == 0) {
                restore_bg_rect(6, 5, 8, 1);
            }
        }

        // 5b. Screen shake on miss
        if (shake_timer > 0) {
            shake_timer--;
            if (shake_timer > 0) {
                int8_t sx = (shake_timer & 1) ? 2 : -2;
                move_bkg((uint8_t)sx, 0);
            } else {
                move_bkg(0, 0);
            }
        }

        // 6. Score display
        update_score_display();

        // 7. Move baby left to right based on progress, alternate crawl frames
        // ~3780 total frames (504 steps * 7.5 frames/step)
        {
            uint8_t progress = (uint8_t)(frame_count / 28u);
            if (progress > 136) progress = 136;
            uint8_t bx = (uint8_t)(12 + progress + 8);
            uint8_t by = (uint8_t)(136 + 16);
            uint8_t crawl_frame = (frame_count / CRAWL_ANIM_PERIOD) & 1;

            // On frame change: hide old sprites and swap palettes
            if (crawl_frame != prev_crawl_frame) {
                for (uint8_t s = BABY_SPRITE_BASE; s < 40; s++) {
                    move_sprite(s, 0, 0);
                }
                if (crawl_frame == 0) {
                    set_sprite_palette(BABY_PAL_BASE, ch1_baby_crawl1_PALETTE_COUNT, ch1_baby_crawl1_palettes);
                } else {
                    set_sprite_palette(BABY_PAL_BASE, ch1_baby_crawl2_PALETTE_COUNT, ch1_baby_crawl2_palettes);
                }
                prev_crawl_frame = crawl_frame;
            }

            if (crawl_frame == 0) {
                move_metasprite_ex(ch1_baby_crawl1_metasprites[0], BABY_TILE_BASE,
                                   BABY_PAL_BASE, BABY_SPRITE_BASE, bx, by);
            } else {
                move_metasprite_ex(ch1_baby_crawl2_metasprites[0], CRAWL2_TILE_BASE,
                                   BABY_PAL_BASE, BABY_SPRITE_BASE, bx, by);
            }
        }

        // 8. End condition — wait for arrows AND music to finish
        if (next_step >= LEVEL_STEPS && active_count == 0 &&
            music_next_step >= LEVEL_STEPS) {
            return;
        }

        frame_count++;
        vsync();
    }
}

// --- Object Cutscene ---

static void ch1_object_scene(void) {
    ch1_stop_sound();
    hide_all_sprites();
    // Text narration first, then reveal the scene image
    scene_play(object_text, 5);
    show_ending_image();
    // Wait for button to dismiss
    while (joypad()) vsync();
    while (!(joypad() & (J_A | J_START))) vsync();
    while (joypad()) vsync();
}

// --- Cleanup ---

static void ch1_cleanup(void) {
    hide_all_sprites();
    HIDE_SPRITES;
}

// --- Public Entry Point ---

void play_chapter1(void) {
    show_intro_image();
    scene_play(intro_text, 3);
    ch1_init_display();
    ch1_countdown();
    ch1_game_loop();
    ch1_object_scene();
    ch1_cleanup();
}
