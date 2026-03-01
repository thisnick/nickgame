; ============================================================
; 余生 - Chapter 2: Bicycle Dash
; NES/Famicom assembly (ca65)
; NROM-256: 32KB PRG + 8KB CHR
; ============================================================

; ---- iNES Header ----
.segment "HEADER"
    .byte "NES", $1A    ; Magic
    .byte 2             ; 2 x 16KB PRG ROM = 32KB
    .byte 1             ; 1 x 8KB CHR ROM
    .byte $00           ; Mapper 0, vertical mirroring (horizontal scroll)
    .byte $00           ; Mapper 0
    .byte $00,$00,$00,$00,$00,$00,$00,$00  ; padding

; ---- PPU Registers ----
PPUCTRL   = $2000
PPUMASK   = $2001
PPUSTATUS = $2002
OAMADDR   = $2003
PPUSCROLL = $2005
PPUADDR   = $2006
PPUDATA   = $2007
OAMDMA    = $4014
JOYPAD1   = $4016

; ---- Zero Page ----
.segment "ZEROPAGE"
nmi_flag:       .res 1  ; set in NMI, cleared by main
frame_count:    .res 1
rng_seed:       .res 1  ; LFSR pseudo-random seed

; Game state
game_state:     .res 1  ; 0=title, 1=playing, 2=crashed, 3=win, 4=gameover

; Player
player_lane:    .res 1  ; 0=top 1=mid 2=bot
player_y:       .res 1  ; current sprite Y
player_y_tgt:   .res 1  ; target Y
player_anim:    .res 1  ; animation counter
invincible:     .res 1  ; invincibility frames

; Scrolling / speed
scroll_lo:      .res 1  ; scroll X low byte (pixel)
scroll_hi:      .res 1  ; scroll X high byte (nametable select bit)
game_speed:     .res 1  ; pixels/frame
speed_timer:    .res 1  ; countdown to increase speed
crash_timer:    .res 1  ; frames in crash state

; Timer (countdown)
timer_secs:     .res 1
timer_frames:   .res 1  ; sub-second frame counter

; Score (BCD, 4 digits: score_bcd[0]=ones, [1]=tens, [2]=hundreds, [3]=thousands)
score_bcd:      .res 4

; Input
joy1_cur:       .res 1
joy1_prev:      .res 1

; Obstacles (MAX 6, each with x_lo, x_hi, y, type, active)
OBJ_MAX = 6
obj_x_lo:   .res OBJ_MAX
obj_x_hi:   .res OBJ_MAX  ; 0 or 1
obj_y:      .res OBJ_MAX
obj_type:   .res OBJ_MAX  ; 0=pothole,1=dog,2=vendor,3=baozi,4=bus,5=barrier
obj_active: .res OBJ_MAX

obj_spawn_timer:  .res 1  ; countdown to next spawn
obj_spawn_speed:  .res 1  ; how often to spawn (decreasing)

; HUD update pending
hud_dirty:    .res 1

; Temp scratch
tmp0:   .res 1
tmp1:   .res 1
tmp2:   .res 1
tmp3:   .res 1

; OAM buffer ($0200)
.segment "OAMBUF"
oam_buf: .res 256

; ---- Constants ----
STATE_TITLE    = 0
STATE_PLAYING  = 1
STATE_CRASHED  = 2
STATE_WIN      = 3
STATE_GAMEOVER = 4

; Lane Y pixel positions (top of bike sprite)
LANE0_Y = 44
LANE1_Y = 92
LANE2_Y = 140

; Player X
PLAYER_X = 40

; Object types
OBJ_POTHOLE = 0
OBJ_DOG     = 1
OBJ_VENDOR  = 2
OBJ_BAOZI   = 3
OBJ_BUS     = 4
OBJ_BARRIER = 5

; Two-lane Y positions (between lanes)
LANE01_Y = 68   ; between lane 0 and lane 1
LANE12_Y = 116  ; between lane 1 and lane 2

; Joypad bits
BTN_A      = %10000000
BTN_B      = %01000000
BTN_SELECT = %00100000
BTN_START  = %00010000
BTN_UP     = %00001000
BTN_DOWN   = %00000100
BTN_LEFT   = %00000010
BTN_RIGHT  = %00000001

; Starting values
TIMER_START = 60    ; seconds
SPEED_START = 1
SPEED_MAX   = 4
SPAWN_START = 90    ; frames between spawns initially
SPAWN_MIN   = 40

; Score tile bases
DIGIT_TILE_BASE = $10   ; tiles $10-$19 = digits 0-9

; ============================================================
; CODE
; ============================================================
.segment "CODE"

; ---- Reset Handler ----
.proc Reset
    sei
    cld
    ldx #$FF
    txs

    ; Disable rendering
    lda #0
    sta PPUCTRL
    sta PPUMASK

    ; Wait for first VBlank
    bit PPUSTATUS
@wait1:
    bit PPUSTATUS
    bpl @wait1

    ; Clear RAM ($00-$07FF)
    lda #0
    ldx #0
@clr:
    sta $0000,x
    sta $0100,x
    sta $0200,x
    sta $0300,x
    sta $0400,x
    sta $0500,x
    sta $0600,x
    sta $0700,x
    inx
    bne @clr

    ; Fill OAM with Y=$FF (hide all sprites)
    lda #$FF
    ldx #0
@hidespr:
    sta oam_buf,x
    inx
    bne @hidespr

    ; Wait for second VBlank
