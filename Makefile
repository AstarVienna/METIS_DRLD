.SECONDEXPANSION:

METIS_DRLD.pdf: \
	METIS_DRLD.tex \
	$$(wildcard *.tex) \
	$$(wildcard *.png)
	@texfot pdflatex $< -file-line-error -shell-escape -jobname=$(subst, .pdf,,$@) -halt-on-error -synctex=1 -interaction=nonstopmode $@
	biber METIS_DRLD
	@texfot pdflatex $< -file-line-error -shell-escape -jobname=$(subst, .pdf,,$@) -halt-on-error -synctex=1 -interaction=nonstopmode $@
	@texfot pdflatex $< -file-line-error -shell-escape -jobname=$(subst, .pdf,,$@) -halt-on-error -synctex=1 -interaction=nonstopmode $@

clean:
	rm *.out *.aux *.log *.lof *.bbl *.bcf *.run.xml *.toc *.blg *.lot METIS_DRLD.pdf
