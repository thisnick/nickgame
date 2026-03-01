ROM = nickgame.nes

.PHONY: all clean web serve

all: $(ROM)

$(ROM): game.cfg src/main.fab
	nesfab game.cfg

web: $(ROM)
	cp $(ROM) web/$(ROM)

clean:
	rm -f $(ROM) web/$(ROM)

serve: web
	python3 -m http.server 8080
