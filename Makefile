METIS_DRLD.pdf: \
	METIS_DRLD.tex \
	$$(wildcard *.tex) \
	$$(wildcard *.pdf) \
	$$(wildcard *.png)
	pdflatex $< -file-line-error -shell-escape -jobname=$(subst, .pdf,,$@) -halt-on-error -synctex=1 -interaction=nonstopmode $@
	biber METIS_DRLD
	pdflatex $< -file-line-error -shell-escape -jobname=$(subst, .pdf,,$@) -halt-on-error -synctex=1 -interaction=nonstopmode $@
	pdflatex $< -file-line-error -shell-escape -jobname=$(subst, .pdf,,$@) -halt-on-error -synctex=1 -interaction=nonstopmode $@
