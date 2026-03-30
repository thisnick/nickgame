#pragma bank 3

#include <gb/gb.h>
#include <gb/cgb.h>
#include <gbdk/font.h>
#include <gbdk/console.h>
#include <gbdk/metasprites.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "chapter3.h"
#include "scene.h"
#include "ch3_airport_data.h"
#include "ch3_city_data.h"
#include "ch3_campus_data.h"
#include "ch3_player_down1.h"
#include "ch3_player_down2.h"
#include "ch3_player_up1.h"
#include "ch3_player_up2.h"
#include "ch3_npc_helper.h"
#include "ch3_npc_student.h"

// --- Constants ---

#define DIR_DOWN  0
#define DIR_UP    1
#define DIR_LEFT  2
#define DIR_RIGHT 3

#define SPR_PLAYER   0   // sprites 0-3
#define SPR_NPC      4   // sprites 4-7

#define TILE_PLAYER_DOWN1  0
#define TILE_PLAYER_DOWN2  4
#define TILE_PLAYER_UP1    8
#define TILE_PLAYER_UP2    12
#define TILE_NPC           16

#define PAL_PLAYER   0
#define PAL_NPC      1

#define MOVE_SPEED   1
#define ANIM_PERIOD  12

// Screen bounds (8 pixels from each edge for walls, in OAM coords)
#define BOUND_LEFT   16
#define BOUND_RIGHT  152
#define BOUND_TOP    24
#define BOUND_BOTTOM 144

// Dialogue box constants
#define DLGBOX_Y     14   // tile row for dialogue box top
#define DLGBOX_H     4    // 4 rows tall

// --- State ---

static uint8_t px, py;       // player position (screen pixels)
static uint8_t direction;
static uint8_t anim_frame;
static uint16_t frame_count;
static uint8_t prev_keys;

// NPC data
static uint8_t npc_x, npc_y;
static uint8_t npc_active;

// --- Helpers ---

static void ch3_wait_release(void) {
    while (joypad()) vsync();
}

static void hide_all_sprites(void) {
    for (uint8_t i = 0; i < 40; i++) {
        move_sprite(i, 0, 0);
    }
}

static void load_bg(const unsigned char *tiles, uint8_t tile_count, uint8_t tile_origin,
                    const unsigned char *map, const unsigned char *map_attr,
                    const palette_color_t *palettes, uint8_t pal_count) {
    VBK_REG = VBK_ATTRIBUTES;
    set_bkg_tiles(0, 0, 20, 18, map_attr);
    VBK_REG = VBK_TILES;
    set_bkg_data(tile_origin, tile_count, tiles);
    set_bkg_tiles(0, 0, 20, 18, map);
    set_bkg_palette(0, pal_count, palettes);
    move_bkg(0, 0);
}

// --- Sprite drawing ---

static void draw_player(void) {
    uint8_t tile_base;
    const metasprite_t* const* ms;

    uint8_t walk_frame = (frame_count / ANIM_PERIOD) & 1;

    switch (direction) {
        case DIR_DOWN:
            if (walk_frame) {
                tile_base = TILE_PLAYER_DOWN2;
                ms = ch3_player_down2_metasprites;
            } else {
                tile_base = TILE_PLAYER_DOWN1;
                ms = ch3_player_down1_metasprites;
            }
            break;
        case DIR_UP:
            if (walk_frame) {
                tile_base = TILE_PLAYER_UP2;
                ms = ch3_player_up2_metasprites;
            } else {
                tile_base = TILE_PLAYER_UP1;
                ms = ch3_player_up1_metasprites;
            }
            break;
        case DIR_LEFT:
        default:
            // Use down sprites for left/right (simpler)
            if (walk_frame) {
                tile_base = TILE_PLAYER_DOWN2;
                ms = ch3_player_down2_metasprites;
            } else {
                tile_base = TILE_PLAYER_DOWN1;
                ms = ch3_player_down1_metasprites;
            }
            break;
    }

    // OAM coords: screen + 8 for x, + 16 for y
    move_metasprite_ex(ms[0], tile_base, PAL_PLAYER, SPR_PLAYER,
                       (uint8_t)(px + 8u), (uint8_t)(py + 16u));
}

static void draw_npc(void) {
    if (npc_active) {
        move_metasprite_ex(ch3_npc_helper_metasprites[0], TILE_NPC, PAL_NPC,
                           SPR_NPC, (uint8_t)(npc_x + 8u), (uint8_t)(npc_y + 16u));
    }
}

