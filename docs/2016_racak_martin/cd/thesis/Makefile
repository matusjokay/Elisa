FILE = thesis

LATEXMK_OPTIONS = -pdf -shell-escape -synctex=1 -interaction=nonstopmode -silent
LINE_WIDTH = error_line=240 half_error_line=160 max_print_line=240

all: pdf

pdf:
	$(LINE_WIDTH) latexmk $(LATEXMK_OPTIONS) $(FILE).tex

watch:
	$(LINE_WIDTH) latexmk -pvc $(LATEXMK_OPTIONS) $(FILE).tex

clean:
	latexmk -C

refresh: clean pdf

.PHONY: all pdf clean refresh
