import glob
import itertools

# noinspection PyUnresolvedReferences
from pprint import pprint

import numpy
import pytest

from codes.drld_parser.data_reduction_library_design import (
    METIS_DataReductionLibraryDesign,
    find_latex_inputs,
    DataItemReference,
    guess_dataitem_type,
    DataItem, Recipe,
)
from codes.drld_parser.hacks import (
    TEMPLATE_IN_DRLD_BUT_NOT_IN_OPERATIONS_WIKI,
    HACK_RECIPES_THAT_ARE_ALLOWED_TO_HAVE_BAD_OUTPUT,
    HACK_RECIPES_THAT_ARE_ALLOWED_TO_BE_MISSING,
    HACK_DATAITEMS_ALLOWED_TO_HAVE_BROKEN_USERS,
    HACK_TEMPLATES_ALLOWED_TO_TRIGGER_RECIPES_WITHOUT_RAW_DATA,
)
from codes.drld_parser.template_manual import METIS_TemplateManual


def print_table(header, columns, rowline=False):
    assert len(header) == len(columns)
    lengths = {
        h: max([len(cell) for cell in col + [h]])
        for h, col in zip(header, columns)
    }
    bars_thick = ["━" * lengths[hh] for hh in header]
    bars_thin = ["─" * lengths[hh] for hh in header]
    print("┏━" + "━┯━".join(bars_thick) + "━┓")
    print(f"┃ " + " │ ".join(f"{hh:<{lengths[hh]}}" for hh in header) + " ┃")
    print("┣━" + "━┿━".join(bars_thick) + "━┫")
    for ri, row in enumerate(zip(*columns)):
        if row[0] == "-" and rowline:
            if ri:
                print("┠─" + "─┼─".join(bars_thin) + "─┨")
        else:
            print(f"┃ " + " │ ".join(f"{cell:<{lengths[header[ci]]}}" for ci, cell in enumerate(row)) + " ┃")
    print("┗━" + "━┷━".join(bars_thick) + "━┛")

dataitems_with_dpr = [
    dataitem for dataitem in METIS_DataReductionLibraryDesign.dataitems.values()
    if dataitem.templates
]




col_dpr_catg = []
col_dpr_tech = []
col_dpr_type = []
col_do_catg = []
col_recipes = []

idem = '"'

for dataitem in dataitems_with_dpr:
    recipes = METIS_DataReductionLibraryDesign.get_recipes_for_dataitem(dataitem.name, name_only=False)

    for ri, recipe in enumerate(recipes):
        if ri == 0:
            col_dpr_catg.append(dataitem.dpr_catg)
            col_dpr_tech.append(dataitem.dpr_tech)
            col_dpr_type.append(dataitem.dpr_type)
            col_do_catg.append(dataitem.do_catg)
        else:
            col_dpr_catg.append(idem)
            col_dpr_tech.append(idem)
            col_dpr_type.append(idem)
            col_do_catg.append(idem)
        col_recipes.append(recipe.name)

print_table(
    header=["DPR.CATG", "DPR.TECH", "DPR.TYPE", "DO.CATG", "recipes"],
    columns=[col_dpr_catg, col_dpr_tech, col_dpr_type, col_do_catg, col_recipes],
)


col_templates = []
col_dpr_catg = []
col_dpr_tech = []
col_dpr_type = []
col_do_catg = []
col_recipes = []

idem = '"'
recipe_none = Recipe(name="")

for dataitem in dataitems_with_dpr:
    recipes = METIS_DataReductionLibraryDesign.get_recipes_for_dataitem(dataitem.name, name_only=False)

    for ri, (template, recipe) in enumerate(itertools.zip_longest(dataitem.templates, recipes, fillvalue=None)):
        recipe = recipe_none if recipe is None else recipe
        template = "" if template is None else template
        if ri == 0:
            col_dpr_catg.append(dataitem.dpr_catg)
            col_dpr_tech.append(dataitem.dpr_tech)
            col_dpr_type.append(dataitem.dpr_type)
            col_do_catg.append(dataitem.do_catg)
        else:
            col_dpr_catg.append(idem)
            col_dpr_tech.append(idem)
            col_dpr_type.append(idem)
            col_do_catg.append(idem)

        col_templates.append(template)
        col_recipes.append(recipe.name)

print_table(
    header=["templates", "DPR.CATG", "DPR.TECH", "DPR.TYPE", "DO.CATG", "recipes"],
    columns=[col_templates, col_dpr_catg, col_dpr_tech, col_dpr_type, col_do_catg, col_recipes],
)




col_templates = []
col_dpr = []
col_do_catg = []
col_recipes = []

for dataitem in dataitems_with_dpr:
    recipes = METIS_DataReductionLibraryDesign.get_recipes_for_dataitem(dataitem.name, name_only=False)
    if " or " in dataitem.dpr_type:
        dpr_types = [line.strip() for line in dataitem.dpr_type.split(" or ")]
        assert len(dpr_types) == 2
        dprs = [
            f"CATG={dataitem.dpr_catg}",
            f"TECH={dataitem.dpr_tech}",
            f"TYPE={dpr_types[0]} or",
            f"     {dpr_types[1]}",
        ]
    else:
        dprs = [
            f"CATG={dataitem.dpr_catg}",
            f"TECH={dataitem.dpr_tech}",
            f"TYPE={dataitem.dpr_type}",
        ]

    col_templates.append("-")
    col_dpr.append("-")
    col_do_catg.append("-")
    col_recipes.append("-")

    for ri, (template, dpr, recipe, do_catg) in enumerate(itertools.zip_longest(dataitem.templates, dprs, recipes, [dataitem.do_catg], fillvalue="")):
        recipe = recipe_none if recipe == "" else recipe
        col_templates.append(template)
        col_dpr.append(dpr)
        col_do_catg.append(do_catg)
        col_recipes.append(recipe.name)

print_table(
    header=["Templates", "DPR.x", "DO.CATG", "Recipes"],
    columns=[col_templates, col_dpr, col_do_catg, col_recipes],
    rowline=True,
)
