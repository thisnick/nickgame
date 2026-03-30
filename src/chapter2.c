#pragma bank 2

#include <gb/gb.h>
#include <gb/cgb.h>
#include <gbdk/font.h>
#include <gbdk/console.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "chapter2.h"
#include "scene.h"
#include "ch2_level.h"
#include "ch2_street_bg_data.h"
#include "ch2_bike_frame1.h"
#include "ch2_bike_frame2.h"
#include "ch2_pothole.h"
#include "ch2_puddle.h"
#include "ch2_dog_frame1.h"
#include "ch2_dog_frame2.h"
#include "ch2_vendor.h"
#include "ch2_bus.h"
#include "ch2_cyclist.h"
#include "ch2_baozi.h"
#include "ch2_textbook.h"

// --- Constants ---

#define MAX_OBSTACLES   4
#define BIKE_SCREEN_X   40
#define BIKE_OAM_X      (BIKE_SCREEN_X + 8)

// Sprite tile base offsets (8x16 mode, tiles counted in 8x16 units)
#define TILE_BIKE1      0    // 12 tiles
#define TILE_BIKE2      12   // 12 tiles
#define TILE_POTHOLE    24   // 4 tiles
#define TILE_PUDDLE     28   // 2 tiles
#define TILE_DOG1       30   // 8 tiles
#define TILE_DOG2       38   // 6 tiles
#define TILE_VENDOR     44   // 16 tiles
#define TILE_BUS        60   // 16 tiles
#define TILE_CYCLIST    76   // 4 tiles
#define TILE_BAOZI      80   // 2 tiles
#define TILE_TEXTBOOK   82   // 2 tiles

// Sprite palette indices (GBC supports 8 sprite palettes)
#define PAL_BIKE        0   // skin, blue, dark
#define PAL_WARM        1   // tan, brown, dkbrown (dog, vendor)
#define PAL_BUS         2   // cream, red, dark
#define PAL_ROAD        3   // ltgray, gray, dkgray (pothole, cyclist approx)
#define PAL_WATER       4   // ltblue, medblue, dkblue (puddle)
#define PAL_COLLECT     5   // white, cream, gold (baozi)
#define PAL_BOOK        6   // white, cblue, dark (textbook)

// Sprite slot allocation (8x16 mode)
#define SPR_BIKE        0   // sprites 0-5 (6 entries for 32x32 bike)
#define SPR_OBS_BASE    6   // sprites 6-37 (4 obstacles * 8 max entries)
#define SPR_PER_OBS     8   // max sprite entries per obstacle

// Scroll speeds (8.8 fixed point)
#define SPEED_NORMAL    0x0100u
#define SPEED_BOOST     0x0200u
#define SPEED_BRAKE     0x0080u

// Lane Y positions (OAM coordinates = screen_y + 16)
// Spaced 32px apart so 32x32 sprites don't overlap between lanes
static const uint8_t lane_y[3] = { 80, 112, 144 };

// Lane switch animation
#define LANE_SWITCH_FRAMES 8

// Invincibility
#define INVINCIBLE_FRAMES  180
#define HIT_TIME_PENALTY   180  // frames lost (3 seconds)

// Collectible scores
#define SCORE_BAOZI     50
#define SCORE_TEXTBOOK  100

// Target distance (total scroll pixels to win)
// Slightly less than CH2_TOTAL_FRAMES so player can arrive before bell
#define TARGET_DISTANCE 5000u

// Distance scoring
#define DISTANCE_SCORE_INTERVAL 100u
#define DISTANCE_SCORE_POINTS   10u

// --- Data Structures ---

typedef struct {
    uint8_t  active;
    uint8_t  type;
    uint8_t  lane;
    uint16_t x_pos;      // screen x in pixels (moves left)
    uint8_t  sprite_base; // first sprite slot
    uint8_t  anim_frame;
} obstacle_t;

// --- State ---

static obstacle_t obstacles[MAX_OBSTACLES];
static uint16_t frame_count;
static uint16_t next_event;
static uint16_t score;
static uint16_t displayed_score;
static uint16_t timer_frames;   // counts down
static uint8_t  timer_seconds;
static uint8_t  displayed_timer;
static uint8_t  bike_lane;
static uint8_t  target_lane;
static uint8_t  bike_y;         // current OAM y
static uint8_t  lane_switch_t;  // 0 = not switching, counts down
static uint8_t  lane_start_y;   // y at start of switch
static uint8_t  invincible_timer;
static uint8_t  shake_timer;
static uint8_t  feedback_timer;
static uint8_t  bike_anim;      // 0 or 1
static uint16_t scroll_accum;   // 8.8 fractional scroll accumulator
static uint16_t total_distance;
static uint8_t  total_crashes;
static uint8_t  total_collected;
static uint8_t  game_won;
static uint16_t distance_score_accum; // accumulates distance for scoring

