"""Create a Graph of all elements of the DPS."""
import glob
import os
import re
from pathlib import Path

from codes.drld_parser.parser_utils import \
    hack_rename_template_header, parse_file_template, get_tpls_from_tex, \
    HACK_TEMPLATE_NAMES_IN_WIKI, hack_rename_template_names_drld, \
    get_template_summaries, get_recipes

################################################################################
# Checking Templates for consistency with DRLD
################################################################################

PATH_HERE = Path(__file__).parent
OPERATIONS_PATH = PATH_HERE / "operations"

template_summaries = get_template_summaries(OPERATIONS_PATH)

type_from_template_name = {tt.lower(): type_tt
                           for type_tt, tps in template_summaries.items()
                           for tt in tps}

templates_all_true = [tt for tpslist in template_summaries.values()
                      for tt in tpslist]
assert len(templates_all_true) == len(set(templates_all_true))
assert len(type_from_template_name) == len(templates_all_true)


files_templates = glob.glob(os.path.join(OPERATIONS_PATH, "metis_*_*.txt"))
templates = [parse_file_template(filename, type_from_template_name)
             for filename in files_templates]
templatesd = {template.name.lower(): template for template in templates}

assert len(templates) == len(templatesd)
for template in templates:
    assert template.name.lower() in templatesd
    for tn in template.references:
        assert tn.lower() in templatesd

tpl_keys = set(tn.split("_")[1] for tn in templatesd.keys())
assert tpl_keys == {
    "img",
    "ifu",
    "acq",
    "obs",
    "gen",
    "pup",
    "spec",
}

print("==== Now Parsing All Wiki Files")
files_wiki = glob.glob("drld_parser/operations/*.txt")
for fn in files_wiki:
    fnstem = Path(fn).stem
    dataw = open(fn, encoding='utf8').read()
    tpls = [tp for tp in re.findall("METIS_[a-zA-Z_]*", dataw, re.IGNORECASE)]
    for tp in tpls:
        tphh = hack_rename_template_header(fnstem, tp)
        tph = HACK_TEMPLATE_NAMES_IN_WIKI.get((fnstem, tphh), tphh)
        if tph and tph.lower() not in templatesd:
            print(f'    ("{fnstem}", "{tp}"): "",')


################################################################################
# Checking DRLD for consistency with Template names
################################################################################


print("===== Now Parsing DRLD =====")

DRLD_PATH = Path(__file__).parent.parent.parent
files_drld = glob.glob(os.path.join(DRLD_PATH, "*.tex")) + \
             glob.glob(os.path.join(DRLD_PATH, "**/*.tex"))

files_drld_tex = glob.glob(os.path.join(DRLD_PATH, "*.tex"))
# files_drld_tikz = glob.glob("../**/*.tex")        # not used anywhere

# Everything starts with metis_ except detmon_ir_lg
recipe_names_u = [
    recname.replace("\\", "")
    for fn in files_drld_tex
    for recname in re.findall("\\\\REC{(.*?)}",
                              open(fn, encoding='utf8').read(), re.IGNORECASE)
    if recname
]
recipe_names_drld = sorted(set(recipe_names_u))

# Ensure recipe names and template names do not overlap.
assert not (templatesd.keys() & set(recipe_names_drld))


recipes = get_recipes(DRLD_PATH)
recipesd = {
    rec.name.lower(): rec
    for rec in recipes
}
assert len(recipes) == len(recipesd)

for recipe in recipes:
    if recipe.templates:
        for tem in recipe.templates:
            if tem.lower() not in templatesd:
                print(recipe.name, tem)

for fn in files_drld:
    fnstem = Path(fn).stem
    tpls = get_tpls_from_tex(fn, recipe_names_drld)
    for ts in tpls:
        if "*" in ts:
            # TODO: Do something sensible here. E.g. are there any templates with that prefix?
            continue
        tshack = hack_rename_template_names_drld(fn, ts)
        # assert tshack.lower() in templatesd or tshack in TEMPLATE_IN_DRLD_BUT_NOT_IN_OPERATIONS_WIKI
        # TODO: Do something sensible with the * ones
        if tshack and tshack.lower() not in templatesd and "*" not in tshack:
            # print("%-50s %-40s" % (fn, ts))
            # print(fnstem, ts, tshack)
            print(f'    ("{fnstem}", "{ts}"): "",')

        if tshack.lower() not in type_from_template_name:
            print(f"{ts}/{tshack} not a true template")