@wait2:
    bit PPUSTATUS
    bpl @wait2

    ; Load palettes
    jsr LoadPalettes

    ; Set up background nametable
    jsr InitNametable

    ; Initialize game
    jsr InitGame

    ; Enable PPU rendering
    ; PPUCTRL: NMI on, sprites=$1000, BG=$0000, 8x8 sprites
    lda #%10001000
    sta PPUCTRL
    ; PPUMASK: show BG, show sprites, no clipping
    lda #%00011110
    sta PPUMASK

    ; Set initial scroll
    lda #0
    sta PPUSCROLL
    sta PPUSCROLL

@main_loop:
    ; Wait for NMI
    lda #0
    sta nmi_flag
@wait_nmi:
    lda nmi_flag
    beq @wait_nmi

    ; Game logic
    jsr ReadJoypad

    lda game_state
    cmp #STATE_PLAYING
    beq @do_play
    cmp #STATE_CRASHED
    beq @do_crash
    cmp #STATE_WIN
    beq @do_win
    cmp #STATE_GAMEOVER
    beq @do_gameover
    ; STATE_TITLE
    jsr HandleTitle
    jmp @end_logic

@do_play:
    jsr UpdatePlayer
    jsr UpdateObstacles
    jsr CheckCollisions
    jsr UpdateTimer
    jsr UpdateSpeed
    jsr DrawGame
    jmp @end_logic

@do_crash:
    jsr UpdateCrash
    jsr DrawGame
    jmp @end_logic

@do_win:
    jsr HandleWin
    jmp @end_logic

@do_gameover:
    jsr HandleGameOver
    jmp @end_logic

@end_logic:
    inc frame_count
    jmp @main_loop
.endproc

; ---- NMI Handler (VBlank) ----
.proc NMI
    pha
    txa
    pha
    tya
    pha

    ; OAM DMA
    lda #$02
    sta OAMDMA

    ; Write PPUCTRL after DMA (NMI enable + sprite table=$1000)
    lda #%10001000
    sta PPUCTRL

    ; Set scroll (must happen after OAM DMA, at end of VBlank preamble)
    lda scroll_lo
    sta PPUSCROLL
    lda #0
    sta PPUSCROLL

    ; Signal main loop
    lda #1
    sta nmi_flag

    pla
    tay
    pla
    tax
    pla
    rti
.endproc

; ---- IRQ ----
.proc IRQ
    rti
.endproc

; ============================================================
; Palettes
; ============================================================
.proc LoadPalettes
    bit PPUSTATUS
    lda #$3F
    sta PPUADDR
    lda #$00
    sta PPUADDR
    ldx #0
@lp:
    lda palette_data,x
    sta PPUDATA
    inx
    cpx #32
    bne @lp
    rts
.endproc

; NES palette values:
; $0F=black, $30=white, $29=deep blue, $19=medium blue
; $16=red,   $28=yellow, $1A=green, $27=tan/brown
; $10=grey,  $00=dark grey
palette_data:
    ; BG palette 0: sky  (black bg, blue shades)
    .byte $0F, $29, $19, $30
    ; BG palette 1: road (black bg, greys)
    .byte $0F, $00, $10, $30
    ; BG palette 2: grass/curb (black, greens)
    .byte $0F, $0A, $1A, $30
    ; BG palette 3: HUD text (black, red, orange, white)
    .byte $0F, $16, $28, $30
    ; Sprite palette 0: player bike (black, red, yellow, white)
    .byte $0F, $16, $28, $30
    ; Sprite palette 1: obstacles/pothole (black, brown, orange, white)
    .byte $0F, $07, $17, $30
    ; Sprite palette 2: dog/cat (black, brown, tan, white)
    .byte $0F, $07, $27, $30
    ; Sprite palette 3: baozi/food (black, orange, yellow, white)
    .byte $0F, $17, $28, $30

; ============================================================
; Init Nametable
; Sets up the scrolling background road layout.
; Nametable 0 ($2000) and Nametable 1 ($2400) both get the
; same road pattern so horizontal scrolling is seamless.
; ============================================================
.proc InitNametable
    ; Draw NT0
    lda #$20
    ldy #$00
    jsr DrawRoadNT

    ; Draw NT1
    lda #$24
    ldy #$00
    jsr DrawRoadNT

    ; Set attribute table for both NTs
    jsr SetAttrNT0
    jsr SetAttrNT1
    rts
.endproc

; Draw road pattern to nametable at high byte A
; Expects: A = high byte ($20 or $24)
.proc DrawRoadNT
    ; Set PPU address = A*256 + 0
    bit PPUSTATUS
    sta PPUADDR
    lda #$00
    sta PPUADDR

    ; 30 rows x 32 cols = 960 tiles
    ; Row layout:
    ;  0-1:  HUD (sky tiles, $01)
    ;  2-3:  Sky ($01)
    ;  4-8:  Lane 0 road ($02)
    ;  9:    Lane divider ($03)
    ; 10-14: Lane 1 road ($02)
    ; 15:    Lane divider ($03)
    ; 16-20: Lane 2 road ($02)
    ; 21-22: Curb ($04)
    ; 23-29: Grass ($05)

    ldx #0          ; row counter
@row_loop:
    ; Determine tile for this row
    cpx #9
    beq @lane_div
    cpx #15
    beq @lane_div
    cpx #4
    bcc @sky_row    ; rows 0-3 = sky
    cpx #21
    bcc @road_row   ; rows 4-20 = road
    cpx #23
    bcc @curb_row   ; rows 21-22 = curb
    ; rows 23-29 = grass
    lda #$05
    jmp @fill_row