// --- Dialogue ---

static void draw_dialogue_box(void) {
    // Clear the bottom 4 rows for dialogue
    for (uint8_t y = DLGBOX_Y; y < DLGBOX_Y + DLGBOX_H; y++) {
        gotoxy(0, y);
        printf("                    ");
    }
    // Draw simple border
    gotoxy(0, DLGBOX_Y);
    printf("--------------------");
}

static void clear_dialogue_box(void) {
    for (uint8_t y = DLGBOX_Y; y < DLGBOX_Y + DLGBOX_H; y++) {
        gotoxy(0, y);
        printf("                    ");
    }
}

static void show_dialogue_line(const char *line, uint8_t row) {
    gotoxy(1, DLGBOX_Y + 1 + row);
    printf("%s", line);
}

static void show_dialogue(const char **lines, uint8_t num_lines) {
    draw_dialogue_box();
    uint8_t row = 0;
    for (uint8_t i = 0; i < num_lines; i++) {
        if (row >= 3) {
            // Wait for A to show more
            gotoxy(15, DLGBOX_Y + 3);
            printf("[A]");
            ch3_wait_release();
            while (!(joypad() & J_A)) vsync();
            ch3_wait_release();
            draw_dialogue_box();
            row = 0;
        }
        show_dialogue_line(lines[i], row);
        row++;
    }
    // Wait for A to dismiss
    gotoxy(15, DLGBOX_Y + 3);
    printf("[A]");
    ch3_wait_release();
    while (!(joypad() & J_A)) vsync();
    ch3_wait_release();
    clear_dialogue_box();
}

static uint8_t show_dialogue_choice(const char *prompt, const char *opt1, const char *opt2) {
    draw_dialogue_box();
    show_dialogue_line(prompt, 0);

    uint8_t cursor = 0;
    gotoxy(1, DLGBOX_Y + 2);
    printf("> %s", opt1);
    gotoxy(1, DLGBOX_Y + 3);
    printf("  %s", opt2);

    ch3_wait_release();

    while (1) {
        uint8_t keys = joypad();
        if ((keys & J_UP) && cursor == 1) {
            cursor = 0;
            gotoxy(1, DLGBOX_Y + 2);
            printf("> %s", opt1);
            gotoxy(1, DLGBOX_Y + 3);
            printf("  %s", opt2);
            ch3_wait_release();
        } else if ((keys & J_DOWN) && cursor == 0) {
            cursor = 1;
            gotoxy(1, DLGBOX_Y + 2);
            printf("  %s", opt1);
            gotoxy(1, DLGBOX_Y + 3);
            printf("> %s", opt2);
            ch3_wait_release();
        } else if (keys & J_A) {
            ch3_wait_release();
            clear_dialogue_box();
            return cursor;
        }
        vsync();
    }
}

// --- Proximity check ---

static uint8_t near_npc(void) {
    if (!npc_active) return 0;
    int16_t dx = (int16_t)px - (int16_t)npc_x;
    int16_t dy = (int16_t)py - (int16_t)npc_y;
    if (dx < 0) dx = -dx;
    if (dy < 0) dy = -dy;
    return (dx < 20 && dy < 20) ? 1 : 0;
}

static uint8_t at_exit(uint8_t exit_x, uint8_t exit_y) {
    int16_t dx = (int16_t)px - (int16_t)exit_x;
    int16_t dy = (int16_t)py - (int16_t)exit_y;
    if (dx < 0) dx = -dx;
    if (dy < 0) dy = -dy;
    return (dx < 12 && dy < 12) ? 1 : 0;
}

// --- Movement ---

static void move_player(void) {
    uint8_t keys = joypad();
    uint8_t pressed = keys & ~prev_keys;

    uint8_t new_x = px;
    uint8_t new_y = py;
    uint8_t moved = 0;

    if (keys & J_UP)    { if (new_y > BOUND_TOP)    { new_y -= MOVE_SPEED; moved = 1; direction = DIR_UP; } }
    if (keys & J_DOWN)  { if (new_y < BOUND_BOTTOM)  { new_y += MOVE_SPEED; moved = 1; direction = DIR_DOWN; } }
    if (keys & J_LEFT)  { if (new_x > BOUND_LEFT)    { new_x -= MOVE_SPEED; moved = 1; direction = DIR_LEFT; } }
    if (keys & J_RIGHT) { if (new_x < BOUND_RIGHT)   { new_x += MOVE_SPEED; moved = 1; direction = DIR_RIGHT; } }

    px = new_x;
    py = new_y;

    if (moved) frame_count++;

    prev_keys = keys;

    // Check A press for NPC interaction
    if (pressed & J_A) {
        // Will be handled by stage-specific logic
    }
}

