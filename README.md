# METIS Data Reduction Library Design (DRLD)

## Special Commands

- Recipes: `\REC{metis_do_something}`
- QC parameters: `\QC{QC SOMETHING OR OTHER}`
- Templates: `\TPL{METIS_gen_cal_dark}`
- Products: `\PROD{SOME_THING}`
- Requirements: `\REQ{METIS-xxx}`
- External calibration files: `\EXTCALIB{some_file}`
- Static calibration files: `\STATCALIB{some_other_file}`
- FITS keywords: `\FITS{EXPTIME}`
- Code: `\CODE{SOMETHING==ELSE}`
- micrometer (correctly!): `\micron`
- stuff that needs to be done: `\TODO{Do this!}` -- none of these should remain in any release version

Use the environment `recipedef` to define a new recipe:
```latex
\begin{recipedef}
  Recipe name:  &  \REC{metis_det_lingain} \\
  Purpose:      & determine non-linearity and gain
\end{recipedef}
```

## tcolorbox

Overleaf complains with this warning:
> Package tcolorbox Warning: Discard zero height first box part due to break problems (possible loss of zero height content) on input line 188.

That problem is [fixed in tcolorbox 6.0.2](https://github.com/T-F-S/tcolorbox/issues/218).
However, that version is not yet in any texlive distribution, so is not available on overleaf. The following files are added to the repository to manually add the features necessary to prevent the warning:

```
tcbbreakable.code.tex
tcbfitting.code.tex
tcbhooks.code.tex
tcbraster.code.tex
tcbskins.code.tex
tcbskinsjigsaw.code.tex
tcbtheorems.code.tex
tcolorbox.sty
tikzfill-common.sty
tikzfill.image.sty
tikzlibraryfill.image.code.tex
```

These files can be removed once overleaf has a texlive version that has tcolorbox 6.0.2+ included.