@sky_row:
    lda #$01
    jmp @fill_row
@road_row:
    lda #$02
    jmp @fill_row
@lane_div:
    lda #$03
    jmp @fill_row
@curb_row:
    lda #$04
@fill_row:
    ; Fill 32 tiles with this value
    pha
    ldy #32
@col_loop:
    pla
    pha
    sta PPUDATA
    dey
    bne @col_loop
    pla

    inx
    cpx #30
    bne @row_loop

    rts
.endproc

; Set attribute table for NT0
; We want: rows 0-3=palette0(sky), rows 4-20=palette1(road),
;          rows 21-22=palette2(curb), rows 23-29=palette2(grass)
; Attribute table = 64 bytes at $23C0
; Each byte covers 4x4 tile area (2x2 metatile blocks)
; Byte format: %33221100
;   bits 0-1 = top-left 2x2 block palette
;   bits 2-3 = top-right 2x2 block palette
;   bits 4-5 = bottom-left 2x2 block palette
;   bits 6-7 = bottom-right 2x2 block palette
.proc SetAttrNT0
    bit PPUSTATUS
    lda #$23
    sta PPUADDR
    lda #$C0
    sta PPUADDR
    ; 8 rows of 8 bytes = 64 attribute bytes
    ; Row 0 attr (covers tile rows 0-3): all sky = palette 0
    ;   byte = %00000000
    ldy #8
    lda #%00000000
@a0:
    sta PPUDATA
    dey
    bne @a0

    ; Row 1 attr (covers tile rows 4-7): all road = palette 1
    ;   byte = %01010101
    ldy #8
    lda #%01010101
@a1:
    sta PPUDATA
    dey
    bne @a1

    ; Row 2 attr (covers tile rows 8-11): road = palette 1
    ldy #8
    lda #%01010101
@a2:
    sta PPUDATA
    dey
    bne @a2

    ; Row 3 attr (covers tile rows 12-15): road = palette 1
    ldy #8
    lda #%01010101
@a3:
    sta PPUDATA
    dey
    bne @a3

    ; Row 4 attr (covers tile rows 16-19): road = palette 1
    ldy #8
    lda #%01010101
@a4:
    sta PPUDATA
    dey
    bne @a4

    ; Row 5 attr (covers tile rows 20-23): mixed road/curb/grass
    ; rows 20=road(1), 21-22=curb(2), 23=grass(2)
    ; top half (rows 20-21): left=road(1), right=road(1)? 
    ; bottom half (rows 22-23): curb/grass = palette 2
    ; byte = %10100101 = bottom=pal2, top=pal1
    ldy #8
    lda #%10100101
@a5:
    sta PPUDATA
    dey
    bne @a5

    ; Row 6 attr (covers tile rows 24-27): grass = palette 2
    ldy #8
    lda #%10101010
@a6:
    sta PPUDATA
    dey
    bne @a6

    ; Row 7 attr (covers tile rows 28-29+): grass = palette 2
    ldy #8
    lda #%10101010
@a7:
    sta PPUDATA
    dey
    bne @a7

    rts
.endproc

; Set attribute table for NT1 (same as NT0)
.proc SetAttrNT1
    bit PPUSTATUS
    lda #$27
    sta PPUADDR
    lda #$C0
    sta PPUADDR
    ; same values as NT0
    ldy #8
    lda #%00000000
@a0: sta PPUDATA
    dey
    bne @a0
    ldy #8
    lda #%01010101
@a1: sta PPUDATA
    dey
    bne @a1
    ldy #8
    lda #%01010101
@a2: sta PPUDATA
    dey
    bne @a2
    ldy #8
    lda #%01010101
@a3: sta PPUDATA
    dey
    bne @a3
    ldy #8
    lda #%01010101
@a4: sta PPUDATA
    dey
    bne @a4
    ldy #8
    lda #%10100101
@a5: sta PPUDATA
    dey
    bne @a5
    ldy #8
    lda #%10101010
@a6: sta PPUDATA
    dey
    bne @a6
    ldy #8
    lda #%10101010
@a7: sta PPUDATA
    dey
    bne @a7
    rts
.endproc

; ============================================================
; Random - 8-bit LFSR pseudo-random number generator
; Taps at bits 7,5,4,3 (polynomial x^8+x^6+x^5+x^4+1)
; Call to get next pseudo-random byte in A and in rng_seed
; ============================================================
.proc Random
    lda rng_seed
    asl a
    bcc @no_feedback
    eor #$B4        ; feedback polynomial
@no_feedback:
    sta rng_seed
    rts
.endproc

; ============================================================
; InitGame
; ============================================================
.proc InitGame
    lda #1
    sta player_lane
    lda #LANE1_Y
    sta player_y
    sta player_y_tgt

    lda #SPEED_START
    sta game_speed
    lda #120
    sta speed_timer

    lda #TIMER_START
    sta timer_secs
    lda #60
    sta timer_frames

    lda #0
    sta score_bcd+0
    sta score_bcd+1
    sta score_bcd+2
    sta score_bcd+3

    ldx #0
@clr_obj:
    sta obj_active,x
    sta obj_x_lo,x
    sta obj_x_hi,x
    inx
    cpx #OBJ_MAX
    bne @clr_obj

    lda #SPAWN_START
    sta obj_spawn_timer
    lda #SPAWN_START
    sta obj_spawn_speed

    lda #0
    sta scroll_lo
    sta scroll_hi
    sta invincible
    sta crash_timer

    ; Seed RNG from frame_count (non-zero seed required for LFSR)
    lda frame_count
    ora #$01        ; ensure non-zero
    sta rng_seed

    lda #STATE_PLAYING
    sta game_state

    rts
