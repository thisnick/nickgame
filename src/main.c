#include <gb/gb.h>
#include <gb/cgb.h>
#include <gbdk/font.h>
#include <gbdk/console.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "title_data.h"

#define NUM_CHAPTERS 9

static const char *chapter_names[NUM_CHAPTERS] = {
    "Birth",
    "Road to School",
    "Cross the Ocean",
    "Love Story",
    "The Code Path",
    "Golden Gate",
    "New Life",
    "The Leap",
    "Legacy"
};

// --- Utility ---

static void wait_release(void) {
    while (joypad()) vsync();
}

static void wait_frames(uint8_t n) {
    for (uint8_t i = 0; i < n; i++) vsync();
}

// --- Title Screen ---

static void fade_palettes(uint8_t step) {
    palette_color_t buf[32];
    for (uint8_t i = 0; i < 32; i++) {
        uint16_t c = title_data_palettes[i];
        uint8_t r = (uint8_t)(c & 0x1Fu);
        uint8_t g = (uint8_t)((c >> 5) & 0x1Fu);
        uint8_t b = (uint8_t)((c >> 10) & 0x1Fu);
        r = (r * step) >> 3;
        g = (g * step) >> 3;
        b = (b * step) >> 3;
        buf[i] = (palette_color_t)(r | (g << 5) | (b << 10));
    }
    set_bkg_palette(0, 8, buf);
}

static void show_title_screen(void) {
    DISPLAY_OFF;

    // Set palettes to black initially
    palette_color_t black[32];
    memset(black, 0, sizeof(black));
    set_bkg_palette(0, 8, black);

    // Load tile data (VRAM bank 0)
    VBK_REG = VBK_TILES;
    set_bkg_data(0, title_data_TILE_COUNT, title_data_tiles);
    set_bkg_tiles(0, 0, 20, 18, title_data_map);

    // Load attribute map (VRAM bank 1)
    VBK_REG = VBK_ATTRIBUTES;
    set_bkg_tiles(0, 0, 20, 18, title_data_map_attributes);
    VBK_REG = VBK_TILES;

    move_bkg(0, 0);
    SHOW_BKG;
    DISPLAY_ON;

    // Fade in: steps 1-8
    for (uint8_t step = 1; step <= 8; step++) {
        fade_palettes(step);
        wait_frames(4);
    }

    // Wait for START
    wait_release();
    while (!(joypad() & J_START)) vsync();
    wait_release();

    // Fade out: steps 7 down to 0
    for (int8_t step = 7; step >= 0; step--) {
        fade_palettes((uint8_t)step);
        wait_frames(4);
    }
}

// --- Text mode setup (for chapter select / WIP) ---

static void setup_text_mode(void) {
    DISPLAY_OFF;

    // Clear attributes (VRAM bank 1) — all palette 0, no flip
    VBK_REG = VBK_ATTRIBUTES;
    init_bkg(0);
    VBK_REG = VBK_TILES;

    // Reload the font into VRAM
    font_init();
    font_load(font_ibm);

    // Clear the background tile map
    init_bkg(0);

    // Set palette 0 to simple grayscale for text
    palette_color_t text_pal[4] = {
        RGB8(255, 255, 255),   // color 0: white (background)
        RGB8(170, 170, 170),   // color 1: light gray
        RGB8(85, 85, 85),      // color 2: dark gray
        RGB8(0, 0, 0)          // color 3: black (text)
    };
    set_bkg_palette(0, 1, text_pal);

    move_bkg(0, 0);
    SHOW_BKG;
}

// --- Chapter Select ---

static void draw_chapter_list(uint8_t cursor) {
    gotoxy(3, 1);
    printf("SELECT CHAPTER");

    for (uint8_t i = 0; i < NUM_CHAPTERS; i++) {
        gotoxy(0, i + 3);
        if (i == cursor)
            printf("> ");
        else
            printf("  ");
        printf("%d.%s", i + 1, chapter_names[i]);
    }
}

static uint8_t show_chapter_select(void) {
    setup_text_mode();
    DISPLAY_ON;

    uint8_t cursor = 0;
    draw_chapter_list(cursor);

    wait_release();

    while (1) {
        uint8_t keys = joypad();

        if ((keys & J_UP) && cursor > 0) {
            cursor--;
            draw_chapter_list(cursor);
            wait_release();
        } else if ((keys & J_DOWN) && cursor < NUM_CHAPTERS - 1) {
            cursor++;
            draw_chapter_list(cursor);
            wait_release();
        } else if (keys & (J_A | J_START)) {
            wait_release();
            return cursor;
        }

        vsync();
    }
}

// --- WIP Screen ---

static void show_wip_screen(uint8_t chapter) {
    setup_text_mode();
    DISPLAY_ON;

    gotoxy(2, 4);
    printf("Chapter %d:", chapter + 1);
    gotoxy(2, 5);
    printf("%s", chapter_names[chapter]);

    gotoxy(2, 9);
    printf("WORK IN PROGRESS");

    gotoxy(2, 13);
    printf("Press any key...");

    // Wait for any button
    wait_release();
    while (!joypad()) vsync();
    wait_release();
}

// --- Main ---

void main(void) {
    while (1) {
        show_title_screen();
        uint8_t chapter = show_chapter_select();
        show_wip_screen(chapter);
    }
}
