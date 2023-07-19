# Replace e.g. \PROD{LM\_RSRF\_RAW} with \PROD{LM_RSRF\_RAW}
#sed -E 's|(\\PROD\{[a-zA-Z_]+)\\_|\1_|g' -i -- *.tex tikz/*.tex
sed -E 's|(\\[A-Z]+\{[0-9a-zA-Z_]+)\\_|\1_|g' -i -- *.tex tikz/*.tex
# And again to get to \PROD{LM_RSRF_RAW}
sed -E 's|(\\[A-Z]+\{[0-9a-zA-Z_]+)\\_|\1_|g' -i -- *.tex tikz/*.tex
# And twice more to get them all
sed -E 's|(\\[A-Z]+\{[0-9a-zA-Z_]+)\\_|\1_|g' -i -- *.tex tikz/*.tex
sed -E 's|(\\[A-Z]+\{[0-9a-zA-Z_]+)\\_|\1_|g' -i -- *.tex tikz/*.tex
sed -E 's|(\\[A-Z]+\{[0-9a-zA-Z_]+)\\_|\1_|g' -i -- *.tex tikz/*.tex

# Also do this for \<n\>, e.g. \QC{QC N LSS FLUX WAVECAL POLYCOEFF<n>
sed -E 's|(\\[A-Z]+\{[0-9a-zA-Z_ ]+)\\<n\\>|\1<n>|g' -i -- *.tex tikz/*.tex

# Replace \FITS{SOME_DATA_ITEM} with \PROD{SOME_DATA_ITEM}
# TODO: What if it should be a STATCALIB or so?
sed -E 's|(dataitem:[0-9a-zA-Z_]*]\{\\)FITS|\1PROD|g' -i -- *.tex tikz/*.tex


# Ensure all dataitem links are like dataitem:badpix_map_2rg.
# First copy the name into the hyperref, matches \hyperref[dataitem:n_lss_trace]{\PROD{N_LSS_TRACE}}
#sed -E 's|dataitem:[0-9a-zA-Z_]*]\{\\PROD\{([0-9a-zA-Z_]+)|dataitem:\1]\{\\PROD\{\1|g' -i -- *.tex tikz/*.tex
sed -E 's!(dataitem|rec):[0-9a-zA-Z_]*]\{\\([A-Z]+)\{([0-9a-zA-Z_ ]+)!\1:\3]\{\\\2\{\3!g' -i -- *.tex tikz/*.tex
sed -E 's!(qc):[0-9a-zA-Z_<>#]*]\{\\([A-Z]+)\{([0-9a-zA-Z_<># ]+)!\1:\3]\{\\\2\{\3!g' -i -- *.tex tikz/*.tex

# Then copy the name into the label
sed -E 's!([A-Z]+)\{([0-9a-zA-Z_]*)}}}\\label\{(dataitem|rec):[0-9a-zA-Z_:]*}!\1\{\2}}}\\label\{\3:\2}!g' -i -- *.tex tikz/*.tex
sed -E 's|([A-Z]+)\{([0-9a-zA-Z_]*)}}}\\label\{drsstructure:[0-9a-zA-Z_:]*}|\1\{\2}}}\\label\{drsstructure:\2}|g' -i -- *.tex tikz/*.tex

# Also copy name into the label for recipes.
# \subsubsection{LM-LSS science reduction recipe \REC{metis_LM_lss_sci}:}\label{rec:lsslmsci}
sed -E 's!\\REC\{([0-9a-zA-Z_]*)([}: ]+)\\label\{rec:[0-9a-zA-Z_:]*}!\\REC\{\1\2\\label\{rec:\1}!g' -i -- *.tex tikz/*.tex
# And for QC
# \paragraph{\QC{QC N LSS STD BACKGD MEDIAN}}\label{qc:nlssstdbackgdmedian}
# \paragraph{\QC{QC N LSS SCI WAVECAL POLYCOEFF<n>}}\label{qc:nlsssciwavecalpolycoeffn}
sed -E 's!\\QC\{([0-9a-zA-Z<>#_ ]*)([}: ]+)\\label\{qc:[0-9a-zA-Z_:<>#]*}!\\QC\{\1\2\\label\{qc:\1}!g' -i -- *.tex tikz/*.tex

# Convert all PRODs that are not yet a link. That is, " \PROD{SOMETHING}"
sed -E 's!([ \(])\\(PROD|RAW|STATCALIB|EXTCALIB)\{([0-9a-zA-Z_]+)}!\1\\hyperref\[dataitem:\3]\{\\\2\{\3}}!g' -i -- *.tex tikz/*.tex
sed -E 's!( \{)\\(PROD|RAW|STATCALIB|EXTCALIB)\{([0-9a-zA-Z_]+)}!\1\\hyperref\[dataitem:\3]\{\\\2\{\3}}!g' -i -- *.tex tikz/*.tex

# Convert all QC that do not yet have a hyperref.
# TODO: enable
#sed -E 's! \\(QC)\{([0-9a-zA-Z_ ]+)}! \\hyperref\[qc:\2]\{\\\1\{\2}}!g' -i -- *.tex tikz/*.tex

# \REC is also used in subsection headers, those should not be hyperrefs.
# \subsubsection{Recipes \REC{metis_det_lingain} and \REC{metis_det_dark}}
# So first replace those with a placeholder.
sed -E 's!(subsection.*\\)REC!\1QQQQQQ!g' -i -- *.tex tikz/*.tex
# Do it twice, because occasionally there are two in a header.
sed -E 's!(subsection.*\\)REC!\1QQQQQQ!g' -i -- *.tex tikz/*.tex
# \REC is also used in the short captions for the table of contents.
#   \caption[Recipe: \REC{metis_lm_img_flat}]{\REC{metis_lm_img_flat} ... }
# This can be determined by checking for the closing ].
# Then add a hyperref to all \REC.
sed -E 's!([ \(])\\REC\{([0-9a-zA-Z_]+)}([^]])!\1\\hyperref\[rec:\2]\{\\REC\{\2}}\3!g' -i -- *.tex tikz/*.tex
sed -E 's!( \{)\\REC\{([0-9a-zA-Z_]+)}([^]])!\1\\hyperref\[rec:\2]\{\\REC\{\2}}\3!g' -i -- *.tex tikz/*.tex
# Finally replace the placeholder again.
sed -E 's!(subsection.*\\)QQQQQQ!\1REC!g' -i -- *.tex tikz/*.tex
sed -E 's!(subsection.*\\)QQQQQQ!\1REC!g' -i -- *.tex tikz/*.tex


# The QC ones can have spaces, we need to removed those
# \hyperref[qc:QC LIN GAIN MEAN]{\QC{QC LIN GAIN MEAN}}
# \paragraph{\QC{QC DARK MEAN}}\label{qc:QC DARK MEAN}
sed -E 's!qc:([A-Z_]+) !qc:\1_!g' -i -- *.tex tikz/*.tex
sed -E 's!qc:([A-Z_]+) !qc:\1_!g' -i -- *.tex tikz/*.tex
sed -E 's!qc:([A-Z_]+) !qc:\1_!g' -i -- *.tex tikz/*.tex
sed -E 's!qc:([A-Z_]+) !qc:\1_!g' -i -- *.tex tikz/*.tex
sed -E 's!qc:([A-Z_]+) !qc:\1_!g' -i -- *.tex tikz/*.tex
sed -E 's!qc:([A-Z_]+) !qc:\1_!g' -i -- *.tex tikz/*.tex
sed -E 's!qc:([A-Z_]+) !qc:\1_!g' -i -- *.tex tikz/*.tex
sed -E 's!qc:([A-Z_]+) !qc:\1_!g' -i -- *.tex tikz/*.tex
sed -E 's!qc:([A-Z_]+) !qc:\1_!g' -i -- *.tex tikz/*.tex
sed -E 's!qc:([A-Z_]+) !qc:\1_!g' -i -- *.tex tikz/*.tex



# Then make all the labels lowercase
sed -E 's|(dataitem:[0-9a-zA-Z_]*)|\L\1|g' -i -- *.tex tikz/*.tex
sed -E 's|(rec:[0-9a-zA-Z_]*)|\L\1|g' -i -- *.tex tikz/*.tex
sed -E 's|(qc:[0-9a-zA-Z_<>#]*)|\L\1|g' -i -- *.tex tikz/*.tex


# The (sub)section headers should have backslashes.
# Forward / needed because
# 6.8.4 Slit loss determination recipes metis_lm/n_adc_slitloss
sed -E 's!(subsection.*\\REC\{[A-Za-z\\_/]*?[A-Za-z])_!\1\\_!g' -i -- *.tex tikz/*.tex
sed -E 's!(subsection.*\\REC\{[A-Za-z\\_/]*?[A-Za-z])_!\1\\_!g' -i -- *.tex tikz/*.tex
sed -E 's!(subsection.*\\REC\{[A-Za-z\\_/]*?[A-Za-z])_!\1\\_!g' -i -- *.tex tikz/*.tex
sed -E 's!(subsection.*\\REC\{[A-Za-z\\_/]*?[A-Za-z])_!\1\\_!g' -i -- *.tex tikz/*.tex
sed -E 's!(subsection.*\\REC\{[A-Za-z\\_/]*?[A-Za-z])_!\1\\_!g' -i -- *.tex tikz/*.tex



# After compiling the document twice, count broken dataitem links with
# grep Hyper METIS_DRLD.log | grep dataitem | awk '{print $5}' | sort | uniq -c | sort -nr


# TODO, e.g. "(\PROD{SOMETHING})"