.endproc

; ============================================================
; ReadJoypad
; ============================================================
.proc ReadJoypad
    lda joy1_cur
    sta joy1_prev

    ; Strobe
    lda #1
    sta JOYPAD1
    lda #0
    sta JOYPAD1

    ; Read 8 buttons
    lda #0
    sta joy1_cur
    ldx #8
@read:
    lda JOYPAD1
    lsr a           ; bit 0 → carry
    rol joy1_cur    ; shift into register
    dex
    bne @read
    rts
.endproc

; Helper: button just pressed (cur & ~prev)
; Input: A = button mask
; Output: A = nonzero if just pressed
.proc BtnPressed
    pha
    lda joy1_cur
    sta tmp0
    lda joy1_prev
    eor #$FF
    and tmp0
    pla
    and tmp0        ; A = joy1_cur & ~joy1_prev & mask
    ; Actually redo: return (cur & ~prev) & mask
    ; tmp0 = joy1_cur, we need (joy1_cur & ~joy1_prev) & A
    pha
    lda joy1_prev
    eor #$FF
    and joy1_cur
    sta tmp0
    pla
    and tmp0
    rts
.endproc

; ============================================================
; HandleTitle
; ============================================================
.proc HandleTitle
    ; Wait for START button
    lda joy1_cur
    and #BTN_START
    beq @done
    jsr InitGame
@done:
    rts
.endproc

; ============================================================
; UpdatePlayer
; ============================================================
.proc UpdatePlayer
    ; Handle input
    lda joy1_cur
    and #BTN_UP
    beq @no_up
    lda joy1_prev
    and #BTN_UP
    bne @no_up      ; held, not just pressed
    ; Move up (lane--)
    lda player_lane
    beq @no_up
    dec player_lane
    jsr UpdatePlayerTarget
@no_up:

    lda joy1_cur
    and #BTN_DOWN
    beq @no_down
    lda joy1_prev
    and #BTN_DOWN
    bne @no_down
    ; Move down (lane++)
    lda player_lane
    cmp #2
    beq @no_down
    inc player_lane
    jsr UpdatePlayerTarget
@no_down:

    ; A button: speed boost
    lda joy1_cur
    and #BTN_A
    beq @no_boost
    lda game_speed
    cmp #SPEED_MAX
    bcs @no_boost
    ; Temporarily boost scroll (handled in UpdateSpeed)
@no_boost:

    ; Animate Y toward target (smooth lane change)
    lda player_y
    cmp player_y_tgt
    beq @done

    bcc @move_down_y
    ; player_y > target: move up
    sec
    sbc #2
    cmp player_y_tgt
    bcs @set_y
    lda player_y_tgt
    jmp @set_y
@move_down_y:
    clc
    adc #2
    cmp player_y_tgt
    bcc @set_y
    lda player_y_tgt
@set_y:
    sta player_y

@done:
    ; Decrement invincibility
    lda invincible
    beq @inv_done
    dec invincible
@inv_done:
    rts
.endproc

.proc UpdatePlayerTarget
    lda player_lane
    cmp #0
    bne @try1
    lda #LANE0_Y
    sta player_y_tgt
    rts
@try1:
    cmp #1
    bne @try2
    lda #LANE1_Y
    sta player_y_tgt
    rts
@try2:
    lda #LANE2_Y
    sta player_y_tgt
    rts
.endproc

; ============================================================
; UpdateObstacles
; ============================================================
.proc UpdateObstacles
    ; Move all active obstacles
    ldx #0
@loop:
    lda obj_active,x
    beq @next

    ; Move left by game_speed
    lda obj_x_lo,x
    sec
    sbc game_speed
    sta obj_x_lo,x
    bcs @no_borrow
    ; Borrow from high byte
    lda obj_x_hi,x
    beq @deactivate ; hi=0, wrapping below 0 → off screen left
    dec obj_x_hi,x
    jmp @no_borrow
@deactivate:
    lda #0
    sta obj_active,x
    jmp @next
@no_borrow:
    ; Check if off screen left (x_hi=0 and x_lo < 8)
    lda obj_x_hi,x
    bne @next
    lda obj_x_lo,x
    cmp #8
    bcs @next
    lda #0
    sta obj_active,x
@next:
    inx
    cpx #OBJ_MAX
    bne @loop

    ; Spawn timer
    dec obj_spawn_timer
    bne @done
    ; Reset spawn timer
    lda obj_spawn_speed
    sta obj_spawn_timer
    ; Try to spawn a new obstacle
    jsr SpawnObstacle
@done:
    rts
.endproc

; Spawn a new obstacle in a free slot
.proc SpawnObstacle
    ; Find free slot
    ldx #0
@find:
    lda obj_active,x
    beq @found
    inx
    cpx #OBJ_MAX
    bne @find
    rts     ; no free slot
