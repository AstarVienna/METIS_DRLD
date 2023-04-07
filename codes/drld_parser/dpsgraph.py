"""Create a Graph of all elements of the DPS."""
import glob
import os
import re
from pathlib import Path

from codes.drld_parser.data_reduction_library_design import METIS_DataReductionLibraryDesign
from codes.drld_parser.hacks import hack_rename_template_names_drld


################################################################################
# Checking DRLD for consistency with Template names
################################################################################


print("===== Now Parsing DRLD =====")

for recipe in METIS_DataReductionLibraryDesign.recipes.values():
    if recipe.templates:
        for tem in recipe.templates:
            pass
            # if tem.lower() not in templatesd:
            #     print(recipe.name, tem)

for fn in METIS_DataReductionLibraryDesign.filenames_tex:
    fnstem = Path(fn).stem
    tpls = METIS_DataReductionLibraryDesign.get_tpls_from_tex(fn)
    for ts in tpls:
        if "*" in ts:
            # TODO: Do something sensible here. E.g. are there any templates with that prefix?
            continue
        tshack = hack_rename_template_names_drld(fn, ts)
        # assert tshack.lower() in templatesd or tshack in TEMPLATE_IN_DRLD_BUT_NOT_IN_OPERATIONS_WIKI
        # TODO: Do something sensible with the * ones
        # if tshack and tshack.lower() not in templatesd and "*" not in tshack:
        #     # print("%-50s %-40s" % (fn, ts))
        #     # print(fnstem, ts, tshack)
        #     print(f'    ("{fnstem}", "{ts}"): "",')
        #
        # if tshack.lower() not in type_from_template_name:
        #     print(f"{ts}/{tshack} not a true template")
