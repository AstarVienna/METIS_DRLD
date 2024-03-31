"""Generate Pipeline Skeleton

Run from root of METIS_DRLD directory as
PYTHONPATH=. python3 codes/drld_parser/generate_pipeline_skeleton.py 
"""
from pathlib import Path
import functools
from graphlib import TopologicalSorter

from astropy.io import fits

from data_reduction_library_design import METIS_DataReductionLibraryDesign

PATH_SKELETON = Path(__file__).parent.parent.parent / "skeleton"
PATH_SKELETON.mkdir(parents=True, exist_ok=True)

PATH_SKELETON_DATA = PATH_SKELETON / "data"
PATH_SKELETON_DATA.mkdir(parents=True, exist_ok=True)


def generate_mock_raw(dataitem):
    """Generate a mock raw dataitem."""
    hdulist = fits.HDUList([
        fits.PrimaryHDU(
            header=fits.Header({
                "INSTRUME": "METIS",
                "MJD-OBS": 50000.5,
                "HIERARCH ESO DPR CATG": dataitem.dpr_catg,
                "HIERARCH ESO DPR TECH": dataitem.dpr_tech,
                "HIERARCH ESO DPR TYPE": dataitem.dpr_type,
            })
        ),
        # fits.ImageHDU(
        #     data=numpy.random.rand(SIZE_X, SIZE_Y),
        # )
    ])
    filename = f"{dataitem.name}.fits"
    hdulist.writeto(PATH_SKELETON / "data" / filename, overwrite=True)


def generate_pycpl_recipes(recipes_ok):
    lines_recipes = []
    for recipe in recipes_ok:
        main_input, *other_input = [
            METIS_DataReductionLibraryDesign.dataitems[dataitemref.name]
            for dataitemref in recipe.input_data
            if dataitemref.name
        ]
        main_output, *other_output = [
            METIS_DataReductionLibraryDesign.dataitems[dataitemref.name]
            for dataitemref in recipe.output_data
            if dataitemref.name
        ]
        lines_recipes.append(f"""
recipe_{recipe.name} = generate_recipe(
    name="{recipe.name}",
    catg_input="{main_input.do_catg}",
    catg_output="{main_output.do_catg}",
)
""")

    with open(PATH_SKELETON / "pycpl_recipes_skeleton.py", "w", encoding="utf-8") as f:
        # f.write("from .generate_recipe import generate_recipe\n")
        for line in lines_recipes:
            f.write(line)


def get_primary_recipe_for_demo(dataitem):
    """Prefer the LM one for simplicity"""
    if len(dataitem.created_by) == 1:
        return dataitem.created_by[0]

    for recref in dataitem.created_by:
        if "lm" in recref.name.lower():
            return recref
        if "2rg" in recref.name.lower():
            return recref
    return dataitem.created_by[0]


@functools.cache
def get_recipes_lower():
    # Why is there a metis_LM_lss_rsrf recipe with uppercase LM?
    recipes_lower = {
        recipe.name.lower(): recipe
        for recipe in METIS_DataReductionLibraryDesign.recipes.values()
    }
    return recipes_lower


