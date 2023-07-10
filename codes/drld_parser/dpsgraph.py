"""Create a Graph of all elements of the DPS.

Colors based on association maps:
                                                                          rawcolor         {235,235,235}
(leg_recipe)     [recipe]        {n_img_flat}      {recipe}               recipecolor     {210,169, 188}
(leg_calproduct) [calibproduct]  {MASTER_DARK_GEO} {calib. product}       calproductcolor {185,184,237}
(leg_sciproduct) [scienceproduct]{N_SCI_REDUCED}   {science product}      sciproductcolor {197,219,183}
(leg_qcproduct)  [qcproduct]     {MASTER_DARK_GEO} {QC product}           qcproductcolor  {255,201,165}
(leg_statcalfile)[statcalfile]   {MASTER_RSRF}     {static calib. file}   calibcolor      {255,250,216}
(leg_calfile)    [extcalfile]    {FLUXSTD_CATALOG} {external calib. file} externalcolor   {183,255,255}
"""

from codes.drld_parser.data_reduction_library_design import (
    METIS_DataReductionLibraryDesign,
    guess_dataitem_type,
)
from codes.drld_parser.template_manual import METIS_TemplateManual

# TODO: Apparently MASTER_DARK_GEO and MASTER_FLAT_GEO should be a QC product?
colors = {
    "RAW": "#%02x%02x%02x" % (235, 235, 235),
    "RECIPE": "#%02x%02x%02x" % (210, 169, 188),
    "CALIB": "#%02x%02x%02x" % (185, 184, 237),
    "PROD": "#%02x%02x%02x" % (197, 219, 183),
    "QC": "#%02x%02x%02x" % (255, 201, 165),
    "STATCALIB": "#%02x%02x%02x" % (255, 250, 216),
    "EXTCALIB": "#%02x%02x%02x" % (183, 255, 255),
    "UNKNOWN": "#%02x%02x%02x" % (197, 219, 183),
    "TEMPLATE": "white",
}

dataitem_names_lower = [
    dataitem.name.lower() for dataitem in METIS_DataReductionLibraryDesign.dataitems.values()
]

template_names_lower = [tn.lower() for tn in METIS_TemplateManual.templates]

boxes_recipes_existing = [
    f'   "{recipe.name.lower()}" [shape=box, fillcolor="{colors["RECIPE"]}", style=filled, label="{recipe.name}"];'
    for recipe in METIS_DataReductionLibraryDesign.recipes.values()
]

boxes_dataitem_existing = [
    f'   "{dataitem.name.lower()}" [shape=box, fillcolor="{colors[guess_dataitem_type(dataitem.name)]}", style=filled, label="{dataitem.name}"];'
    for dataitem in METIS_DataReductionLibraryDesign.dataitems.values()
]

boxes_template_existing = [
    f'   "{template.name.lower()}" [shape=box, fillcolor="{colors["TEMPLATE"]}", style=filled, label="{template.name}"];'
    for template in METIS_TemplateManual.templates.values()
    if template.ttype in ["Calibration", "Observing"]
    or template.name in METIS_DataReductionLibraryDesign.templates_acquisition_used
]

boxes_dataitem_missing = [
    f'   "{diref.get_name().lower()}" [shape=box, fillcolor="{colors["UNKNOWN"]}", color=red, style="filled,dashed", penwidth="4.0", label="{diref.get_name()}"];'
    for recipe in METIS_DataReductionLibraryDesign.recipes.values()
    for diref in recipe.input_data + recipe.output_data
    if diref.get_name().lower() not in dataitem_names_lower
]

boxes_templates_missing = [
    f'   "{tni.lower()}" [shape=box, fillcolor={colors["TEMPLATE"]}, color=red, style="filled,dashed", penwidth="4.0", label="{tni}"];'
    for recipe in METIS_DataReductionLibraryDesign.recipes.values()
    for tn in recipe.templates
    for tni in METIS_TemplateManual.expand_wildcards(tn)
    if METIS_TemplateManual.get_template(tni) is None
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
    f'    "{recipe.name.lower()}" -- "{tni.lower()}"'
    for recipe in METIS_DataReductionLibraryDesign.recipes.values()
    for template in recipe.templates
    for tni in METIS_TemplateManual.expand_wildcards(template)
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
