GBDK_HOME = $(HOME)/gbdk/
LCC = $(GBDK_HOME)bin/lcc

PROJECTNAME = nickgame
BINS = $(PROJECTNAME).gb

CSOURCES := $(wildcard src/*.c)
ASMSOURCES := $(wildcard src/*.s)

all: $(BINS)

$(BINS): $(CSOURCES) $(ASMSOURCES)
	$(LCC) -o $@ $(CSOURCES) $(ASMSOURCES)

web: $(BINS)
	cp $(BINS) web/$(BINS)

serve: web
	python3 -m http.server 8080 -d web

clean:
	rm -f *.o *.lst *.map *.gb *.ihx *.sym *.cdb *.adb *.asm *.noi *.rst
	rm -f src/*.o src/*.lst src/*.asm src/*.sym src/*.rst src/*.noi
	rm -f web/$(BINS)

.PHONY: all clean web serve
