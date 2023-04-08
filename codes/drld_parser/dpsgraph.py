"""Create a Graph of all elements of the DPS."""

from codes.drld_parser.data_reduction_library_design import (
    METIS_DataReductionLibraryDesign,
    find_latex_inputs,
)
from codes.drld_parser.template_manual import METIS_TemplateManual

for recipe in METIS_DataReductionLibraryDesign.recipes.values():
    print()
    print(recipe.name)
    if recipe.input_data:
        print(" - input data")
        for thing in recipe.input_data:
            print("   -", thing)
    if recipe.output_data:
        print(" - output data")
        for thing in recipe.output_data:
            print("   -", thing)
