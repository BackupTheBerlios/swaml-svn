# SWAML Makefile

NAME=SWAML
DESTDIR =
ZIP=gzip
DOCDIR=doc
PYTHON=python

install:
	cp setup/swaml $(DESTDIR)/usr/bin/swaml
	chmod 755 $(DESTDIR)/usr/bin/swaml
	mkdir -p $(DESTDIR)/usr/share/swaml/
	cp -r __init__.py run.py src includes $(DESTDIR)/usr/share/swaml/
	mkdir -p $(DESTDIR)/usr/share/doc/swaml/examples
	cp -r config $(DESTDIR)/usr/share/doc/swaml/examples
	mkdir tmp
	$(ZIP) -9 -c manpages/swaml.1 > tmp/swaml.1.gz
	mv tmp/swaml.1.gz $(DESTDIR)/usr/share/man/man1/
	rm -r tmp

uninstall:
	rm -f $(DESTDIR)/usr/bin/swaml
	rm -rf $(DESTDIR)/usr/share/swaml
	rm -rf $(DESTDIR)/usr/share/doc/swaml/examples
	rm -f $(DESTDIR)/usr/share/man/man1/swaml.1.gz

gendoc:
	rm -rf $(DOCDIR)
	mkdir -p $(DOCDIR)
	epydoc -n $(NAME) -o $(DOCDIR) --html __init__.py run.py src/swaml/

pubdoc:	gendoc
	scp -r $(DOCDIR)/* $(USER)@shell.berlios.de:/home/groups/swaml/htdocs/$(DOCDIR)/

tests:
	@echo $(NAME) unittests
	@echo ---------------
	#$(PYTHON) test/swaml/rdf/swse.py
	#$(PYTHON) test/swaml/rdf/sindice.py

clean:
	rm -rf archive/
	rm -rf $(DOCDIR)
	rm -f `find . -name "*~"`
	rm -f `find . -name "*.pyc"`