// --- Helpers ---

static void ch2_wait_frames(uint8_t n) {
    for (uint8_t i = 0; i < n; i++) vsync();
}

static void hide_all_sprites(void) {
    for (uint8_t i = 0; i < 40; i++) {
        move_sprite(i, 0, 0);
    }
}

// --- Sound ---

static void ch2_init_sound(void) {
    NR52_REG = 0x80;
    NR50_REG = 0x77;
    NR51_REG = 0xFF;
}

static void ch2_stop_sound(void) {
    NR52_REG = 0x00;
}

static void sfx_hit(void) {
    // Noise channel: short harsh burst
    NR41_REG = 0x00;
    NR42_REG = 0xC1;
    NR43_REG = 0x37;
    NR44_REG = 0x80;
}

static void sfx_collect(void) {
    // Pulse 1: quick ascending chime
    NR10_REG = 0x00;
    NR11_REG = 0x80;
    NR12_REG = 0xA3;
    NR13_REG = 0x80;
    NR14_REG = 0x86;
}

// --- Background Restore ---

static void restore_bg_rect(uint8_t x, uint8_t y, uint8_t w, uint8_t h) {
    for (uint8_t r = 0; r < h; r++) {
        uint16_t off = (uint16_t)(y + r) * 32u + x;
        VBK_REG = 1;
        set_bkg_tiles(x, y + r, w, 1, &ch2_street_bg_data_map_attributes[off]);
        VBK_REG = 0;
        set_bkg_tiles(x, y + r, w, 1, &ch2_street_bg_data_map[off]);
    }
}

// --- Intro Text ---

static const scene_line_t intro_p1[] = {
    { 1, 6, "You're a kid now." },
    { 1, 8, "School starts early." },
    { 1, 10, "Don't be late!" },
};

static const scene_line_t intro_p2[] = {
    { 1, 5, "Hop on your bike" },
    { 1, 7, "and ride through" },
    { 1, 9, "the streets of" },
    { 1, 11, "Kunming." },
};

static const scene_line_t intro_p3[] = {
    { 1, 6, "Dodge potholes," },
    { 1, 8, "stray dogs, and" },
    { 1, 10, "morning traffic!" },
};

static const scene_page_t intro_text[] = {
    { intro_p1, 3, SCENE_WAIT_BUTTON, 0, NULL },
    { intro_p2, 4, SCENE_WAIT_BUTTON, 0, NULL },
    { intro_p3, 3, SCENE_WAIT_BUTTON, 0, NULL },
};

// --- Sprite Loading ---

static void ch2_load_sprites(void) {
    // Bike frames
    set_sprite_data(TILE_BIKE1, ch2_bike_frame1_TILE_COUNT, ch2_bike_frame1_tiles);
    set_sprite_data(TILE_BIKE2, ch2_bike_frame2_TILE_COUNT, ch2_bike_frame2_tiles);

    // Obstacles
    set_sprite_data(TILE_POTHOLE, ch2_pothole_TILE_COUNT, ch2_pothole_tiles);
    set_sprite_data(TILE_PUDDLE, ch2_puddle_TILE_COUNT, ch2_puddle_tiles);
    set_sprite_data(TILE_DOG1, ch2_dog_frame1_TILE_COUNT, ch2_dog_frame1_tiles);
    set_sprite_data(TILE_DOG2, ch2_dog_frame2_TILE_COUNT, ch2_dog_frame2_tiles);
    set_sprite_data(TILE_VENDOR, ch2_vendor_TILE_COUNT, ch2_vendor_tiles);
    set_sprite_data(TILE_BUS, ch2_bus_TILE_COUNT, ch2_bus_tiles);
    set_sprite_data(TILE_CYCLIST, ch2_cyclist_TILE_COUNT, ch2_cyclist_tiles);

    // Collectibles
    set_sprite_data(TILE_BAOZI, ch2_baozi_TILE_COUNT, ch2_baozi_tiles);
    set_sprite_data(TILE_TEXTBOOK, ch2_textbook_TILE_COUNT, ch2_textbook_tiles);

    // Palettes (GBC has 8 sprite palettes)
    set_sprite_palette(PAL_BIKE, 1, ch2_bike_frame1_palettes);
    set_sprite_palette(PAL_WARM, 1, ch2_dog_frame1_palettes);
    set_sprite_palette(PAL_BUS, 1, ch2_bus_palettes);
    set_sprite_palette(PAL_ROAD, 1, ch2_pothole_palettes);
    set_sprite_palette(PAL_WATER, 1, ch2_puddle_palettes);
    set_sprite_palette(PAL_COLLECT, 1, ch2_baozi_palettes);
    set_sprite_palette(PAL_BOOK, 1, ch2_textbook_palettes);
}

