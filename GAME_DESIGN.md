# Nick's Life: A Game Boy Biographical RPG

## Concept
A chapter-based RPG where each stage of Nick's life is a unique mini-game. Between chapters, there's an overworld/narrative screen with pixel art cutscenes and dialogue. The player makes choices that echo real life — but the mini-games are the heart of it.

**Platform:** Game Boy Color (GBDK-2020, C language)

**Tone:** Warm, funny, occasionally tough. Not a documentary — a game *inspired by* a life.

**Working Title:** "Nick's Quest" / "余生" (yú shēng — a pun: 余 is Nick's surname, 余生 means "the rest of one's life")

---

## Chapter Structure

### Chapter 1: Early Steps — Kunming, China
**Narrative:** Nick is born in the quiet town of Kunming, China. The story opens with the Zhuazhou tradition: lay objects before the baby, and whatever he grabs reveals his future. The player helps baby Nick take his first steps toward his destiny.

**Story Intro (3 text screens):**
1. "This is Nick. Born in the quiet town of Kunming, China."
2. "A long life awaits, but first... a tradition. Lay objects before the baby. What he picks will reveal his future."
3. "Help baby Nick take his first steps!"

**Mini-game: "First Steps" (DDR Rhythm Game)**
- **Mechanic:** Arrows scroll upward in 4 columns (Left, Up, Down, Right). The player presses the matching D-pad direction when arrows reach the target zone at the top. Hit detection: PERFECT (3px window, 100pts), GOOD (8px window, 50pts), MISS (passed the zone).
- **Controls:** D-pad only. Each direction matches its column. Edge-detection prevents held buttons from registering multiple hits.
- **Music:** Original 4-channel Game Boy music plays in sync with the arrows — two pulse channels (melody + harmony), wave channel (bass), and noise channel (drums). 120 BPM, ~63 seconds. The song has a gentle Chinese-inspired feel with a melodic lead over a steady bass and light percussion.
- **Visual:** Baby sprite walks from left to right across the bottom of the screen as the song progresses, representing the journey toward the objects. Score HUD at top. Colored arrow sprites (red/green/blue/yellow) per direction.
- **Level data:** 504-step chart at 120 BPM (8 steps/sec), 99 total arrows, with a 3-second lead-in. Arrows are spawned ahead of the beat to account for scroll travel time (~69 frames at 1.5 px/frame).
- **No score screen:** Instead, the game flows directly into the story ending.

**Ending Cutscene (Zhuazhou):**
After the rhythm game, baby Nick reaches the pile of objects. A series of timed text screens play:
1. "Nick reaches the pile of objects..."
2. "A ball... a book... a paintbrush..."
3. "He reaches out and grabs..."
4. "...the calculator!"
5. "His future is already taking shape." (press A to continue)

The baby always picks the calculator — foreshadowing Nick's path into tech. No player choice; the story ending IS the payoff.

### Chapter 2: 上学路 (Road to School) — Kunming
**Narrative:** You're a kid now. School starts early. Don't be late!
**Mini-game: "Bicycle Dash"**
- **Mechanic:** Side-scrolling obstacle course (like Excitebike meets Paperboy).
- **Controls:** D-pad to steer up/down (lanes), A to pedal faster, B to brake.
- **Obstacles:** Potholes, street vendors (烧烤摊), stray dogs, buses pulling out, puddles after rain, other cyclists.
- **Collectibles:** 包子 (baozi) for energy/points, textbooks you dropped.
- **Timer:** Must reach school gate before the bell rings.
- **Fun detail:** If you crash into the 烧烤摊, the vendor yells at you in text (要不要来串？).
- **Win condition:** Arrive at school on time.

### Chapter 3: 远渡重洋 (Crossing the Ocean) — China → Canada (Vancouver/UBC)
**Narrative:** Big decision cutscene. Family discussion. Packing montage. Plane lands. Everything is different.
**Mini-game: "New World"**
- **Mechanic:** Multi-stage adventure/puzzle. Each stage represents mastering a piece of Canadian life. Top-down exploration with quests.
- **Controls:** D-pad to move, A to interact/talk, B to open inventory.
- **Visual twist:** Signs/text start garbled (you don't read English yet). As you progress, the world becomes readable AND more colorful (palette shifts from muted grey-blue to vibrant).

**Stage 1 — "Finding Home"**
- You arrive at Vancouver airport. Navigate to the exit (confusing signs, wrong turns).
- Find the right bus to your temporary housing. Talk to people — most responses are garbled, but one kind person (with a 🍁 above their head) speaks slowly and points you the right way.
- Fail state: Get on the wrong bus → end up lost → walk back and try again.

**Stage 2 — "The Way to UBC"**
- Goal: Get from your place to UBC campus for the first day.
- Sub-tasks: (1) Figure out the bus route — find a transit map at the bus stop, (2) Get exact change for fare (go to a convenience store, interact with cashier — dialogue puzzle with limited English options), (3) Board the right bus on time (a timer ticks).
- If you miss the bus, you wait for the next one and arrive late — NPC professor gives you a look but lets you in. Second time you know the route.

**Stage 3 — "Making a Connection"**
- On campus. Everyone's in groups. You're alone.
- Find the international student center (explore campus buildings, ask for directions).
- Meet another student — dialogue choices. Some options are awkward/wrong language, some land. Build enough rapport to get invited to a study group.
- **Win condition:** You have a friend, you know the bus route, the world is in full color. A text box: "This place is starting to feel like home."

**Emotional arc:** Lonely → confused → small victories → belonging. The palette transition makes this *feel* earned.

### Chapter 4: 💕 (Love Story) — Asking Yvonna Out
**Narrative:** You've met someone. Now you need to actually ask her out. Easier said than done.
**Mini-game: "Heart Quest"**
- **Mechanic:** Multi-round dialogue/strategy game. Think Phoenix Wright but for romance — read the situation, pick the right approach, build courage.

**Round 1 — "The Approach"**
- You see Yvonna. A courage meter appears (starts low).
- Build courage first: talk to friends for advice (each friend gives a different tip, some good, some terrible). Buy flowers? Too much. Practice what to say in the mirror? Helps a little.
- When courage is high enough, you can walk up to her. Too low = you chicken out and have to try another day.

**Round 2 — "The Conversation"**
- Dialogue tree with branching paths. 3-4 exchanges, each with 3 choices:
  - 🟢 Smooth (genuinely interested, asks about her)
  - 🟡 Awkward but endearing (nervous, stumbles, but honest)  
  - 🔴 Cringe (brags, tries too hard, talks about yourself too much)
- She has a hidden "interest meter." Green choices raise it. Red drops it. Yellow is a wildcard — sometimes she finds it cute, sometimes not (randomized, like real life).
- Key moments: She mentions something she likes. If you remember it and reference it later → big bonus.

**Round 3 — "The Ask"**
- Final dialogue. Based on how Round 2 went:
  - High interest: Almost any ask works. She smiles. "Sure, I'd like that."
  - Medium interest: Only the genuine/honest option works. The try-hard one fails.
  - Low interest: She says "maybe another time." You get a retry with different dialogue next "day."
- **Wrong answers are funny:** "Want to see my GitHub?" → she looks confused. "I made you a spreadsheet of date ideas" → 😬
- **Win condition:** She says yes. A heart floats up. You walk away and do a little jump sprite animation. 

**Design note:** You can't "game" it perfectly on the first try. The randomized yellow responses mean you have to adapt, not memorize. Just like real dating.

### Chapter 5: 码农之路 (The Code Path) — Engineer in the US
**Narrative:** Got the job. Moving to America. Time to prove yourself.
**Mini-game: "Debug Rush"**
- **Mechanic:** Falling-block puzzle (Tetris-inspired but with code blocks).
- **Concept:** Lines of code fall from the top. Some have bugs (red blocks). You need to rotate/place correct blocks to fix the bugs before they stack up.
- **Controls:** D-pad to move, A to rotate, B to hard drop.
- **Power-ups:** "Stack Overflow" (clears a row), "Coffee" (slows time), "Code Review" (highlights bugs).
- **Difficulty:** Speeds up over time. Bugs get trickier.
- **Win condition:** Survive long enough to "ship the product." Celebration screen with confetti.

### Chapter 6: 金门之城 (Golden Gate City) — San Francisco
**Narrative:** You made it to SF. Enjoy the moment.
**Mini-game: "City Explorer"**
- **Mechanic:** Relaxed exploration. Top-down city map of SF landmarks.
- **No fail state.** This is the breather chapter.
- **Explore:** Golden Gate Bridge, Chinatown (get dim sum!), Dolores Park, the office.
- **Collectibles:** Memories (photos) at each landmark. Find all 8 to complete the chapter.
- **Easter eggs:** A tech bro NPC says "we should disrupt this" about everything. A $15 toast at a café.
- **Vibe:** Chill music. The calm before the storm.

### Chapter 7: 新生命 (New Life) — The Birth of Colette
**Narrative:** The most intense day of your life.
**Mini-game: "Coach Mode"**
- **Mechanic:** Multi-task management game (like Diner Dash but in a hospital).
- **Tasks appear simultaneously:** Hold Yvonna's hand (mash A), breathe together (rhythm prompt), talk to the nurse (dialogue choice), get ice chips (fetch quest across the room), stay calm (don't press any button when the "PANIC" prompt appears — restraint!).
- **The twist:** You can't do everything perfectly. Things get missed. That's the point.
- **Climax:** Baby arrives. Screen goes white. Then: a tiny sprite. A cry sound effect. Text: "余可莱 has entered the world."
- **Win condition:** You can't lose this one. But your "score" reflects how well you managed. Either way, the baby comes. 🥹

### Chapter 8: 创业 (The Leap) — Quitting & Entrepreneurship
**Narrative:** Dramatic cutscene. The resignation letter. The leap of faith. "What's the worst that can happen?"
**Mini-game: "Startup Survival"**
- **Mechanic:** Turn-based strategy game. Each "turn" is a month. You make decisions, see results, adapt.

**Resources (always visible):**
- 💰 Runway (months of money left, starts at 12)
- 🔥 Momentum (product progress + market traction)
- ❤️ Family happiness (neglect it and bad things happen)
- 🧠 Sanity (hits zero = burnout, forced to rest a turn)

**Each turn, choose 2 actions from:**
- **Build:** Pick a product direction (3 options with different risk/reward profiles)
  - Safe feature (low risk, low reward, slow momentum)
  - Bold bet (high risk, could 2x momentum or waste the month)
  - Pivot (reset momentum to 50% but unlock new product options)
- **Hustle:** Talk to users, pitch investors, find design partners
- **Hire:** Pick a co-founder/partner (each has stats + personality — some are talented but hard to work with, some are loyal but limited)
- **Family:** Spend time with Yvonna and kids. Restores ❤️ and 🧠. Costs momentum.
- **Rest:** Recover sanity. That's it. Sometimes you need it.

**Events (random each playthrough):**
- "A competitor just launched the same thing." → Do you pivot or double down?
- "Investor offers money but wants 40% equity." → Take it or keep bootstrapping?
- "Yvonna says the kids miss you." → Skip family this month? ❤️ drops hard.
- "Your co-founder wants to quit." → Convince them to stay (costs sanity) or let them go?

**The PMF moment:** When Momentum hits a threshold AND you have paying users (from Hustle actions), you hit Product-Market Fit. Screen flashes. Music changes. But it takes multiple tries to find the right combo.

**Failing is the game:** Runway hits 0 → "GAME OVER?" → "Continue? Y/N." You always continue. But you restart with knowledge: "Last time you learned: [tip based on what went wrong]." Different product choices appear. Your strategy evolves.

**Win condition:** Reach PMF before running out of retries (3 total "lives"). Each life you start with slightly more knowledge (tips persist). The message: persistence + learning from failure = eventual success.

**Meta-touch:** The "winning" product is never the first one you pick. The game is literally designed so the first attempt fails. Just like real startups.

### Chapter 9: 传承 (Legacy) — Watching Them Grow
**Narrative:** The startup is running. But the real game was never the company.
**Mini-game: "Three Seeds"**
- **Mechanic:** Garden/nurture simulation. You're raising three plants (Colette 🌸, Colyn 🌿, Connie 🌱), each representing a child at different growth stages.

**Gameplay:**
- The screen shows three plots in a garden. Each plant is different — grows differently, needs different things.
- **Colette (oldest, 🌸):** Already a small tree. Needs pruning (guidance), not over-watering (hovering). If you give her space, she grows flowers. If you over-tend, she wilts slightly.
- **Colyn (middle, 🌿):** A wild vine. Grows in unexpected directions. You can build a trellis (structure) for him, or let him go wild. Both paths lead somewhere interesting — just different shapes.
- **Connie (youngest, 🌱):** A tiny sprout. Needs water and sunlight (attention, love). Simple needs, but miss a turn and she droops.

**Each turn:** You have limited actions (just like real parenting — you can't be everywhere).
- 💧 Water (give attention/love)
- ✂️ Prune (set boundaries/guide)
- ☀️ Sunlight (encouragement/play)
- 🌍 Open the gate (let them explore — risky but they grow faster)

**The twist:** You don't control what they become. Your actions influence the *shape* and *health*, but each plant has its own randomized destiny. A healthy Colette might become a towering oak or a beautiful cherry blossom — you don't choose which. You just help her grow strong enough to become *whatever she becomes*.

**Ending sequence:**
- Time fast-forwards. The garden grows. The three plants become full-grown, unique, beautiful.
- The camera pulls back. You see the whole garden — and behind it, all the chapters: the room where you took first steps, the bicycle, the streets of Vancouver, the place you met Yvonna, the code, the city, the hospital, the startup.
- Your character sprite, now older, sits on a bench in the garden. The three "plants" have become young people standing beside you. Yvonna sits next to you.
- Text: "The game isn't over. It never was."
- **Credits roll over a montage of pixel-art scenes from every chapter.**
- **Post-credits:** The screen shows Chapter 1 again. But this time, it's Colette's sprite taking her first steps. The title card reads: "余生 II?" with a wink emoji. 😉

---

## Scoring System 🏆

**Points-based. Competitive. Every chapter awards a score.**

### How It Works
- Each chapter has a **max score of 1000 points**
- Total game max: **9000 points**
- Points come from: speed, accuracy, choices, and hidden bonuses
- After each chapter, your score is shown with a letter grade (S/A/B/C/D)

### Per-Chapter Scoring

| Chapter | Speed Bonus | Skill Bonus | Secret Bonus |
|---------|------------|-------------|--------------|
| 1 - Early Steps | PERFECT hit % | Combo streaks | Full combo (no misses) |
| 2 - Bicycle Dash | Finish with time left | No crashes | Collect all 包子 |
| 3 - New World | Complete stages quickly | No wrong buses | Find hidden 奶茶 shop |
| 4 - Heart Quest | Ask her out on day 1 | All green answers | Find the "perfect" wildcard combo |
| 5 - Debug Rush | Survive longest | Combo chains (fix bugs in a row) | Clear the entire board |
| 6 - City Explorer | Find all landmarks fast | Talk to every NPC | Find the secret 7th landmark |
| 7 - Coach Mode | Complete all tasks | Perfect rhythm on breathing | Don't press anything during PANIC (restraint bonus) |
| 8 - Startup Survival | Reach PMF fastest | Keep all 4 bars above 50% | Find PMF on life 1 (nearly impossible) |
| 9 - Three Seeds | All 3 plants healthy | Balanced attention | All 3 become their "best" form |

### High Score Table
- **Top 3 scores saved to cartridge RAM (battery-backed SRAM)**
- Player enters 3-character initials (classic arcade style)
- Shown on title screen: "TOP SCORES" with initials + total points
- Bragging rights. Pure Game Boy energy.

### Grade Thresholds (per chapter)
- **S:** 900-1000 (near perfect)
- **A:** 750-899 (great)
- **B:** 500-749 (solid)
- **C:** 300-499 (made it)
- **D:** 0-299 (rough but you survived)

### End-Game Summary
After Chapter 9, a full scorecard shows:
```
  余 生 — FINAL SCORE
  ─────────────────────
  Ch1  First Steps    850  [A]
  Ch2  Bicycle Dash   920  [S]
  Ch3  New World      640  [B]
  ...
  ─────────────────────
  TOTAL              6430
  RANK:  A
  ─────────────────────
  NEW HIGH SCORE? ███
```

---

## Overworld / Hub
Between chapters, a simple timeline screen:
```
[Birth]---[School]---[Canada]---[Love]---[Code]---[SF]---[Baby]---[Startup]---[???]
   ★         ★         ★        ☆        ☆       ☆       ☆         ☆         ☆
```
Stars fill in as you complete chapters. Player can replay completed chapters for better scores.

## Art Style
- 8-bit pixel art, Game Boy Color palette (up to 8 BG palettes, 8 sprite palettes, 4 colors each)
- Each chapter has a distinct color palette reflecting the mood
- Character sprite evolves: baby → kid → teen → adult → parent → entrepreneur
- Reusable scene system supports text pages and full-screen image pages for cutscenes

## Music
- Each chapter has a unique BGM using Game Boy's 4 sound channels
- Ch1: Gentle melody with Chinese-inspired feel (2 pulse + wave bass + noise drums)
- Ch2: Upbeat, energetic. Ch3: Bittersweet. Ch4: Romantic 8-bit. Ch5: Techno. Ch6: Chill lo-fi. Ch7: Intense → tender. Ch8: Epic → somber → hopeful.

## Technical Notes
- Game Boy Color ROM built with GBDK-2020 (C language)
- 32KB ROM (expandable with bank switching if needed — MBC1/MBC5)
- Each mini-game is a separate module (chapter1.c, chapter2.c, etc.)
- Reusable scene system (scene.h/scene.c) for text and image cutscenes across chapters
- Sprite-based gameplay overlays on BG text layer
- 160x144 resolution, 40 sprites max, 192 unique BG tiles

---

## Scope Reality Check
This is ambitious for Game Boy. For a buildable MVP:
- **Phase 1:** Chapters 1-3 (Early Steps, Bicycle, Canada) — 3 distinct mini-games
- **Phase 2:** Chapters 4-6 (Love, Code, SF)
- **Phase 3:** Chapters 7-9 (Baby, Startup, Ending)

Chapter 1 (Early Steps — DDR rhythm game) is complete and playable. Chapter 2 (Bicycle Dash) is next.
