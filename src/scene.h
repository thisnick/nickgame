#ifndef SCENE_H
#define SCENE_H

#include <gb/gb.h>
#include <gb/cgb.h>
#include <stdint.h>

#define SCENE_WAIT_BUTTON 0   // wait for A/START, shows prompt
#define SCENE_WAIT_TIMED  1   // auto-advance after delay_frames

// --- Text page data ---

typedef struct {
    uint8_t x;
    uint8_t y;
    const char *text;
} scene_line_t;

// --- Image page data ---

typedef struct {
    const unsigned char *tiles;
    const unsigned char *map;           // NULL = fill screen with tile 0
    const unsigned char *map_attr;      // CGB attributes (NULL = all palette 0)
    const palette_color_t *palettes;
    uint8_t tile_count;
    uint8_t pal_count;
} scene_image_t;

// --- Page (one screen in a scene) ---
// If image is non-NULL, it's an image page (lines/num_lines ignored).
// If image is NULL, it's a text page.

typedef struct {
    const scene_line_t *lines;
    uint8_t num_lines;
    uint8_t wait_mode;
    uint8_t delay_frames;
    const scene_image_t *image;
} scene_page_t;

// Sets up text mode (font, palette, clear screen, DISPLAY_ON)
void scene_init(void);

// Clears all 20x18 background tiles
void scene_clear(void);

// Plays a sequence of pages
void scene_play(const scene_page_t *pages, uint8_t num_pages);

#endif