@found:
    lda #1
    sta obj_active,x

    ; X position = 270 = $010E
    lda #$0E
    sta obj_x_lo,x
    lda #$01
    sta obj_x_hi,x

    ; Save slot index in tmp1
    stx tmp1

    ; --- Pick random TYPE ---
    ; Use LFSR: get random byte
    jsr Random          ; A = random byte, also updates rng_seed
    sta tmp2            ; save for type selection

    ; Type selection:
    ; 0-2 (3/8 = ~37.5%) → OBJ_BAOZI
    ; 3-4 (2/8 = 25%)    → OBJ_POTHOLE
    ; 5   (1/8 = 12.5%)  → OBJ_DOG
    ; 6   (1/8 = 12.5%)  → OBJ_VENDOR
    ; 7   (1/8 = 12.5%)  → OBJ_BUS or OBJ_BARRIER (alternating)

    and #$07            ; 0-7
    cmp #3
    bcs @not_baozi
    ; type = OBJ_BAOZI
    ldx tmp1
    lda #OBJ_BAOZI
    sta obj_type,x
    jmp @pick_lane

@not_baozi:
    cmp #5
    bcs @not_pothole
    ; type = OBJ_POTHOLE
    ldx tmp1
    lda #OBJ_POTHOLE
    sta obj_type,x
    jmp @pick_lane

@not_pothole:
    cmp #6
    bcs @not_dog
    ; type = OBJ_DOG
    ldx tmp1
    lda #OBJ_DOG
    sta obj_type,x
    jmp @pick_lane

@not_dog:
    cmp #7
    bcs @not_vendor
    ; type = OBJ_VENDOR
    ldx tmp1
    lda #OBJ_VENDOR
    sta obj_type,x
    jmp @pick_lane

@not_vendor:
    ; type = OBJ_BUS or OBJ_BARRIER (alternate using rng_seed LSB)
    lda rng_seed
    and #$01
    beq @pick_bus
    ldx tmp1
    lda #OBJ_BARRIER
    sta obj_type,x
    jmp @pick_two_lane

@pick_bus:
    ldx tmp1
    lda #OBJ_BUS
    sta obj_type,x
    ; fall through to @pick_two_lane

@pick_two_lane:
    ; Two-lane blockers: position between lanes using LFSR
    jsr Random
    and #$01
    beq @two_lane_01
    ; between lane1 and lane2
    ldx tmp1
    lda #LANE12_Y
    sta obj_y,x
    rts
@two_lane_01:
    ldx tmp1
    lda #LANE01_Y
    sta obj_y,x
    rts

@pick_lane:
    ; Single lane: use LFSR to pick 0,1,2
    jsr Random
    ; Map 0-255 to 0,1,2 via modulo 3
    ; Simple approach: use bits 0-1, remap 3→2
    and #$03
    cmp #$03
    bne @lane_ok
    ; 3 → 0 (just wrap)
    lda #0
@lane_ok:
    ; A = lane 0,1,2 → convert to Y
    cmp #0
    bne @try1
    ldx tmp1
    lda #LANE0_Y
    sta obj_y,x
    rts
@try1:
    cmp #1
    bne @try2
    ldx tmp1
    lda #LANE1_Y
    sta obj_y,x
    rts
@try2:
    ldx tmp1
    lda #LANE2_Y
    sta obj_y,x
    rts
.endproc

; ============================================================
; CheckCollisions
; ============================================================
.proc CheckCollisions
    ; Don't check if invincible
    lda invincible
    bne @done

    ldx #0
@loop:
    lda obj_active,x
    beq @next

    ; Check X overlap: player is at X=PLAYER_X..PLAYER_X+15
    ; Obstacle is at obj_x..obj_x+15
    ; Only check if obj_x_hi=0 (on screen)
    lda obj_x_hi,x
    bne @next

    lda obj_x_lo,x
    ; Need obj_x < PLAYER_X+16 AND obj_x+16 > PLAYER_X
    clc
    adc #16
    cmp #PLAYER_X
    bcc @next   ; obj right edge < player left edge
    lda obj_x_lo,x
    cmp #(PLAYER_X+16)
    bcs @next   ; obj left edge >= player right edge

    ; Check Y overlap
    ; For bus/barrier (two-lane blockers), use height 32 to cover both lanes
    ; Otherwise use height 12 for single-lane objects
    lda player_y
    clc
    adc #16         ; A = player_y + 16
    cmp obj_y,x
    bcc @next       ; if player_y+16 <= obj_y, no overlap
    beq @next

    ; Determine object height
    lda obj_type,x
    cmp #OBJ_BUS
    beq @tall_obj
    cmp #OBJ_BARRIER
    beq @tall_obj
    ; Single-lane height
    lda obj_y,x
    clc
    adc #12         ; A = obj_y + 12
    jmp @y_check_done
@tall_obj:
    ; Two-lane height: covers ~48 pixels
    lda obj_y,x
    clc
    adc #32         ; A = obj_y + 32
@y_check_done:
    cmp player_y
    bcc @next       ; if obj_bottom <= player_y, no overlap
    beq @next
    jmp @check_type

@next:
    inx
    cpx #OBJ_MAX
    bne @loop
    jmp @done

@check_type:
    ; Check if baozi (collectible) or obstacle
    lda obj_type,x
    cmp #OBJ_BAOZI
    bne @hit_obstacle

    ; Collect baozi!
    lda #0
    sta obj_active,x
    jsr AddScore    ; +10 points
    jmp @next_after_hit

@hit_obstacle:
    ; Crash!
    lda #0
    sta obj_active,x
    lda #90
    sta crash_timer
    lda #STATE_CRASHED
    sta game_state
    ; Lose 5 seconds
    lda timer_secs
    cmp #5
    bcc @min_time
    sec
    sbc #5
    sta timer_secs
    jmp @next_after_hit
@min_time:
    lda #1
    sta timer_secs

@next_after_hit:
    inx
    cpx #OBJ_MAX
    bne @loop

@done:
    rts
.endproc

