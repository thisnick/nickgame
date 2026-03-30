GBDK_HOME = $(HOME)/gbdk/
LCC = $(GBDK_HOME)bin/lcc
PNG2ASSET = $(GBDK_HOME)bin/png2asset

LCCFLAGS = -Wm-yc -Wm-yt0x19 -Wm-yoA -Wm-ya0 -autobank -Wb-ext=.rel

PROJECTNAME = nickgame
BINS = $(PROJECTNAME).gb
OBJDIR = obj

# Generated asset sources (excluded from wildcard, listed explicitly)
GEN_SOURCES = src/title_data.c src/ch1_bg_data.c src/ch1_gameplay_bg_data.c \
	src/ch1_baby_sitting.c src/ch1_baby_calc.c \
	src/ch1_baby_crawl1.c src/ch1_baby_crawl2.c \
	src/ch1_obj_calc.c src/ch1_obj_book.c src/ch1_obj_ball.c \
	src/ch2_street_bg_data.c \
	src/ch2_bike_frame1.c src/ch2_bike_frame2.c \
	src/ch2_pothole.c src/ch2_puddle.c \
	src/ch2_dog_frame1.c src/ch2_dog_frame2.c \
	src/ch2_vendor.c src/ch2_bus.c src/ch2_cyclist.c \
	src/ch2_baozi.c src/ch2_textbook.c \
	src/ch3_airport_data.c src/ch3_city_data.c src/ch3_campus_data.c \
	src/ch3_player_down1.c src/ch3_player_down2.c \
	src/ch3_player_up1.c src/ch3_player_up2.c \
	src/ch3_npc_helper.c src/ch3_npc_student.c
CSOURCES := $(filter-out $(GEN_SOURCES),$(wildcard src/*.c))
ASMSOURCES := $(wildcard src/*.s)

ALL_SOURCES = $(GEN_SOURCES) $(CSOURCES) $(ASMSOURCES)
OBJS = $(patsubst src/%.c,$(OBJDIR)/%.o,$(filter %.c,$(ALL_SOURCES))) \
       $(patsubst src/%.s,$(OBJDIR)/%.o,$(filter %.s,$(ALL_SOURCES)))

all: $(BINS)

$(OBJDIR):
	mkdir -p $(OBJDIR)

src/title_data.c: assets/title_screen.png
	$(PNG2ASSET) $< -map -use_map_attributes -o $@

$(OBJDIR)/%.o: src/%.c | $(OBJDIR)
	$(LCC) $(LCCFLAGS) -c -o $@ $<

$(OBJDIR)/%.o: src/%.s | $(OBJDIR)
	$(LCC) $(LCCFLAGS) -c -o $@ $<

$(BINS): $(OBJS)
	$(LCC) $(LCCFLAGS) -o $@ $(OBJS)

web: $(BINS)
	cp $(BINS) web/$(BINS)

serve: web
	python3 -m http.server 8080 -d web

clean:
	rm -f *.o *.lst *.map *.gb *.ihx *.sym *.cdb *.adb *.asm *.noi *.rst
	rm -f src/*.o src/*.lst src/*.asm src/*.sym src/*.rst src/*.noi
	rm -rf $(OBJDIR)
	rm -f src/title_data.c src/title_data.h
	rm -f web/$(BINS)

.PHONY: all clean web serve