// --- Display Init ---

static void ch2_init_display(void) {
    DISPLAY_OFF;
    SPRITES_8x16;

    // Load font (tiles 0-127)
    font_init();
    font_load(font_ibm);

    // Load background (tiles at origin 128)
    set_bkg_data(ch2_street_bg_data_TILE_ORIGIN,
                 ch2_street_bg_data_TILE_COUNT, ch2_street_bg_data_tiles);
    VBK_REG = 1;
    set_bkg_tiles(0, 0, 32, 18, ch2_street_bg_data_map_attributes);
    VBK_REG = 0;
    set_bkg_tiles(0, 0, 32, 18, ch2_street_bg_data_map);
    set_bkg_palette(0, ch2_street_bg_data_PALETTE_COUNT, ch2_street_bg_data_palettes);

    // Load all sprite tiles and palettes
    ch2_load_sprites();

    hide_all_sprites();

    // Init state
    frame_count = 0;
    next_event = 0;
    score = 0;
    displayed_score = 0xFFFFu;
    timer_frames = CH2_TOTAL_FRAMES;
    timer_seconds = 90;
    displayed_timer = 0xFF;
    bike_lane = LANE_MID;
    target_lane = LANE_MID;
    bike_y = lane_y[LANE_MID];
    lane_switch_t = 0;
    lane_start_y = lane_y[LANE_MID];
    invincible_timer = 0;
    shake_timer = 0;
    feedback_timer = 0;
    bike_anim = 0;
    scroll_accum = 0;
    total_distance = 0;
    total_crashes = 0;
    total_collected = 0;
    game_won = 0;
    distance_score_accum = 0;

    for (uint8_t i = 0; i < MAX_OBSTACLES; i++) {
        obstacles[i].active = 0;
    }

    // Init sound
    ch2_init_sound();

    // Draw initial HUD
    gotoxy(0, 0);
    printf("T:01:30  SCORE:00000");

    // Place bike in middle lane
    move_metasprite_ex(ch2_bike_frame1_metasprites[0], TILE_BIKE1,
                       PAL_BIKE, SPR_BIKE, BIKE_OAM_X, bike_y);

    move_bkg(0, 0);
    SHOW_BKG;
    SHOW_SPRITES;
    DISPLAY_ON;
}

// --- Countdown ---

static void ch2_countdown(void) {
    gotoxy(8, 9);
    printf("  3  ");
    ch2_wait_frames(60);

    gotoxy(8, 9);
    printf("  2  ");
    ch2_wait_frames(60);

    gotoxy(8, 9);
    printf("  1  ");
    ch2_wait_frames(60);

    gotoxy(8, 9);
    printf(" GO! ");
    ch2_wait_frames(30);

    restore_bg_rect(8, 9, 5, 1);
}

// --- HUD Updates ---

static void update_timer_display(void) {
    if (timer_seconds != displayed_timer) {
        displayed_timer = timer_seconds;
        uint8_t mins = timer_seconds / 60;
        uint8_t secs = timer_seconds % 60;
        gotoxy(2, 0);
        printf("%u%u:%u%u", (unsigned int)(mins / 10), (unsigned int)(mins % 10),
               (unsigned int)(secs / 10), (unsigned int)(secs % 10));
    }
}

static void update_score_display(void) {
    if (score != displayed_score) {
        displayed_score = score;
        gotoxy(15, 0);
        printf("%u", (unsigned int)(score / 10000));
        printf("%u", (unsigned int)((score / 1000) % 10));
        printf("%u", (unsigned int)((score / 100) % 10));
        printf("%u", (unsigned int)((score / 10) % 10));
        printf("%u", (unsigned int)(score % 10));
    }
}

static void show_feedback(const char *text) {
    gotoxy(6, 5);
    printf("%s", text);
    feedback_timer = 20;
}

// --- Obstacle Management ---

