import re
import os
import glob
from pathlib import Path

from codes.drld_parser.base_classes import Recipe

PATH_HERE = Path(__file__).parent


def get_tpls_from_tex(filename, recipe_names):
    """
    Get templates from tex files
    """

    not_templates = [
        "METIS_IMAGE",
        "METIS_CUBE",
    ] + recipe_names
    datat = open(filename, encoding="utf8").read()
    # Using TPL macro
    # TODO: There are TPL macros that are not templates!!
    tpls_macro = [
        tsii.replace("\\", "")
        for tsii in re.findall("\\\\TPL{(M.*?)}", datat, re.IGNORECASE)
    ]
    # Normal LaTeX, includes tikzs
    tpls_latex = [
        tsii.replace("\\", "").replace("$ast$", "*")
        for tsii in
        # re.findall("metis\\\\_[iaogps][a-z_\\*\\\\]*", datat, re.IGNORECASE)
        re.findall("metis\\\\_[a-z_*\\\\ast$]*", datat, re.IGNORECASE)
    ]
    # TODO: does not work for tikz
    return [tsi for tsi in tpls_macro + tpls_latex if tsi not in not_templates]


def parse_recipes(filenames):
    # Just concatenate all the contents
    # 12_0-QC_parameters.tex uses recipedef for QC params
    # CalDB_data_items.tex uses recipedef for dataitems
    # IMG_drl_functions.tex uses recipedef for functions
    filenames_ok = [
        fni
        for fni in filenames
        if "12_0-QC_parameters" not in fni
        and "CalDB_data_items" not in fni
        and "LSS_data_items" not in fni
        and "IMG_drl_functions" not in fni
    ]
    data_all = "\n\n".join(open(fni, encoding="utf8").read() for fni in filenames_ok)
    # TODO: Assure we don't miss the first recipe by accident.
    srecipes = [
        dd.split("\\end{recipedef}")[0]
        for dd in data_all.split("\\begin{recipedef}")
        if "recipe parameters" in dd.lower() or "qc1" in dd.lower()
    ][1:]
    return [Recipe.parse_recipe_from_table(stable) for stable in srecipes]


def get_recipes(drld_path):
    files_drld = glob.glob(os.path.join(drld_path, "*.tex")) + glob.glob(
        os.path.join(drld_path, "**/*.tex")
    )
    return parse_recipes(files_drld)
