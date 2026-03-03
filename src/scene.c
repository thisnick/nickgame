#include <gb/gb.h>
#include <gb/cgb.h>
#include <gbdk/font.h>
#include <gbdk/console.h>
#include <stdint.h>
#include <stdio.h>

#include "scene.h"

static uint8_t last_was_image;

void scene_init(void) {
    DISPLAY_OFF;
    VBK_REG = VBK_ATTRIBUTES;
    init_bkg(0);
    VBK_REG = VBK_TILES;
    font_init();
    font_load(font_ibm);
    init_bkg(0);
    palette_color_t text_pal[4] = {
        RGB8(255, 255, 255),
        RGB8(170, 170, 170),
        RGB8(85, 85, 85),
        RGB8(0, 0, 0)
    };
    set_bkg_palette(0, 1, text_pal);
    move_bkg(0, 0);
    SHOW_BKG;
    HIDE_SPRITES;
    DISPLAY_ON;
    last_was_image = 0;
}

void scene_clear(void) {
    for (uint8_t y = 0; y < 18; y++) {
        gotoxy(0, y);
        printf("                    ");
    }
}

static void show_image_page(const scene_image_t *img) {
    DISPLAY_OFF;

    // Load CGB tile attributes
    VBK_REG = VBK_ATTRIBUTES;
    if (img->map_attr) {
        set_bkg_tiles(0, 0, 20, 18, img->map_attr);
    } else {
        init_bkg(0);
    }
    VBK_REG = VBK_TILES;

    // Load tiles and map
    set_bkg_data(0, img->tile_count, img->tiles);
    if (img->map) {
        set_bkg_tiles(0, 0, 20, 18, img->map);
    } else {
        init_bkg(0);
    }

    set_bkg_palette(0, img->pal_count, img->palettes);
    move_bkg(0, 0);
    SHOW_BKG;
    HIDE_SPRITES;
    DISPLAY_ON;
}

void scene_play(const scene_page_t *pages, uint8_t num_pages) {
    scene_init();

    for (uint8_t p = 0; p < num_pages; p++) {
        if (pages[p].image) {
            // Image page
            show_image_page(pages[p].image);
            last_was_image = 1;
        } else {
            // Text page — reinit text mode if previous page was an image
            if (last_was_image) {
                scene_init();
            }
            scene_clear();
            for (uint8_t i = 0; i < pages[p].num_lines; i++) {
                gotoxy(pages[p].lines[i].x, pages[p].lines[i].y);
                printf("%s", pages[p].lines[i].text);
            }
            last_was_image = 0;
        }

        if (pages[p].wait_mode == SCENE_WAIT_BUTTON) {
            // Only show text prompt on text pages
            if (!pages[p].image) {
                gotoxy(5, 16);
                printf("- A to go -");
            }
            while (joypad()) vsync();
            while (!(joypad() & (J_A | J_START))) vsync();
            while (joypad()) vsync();
        } else {
            for (uint8_t f = 0; f < pages[p].delay_frames; f++) {
                vsync();
            }
        }
    }
}