static uint8_t get_tile_base(uint8_t type) {
    switch (type) {
        case OBS_POTHOLE:  return TILE_POTHOLE;
        case OBS_PUDDLE:   return TILE_PUDDLE;
        case OBS_DOG:      return TILE_DOG1;
        case OBS_CYCLIST:  return TILE_CYCLIST;
        case OBS_VENDOR:   return TILE_VENDOR;
        case OBS_BUS:      return TILE_BUS;
        case COL_BAOZI:    return TILE_BAOZI;
        case COL_TEXTBOOK: return TILE_TEXTBOOK;
        default:           return 0;
    }
}

static uint8_t get_palette(uint8_t type) {
    switch (type) {
        case OBS_DOG:
        case OBS_VENDOR:
            return PAL_WARM;
        case OBS_BUS:
            return PAL_BUS;
        case OBS_CYCLIST:
        case OBS_POTHOLE:
            return PAL_ROAD;
        case OBS_PUDDLE:
            return PAL_WATER;
        case COL_BAOZI:
            return PAL_COLLECT;
        case COL_TEXTBOOK:
            return PAL_BOOK;
        default:
            return PAL_ROAD;
    }
}

static const metasprite_t* const* get_metasprite(uint8_t type, uint8_t anim) {
    switch (type) {
        case OBS_POTHOLE:  return ch2_pothole_metasprites;
        case OBS_PUDDLE:   return ch2_puddle_metasprites;
        case OBS_DOG:      return anim ? ch2_dog_frame2_metasprites : ch2_dog_frame1_metasprites;
        case OBS_CYCLIST:  return ch2_cyclist_metasprites;
        case OBS_VENDOR:   return ch2_vendor_metasprites;
        case OBS_BUS:      return ch2_bus_metasprites;
        case COL_BAOZI:    return ch2_baozi_metasprites;
        case COL_TEXTBOOK: return ch2_textbook_metasprites;
        default:           return ch2_pothole_metasprites;
    }
}

static uint8_t get_anim_tile_base(uint8_t type, uint8_t anim) {
    if (type == OBS_DOG && anim) return TILE_DOG2;
    return get_tile_base(type);
}

static void spawn_obstacle(uint8_t type, uint8_t lane) {
    for (uint8_t i = 0; i < MAX_OBSTACLES; i++) {
        if (!obstacles[i].active) {
            obstacles[i].active = 1;
            obstacles[i].type = type;
            obstacles[i].lane = lane;
            obstacles[i].x_pos = 176; // spawn off right edge (wider sprites)
            obstacles[i].sprite_base = SPR_OBS_BASE + (i * SPR_PER_OBS);
            obstacles[i].anim_frame = 0;
            return;
        }
    }
}

static void hide_obstacle_sprites(uint8_t slot) {
    uint8_t base = SPR_OBS_BASE + (slot * SPR_PER_OBS);
    for (uint8_t s = base; s < base + SPR_PER_OBS; s++) {
        move_sprite(s, 0, 0);
    }
}

// --- Game Loop ---

