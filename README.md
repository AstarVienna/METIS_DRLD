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

# Automatic Consistency Checks

The METIS_DRLD repository contains various consistency checks, both internal and with external documents.

## Run the tests locally

First install the dependencies
```bash
pip install -r codes/requirements.github_actions.txt
```

Then run the consistency tests
```bash
python -m pytest
```

This will output something like
```
================================= test session starts =================================
platform linux -- Python 3.11.5, pytest-8.2.1, pluggy-1.5.0
rootdir: /mnt/bulk/hugo/repos/METIS_DRLD
configfile: pyproject.toml
plugins: anyio-3.7.1, cov-4.1.0
collected 35 items                                                                    

codes/tests/test_datareductionlibrarydesign.py .....xx.........x..............s [ 91%]
                                                                                [ 91%]
codes/tests/test_templatemanual.py ...                                          [100%]

====================== 31 passed, 1 skipped, 3 xfailed in 0.70s =======================
```

No test should be marked as failed.
However, some tests are expected to fail, marked as `xfailed`.
These xfailed tests mean that there are still some consistency problems with the DRLD that should be fixed, but we know about them and find them acceptable for now.

## Run the tests on github.

There is a [github workflow](https://github.com/AstarVienna/METIS_DRLD/blob/master/.github/workflows/tests.yml) to run the tests automatically or manually on github.

## Syncing with the Template Manual

The tests compares the DRLD with the Template Manual; in particular it tests whether the data from all templates is processed by the pipeline.
The Template Manual is constructed from the [METIS wiki](https://metis.strw.leidenuniv.nl/wiki/doku.php?id=operations:metis_templates).
The tests compare against these wiki files instead of comparing to the Template Manual itself.
There is a [copy of the relevant wiki pages](https://github.com/AstarVienna/METIS_DRLD/tree/master/codes/drld_parser/operations) in the DRLD repository.

This copy of the templates is automatically downloaded from the same [wiki export](https://home.strw.leidenuniv.nl/~burtscher/metis_operations/) that is also used by the operations group to generate the template manual.
In particular, there is a [github workflow](https://github.com/AstarVienna/METIS_DRLD/blob/master/.github/workflows/update_operations.yml) that downloads the latest wiki export and that generates a Pull Request to update the local copy.

The full process to verify a change in the Template Manual is consistent with the DRLD:

- Make a change to a template on the [METIS wiki](https://metis.strw.leidenuniv.nl/wiki/doku.php?id=operations:metis_templates).
- Wait till a [new export is generated](https://home.strw.leidenuniv.nl/~burtscher/metis_operations/), currently once an hour.
- Wait till the [`update_operations` github action runs](https://github.com/AstarVienna/METIS_DRLD/blob/master/.github/workflows/update_operations.yml), or [run it matually](https://github.com/AstarVienna/METIS_DRLD/actions/workflows/update_operations.yml).
- That workflow runs the [`download_operations_wiki.py` script](https://github.com/AstarVienna/METIS_DRLD/blob/master/codes/drld_parser/download_operations_wiki.py),  which you can also run locally.
- The github workflow subsequently creates a Pull Request (if necessary) to update the [local template files](https://github.com/AstarVienna/METIS_DRLD/tree/master/codes/drld_parser/operations), which should be merged, or after running the 
- Finally, run the [`tests`](https://github.com/AstarVienna/METIS_DRLD/actions/workflows/tests.yml) workflow.