; Add 10 to BCD score
.proc AddScore
    ; score_bcd[0] = ones digit
    lda score_bcd+0
    clc
    adc #10
    cmp #100
    bcc @done0
    sec
    sbc #100
    ; Carry to hundreds
    lda score_bcd+1
    clc
    adc #1
    cmp #10
    bcc @done1
    lda #0
    sta score_bcd+1
    lda score_bcd+2
    clc
    adc #1
    cmp #10
    bcc @done2
    lda #0
    sta score_bcd+2
    lda score_bcd+3
    clc
    adc #1
    cmp #10
    bcc @done3
    lda #9  ; cap at 9999
@done3:
    sta score_bcd+3
    jmp @done0
@done2:
    sta score_bcd+2
    jmp @done0
@done1:
    sta score_bcd+1
@done0:
    sta score_bcd+0
    rts
.endproc

; Add speed bonus to score (1 point × speed per frame, every 60 frames)
.proc AddSpeedScore
    lda game_speed
    cmp #1
    bcc @done
    lda score_bcd+0
    clc
    adc game_speed
    cmp #10
    bcc @s0_ok
    sec
    sbc #10
    lda score_bcd+1
    clc
    adc #1
    cmp #10
    bcc @s1_ok
    lda #0
    sta score_bcd+1
    jmp @s0_ok
@s1_ok:
    sta score_bcd+1
@s0_ok:
    sta score_bcd+0
@done:
    rts
.endproc

; ============================================================
; UpdateTimer
; ============================================================
.proc UpdateTimer
    dec timer_frames
    bne @done

    lda #60
    sta timer_frames

    ; Decrement seconds
    lda timer_secs
    beq @gameover
    dec timer_secs
    bne @done

    ; Timer hit zero - check if we won (simplified: after 60sec you win)
    ; In a full game, you'd check if player reached the school gate sprite
    lda #STATE_WIN
    sta game_state
    jmp @done

@gameover:
    lda #STATE_GAMEOVER
    sta game_state

    ; Add speed score every second
@done:
    jsr AddSpeedScore
    rts
.endproc

; ============================================================
; UpdateSpeed
; ============================================================
.proc UpdateSpeed
    ; Scroll the background
    lda scroll_lo
    clc
    adc game_speed
    ; A button: extra speed
    lda joy1_cur
    and #BTN_A
    beq @no_turbo
    lda scroll_lo
    clc
    adc #1          ; +1 extra
    sta scroll_lo
    jmp @done
@no_turbo:
    lda scroll_lo
    clc
    adc game_speed
    ; Check for carry (scroll_lo wraps 255→0, toggle nametable)
    bcc @no_carry
    ; Wrapped: toggle high bit of scroll / nametable select
    lda scroll_hi
    eor #1
    sta scroll_hi
@no_carry:
    sta scroll_lo

@done:
    ; Increase speed over time
    dec speed_timer
    bne @done2
    lda #120
    sta speed_timer
    lda game_speed
    cmp #SPEED_MAX
    bcs @done2
    inc game_speed
    ; Also increase spawn frequency
    lda obj_spawn_speed
    cmp #SPAWN_MIN
    beq @done2
    sec
    sbc #10
    cmp #SPAWN_MIN
    bcs @set_spawn
    lda #SPAWN_MIN
@set_spawn:
    sta obj_spawn_speed
@done2:
    rts
.endproc

; ============================================================
; UpdateCrash
; ============================================================
.proc UpdateCrash
    dec crash_timer
    bne @done
    ; Respawn
    lda #60
    sta invincible
    lda #STATE_PLAYING
    sta game_state
@done:
    rts
.endproc

; ============================================================
; HandleWin
; ============================================================
.proc HandleWin
    ; Wait for any button to restart
    lda joy1_cur
    and #(BTN_START | BTN_A)
    beq @done
    jsr InitGame
@done:
    rts
.endproc

; ============================================================
; HandleGameOver
; ============================================================
.proc HandleGameOver
    lda joy1_cur
    and #(BTN_START | BTN_A)
    beq @done
    jsr InitGame
@done:
    rts
.endproc

; ============================================================
; DrawGame - Update OAM buffer with all sprites
; ============================================================
.proc DrawGame
    ; Clear all sprite slots first (Y=$FF = hidden)
    ldx #0
    lda #$FF
@clr:
    sta oam_buf,x
    inx
    bne @clr

    ; Draw player bike (sprites 0-3, OAM slots 0-3 = bytes 0-15)
    ldx #0
    jsr DrawBike

    ; Draw obstacles (OAM slots 4+, starts at byte 16)
    ldx #16
    jsr DrawObstacles

    ; Draw HUD digits (OAM slot starting at byte 48)
    ldx #48
    jsr DrawHUD

    rts
.endproc

; Draw bike at OAM offset X
; Uses player_y for Y, PLAYER_X for X
; Flashes when invincible (skip every other frame)
.proc DrawBike
    lda invincible
    beq @draw
    lda frame_count
    and #$04
    bne @draw
    rts         ; blink: skip drawing

@draw:
    lda game_state
    cmp #STATE_CRASHED
    bne @normal

    ; Crash state: draw crash star
    lda player_y
    sta oam_buf,x   ; Y
    inx
    lda #$0E        ; crash star tile
    sta oam_buf,x
    inx
    lda #$00        ; palette 0
    sta oam_buf,x
    inx
    lda #PLAYER_X
    sta oam_buf,x
    inx
    rts

