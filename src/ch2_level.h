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
    {  260, LANE_TOP, OBS_POTHOLE },
    {  400, LANE_BOT, OBS_PUDDLE  },

    // Segment 2 (450-800): slightly faster, mixed lanes
    {  500, LANE_MID, OBS_POTHOLE },
    {  620, LANE_BOT, OBS_POTHOLE },
    {  740, LANE_TOP, OBS_PUDDLE  },
    {  860, LANE_MID, OBS_PUDDLE  },

    // Segment 3 (900-1200): two obstacles closer together
    {  940, LANE_TOP, OBS_POTHOLE },
    { 1020, LANE_BOT, OBS_POTHOLE },
    { 1120, LANE_MID, OBS_PUDDLE  },
    { 1200, LANE_TOP, OBS_PUDDLE  },

    // Segment 4 (1260-1500): 2-lane block (must go to specific lane)
    { 1300, LANE_TOP, OBS_POTHOLE },
    { 1300, LANE_MID, OBS_POTHOLE },  // blocks top+mid, must go bottom
    { 1480, LANE_BOT, OBS_PUDDLE  },
    { 1480, LANE_MID, OBS_PUDDLE  },  // blocks bot+mid, must go top

    // Segment 5 (1560-1800): faster rhythm, first collectible!
    { 1580, LANE_BOT, OBS_POTHOLE },
    { 1660, LANE_MID, COL_BAOZI   },  // reward for surviving phase 1
    { 1760, LANE_TOP, OBS_PUDDLE  },

    // === PHASE 2: Ramping Up (30-60s, frames 1800-3600) ===
    // Segment 6 (1800-2160): introduce dogs!
    { 1860, LANE_MID, OBS_DOG     },
    { 2000, LANE_TOP, OBS_POTHOLE },
    { 2100, LANE_BOT, OBS_DOG     },

    // Segment 7 (2200-2520): introduce cyclists
    { 2220, LANE_TOP, OBS_CYCLIST },
    { 2360, LANE_BOT, OBS_DOG     },
    { 2460, LANE_MID, COL_BAOZI   },

    // Segment 8 (2520-2880): 2-lane blocks with dogs
    { 2580, LANE_TOP, OBS_DOG     },
    { 2580, LANE_MID, OBS_POTHOLE },  // top+mid blocked
    { 2760, LANE_BOT, OBS_CYCLIST },
    { 2760, LANE_MID, OBS_PUDDLE  },  // bot+mid blocked
    { 2920, LANE_TOP, COL_BAOZI   },

    // Segment 9 (2960-3240): faster pace, more collectibles
    { 2980, LANE_MID, OBS_DOG     },
    { 3100, LANE_TOP, OBS_CYCLIST },
    { 3200, LANE_MID, COL_BAOZI   },
    { 3300, LANE_BOT, OBS_DOG     },

    // Segment 10 (3360-3600): intense, first textbook!
    { 3380, LANE_TOP, OBS_DOG     },
    { 3380, LANE_BOT, OBS_CYCLIST },  // top+bot blocked, mid safe
    { 3520, LANE_MID, OBS_POTHOLE },
    { 3600, LANE_TOP, COL_TEXTBOOK }, // big reward!

    // === PHASE 3: Hectic (60-90s, frames 3600-5400) ===
    // Segment 11 (3660-3960): introduce buses!
    { 3700, LANE_MID, OBS_BUS     },  // single bus, imposing
    { 3860, LANE_BOT, OBS_DOG     },
    { 3940, LANE_MID, COL_BAOZI   },

    // Segment 12 (3960-4320): introduce vendor stalls!
    { 4020, LANE_BOT, OBS_VENDOR  },  // 要不要来串？
    { 4180, LANE_TOP, OBS_BUS     },
    { 4340, LANE_BOT, OBS_DOG     },
    { 4420, LANE_MID, COL_BAOZI   },

    // Segment 13 (4440-4700): rapid fire (spaced for 4 max)
    { 4460, LANE_TOP, OBS_DOG     },
    { 4560, LANE_BOT, OBS_CYCLIST },
    { 4660, LANE_MID, COL_TEXTBOOK }, // textbook in the chaos
    { 4760, LANE_TOP, OBS_VENDOR  },

    // Segment 14 (4800-5100): peak difficulty
    { 4840, LANE_MID, OBS_BUS     },
    { 4960, LANE_BOT, OBS_DOG     },
    { 5040, LANE_TOP, OBS_CYCLIST },
    { 5100, LANE_MID, COL_BAOZI   },

    // Segment 15 (5140-5400): final stretch — school in sight!
    { 5160, LANE_MID, OBS_DOG     },
    { 5240, LANE_TOP, OBS_POTHOLE },
    { 5300, LANE_MID, COL_TEXTBOOK }, // last big reward
    { 5360, LANE_BOT, OBS_PUDDLE  },  // one last obstacle
};

#define CH2_NUM_EVENTS (sizeof(ch2_events) / sizeof(ch2_events[0]))
#define CH2_TOTAL_FRAMES 5400u  // 90 seconds at 60fps

#endif
