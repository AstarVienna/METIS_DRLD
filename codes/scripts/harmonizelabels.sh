# Replace e.g. \PROD{LM\_RSRF\_RAW} with \PROD{LM_RSRF\_RAW}
#sed -E 's|(\\PROD\{[a-zA-Z_]+)\\_|\1_|g' -i *.tex
sed -E 's|(\\[A-Z]+\{[0-9a-zA-Z_]+)\\_|\1_|g' -i *.tex
# And again to get to \PROD{LM_RSRF_RAW}
sed -E 's|(\\[A-Z]+\{[0-9a-zA-Z_]+)\\_|\1_|g' -i *.tex
# And twice more to get them all
sed -E 's|(\\[A-Z]+\{[0-9a-zA-Z_]+)\\_|\1_|g' -i *.tex
sed -E 's|(\\[A-Z]+\{[0-9a-zA-Z_]+)\\_|\1_|g' -i *.tex
sed -E 's|(\\[A-Z]+\{[0-9a-zA-Z_]+)\\_|\1_|g' -i *.tex


# Replace \FITS{SOME_DATA_ITEM} with \PROD{SOME_DATA_ITEM}
# TODO: What if it should be a STATCALIB or so?
sed -E 's|(dataitem:[0-9a-zA-Z_]*]\{\\)FITS|\1PROD|g' -i *.tex


# Ensure all dataitem links are like dataitem:badpix_map_2rg.
# First copy the name into the hyperref, matches \hyperref[dataitem:n_lss_trace]{\PROD{N_LSS_TRACE}}
#sed -E 's|dataitem:[0-9a-zA-Z_]*]\{\\PROD\{([0-9a-zA-Z_]+)|dataitem:\1]\{\\PROD\{\1|g' -i *.tex
sed -E 's|dataitem:[0-9a-zA-Z_]*]\{\\([A-Z]+)\{([0-9a-zA-Z_]+)|dataitem:\2]\{\\\1\{\2|g' -i *.tex
# Then copy the name into the label
sed -E 's|([A-Z]+)\{([0-9a-zA-Z_]*)}}}\\label\{dataitem:[0-9a-zA-Z_:]*}|\1\{\2}}}\\label\{dataitem:\2}|g' -i *.tex
sed -E 's|([A-Z]+)\{([0-9a-zA-Z_]*)}}}\\label\{drsstructure:[0-9a-zA-Z_:]*}|\1\{\2}}}\\label\{drsstructure:\2}|g' -i *.tex

# Convert all PRODs that are not yet a link. That is, " \PROD{SOMETHING}"
# Run manually
#sed -E 's! \\(PROD|RAW|STATCALIB|EXTCALIB)\{([0-9a-zA-Z_]+)}! \\hyperref\[dataitem:\2]\{\\\1\{\2}}!g' -i *.tex

# Then make all the labels lowercase
sed -E 's|(dataitem:[0-9a-zA-Z_]*)|\L\1|g' -i *.tex



# TODO, e.g. "(\PROD{SOMETHING})"