// --- Stage 1: Airport ---

static void ch3_stage1_airport(void) {
    DISPLAY_OFF;
    SPRITES_8x16;

    // Load font first (tiles 0-127)
    font_init();
    font_load(font_ibm);

    // Load airport background (tiles at 128+)
    load_bg(ch3_airport_data_tiles, ch3_airport_data_TILE_COUNT,
            ch3_airport_data_TILE_ORIGIN,
            ch3_airport_data_map, ch3_airport_data_map_attributes,
            ch3_airport_data_palettes, ch3_airport_data_PALETTE_COUNT);

    // Load player sprite tiles
    set_sprite_data(TILE_PLAYER_DOWN1, ch3_player_down1_TILE_COUNT, ch3_player_down1_tiles);
    set_sprite_data(TILE_PLAYER_DOWN2, ch3_player_down2_TILE_COUNT, ch3_player_down2_tiles);
    set_sprite_data(TILE_PLAYER_UP1, ch3_player_up1_TILE_COUNT, ch3_player_up1_tiles);
    set_sprite_data(TILE_PLAYER_UP2, ch3_player_up2_TILE_COUNT, ch3_player_up2_tiles);
    set_sprite_data(TILE_NPC, ch3_npc_helper_TILE_COUNT, ch3_npc_helper_tiles);

    // Sprite palettes
    set_sprite_palette(PAL_PLAYER, 1, ch3_player_down1_palettes);
    set_sprite_palette(PAL_NPC, 1, ch3_npc_helper_palettes);

    hide_all_sprites();

    // Player starts at top-center
    px = 80;
    py = 32;
    direction = DIR_DOWN;
    anim_frame = 0;
    frame_count = 0;
    prev_keys = 0xFF;

    // NPC: airport helper in the middle area
    npc_x = 80;
    npc_y = 64;
    npc_active = 1;

    SHOW_BKG;
    SHOW_SPRITES;
    DISPLAY_ON;

    uint8_t talked_to_npc = 0;
    // Exit at bottom center: tile (9,16) = pixel (72, 128)
    uint8_t exit_x = 76;
    uint8_t exit_y = 128;

    while (1) {
        uint8_t keys = joypad();
        uint8_t pressed = keys & ~prev_keys;

        move_player();
        draw_player();
        draw_npc();

        // NPC interaction
        if ((pressed & J_A) && near_npc() && !talked_to_npc) {
            static const char *helper_lines[] = {
                "Welcome to Canada!",
                "The exit is down",
                "there. Follow the",
                "signs... oh wait.",
                "Just go south!",
            };
            show_dialogue(helper_lines, 5);
            talked_to_npc = 1;
        }

        // Exit trigger
        if (at_exit(exit_x, exit_y)) {
            // Fade out
            for (int8_t step = 7; step >= 0; step--) {
                palette_color_t buf[32];
                for (uint8_t i = 0; i < ch3_airport_data_PALETTE_COUNT * 4u; i++) {
                    uint16_t c = ch3_airport_data_palettes[i];
                    uint8_t r = (uint8_t)(c & 0x1Fu);
                    uint8_t g = (uint8_t)((c >> 5) & 0x1Fu);
                    uint8_t b = (uint8_t)((c >> 10) & 0x1Fu);
                    r = (r * (uint8_t)step) >> 3;
                    g = (g * (uint8_t)step) >> 3;
                    b = (b * (uint8_t)step) >> 3;
                    buf[i] = (palette_color_t)(r | (g << 5) | (b << 10));
                }
                set_bkg_palette(0, ch3_airport_data_PALETTE_COUNT, buf);
                for (uint8_t f = 0; f < 4; f++) vsync();
            }
            return;
        }

        prev_keys = keys;
        vsync();
    }
}

// --- Stage 2: City Street ---

