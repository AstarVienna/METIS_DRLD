"""Create a Graph of all elements of the DPS."""

from codes.drld_parser.data_reduction_library_design import (
    METIS_DataReductionLibraryDesign,
    guess_dataitem_type,
)
from codes.drld_parser.template_manual import METIS_TemplateManual

for dn in METIS_DataReductionLibraryDesign.dataitems:
    dtype = guess_dataitem_type(dn)
#     print(dn, dtype)

dataitem_names_lower = [
    dataitem.name.lower()
    for dataitem in METIS_DataReductionLibraryDesign.dataitems.values()
]

template_names_lower = [tn.lower() for tn in METIS_TemplateManual.templates]

boxes_recipes_existing = [
    f'   "{recipe.name.lower()}" [shape=box, fillcolor=green, style=filled, label="{recipe.name}"];'
    for recipe in METIS_DataReductionLibraryDesign.recipes.values()
]

boxes_dataitem_existing = [
    f'   "{dataitem.name.lower()}" [shape=box, fillcolor=purple, style=filled, label="{dataitem.name}"];'
    for dataitem in METIS_DataReductionLibraryDesign.dataitems.values()
]

boxes_template_existing = [
    f'   "{template.name.lower()}" [shape=box, fillcolor=orange, style=filled, label="{template.name}"];'
    for template in METIS_TemplateManual.templates.values()
]

boxes_dataitem_missing = [
    f'   "{diref.get_name().lower()}" [shape=box, fillcolor=purple, color=red, style="filled,dashed", penwidth="4.0", label="{diref.get_name()}"];'
    for recipe in METIS_DataReductionLibraryDesign.recipes.values()
    for diref in recipe.input_data + recipe.output_data
    if diref.get_name().lower() not in dataitem_names_lower
]

boxes_templates_missing = [
    f'   "{tn.lower()}" [shape=box, fillcolor=orange, color=red, style="filled,dashed", penwidth="4.0", label="{tn}"];'
    for recipe in METIS_DataReductionLibraryDesign.recipes.values()
    for tn in recipe.templates
]

edges_recipe_output = [
    f'    "{output.get_name().lower()}" -- "{recipe.name.lower()}"'
    for recipe in METIS_DataReductionLibraryDesign.recipes.values()
    for output in recipe.output_data
]

edges_recipe_input = [
    f'    "{recipe.name.lower()}" -- "{rinput.get_name().lower()}"'
    for recipe in METIS_DataReductionLibraryDesign.recipes.values()
    for rinput in recipe.input_data
]

edges_recipe_template = [
    f'    "{recipe.name.lower()}" -- "{template.lower()}"'
    for recipe in METIS_DataReductionLibraryDesign.recipes.values()
    for template in recipe.templates
]

s_boxes_edges = "\n".join(
    boxes_recipes_existing
    + boxes_dataitem_existing
    + boxes_template_existing
    + boxes_dataitem_missing
    + boxes_templates_missing
    + edges_recipe_output
    + edges_recipe_input
    + edges_recipe_template
)

s_dot = f"""graph METISDPS {{

    rankdir=RL

{s_boxes_edges}
}}"""

print(s_dot)