@normal:
    ; Sprite 0: top-left (tile $00)
    lda player_y
    sta oam_buf,x
    inx
    lda #$00
    sta oam_buf,x
    inx
    lda #$00        ; palette 0, no flip
    sta oam_buf,x
    inx
    lda #PLAYER_X
    sta oam_buf,x
    inx

    ; Sprite 1: top-right (tile $01)
    lda player_y
    sta oam_buf,x
    inx
    lda #$01
    sta oam_buf,x
    inx
    lda #$00
    sta oam_buf,x
    inx
    lda #(PLAYER_X+8)
    sta oam_buf,x
    inx

    ; Sprite 2: bottom-left (tile $02)
    lda player_y
    clc
    adc #8
    sta oam_buf,x
    inx
    lda #$02
    sta oam_buf,x
    inx
    lda #$00
    sta oam_buf,x
    inx
    lda #PLAYER_X
    sta oam_buf,x
    inx

    ; Sprite 3: bottom-right (tile $03)
    lda player_y
    clc
    adc #8
    sta oam_buf,x
    inx
    lda #$03
    sta oam_buf,x
    inx
    lda #$00
    sta oam_buf,x
    inx
    lda #(PLAYER_X+8)
    sta oam_buf,x
    inx

    rts
.endproc

; Draw all active obstacles, OAM offset in X
.proc DrawObstacles
    stx tmp0        ; save OAM offset
    ldy #0          ; obstacle index
@loop:
    lda obj_active,y
    beq @skip_to_next

    ; Only draw if on screen (x_hi = 0)
    lda obj_x_hi,y
    beq @draw_it
@skip_to_next:
    jmp @next
@draw_it:
    ldx tmp0
    ; Each obstacle uses 4 bytes per sprite: Y, tile, attr, X

    lda obj_type,y
    cmp #OBJ_BAOZI
    bne @not_baozi

    ; Baozi: single 8x8 sprite, tile $05, palette 3
    lda obj_y,y
    sta oam_buf,x
    inx
    lda #$05
    sta oam_buf,x
    inx
    lda #$03        ; palette 3
    sta oam_buf,x
    inx
    lda obj_x_lo,y
    sta oam_buf,x
    inx
    jmp @update_offset

@not_baozi:
    cmp #OBJ_POTHOLE
    bne @not_pothole

    ; Pothole: single 8x8, tile $04, palette 1
    lda obj_y,y
    sta oam_buf,x
    inx
    lda #$04
    sta oam_buf,x
    inx
    lda #$01        ; palette 1
    sta oam_buf,x
    inx
    lda obj_x_lo,y
    sta oam_buf,x
    inx
    jmp @update_offset

@not_pothole:
    cmp #OBJ_DOG
    bne @not_dog

    ; Dog: 2x2 tiles ($06-$09), palette 2
    ; TL
    lda obj_y,y
    sta oam_buf,x
    inx
    lda #$06
    sta oam_buf,x
    inx
    lda #$02
    sta oam_buf,x
    inx
    lda obj_x_lo,y
    sta oam_buf,x
    inx
    ; TR
    lda obj_y,y
    sta oam_buf,x
    inx
    lda #$07
    sta oam_buf,x
    inx
    lda #$02
    sta oam_buf,x
    inx
    lda obj_x_lo,y
    clc
    adc #8
    sta oam_buf,x
    inx
    ; BL
    lda obj_y,y
    clc
    adc #8
    sta oam_buf,x
    inx
    lda #$08
    sta oam_buf,x
    inx
    lda #$02
    sta oam_buf,x
    inx
    lda obj_x_lo,y
    sta oam_buf,x
    inx
    ; BR
    lda obj_y,y
    clc
    adc #8
    sta oam_buf,x
    inx
    lda #$09
    sta oam_buf,x
    inx
    lda #$02
    sta oam_buf,x
    inx
    lda obj_x_lo,y
    clc
    adc #8
    sta oam_buf,x
    inx
    jmp @update_offset

@not_dog:
    cmp #OBJ_VENDOR
    bne @not_vendor

    ; OBJ_VENDOR: cart 2x2 ($0A-$0D), palette 1
    ; TL
    lda obj_y,y
    sta oam_buf,x
    inx
    lda #$0A
    sta oam_buf,x
    inx
    lda #$01
    sta oam_buf,x
    inx
    lda obj_x_lo,y
    sta oam_buf,x
    inx
    ; TR
    lda obj_y,y
    sta oam_buf,x
    inx
    lda #$0B
    sta oam_buf,x
    inx
    lda #$01
    sta oam_buf,x
    inx
    lda obj_x_lo,y
    clc
    adc #8
    sta oam_buf,x
    inx
    ; BL
    lda obj_y,y
    clc
    adc #8
    sta oam_buf,x
    inx
    lda #$0C
    sta oam_buf,x
    inx
    lda #$01
    sta oam_buf,x
    inx
    lda obj_x_lo,y
    sta oam_buf,x
    inx
    ; BR
    lda obj_y,y
    clc
    adc #8
    sta oam_buf,x
    inx
    lda #$0D
    sta oam_buf,x
    inx
    lda #$01
    sta oam_buf,x
    inx
    lda obj_x_lo,y
    clc
    adc #8
    sta oam_buf,x
    inx
    jmp @update_offset