static void ch3_stage2_city(void) {
    DISPLAY_OFF;

    font_init();
    font_load(font_ibm);

    load_bg(ch3_city_data_tiles, ch3_city_data_TILE_COUNT,
            ch3_city_data_TILE_ORIGIN,
            ch3_city_data_map, ch3_city_data_map_attributes,
            ch3_city_data_palettes, ch3_city_data_PALETTE_COUNT);

    // Reuse same sprite tiles (already loaded)
    set_sprite_palette(PAL_PLAYER, 1, ch3_player_down1_palettes);
    set_sprite_palette(PAL_NPC, 1, ch3_npc_helper_palettes);
    hide_all_sprites();

    // Player starts at top-left area (sidewalk)
    px = 40;
    py = 80;
    direction = DIR_DOWN;
    frame_count = 0;
    prev_keys = 0xFF;

    // No NPC in this stage, but bus stop is the goal
    npc_active = 0;

    SHOW_BKG;
    SHOW_SPRITES;
    DISPLAY_ON;

    uint8_t got_fare = 0;
    uint8_t at_bus = 0;
    uint8_t wait_timer = 0;

    // Shop door at roughly (24, 72)
    // Bus stop at roughly (128, 72)

    while (1) {
        uint8_t keys = joypad();
        uint8_t pressed = keys & ~prev_keys;

        move_player();
        draw_player();

        // Check if near shop (left area, tx=3, ty=9-10 area)
        if ((pressed & J_A) && !got_fare) {
            int16_t dx = (int16_t)px - 24;
            int16_t dy = (int16_t)py - 76;
            if (dx < 0) dx = -dx;
            if (dy < 0) dy = -dy;
            if (dx < 20 && dy < 20) {
                static const char *shop_lines[] = {
                    "A small shop...",
                    "You find some",
                    "coins for the bus!",
                };
                show_dialogue(shop_lines, 3);
                got_fare = 1;
            }
        }

        // Check if near bus stop
        if ((pressed & J_A) && got_fare && !at_bus) {
            int16_t dx = (int16_t)px - 128;
            int16_t dy = (int16_t)py - 64;
            if (dx < 0) dx = -dx;
            if (dy < 0) dy = -dy;
            if (dx < 20 && dy < 20) {
                static const char *bus_lines[] = {
                    "The bus is coming.",
                    "You board the #99.",
                    "Next stop: UBC.",
                };
                show_dialogue(bus_lines, 3);
                at_bus = 1;
            }
        }

        // Not got fare, remind if near bus stop
        if ((pressed & J_A) && !got_fare) {
            int16_t dx = (int16_t)px - 128;
            int16_t dy = (int16_t)py - 64;
            if (dx < 0) dx = -dx;
            if (dy < 0) dy = -dy;
            if (dx < 20 && dy < 20) {
                static const char *no_fare[] = {
                    "Need bus fare...",
                    "Try the shop.",
                };
                show_dialogue(no_fare, 2);
            }
        }

        if (at_bus) {
            wait_timer++;
            if (wait_timer > 60) {
                // Fade out
                for (int8_t step = 7; step >= 0; step--) {
                    palette_color_t buf[32];
                    for (uint8_t i = 0; i < ch3_city_data_PALETTE_COUNT * 4u; i++) {
                        uint16_t c = ch3_city_data_palettes[i];
                        uint8_t r = (uint8_t)(c & 0x1Fu);
                        uint8_t g = (uint8_t)((c >> 5) & 0x1Fu);
                        uint8_t b = (uint8_t)((c >> 10) & 0x1Fu);
                        r = (r * (uint8_t)step) >> 3;
                        g = (g * (uint8_t)step) >> 3;
                        b = (b * (uint8_t)step) >> 3;
                        buf[i] = (palette_color_t)(r | (g << 5) | (b << 10));
                    }
                    set_bkg_palette(0, ch3_city_data_PALETTE_COUNT, buf);
                    for (uint8_t f = 0; f < 4; f++) vsync();
                }
                return;
            }
        }

        prev_keys = keys;
        vsync();
    }
}

// --- Stage 3: UBC Campus ---

