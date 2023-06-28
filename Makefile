c_error		:= $(shell tput sgr0; tput bold; tput setaf 1)
c_action	:= $(shell tput sgr0; tput bold; tput setaf 4)
c_filename	:= $(shell tput sgr0; tput setaf 5)
c_special	:= $(shell tput sgr0; tput setaf 3)
c_default	:= $(shell tput sgr0; tput setaf 15)

.SECONDEXPANSION:

# Ignore interactive mode with texfot
TEXFOT_ARGS=--no-interactive \
	--ignore 'Underfull.*'

# On the first run, also ignore missing cross-references and acronyms
TEXFOT_ARGS_FIRST=${TEXFOT_ARGS} \
	--ignore 'LaTeX Warning: Hyper reference.*' \
	--ignore 'LaTeX Warning: Reference.*' \
	--ignore 'LaTeX Warning: Citation.*' \
	--ignore 'Package acronym Warning: Acronym.*'

define pdflatex
	@echo -e '$(c_action)[pdflatex] Compiling PDF file $(c_filename)$@$(c_action): $(1) run$(c_default)'
	@texfot $(2) pdflatex $< -file-line-error -shell-escape -jobname=$(subst .pdf,,$@) -halt-on-error -synctex=1 -interaction=nonstopmode $@
endef


figures/%.pdf: tikz/%.tex
	# SOURCE_DATE_EPOCH to make sure the files are reproducible
	SOURCE_DATE_EPOCH=1830294000 TEXINPUTS=tikz: pdflatex -output-directory=figures $<


# The main document file
METIS_DRLD.pdf: \
	METIS_DRLD.tex \
	$$(wildcard *.tex) \
	$$(wildcard *.png) \
	$$(subst figures/,tikz/,$$(wildcard tikz/*.tex)) \
	$$(wildcard figures/*.*)
	$(call pdflatex,primary,${TEXFOT_ARGS_FIRST})
	biber METIS_DRLD
	$(call pdflatex,secondary,${TEXFOT_ARGS})
	$(call pdflatex,tertiary,${TEXFOT_ARGS})

all: METIS_DRLD.pdf

clean:
	rm -f *.out *.aux *.log *.lof *.bbl *.bcf *.run.xml *.toc *.blg *.lot $(figures_from_tikz) METIS_DRLD.pdf
