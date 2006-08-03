# SWAML PFC Makefile

DESTDIR =
NAME = swaml
PDFVIEWER = evince

all:	clean $(NAME).pdf

$(NAME).pdf:	
	pdflatex $(NAME).tex
	bibtex $(NAME)
	pdflatex $(NAME).tex
	bibtex $(NAME)
	pdflatex $(NAME).tex

view:	$(NAME).pdf
	$(PDFVIEWER) $(NAME).pdf &

src:
	python2.4 python2text.py ../../swaml/trunk/*.py #output dir?

clean:
	rm -f *.aux *.log *.dvi *.toc *.pdf *.bbl *.blg *.lof
	rm -f `find . -name "*.backup"`
	rm -f `find . -name "*~"`