@not_vendor:
    cmp #OBJ_BUS
    bne @not_bus

    ; OBJ_BUS: bus 2x2 ($13-$16), palette 0 (use sprite pal 0 = blue)
    ; TL
    lda obj_y,y
    sta oam_buf,x
    inx
    lda #$13
    sta oam_buf,x
    inx
    lda #$00
    sta oam_buf,x
    inx
    lda obj_x_lo,y
    sta oam_buf,x
    inx
    ; TR
    lda obj_y,y
    sta oam_buf,x
    inx
    lda #$14
    sta oam_buf,x
    inx
    lda #$00
    sta oam_buf,x
    inx
    lda obj_x_lo,y
    clc
    adc #8
    sta oam_buf,x
    inx
    ; BL
    lda obj_y,y
    clc
    adc #8
    sta oam_buf,x
    inx
    lda #$15
    sta oam_buf,x
    inx
    lda #$00
    sta oam_buf,x
    inx
    lda obj_x_lo,y
    sta oam_buf,x
    inx
    ; BR
    lda obj_y,y
    clc
    adc #8
    sta oam_buf,x
    inx
    lda #$16
    sta oam_buf,x
    inx
    lda #$00
    sta oam_buf,x
    inx
    lda obj_x_lo,y
    clc
    adc #8
    sta oam_buf,x
    inx
    jmp @update_offset

@not_bus:
    ; OBJ_BARRIER: 2x2 ($17-$1A), palette 3 (orange/warning)
    ; TL
    lda obj_y,y
    sta oam_buf,x
    inx
    lda #$17
    sta oam_buf,x
    inx
    lda #$03
    sta oam_buf,x
    inx
    lda obj_x_lo,y
    sta oam_buf,x
    inx
    ; TR
    lda obj_y,y
    sta oam_buf,x
    inx
    lda #$18
    sta oam_buf,x
    inx
    lda #$03
    sta oam_buf,x
    inx
    lda obj_x_lo,y
    clc
    adc #8
    sta oam_buf,x
    inx
    ; BL
    lda obj_y,y
    clc
    adc #8
    sta oam_buf,x
    inx
    lda #$19
    sta oam_buf,x
    inx
    lda #$03
    sta oam_buf,x
    inx
    lda obj_x_lo,y
    sta oam_buf,x
    inx
    ; BR
    lda obj_y,y
    clc
    adc #8
    sta oam_buf,x
    inx
    lda #$1A
    sta oam_buf,x
    inx
    lda #$03
    sta oam_buf,x
    inx
    lda obj_x_lo,y
    clc
    adc #8
    sta oam_buf,x
    inx

@update_offset:
    stx tmp0        ; update saved OAM offset

@next:
    iny
    cpy #OBJ_MAX
    beq @done
    jmp @loop
@done:
    rts
.endproc

; Draw HUD: TIME and SCORE using sprites
; OAM offset in X
.proc DrawHUD
    ; "TIME:" label at top of screen
    ; We'll use BG tiles for static labels (written once during init)
    ; Here draw the digit sprites for timer and score

    ; Timer digits (2 digits: tens, ones)
    ; Position: top-left area, Y=0 (just above road), X=64,72
    ; tens digit
    lda timer_secs
    ; BCD tens = secs / 10
    sta tmp0
    lda #0
    sta tmp1
@div10:
    lda tmp0
    cmp #10
    bcc @div_done
    sec
    sbc #10
    sta tmp0
    inc tmp1
    jmp @div10
@div_done:
    ; tmp1 = tens, tmp0 = ones

    ; Draw tens digit sprite
    lda #0          ; Y = 0 (top of screen)
    sta oam_buf,x
    inx
    lda tmp1
    clc
    adc #DIGIT_TILE_BASE    ; tile $10 + digit
    sta oam_buf,x
    inx
    lda #$03        ; palette 3 (HUD)
    sta oam_buf,x
    inx
    lda #64         ; X position
    sta oam_buf,x
    inx

    ; Draw ones digit sprite
    lda #0
    sta oam_buf,x
    inx
    lda tmp0
    clc
    adc #DIGIT_TILE_BASE
    sta oam_buf,x
    inx
    lda #$03
    sta oam_buf,x
    inx
    lda #72
    sta oam_buf,x
    inx

    ; Score digits (4 digits)
    ; Positions: X = 160, 168, 176, 184
    ; score_bcd[3]=thousands, [2]=hundreds, [1]=tens, [0]=ones

    lda #0          ; Y
    sta oam_buf,x
    inx
    lda score_bcd+3
    clc
    adc #DIGIT_TILE_BASE
    sta oam_buf,x
    inx
    lda #$03
    sta oam_buf,x
    inx
    lda #160
    sta oam_buf,x
    inx

    lda #0
    sta oam_buf,x
    inx
    lda score_bcd+2
    clc
    adc #DIGIT_TILE_BASE
    sta oam_buf,x
    inx
    lda #$03
    sta oam_buf,x
    inx
    lda #168
    sta oam_buf,x
    inx

    lda #0
    sta oam_buf,x
    inx
    lda score_bcd+1
    clc
    adc #DIGIT_TILE_BASE
    sta oam_buf,x
    inx
    lda #$03
    sta oam_buf,x
    inx
    lda #176
    sta oam_buf,x
    inx

    lda #0
    sta oam_buf,x
    inx
    lda score_bcd+0
    clc
    adc #DIGIT_TILE_BASE
    sta oam_buf,x
    inx
    lda #$03
    sta oam_buf,x
    inx
    lda #184
    sta oam_buf,x
    inx

    rts
.endproc

; ============================================================
; CHR Data (embedded in CHARS segment)
; ============================================================
.segment "CHARS"
.incbin "../chr/tiles.chr"

; ============================================================
; Vectors
; ============================================================
.segment "VECTORS"
    .word NMI
    .word Reset
    .word IRQ
