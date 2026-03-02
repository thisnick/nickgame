#include <gb/gb.h>
#include <stdint.h>
#include <stdio.h>

void main(void) {
    // The Game Boy has a built-in font we can use with printf
    // stdio.h's printf writes to the background layer automatically
    printf("   HELLO WORLD!\n\n");
    printf("  NICK'S LIFE\n\n");
    printf("  PRESS START");

    SHOW_BKG;

    // Wait for START button
    while (1) {
        uint8_t keys = joypad();
        if (keys & J_START) {
            // Flash the screen to show input works
            printf("\n\n   LET'S GO!");
        }
        vsync();
    }
}
