GBDK_HOME = $(HOME)/gbdk/
LCC = $(GBDK_HOME)bin/lcc
PNG2ASSET = $(GBDK_HOME)bin/png2asset

LCCFLAGS = -Wm-yc

PROJECTNAME = nickgame
BINS = $(PROJECTNAME).gb

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
	src/ch2_baozi.c src/ch2_textbook.c
CSOURCES := $(filter-out $(GEN_SOURCES),$(wildcard src/*.c))
ASMSOURCES := $(wildcard src/*.s)

all: $(BINS)

src/title_data.c: assets/title_screen.png
	$(PNG2ASSET) $< -map -use_map_attributes -o $@

$(BINS): $(GEN_SOURCES) $(CSOURCES) $(ASMSOURCES)
	$(LCC) $(LCCFLAGS) -o $@ $(GEN_SOURCES) $(CSOURCES) $(ASMSOURCES)

web: $(BINS)
	cp $(BINS) web/$(BINS)

serve: web
	python3 -m http.server 8080 -d web

clean:
	rm -f *.o *.lst *.map *.gb *.ihx *.sym *.cdb *.adb *.asm *.noi *.rst
	rm -f src/*.o src/*.lst src/*.asm src/*.sym src/*.rst src/*.noi
	rm -f src/title_data.c src/title_data.h
	rm -f web/$(BINS)

.PHONY: all clean web serve