def generate_workflow(dataitems_raw):
    # Finally the workflow.
    lines_raw_class = [
        (
            f"{di.name.lower()}_class = classification_rule("
            f"'{di.name}', {{dpr_catg: '{di.dpr_catg}', dpr_tech: '{di.dpr_tech}', dpr_type: '{di.dpr_type}'}})"
        )
        for di in dataitems_raw
    ]

    # lines_master =
    # TODO: We don't know which of the processed data is CALIB

    lines_raw = [
        f"""
{di.name.lower()} = (data_source()
    .with_classification_rule({di.name.lower()}_class)
    .build())
"""
        for di in dataitems_raw
    ]

    recipes_lower = get_recipes_lower()
    lines_tasks = []
    dataitems_prod_recipe_ok_unsorted = [
        (dataitem, recipes_lower[get_primary_recipe_for_demo(dataitem).name.lower()])
        for dataitem in METIS_DataReductionLibraryDesign.dataitems.values()
        if dataitem.created_by
        and dataitem.name == dataitem.name.upper()
        and dataitem.name not in ["PERSISTENCE_MAP"]
        # E.g. ATM_LINE_CAT
        and get_primary_recipe_for_demo(dataitem).name
    ]
    dataitems_names_ok = [di.name for di, _ in dataitems_prod_recipe_ok_unsorted]

    dataitems_prod_recipe_ok = sorted(
        dataitems_prod_recipe_ok_unsorted,
        key=functools.cmp_to_key(compare),
    )

    dataitems_graph = {
        di.name: [dii.name for dii in recipe.input_data]
        for di, recipe in dataitems_prod_recipe_ok
    }

    ts = TopologicalSorter(dataitems_graph)

    dataitems_topo_sorted = tuple(ts.static_order())

    for dataitem_name in dataitems_topo_sorted:
        if dataitem_name not in dataitems_names_ok:
            continue
        dataitem = METIS_DataReductionLibraryDesign.dataitems[dataitem_name]
        recipe = recipes_lower[get_primary_recipe_for_demo(dataitem).name.lower()]

        main_input, *other_input = [
            METIS_DataReductionLibraryDesign.dataitems[dataitemref.name]
            for dataitemref in recipe.input_data
            if dataitemref.name
        ]

        line_task = f"""
{dataitem.name.lower()} = (task('{dataitem.name}')
    .with_recipe('{recipe.name}')
    .with_main_input({main_input.name.lower()})
    #.with_associated_input()
    .build())
"""
        lines_tasks.append(line_task)

    srawclasss = "\n".join(lines_raw_class)
    sraws = "\n".join(lines_raw)
    stasks = "\n".join(lines_tasks)

    swkf = f"""
from edps import SCIENCE, QC1_CALIB, QC0, CALCHECKER
from edps import task, ReportInput
from edps import data_source
from edps import classification_rule
from edps import match

# HEADER KEYWORDS USED FOR CLASSIFICATION, GROUPING, AND ASSOCIATION.
instrume = "instrume"
pro_catg = "pro.catg"
dpr_type = "dpr.type"
dpr_catg = "dpr.catg"
dpr_tech = "dpr.tech"
tpl_nexp = "tpl.nexp"
obs_id = "obs.id"
tpl_start = "tpl.start"
ins_mode = "ins.mode"
arcfile = "arcfile"
mjd_obs = "mjd-obs"

{srawclasss}

{sraws}

{stasks}

"""

    with open(PATH_SKELETON / "metis_wkf.py", "w", encoding="utf-8") as f:
        f.write(swkf)


@functools.cache
def get_full_input(dataitem_name):
    """Trace the full input."""
    recipes_lower = get_recipes_lower()
    dataitem = METIS_DataReductionLibraryDesign.dataitems[dataitem_name]
    if not dataitem.created_by:
        return []
    if dataitem.name in ["PERSISTENCE_MAP"]:
        return []
    reciperef = get_primary_recipe_for_demo(dataitem)
    if not reciperef.name:
        return []
    recipe = recipes_lower[reciperef.name.lower()]
    
    new_input = [
        diref.name
        for diref in recipe.input_data
    ]
    some_input = new_input
    for di in new_input:
        some_input += get_full_input(di)
    return some_input


def compare(left, right):
    """Check whether one dataitem is in the dependency graph of another."""
    di_left, recipe_left = left
    di_right, recipe_right = right
    if di_left.name in get_full_input(di_right.name):
        return -1
    if di_right.name in get_full_input(di_left.name):
        return 1
    return 0
    

def main():
    dataitems_raw = [
        di
        for di in METIS_DataReductionLibraryDesign.dataitems.values()
        # E.g. GAIN_MAP_det, then GAIN_MAP_GEO is also there.
        if di.name == di.name.upper()
        and di.dtype == "RAW"
    ]

    for dataitem in dataitems_raw:
        generate_mock_raw(dataitem)

    # Now the recipes.
    recipes_ok = [
        recipe
        for recipe in METIS_DataReductionLibraryDesign.recipes.values()
        # metis_img_chophome has no named output yet
        if recipe.output_data[0].name
    ]
    generate_pycpl_recipes(recipes_ok)

    # TODO: external calibration files

    generate_workflow(dataitems_raw)


if __name__ == "__main__":
    main()