static void ch2_game_loop(void) {
    uint8_t prev_keys = 0xFF; // suppress ghost presses

    while (1) {
        // 1. Read input
        uint8_t keys = joypad();
        uint8_t pressed = keys & ~prev_keys;
        prev_keys = keys;

        // 2. Determine scroll speed
        uint16_t scroll_speed = SPEED_NORMAL;
        if (keys & J_A) scroll_speed = SPEED_BOOST;
        if (keys & J_B) scroll_speed = SPEED_BRAKE;

        // 3. Lane switching
        if (lane_switch_t == 0) {
            if ((pressed & J_UP) && target_lane > 0) {
                target_lane--;
                lane_switch_t = LANE_SWITCH_FRAMES;
                lane_start_y = bike_y;
            } else if ((pressed & J_DOWN) && target_lane < 2) {
                target_lane++;
                lane_switch_t = LANE_SWITCH_FRAMES;
                lane_start_y = bike_y;
            }
        }

        // Smooth lane transition
        if (lane_switch_t > 0) {
            lane_switch_t--;
            uint8_t target_y_val = lane_y[target_lane];
            if (lane_switch_t == 0) {
                bike_y = target_y_val;
                bike_lane = target_lane;
            } else {
                // Linear interpolation
                int16_t diff = (int16_t)target_y_val - (int16_t)lane_start_y;
                int16_t progress = (int16_t)(LANE_SWITCH_FRAMES - lane_switch_t);
                bike_y = (uint8_t)((int16_t)lane_start_y + (diff * progress) / LANE_SWITCH_FRAMES);
            }
        }

        // 4. Scroll background
        scroll_accum += scroll_speed;
        uint8_t scroll_px = (uint8_t)(scroll_accum >> 8);
        scroll_accum &= 0x00FF;
        total_distance += scroll_px;

        if (scroll_px > 0) {
            scroll_bkg(scroll_px, 0);
        }

        // Distance scoring: +10 points per 100 pixels traveled
        distance_score_accum += scroll_px;
        while (distance_score_accum >= DISTANCE_SCORE_INTERVAL) {
            distance_score_accum -= DISTANCE_SCORE_INTERVAL;
            score += DISTANCE_SCORE_POINTS;
        }

        // 5. Animate bike (pedaling every 8 frames)
        bike_anim = (frame_count >> 3) & 1;

        // Blink bike during invincibility
        uint8_t show_bike = 1;
        if (invincible_timer > 0) {
            show_bike = (frame_count >> 2) & 1;
        }

        if (show_bike) {
            if (bike_anim) {
                move_metasprite_ex(ch2_bike_frame2_metasprites[0], TILE_BIKE2,
                                   PAL_BIKE, SPR_BIKE, BIKE_OAM_X, bike_y);
            } else {
                move_metasprite_ex(ch2_bike_frame1_metasprites[0], TILE_BIKE1,
                                   PAL_BIKE, SPR_BIKE, BIKE_OAM_X, bike_y);
            }
        } else {
            for (uint8_t s = SPR_BIKE; s < SPR_OBS_BASE; s++) {
                move_sprite(s, 0, 0);
            }
        }

        // 6. Spawn obstacles from level data
        while (next_event < CH2_NUM_EVENTS && ch2_events[next_event].frame <= frame_count) {
            spawn_obstacle(ch2_events[next_event].type, ch2_events[next_event].lane);
            next_event++;
        }

        // 7. Update obstacles
        for (uint8_t i = 0; i < MAX_OBSTACLES; i++) {
            if (!obstacles[i].active) continue;

            // Move left at scroll speed
            if (obstacles[i].x_pos <= scroll_px) {
                // Off screen left
                obstacles[i].active = 0;
                hide_obstacle_sprites(i);
                continue;
            }
            obstacles[i].x_pos -= scroll_px;

            // Animate dogs
            if (obstacles[i].type == OBS_DOG) {
                obstacles[i].anim_frame = (frame_count >> 3) & 1;
            }

            // Draw obstacle
            uint8_t tile = get_anim_tile_base(obstacles[i].type, obstacles[i].anim_frame);
            uint8_t pal = get_palette(obstacles[i].type);
            const metasprite_t* const* ms = get_metasprite(obstacles[i].type, obstacles[i].anim_frame);
            uint8_t oam_x = (uint8_t)(obstacles[i].x_pos + 8);
            uint8_t oam_y = lane_y[obstacles[i].lane];

            move_metasprite_ex(ms[0], tile, pal, obstacles[i].sprite_base, oam_x, oam_y);

            // 8. Collision detection
            // Check if obstacle overlaps bike horizontally (bike at x 40, width ~32)
            uint8_t obs_x = (uint8_t)obstacles[i].x_pos;
            uint8_t is_collectible = (obstacles[i].type & 0x80) ? 1 : 0;

            if (obs_x >= 16 && obs_x <= 72) {
                // Check lane overlap
                uint8_t obs_lane = obstacles[i].lane;
                uint8_t bike_in_lane = (bike_lane == obs_lane) ? 1 : 0;

                // Also check during transition
                if (lane_switch_t > 0 && target_lane == obs_lane) {
                    bike_in_lane = 1;
                }

                if (bike_in_lane) {
                    if (is_collectible) {
                        // Collect!
                        if (obstacles[i].type == COL_BAOZI) {
                            score += SCORE_BAOZI;
                            show_feedback(" Baozi! ");
                        } else {
                            score += SCORE_TEXTBOOK;
                            show_feedback("Textbook!");
                        }
                        sfx_collect();
                        total_collected++;
                        obstacles[i].active = 0;
                        hide_obstacle_sprites(i);
                    } else if (invincible_timer == 0) {
                        // Hit!
                        sfx_hit();
                        total_crashes++;
                        invincible_timer = INVINCIBLE_FRAMES;
                        shake_timer = 10;

                        // Time penalty
                        if (timer_frames > HIT_TIME_PENALTY) {
                            timer_frames -= HIT_TIME_PENALTY;
                        } else {
                            timer_frames = 0;
                        }
                        timer_seconds = (uint8_t)(timer_frames / 60u);

                        if (obstacles[i].type == OBS_VENDOR) {
                            show_feedback("Skewers?!");
                        } else {
                            show_feedback(" Crash! ");
                        }

                        obstacles[i].active = 0;
                        hide_obstacle_sprites(i);
                    }
                }
            }
        }

        // 9. Invincibility countdown
        if (invincible_timer > 0) {
            invincible_timer--;
        }

        // 10. Screen shake
        if (shake_timer > 0) {
            shake_timer--;
            if (shake_timer > 0) {
                int8_t sx = (shake_timer & 1) ? 2 : -2;
                // We need to account for scroll position - just offset temporarily
                // The scroll_bkg already moved, so we just shift y a bit
                move_bkg(0, (uint8_t)sx);
            } else {
                move_bkg(0, 0);
            }
        }

        // 11. Feedback timer
        if (feedback_timer > 0) {
            feedback_timer--;
            if (feedback_timer == 0) {
                restore_bg_rect(6, 5, 10, 1);
            }
        }

        // 12. Timer countdown
        if (timer_frames > 0) {
            timer_frames--;
            uint8_t new_secs = (uint8_t)(timer_frames / 60u);
            if (new_secs != timer_seconds) {
                timer_seconds = new_secs;
            }
        }

        // 13. Update HUD
        update_timer_display();
        update_score_display();

        // 14. End conditions
        if (total_distance >= TARGET_DISTANCE) {
            game_won = 1;
            return;
        }
        if (timer_frames == 0) {
            game_won = 0;
            return;
        }

        frame_count++;
        vsync();
    }
}

