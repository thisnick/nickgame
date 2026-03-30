#ifndef CH2_LEVEL_H
#define CH2_LEVEL_H

#include <stdint.h>

// Obstacle types
#define OBS_NONE      0
#define OBS_POTHOLE   1
#define OBS_PUDDLE    2
#define OBS_DOG       3
#define OBS_CYCLIST   4
#define OBS_VENDOR    5
#define OBS_BUS       6

// Collectible types (high bit set)
#define COL_BAOZI     0x81
#define COL_TEXTBOOK  0x82

// Lane indices
#define LANE_TOP      0
#define LANE_MID      1
#define LANE_BOT      2

// Level entry: {frame, lane, type}
typedef struct {
    uint16_t frame;
    uint8_t  lane;
    uint8_t  type;
} ch2_event_t;

// 90 seconds at 60fps = 5400 frames
// 15 segments of ~360 frames (6 seconds) each
// Phase 1 (seg 1-5):  potholes, puddles only — teach lane switching
// Phase 2 (seg 6-10): add dogs, cyclists, 2-lane blocks, baozi
// Phase 3 (seg 11-15): buses, vendors, rapid sequences, textbooks

static const ch2_event_t ch2_events[] = {
    // === PHASE 1: Learning (0-30s, frames 0-1800) ===
    // Segment 1 (0-360): gentle intro, single potholes
    {  120, LANE_MID, OBS_POTHOLE },
    {  240, LANE_TOP, OBS_POTHOLE },
    {  330, LANE_BOT, OBS_PUDDLE  },

    // Segment 2 (360-720): slightly faster, mixed lanes
    {  420, LANE_MID, OBS_POTHOLE },
    {  500, LANE_BOT, OBS_POTHOLE },
    {  580, LANE_TOP, OBS_PUDDLE  },
    {  660, LANE_MID, OBS_PUDDLE  },

    // Segment 3 (720-1080): two obstacles closer together
    {  780, LANE_TOP, OBS_POTHOLE },
    {  840, LANE_BOT, OBS_POTHOLE },
    {  960, LANE_MID, OBS_PUDDLE  },
    { 1020, LANE_TOP, OBS_PUDDLE  },

    // Segment 4 (1080-1440): introduce 2-lane block (must go to specific lane)
    { 1140, LANE_TOP, OBS_POTHOLE },
    { 1140, LANE_MID, OBS_POTHOLE },  // blocks top+mid, must go bottom
    { 1300, LANE_BOT, OBS_PUDDLE  },
    { 1300, LANE_MID, OBS_PUDDLE  },  // blocks bot+mid, must go top
    { 1400, LANE_TOP, OBS_POTHOLE },

    // Segment 5 (1440-1800): faster rhythm, first collectible!
    { 1500, LANE_BOT, OBS_POTHOLE },
    { 1560, LANE_TOP, OBS_POTHOLE },
    { 1620, LANE_MID, COL_BAOZI   },  // reward for surviving phase 1
    { 1700, LANE_BOT, OBS_PUDDLE  },
    { 1760, LANE_TOP, OBS_PUDDLE  },

    // === PHASE 2: Ramping Up (30-60s, frames 1800-3600) ===
    // Segment 6 (1800-2160): introduce dogs!
    { 1860, LANE_MID, OBS_DOG     },
    { 1950, LANE_TOP, OBS_POTHOLE },
    { 2040, LANE_BOT, OBS_DOG     },
    { 2100, LANE_MID, COL_BAOZI   },

    // Segment 7 (2160-2520): introduce cyclists
    { 2220, LANE_TOP, OBS_CYCLIST },
    { 2300, LANE_BOT, OBS_DOG     },
    { 2380, LANE_MID, OBS_CYCLIST },
    { 2440, LANE_TOP, COL_BAOZI   },
    { 2500, LANE_BOT, OBS_POTHOLE },

    // Segment 8 (2520-2880): 2-lane blocks with dogs
    { 2580, LANE_TOP, OBS_DOG     },
    { 2580, LANE_MID, OBS_POTHOLE },  // top+mid blocked
    { 2700, LANE_BOT, OBS_CYCLIST },
    { 2700, LANE_MID, OBS_PUDDLE  },  // bot+mid blocked
    { 2820, LANE_TOP, COL_BAOZI   },
    { 2860, LANE_BOT, OBS_DOG     },

    // Segment 9 (2880-3240): faster pace, more collectibles
    { 2940, LANE_MID, OBS_DOG     },
    { 3000, LANE_TOP, OBS_CYCLIST },
    { 3060, LANE_BOT, OBS_POTHOLE },
    { 3100, LANE_MID, COL_BAOZI   },
    { 3140, LANE_TOP, OBS_DOG     },
    { 3200, LANE_BOT, OBS_CYCLIST },

    // Segment 10 (3240-3600): intense, first textbook!
    { 3300, LANE_TOP, OBS_DOG     },
    { 3300, LANE_BOT, OBS_CYCLIST },  // top+bot blocked, mid safe
    { 3400, LANE_MID, OBS_POTHOLE },
    { 3460, LANE_TOP, COL_TEXTBOOK }, // big reward!
    { 3520, LANE_BOT, OBS_DOG     },
    { 3560, LANE_MID, OBS_CYCLIST },

    // === PHASE 3: Hectic (60-90s, frames 3600-5400) ===
    // Segment 11 (3600-3960): introduce buses (block 2 lanes!)
    { 3660, LANE_TOP, OBS_BUS     },  // bus blocks top+mid
    { 3660, LANE_MID, OBS_BUS     },
    { 3800, LANE_BOT, OBS_DOG     },
    { 3900, LANE_MID, COL_BAOZI   },
    { 3940, LANE_TOP, OBS_CYCLIST },

    // Segment 12 (3960-4320): introduce vendor stalls!
    { 4020, LANE_BOT, OBS_VENDOR  },  // 要不要来串？
    { 4120, LANE_TOP, OBS_BUS     },
    { 4120, LANE_MID, OBS_BUS     },
    { 4240, LANE_BOT, OBS_DOG     },
    { 4280, LANE_MID, COL_BAOZI   },
    { 4300, LANE_TOP, OBS_CYCLIST },

    // Segment 13 (4320-4680): rapid fire
    { 4360, LANE_TOP, OBS_DOG     },
    { 4400, LANE_BOT, OBS_POTHOLE },
    { 4440, LANE_MID, OBS_CYCLIST },
    { 4480, LANE_TOP, OBS_PUDDLE  },
    { 4520, LANE_BOT, OBS_DOG     },
    { 4560, LANE_MID, COL_TEXTBOOK }, // textbook in the chaos
    { 4620, LANE_TOP, OBS_VENDOR  },
    { 4660, LANE_BOT, OBS_CYCLIST },

    // Segment 14 (4680-5040): peak difficulty
    { 4720, LANE_TOP, OBS_BUS     },
    { 4720, LANE_MID, OBS_BUS     },
    { 4800, LANE_BOT, OBS_DOG     },
    { 4840, LANE_TOP, OBS_DOG     },
    { 4880, LANE_MID, OBS_VENDOR  },
    { 4920, LANE_BOT, OBS_CYCLIST },
    { 4960, LANE_TOP, COL_BAOZI   },
    { 5000, LANE_MID, OBS_POTHOLE },
    { 5000, LANE_BOT, OBS_PUDDLE  },

    // Segment 15 (5040-5400): final stretch — school in sight!
    { 5080, LANE_MID, OBS_DOG     },
    { 5120, LANE_TOP, OBS_CYCLIST },
    { 5160, LANE_BOT, OBS_POTHOLE },
    { 5200, LANE_MID, COL_BAOZI   },
    { 5240, LANE_TOP, OBS_PUDDLE  },
    { 5280, LANE_BOT, OBS_DOG     },
    { 5320, LANE_MID, COL_TEXTBOOK }, // last big reward
    { 5360, LANE_TOP, OBS_POTHOLE },  // one last obstacle
};

#define CH2_NUM_EVENTS (sizeof(ch2_events) / sizeof(ch2_events[0]))
#define CH2_TOTAL_FRAMES 5400u  // 90 seconds at 60fps

#endif
