CC65   = /tmp/cc65/bin
CA65   = $(CC65)/ca65
LD65   = $(CC65)/ld65

ROM    = nickgame.nes
SRC    = src/main.s
CFG    = cfg/nrom256.cfg
CHR    = chr/tiles.chr
OBJ    = build/main.o

.PHONY: all clean run

all: $(ROM)

# Generate CHR data
$(CHR): tools/make_chr.py
	@mkdir -p chr
	python3 tools/make_chr.py

# Assemble
$(OBJ): $(SRC) $(CHR)
	@mkdir -p build
	$(CA65) -o $(OBJ) $(SRC)

# Link
$(ROM): $(OBJ) $(CFG)
	$(LD65) -o $(ROM) -C $(CFG) $(OBJ)
	@echo "Build successful: $(ROM)"
	@ls -lh $(ROM)

clean:
	rm -rf build $(ROM) chr/tiles.chr

# Serve browser emulator
serve:
	python3 -m http.server 8080
