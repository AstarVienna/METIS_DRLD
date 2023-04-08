"""The Data Reduction Library Design."""

import dataclasses
import glob
import itertools
import os
from pathlib import Path
import re
from typing import List, Tuple

from codes.drld_parser.hacks import HACK_BAD_NAMES, HACK_TEMPLATE_NAMES_IN_DRLD


def find_latex_inputs(path):
    """Flatten a tex file."""
    lines = open(path).readlines()
    lines_with_input = [
        line for line in lines if line.strip() and line.strip().startswith(r"\input{")
    ]
    paths_inputted = [
        path.parent / (ll + ".tex")
        for line in lines_with_input
        for ll in re.findall(r"\\input{(.*?)}", line)
    ]
    paths_to_return = [fn for fn in paths_inputted]
    for fn in paths_inputted:
        paths_to_return + find_latex_inputs(fn)

    return paths_to_return


@dataclasses.dataclass
class DataItem:
    """A Raw / Processed / External DataItem."""

    name: str = None
    hyperref: str = None
    labels: List[str] = None


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
                elif field_old in ["output_data", "input_data"]:
                    # TODO: These should all be \PROD{something} but are not
                    value = value.split("\n")

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
        # The Recipes defined in the DRLD.

        self.dataitems = self.get_dataitems()
        # The DataItems defined in the DRLD.

        self.recipe_names_used = self.get_recipe_names_used()
        self.template_names_used = self.get_template_names_used()

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

    def get_dataitems(self):
        """Read all DataItems defined in 'DRL DATA ITEMS AND STRUCTURES'.

        The DataItems are all defined in 09_0-DRL-Data-Structures.tex, which
        \input's all *_data_item.tex files. Those files have paragraphs like

        \paragraph{\hyperref[dataitem:lmlsssciflux2d]{\PROD{LM_LSS_SCI_FLUX_2D}}}\label{dataitem:lmlsssciflux2d}

        but some are

        '\\paragraph{\\hyperref[dataitem:masterdark2rg]{\\PROD{MASTER_DARK_2RG}} and \\hyperref[dataitem:masterdarkgeo]{\\PROD{MASTER_DARK_GEO}}}\\label{dataitem:masterdark}\\label{dataitem:masterdark2rg}\\label{dataitem:masterdarkgeo}'

        or

        \paragraph{\hyperref[dataitem:badpixmap2rg]{\PROD{BADPIX_MAP_2RG}} and \hyperref[dataitem:badpixmapgeo]{\PROD{BADPIX_MAP_GEO}}}\label{dataitem:badpixmap}\label{dataitem:badpixmap2rg}\label{dataitem:badpixmapgeo}


        """
        path_dataitems = self.path_drld / "09_0-DRL-Data-Structures.tex"
        paths_with_dataitems = find_latex_inputs(path_dataitems)

        data_all = (
            "\n"
            + "\n".join(
                open(pp).read() for pp in [path_dataitems] + paths_with_dataitems
            )
            + "\n"
        )
        data_all = data_all.replace("\n", "\n\n")
        # All these \n's are there because HB doesn't know how to do proper
        # look-ahead or look-backwards in Python regular expressions.

        dataitems1 = re.findall(
            r"[^%](\\paragraph{\\hyperref\[(.*?)]{\\PROD{(.*?)}}}\\label{(.*?)}*)\n",
            data_all,
        )

        dataitems2 = []
        for line, hyperref, name, label in dataitems1:
            if " and " in name:
                # beware of ZA̡͊͠͝LGΌ
                mm = re.match(
                    r"\\paragraph{\\hyperref\[(.*?)]{\\PROD{(.*?)}} and \\hyperref\[(.*?)]{\\PROD{(.*?)}}}(\\label{.*?})$",
                    line,
                )
                hyperref1, name1, hyperref2, name2, labelsg = mm.groups()
                hyperref_common = "".join(
                    a[0]
                    for a in itertools.takewhile(
                        lambda a: a[0] == a[1], zip(hyperref1, hyperref2)
                    )
                )
                labels = re.findall(r"\\label{(.*?)}", labelsg)
                assert hyperref_common in labels
                assert hyperref2 in labels
                assert hyperref1 in labels
                dataitems2 += [
                    [name1, hyperref1, labels],
                    [name2, hyperref2, labels],
                ]
            else:
                assert hyperref == label
                # namel = name.lower().replace("_", "")
                # print(f"dataitem:{namel}" == hyperref, name, hyperref)
                dataitems2 += [[name, hyperref, [label]]]

        dataitems3 = {}
        for name, hyperref, labels in dataitems2:
            assert name not in dataitems3
            dataitems3[name] = DataItem(
                name=name,
                hyperref=hyperref,
                labels=labels,
            )

        return dataitems3

    def get_template_names_used(self):
        """
        Get templates from tex files
        """

        not_templates = [
            "METIS_IMAGE",
            "METIS_CUBE",
        ] + list(self.recipes.keys())
        not_templates += [rec.lower() for rec in not_templates]
        template_names = []
        for filename in self.filenames_tex + self.filenames_tikz:
            datat = open(filename, encoding="utf8").read()
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
            template_names += [
                tsi
                for tsi in tpls_macro + tpls_latex
                if tsi.lower() not in not_templates
            ]

        return template_names

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
