.SECONDEXPANSION:

tikz.pdf: \
	all.tex \
	$$(wildcard *.tex)
	@texfot pdflatex $< -file-line-error -shell-escape -jobname=$(subst .pdf,,$@) -halt-on-error -synctex=1 -interaction=nonstopmode $@