// --- End Screens ---

static char ch2_get_grade(void) {
    if (total_crashes == 0 && timer_seconds >= 15) return 'A';
    if (total_crashes <= 2) return 'B';
    if (total_crashes <= 5) return 'C';
    return 'D';
}

static void ch2_show_end_screen(void) {
    ch2_stop_sound();
    hide_all_sprites();

    // Reset scroll so street BG is visible behind text
    move_bkg(0, 0);

    // Load font into tiles 0-127 (street BG uses 128+)
    font_init();
    font_load(font_ibm);

    // Bonus for no crashes on win
    if (game_won && total_crashes == 0) {
        score += 500;
    }

    if (game_won) {
        char grade = ch2_get_grade();

        gotoxy(3, 2);
        printf("  YOU MADE IT!  ");

        gotoxy(2, 4);
        printf("Time left: %u:%u%u",
               (unsigned int)(timer_seconds / 60),
               (unsigned int)((timer_seconds % 60) / 10),
               (unsigned int)(timer_seconds % 10));

        gotoxy(2, 6);
        printf("Score: %u", (unsigned int)score);

        gotoxy(2, 8);
        printf("Crashes: %u", (unsigned int)total_crashes);

        gotoxy(2, 10);
        printf("Items: %u", (unsigned int)total_collected);

        if (total_crashes == 0) {
            gotoxy(2, 12);
            printf("PERFECT RIDE! +500");
        }

        gotoxy(2, 14);
        printf("Grade: %c", grade);
    } else {
        gotoxy(2, 3);
        printf("The bell rang...");

        gotoxy(2, 5);
        printf("You were late!");

        gotoxy(2, 7);
        printf("Score: %u", (unsigned int)score);

        gotoxy(2, 9);
        printf("Crashes: %u", (unsigned int)total_crashes);

        gotoxy(2, 11);
        printf("Items: %u", (unsigned int)total_collected);

        gotoxy(2, 13);
        printf("Grade: F");
    }

    gotoxy(3, 16);
    printf("Press A...");

    while (joypad()) vsync();
    while (!(joypad() & (J_A | J_START))) vsync();
    while (joypad()) vsync();
}


// --- Cleanup ---

static void ch2_cleanup(void) {
    hide_all_sprites();
    HIDE_SPRITES;
}

// --- Public Entry Point ---

BANKREF(chapter2)

void play_chapter2(void) BANKED {
    // 1. Intro text
    scene_play(intro_text, 3);

    // 2. Init display
    ch2_init_display();

    // 3. Countdown
    ch2_countdown();

    // 4. Game loop
    ch2_game_loop();

    // 5. End screen
    ch2_show_end_screen();

    // 6. Cleanup
    ch2_cleanup();
}
