# METIS Data Reduction Library Design (DRLD)

## Special Commands

- Recipes: `\REC{met_do_something}`
- QC parameters: `\QC{QC SOMETHING OR OTHER}`
- Templates: `\TPL{DARK_LM}`
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
