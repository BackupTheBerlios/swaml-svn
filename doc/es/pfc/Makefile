# SWAML PFC Makefile

DESTDIR =

all:	clean
	pdflatex swaml.tex
	bibtex swaml
	pdflatex swaml.tex
	bibtex swaml
	pdflatex swaml.tex

src:
	python2.4 python2text.py ../../swaml/trunk/*.py #output dir?

clean:
	rm -f *.aux *.log *.dvi *.toc *.pdf *.bbl *.blg *.lof
	rm -f `find . -name "*.backup"`
	rm -f `find . -name "*~"`