static void ch3_stage3_campus(void) {
    DISPLAY_OFF;

    font_init();
    font_load(font_ibm);

    load_bg(ch3_campus_data_tiles, ch3_campus_data_TILE_COUNT,
            ch3_campus_data_TILE_ORIGIN,
            ch3_campus_data_map, ch3_campus_data_map_attributes,
            ch3_campus_data_palettes, ch3_campus_data_PALETTE_COUNT);

    // Load student NPC sprite
    set_sprite_data(TILE_NPC, ch3_npc_student_TILE_COUNT, ch3_npc_student_tiles);
    set_sprite_palette(PAL_PLAYER, 1, ch3_player_down1_palettes);
    set_sprite_palette(PAL_NPC, 1, ch3_npc_student_palettes);
    hide_all_sprites();

    // Player starts at bottom
    px = 80;
    py = 120;
    direction = DIR_UP;
    frame_count = 0;
    prev_keys = 0xFF;

    // Student NPC inside student center area
    npc_x = 80;
    npc_y = 64;
    npc_active = 1;

    SHOW_BKG;
    SHOW_SPRITES;
    DISPLAY_ON;

    uint8_t talked = 0;

    while (1) {
        uint8_t keys = joypad();
        uint8_t pressed = keys & ~prev_keys;

        move_player();
        draw_player();
        draw_npc();

        if ((pressed & J_A) && near_npc() && !talked) {
            static const char *greet[] = {
                "Hey! Are you new?",
                "Welcome to UBC!",
            };
            show_dialogue(greet, 2);

            uint8_t choice = show_dialogue_choice(
                "Want to grab food?",
                "Sure, let's go!",
                "Maybe later..."
            );

            if (choice == 0) {
                static const char *yes_lines[] = {
                    "Awesome! I know a",
                    "great ramen place.",
                    "This place is",
                    "starting to feel",
                    "like home.",
                };
                show_dialogue(yes_lines, 5);
            } else {
                static const char *no_lines[] = {
                    "No worries! I'll",
                    "be around. This",
                    "place grows on you.",
                    "It already feels",
                    "a bit like home.",
                };
                show_dialogue(no_lines, 5);
            }
            talked = 1;
        }

        if (talked) {
            // Chapter complete — fade out
            for (int8_t step = 7; step >= 0; step--) {
                palette_color_t buf[32];
                for (uint8_t i = 0; i < ch3_campus_data_PALETTE_COUNT * 4u; i++) {
                    uint16_t c = ch3_campus_data_palettes[i];
                    uint8_t r = (uint8_t)(c & 0x1Fu);
                    uint8_t g = (uint8_t)((c >> 5) & 0x1Fu);
                    uint8_t b = (uint8_t)((c >> 10) & 0x1Fu);
                    r = (r * (uint8_t)step) >> 3;
                    g = (g * (uint8_t)step) >> 3;
                    b = (b * (uint8_t)step) >> 3;
                    buf[i] = (palette_color_t)(r | (g << 5) | (b << 10));
                }
                set_bkg_palette(0, ch3_campus_data_PALETTE_COUNT, buf);
                for (uint8_t f = 0; f < 4; f++) vsync();
            }
            return;
        }

        prev_keys = keys;
        vsync();
    }
}

// --- Cleanup ---

static void ch3_cleanup(void) {
    hide_all_sprites();
    HIDE_SPRITES;
}

// --- Intro/Outro Text ---

static const scene_line_t intro_p1[] = {
    { 1, 4, "A new chapter." },
    { 1, 6, "Nick boards a plane" },
    { 1, 7, "to Vancouver," },
    { 1, 8, "Canada." },
};

static const scene_line_t intro_p2[] = {
    { 1, 5, "Everything is new." },
    { 1, 7, "The signs are" },
    { 1, 8, "unreadable." },
    { 1, 10, "The air is cold." },
};

static const scene_line_t intro_p3[] = {
    { 2, 6, "Find your way." },
    { 2, 8, "Find your home." },
};

static const scene_page_t intro_text[] = {
    { intro_p1, 4, SCENE_WAIT_BUTTON, 0, NULL },
    { intro_p2, 4, SCENE_WAIT_BUTTON, 0, NULL },
    { intro_p3, 2, SCENE_WAIT_BUTTON, 0, NULL },
};

static const scene_line_t outro_p1[] = {
    { 1, 5, "Vancouver became" },
    { 1, 6, "home, one small" },
    { 1, 7, "step at a time." },
};

static const scene_line_t outro_p2[] = {
    { 1, 5, "The cold air felt" },
    { 1, 6, "a little warmer." },
    { 1, 8, "The signs started" },
    { 1, 9, "to make sense." },
};

static const scene_page_t outro_text[] = {
    { outro_p1, 3, SCENE_WAIT_BUTTON, 0, NULL },
    { outro_p2, 4, SCENE_WAIT_BUTTON, 0, NULL },
};

// --- Public Entry Point ---

BANKREF(chapter3)

void play_chapter3(void) BANKED {
    scene_play(intro_text, 3);
    ch3_stage1_airport();
    ch3_stage2_city();
    ch3_stage3_campus();
    scene_play(outro_text, 2);
    ch3_cleanup();
}
