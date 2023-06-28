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

figures_from_tikz = figures/IFU_assomap_tikz.pdf \
	figures/IMG_LM_assomap_tikz.pdf \
	figures/IMG_N_assomap_tikz.pdf \
	figures/metis_det_dark.pdf \
	figures/metis_det_lingain.pdf \
	figures/metis_ifu_distortion.pdf \
	figures/metis_ifu_rsrf.pdf \
	figures/metis_ifu_sci_postprocess.pdf \
	figures/metis_ifu_sci_process.pdf \
	figures/metis_ifu_std_process.pdf \
	figures/metis_ifu_tellcorr.pdf \
	figures/metis_ifu_wavecal.pdf \
	figures/metis_lm_img_background.pdf \
	figures/metis_lm_img_basic_reduce.pdf \
	figures/metis_lm_img_distortion.pdf \
	figures/metis_lm_img_flat.pdf \
	figures/metis_lm_img_sci_postprocess.pdf \
	figures/metis_n_img_distortion.pdf \
	figures/metis_n_img_flat.pdf

METIS_DRLD.pdf: \
	METIS_DRLD.tex \
	$$(wildcard *.tex) \
	$$(wildcard *.png) \
	$$(wildcard figures/*.*) \
	$(figures_from_tikz)
	$(call pdflatex,primary,${TEXFOT_ARGS_FIRST})
	biber METIS_DRLD
	$(call pdflatex,secondary,${TEXFOT_ARGS})
	$(call pdflatex,tertiary,${TEXFOT_ARGS})

figures/metis_det_dark.pdf: tikz/metis_det_dark.tex
	# SOURCE_DATE_EPOCH to make sure the files are reproducible
	SOURCE_DATE_EPOCH=1830294000 TEXINPUTS=tikz: pdflatex -output-directory=figures metis_det_dark.tex

figures/metis_lm_img_flat.pdf: tikz/metis_lm_img_flat.tex
	# SOURCE_DATE_EPOCH to make sure the files are reproducible
	SOURCE_DATE_EPOCH=1830294000 TEXINPUTS=tikz: pdflatex -output-directory=figures metis_lm_img_flat.tex

clean:
	rm -f *.out *.aux *.log *.lof *.bbl *.bcf *.run.xml *.toc *.blg *.lot $(figures_from_tikz) METIS_DRLD.pdf
