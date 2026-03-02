GBDK_HOME = $(HOME)/gbdk/
LCC = $(GBDK_HOME)bin/lcc
PNG2ASSET = $(GBDK_HOME)bin/png2asset

LCCFLAGS = -Wm-yc

PROJECTNAME = nickgame
BINS = $(PROJECTNAME).gb

CSOURCES := $(wildcard src/*.c)
ASMSOURCES := $(wildcard src/*.s)

all: $(BINS)

src/title_data.c: assets/title_screen.png
	$(PNG2ASSET) $< -map -use_map_attributes -o $@

$(BINS): src/title_data.c $(CSOURCES) $(ASMSOURCES)
	$(LCC) $(LCCFLAGS) -o $@ src/title_data.c $(CSOURCES) $(ASMSOURCES)

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
