"""The Data Reduction Library Design."""

import dataclasses
import glob
import os
from pathlib import Path
import re
from typing import List, Tuple

from codes.drld_parser.hacks import HACK_BAD_NAMES, HACK_TEMPLATE_NAMES_IN_DRLD


@dataclasses.dataclass
class Recipe:
    name: str = None
    purpose: str = None
    type: str = None
    templates: List[str] = None
    input_data: List[str] = None
    parameters: List[str] = None
    algorithm: str = None
    output_data: List[Tuple[str, str]] = None
    expected_accuracies: str = None
    qc1_parameters: List[str] = None
    hdrl_functions: List[str] = None
    requirements: List[str] = None
    matched_keywords: List[str] = None

    @staticmethod
    def parse_recipe_from_table(stable):
        """Parse a Recipe from a table"""
        rows1 = [
            line.strip()
            for line in stable.splitlines()
            if line.strip() and not line.strip().startswith("%")
        ]

        # Concatenate lines.. Aargh
        rows2 = []
        thisline = ""
        for line in rows1:
            thisline += line
            if thisline.endswith("\\\\"):
                rows2.append(thisline)
                thisline = ""

        rows3 = [
            line.strip().strip("\\").strip().split("&")
            for line in rows2
            # TODO: Do something sensible if there is no &
            if "&" in line
        ]

        rows4 = [(aa.strip().strip(":").strip(), bb.strip()) for aa, bb in rows3]

        value = ""
        field_old = ""
        thedata = {}
        for row in rows4:
            field1 = row[0].lower().replace(" ", "_")
            field1 = re.sub("label{.*?}", "", field1)
            if field1 == "":
                value += "\n" + row[1]
                continue

            # Previous one must be finished
            if field_old:
                if field_old == "templates":
                    value = re.sub("\\\\TPL{(.*?)}", " \\1 ", value)
                    value = value.replace(",", " ")
                    if "tbd" in value.lower():
                        value = ["TBD"]
                    elif value.lower() == "none" or "--" in value:
                        value = []
                    else:
                        value = value.split()
                        value = [
                            HACK_TEMPLATE_NAMES_IN_DRLD.get(vi.lower(), vi.lower())
                            for vi in value
                        ]
                thedata[field_old] = value

            field = HACK_BAD_NAMES.get(field1, field1)
            value = row[1]

            if "name" in field:
                value = re.sub(r"\\REC{(.*?)}", "\\1", value)
                value = re.sub(r"\\hyperref\[.*?]{(.*?)}", "\\1", value)
                # print(field, ":::", value)

            # noinspection PyUnresolvedReferences
            if field not in Recipe.__dataclass_fields__:
                print(field, field1, row[0])

            # Cannot yet add the value to thedata dictionary because the value
            # might continue on other rows.
            field_old = field

        return Recipe(**thedata)


class DataReductionLibraryDesign:
    """The information from the DRLD"""
    # TODO: Check all tex files

    def __init__(self):
        path_here = Path(__file__).parent

        self.path_drld = path_here.parent.parent
        # The path of the DRLD

        self.filenames_tex = glob.glob(os.path.join(self.path_drld, "*.tex"))
        # Regular tex files.

        self.filenames_tikz = glob.glob(os.path.join(self.path_drld, "**/*.tex"))
        # Tikz figures.

        self.recipes = self.get_recipes()
        # The recipes as defined in the DRLD.

        self.recipe_names_used = self.get_recipe_names_used()

    def get_recipes(self):
        """"""
        # TODO: Verify that there are no recipes defined in other tex files.
        files_drld = glob.glob(os.path.join(self.path_drld, "Recipes*.tex"))
        recipes = {}
        for filename in files_drld:
            data = open(filename, encoding="utf8").read()
            srecipes = [
                dd.split("\\end{recipedef}")[0]
                for dd in data.split("\\begin{recipedef}")
                if "recipe parameters" in dd.lower() or "qc1" in dd.lower()
            ]
            for stable in srecipes:
                recipe = Recipe.parse_recipe_from_table(stable)
                recipes[recipe.name] = recipe

        return recipes

    def get_tpls_from_tex(self, filename):
        """
        Get templates from tex files
        """

        not_templates = [
            "METIS_IMAGE",
            "METIS_CUBE",
        ] + list(self.recipes.keys())
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

    def get_recipe_names_used(self):
        """All recipes names used in the DRLD."""
        # TODO: Also search in the figures.

        # TODO: Ensure that these abbreviations are handled somehow:
        #       "The prefix ``\REC{metis_}'' has been
        #     omitted from the recipe names to improve clarity. The product
        #     names omit ``\PROD{LM_}''.}"

        # Everything starts with metis_ except detmon_ir_lg
        not_recipes = {"metis_do_stuff", "metis_", ""}
        recipe_names_u = [
            recname.replace("\\", "")
            for fn in self.filenames_tex
            for recname in re.findall(
                "\\\\REC{(.*?)}", open(fn, encoding="utf8").read()
            )
            if recname not in not_recipes
        ]
        return sorted(set(recipe_names_u))


METIS_DataReductionLibraryDesign = DataReductionLibraryDesign()
