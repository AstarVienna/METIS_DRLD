import glob

# noinspection PyUnresolvedReferences
from pprint import pprint

import numpy
import pytest

from ..drld_parser.data_reduction_library_design import (
    METIS_DataReductionLibraryDesign,
    find_latex_inputs,
    DataItemReference,
    guess_dataitem_type,
    DataItem,
)
from ..drld_parser.hacks import (
    TEMPLATE_IN_DRLD_BUT_NOT_IN_OPERATIONS_WIKI,
    HACK_RECIPES_THAT_ARE_ALLOWED_TO_HAVE_BAD_OUTPUT,
    HACK_RECIPES_THAT_ARE_ALLOWED_TO_BE_MISSING,
    HACK_DATAITEMS_ALLOWED_TO_HAVE_BROKEN_USERS,
    HACK_TEMPLATES_ALLOWED_TO_TRIGGER_RECIPES_WITHOUT_RAW_DATA,
)
from ..drld_parser.template_manual import METIS_TemplateManual


class TestDataReductionLibraryDesign:
    def test_number_of_recipes_extracted_is_not_none(self):
        assert len(METIS_DataReductionLibraryDesign.recipes) > 0

    def test_number_of_dataitems_extracted_is_not_none(self):
        assert len(METIS_DataReductionLibraryDesign.dataitems) > 0

    def test_dataitem_extraction(self):
        """Another way to find the datatimes."""
        sglob = str(METIS_DataReductionLibraryDesign.path_drld / "*.tex")
        paths_tex = glob.glob(sglob)
        lines_single = [
            line
            for path in paths_tex
            for line in open(path).readlines()
            if "paragraph" in line and "dataitem" in line and not line.startswith("%")
        ]
        lines_full = []
        for line in lines_single:
            lmulti = [line]
            for lmn in ["LM", "N", "IFU", "2RG", "GEO"]:
                if f"{{{lmn}_" in line:
                    lmulti.append(line.replace(f"{{{lmn}_", "{det_"))
                if f"_{lmn}}}" in line:
                    lmulti.append(line.replace(f"_{lmn}}}", "_det}"))
                if f"_{lmn}_" in line:
                    lmulti.append(line.replace(f"_{lmn}_", "_det_"))
                if "{det_" in line:
                    lmulti.append(line.replace("{det_", f"{{{lmn}_"))
                if "_det}" in line:
                    lmulti.append(line.replace("_det}", f"_{lmn}}}"))
                if "_det_" in line:
                    lmulti.append(line.replace("_det_", f"_{lmn}_"))
            lines_full.append(lmulti)

        lines_with_and = [line for line in lines_full if " and " in line]

        is_used = numpy.zeros(len(lines_full), dtype=bool)
        not_found = []
        found_more_than_once = []

        # Are all dataitems in the DRLD also in the lines above?
        for di in METIS_DataReductionLibraryDesign.dataitems:
            found = numpy.array(
                [any(di in line for line in lmulti) for lmulti in lines_full]
            )
            foundsingle = numpy.array(
                [
                    # IFU_SCI_COMBINED is there, but also IFU_SCI_COMBINED_TAC,
                    # and they should all have a drsstructure line as well
                    di in line and f"{di}_" not in line and "drsstructure" not in line
                    for line in lines_single
                ]
            )
            if not found.any():
                not_found.append(di)
            if foundsingle.sum() > 1:
                found_more_than_once.append(di)
            is_used |= found | foundsingle

        # Are all lines used for some dataitem?
        not_used_anywhere = [
            (linesingle, linefull)
            for linesingle, linefull, used in zip(lines_single, lines_full, is_used)
            if not used
        ]

        assert not not_found
        assert not found_more_than_once
        assert not not_used_anywhere
        assert all(is_used)
        assert not lines_with_and
        # TODO: Perhaps remove all the _det_ ones and put the actual data
        # product there.
        # assert len(lines_full) + len(lines_with_and) == len(
        #     METIS_DataReductionLibraryDesign.dataitems
        # )

    def test_template_and_recipe_names_do_not_overlap(self):
        names_recipes = {
            name.lower() for name in METIS_DataReductionLibraryDesign.recipes.keys()
        }
        names_templates = {
            name.lower() for name in METIS_TemplateManual.templates.keys()
        }
        assert not (names_recipes & names_templates)

    def test_all_recipe_names_used_also_exist(self):
        names_existing = METIS_DataReductionLibraryDesign.recipes.keys()
        names_used = METIS_DataReductionLibraryDesign.recipe_names_used
        names_existing_lower = [name.lower() for name in names_existing]
        names_not_existing = [
            name
            for name in names_used
            if name not in names_existing
            and name.lower() not in names_existing_lower
            and name not in HACK_RECIPES_THAT_ARE_ALLOWED_TO_BE_MISSING
        ]

        assert (
            not names_not_existing
        ), f"Non existing recipe names: {names_not_existing}"

    @pytest.mark.xfail(
        reason="There are references to recipes with incorrect capitalization, e.g. in LSS_data_items.tex."
    )
    def test_all_recipe_names_are_correctly_capitalized(self):
        names_existing = METIS_DataReductionLibraryDesign.recipes.keys()
        names_used = METIS_DataReductionLibraryDesign.recipe_names_used
        names_existing_lower = [name.lower() for name in names_existing]

        names_bad_capitalization = [
            name
            for name in names_used
            if name not in names_existing and name.lower() in names_existing_lower
        ]
        assert (
            not names_bad_capitalization
        ), f"Recipe names with incorrect capitalization: {names_bad_capitalization}"

    @pytest.mark.xfail(
        reason="There are a few references to templates that do not exist in the normal DRLD.."
    )
    def test_all_templates_used_also_exist_hard(self):
        self.all_templates_used_also_exist(hard=True)

    def test_all_templates_used_also_exist_soft(self):
        self.all_templates_used_also_exist(hard=False)

    def all_templates_used_also_exist(self, hard=True):
        # TODO: hack_rename_template_names_drld and
        #  TEMPLATE_IN_DRLD_BUT_NOT_IN_OPERATIONS_WIKI are currently not
        #  used anymore.
        names_existing = set(METIS_TemplateManual.templates.keys())
        if not hard:
            names_existing = names_existing.union(
                set(TEMPLATE_IN_DRLD_BUT_NOT_IN_OPERATIONS_WIKI)
            )
        names_used = METIS_DataReductionLibraryDesign.template_names_used
        names_existing_lower = [name.lower() for name in names_existing]
        names_not_existing = [
            name
            for name in names_used
            if name not in names_existing and name.lower() not in names_existing_lower
            # TODO: Do something sensible with *'s in these names.
            and "*" not in name
        ]

        assert (
            not names_not_existing
        ), f"Non existing template names: {names_not_existing}"

    def test_all_recipe_data_has_a_name(self):
        bad_input_data = [
            (recipe.name, diref)
            for recipe in METIS_DataReductionLibraryDesign.recipes.values()
            for diref in recipe.input_data
            if diref.name is None
        ]
        bad_output_data = [
            (recipe.name, diref)
            for recipe in METIS_DataReductionLibraryDesign.recipes.values()
            for diref in recipe.output_data
            if diref.name is None
            and recipe.name not in HACK_RECIPES_THAT_ARE_ALLOWED_TO_HAVE_BAD_OUTPUT
        ]
        if bad_input_data:
            pprint(bad_input_data)
        if bad_output_data:
            pprint(bad_output_data)
        assert not bad_input_data
        assert not bad_output_data

    def test_all_recipe_data_is_defined(self):
        bad_input_data = [
            (recipe.name, diref)
            for recipe in METIS_DataReductionLibraryDesign.recipes.values()
            for diref in recipe.input_data
            if diref.name is not None
            and diref.name not in METIS_DataReductionLibraryDesign.dataitems
        ]
        bad_output_data = [
            (recipe.name, diref)
            for recipe in METIS_DataReductionLibraryDesign.recipes.values()
            for diref in recipe.output_data
            if diref.name is not None
            and diref.name not in METIS_DataReductionLibraryDesign.dataitems
        ]
        assert not bad_input_data
        assert not bad_output_data

    def test_input_data_is_created(self):
        """All input data should be created somewhere."""
        # TODO: This test only passes due to HACK_INCORRECT_INPUT_DATA.
        #   So it still needs to be fixed.
        all_output_names = [
            diref.name
            for recipe in METIS_DataReductionLibraryDesign.recipes.values()
            for diref in recipe.output_data
            if diref.name is not None
        ]
        bad_input_data = [
            (recipe.name, diref)
            for recipe in METIS_DataReductionLibraryDesign.recipes.values()
            for diref in recipe.input_data
            if diref.name is not None
            and diref.dtype == "PROD"
            and diref.name not in all_output_names
        ]
        assert not bad_input_data

    def test_datatype_can_be_guessed(self):
        for dn in METIS_DataReductionLibraryDesign.dataitems:
            _ = guess_dataitem_type(dn, raise_exception=True)

    def test_datatypes_are_known(self):
        datatypes_acceptable = {"PROD", "RAW", "EXTCALIB", "STATCALIB"}
        for recipe in METIS_DataReductionLibraryDesign.recipes.values():
            for diref in recipe.input_data + recipe.output_data:
                assert (
                    diref.dtype in datatypes_acceptable
                ), f"Dataitem {diref.name} has type {diref.dtype} which is not allowed."

    def test_datatypes_are_known_strict(self):
        dtypes = [
            diref.dtype
            for recipe in METIS_DataReductionLibraryDesign.recipes.values()
            for diref in recipe.input_data + recipe.output_data
        ]
        # TODO: They should never be FITS or CODE
        assert set(dtypes) == {"PROD", "RAW", "EXTCALIB", "STATCALIB"}

    def test_only_correct_template_types_are_used(self):
        for recipe in METIS_DataReductionLibraryDesign.recipes.values():
            for tn in recipe.templates:
                template = METIS_TemplateManual.get_template(tn)
                # TODO: Why do we process METIS_spec_lm_acq and METIS_spec_n_acq
                assert (
                    template is None
                    or template.ttype in ["Calibration", "Observing", "Engineering"]
                    or template.name
                    in METIS_DataReductionLibraryDesign.templates_acquisition_used
                )

    def test_whether_templates_are_understood(self):
        template_not_in_manual = [
            tn.lower() for tn in TEMPLATE_IN_DRLD_BUT_NOT_IN_OPERATIONS_WIKI
        ]
        problems = []
        for recipe in METIS_DataReductionLibraryDesign.recipes.values():
            for template in recipe.templates:
                if (
                    template is not None
                    and METIS_TemplateManual.get_template(template) is None
                    and template not in template_not_in_manual
                ):
                    problems.append((recipe.name, template))
        assert not problems

    @pytest.mark.xfail(
        rason="['METIS_spec_lmn_obs_AutoChopNodOnSlit', 'METIS_img_lm_cal_platescale', 'METIS_img_n_cal_platescale', 'METIS_ifu_cal_platescale']"
    )
    def test_template_manual_templates_are_used(self):
        """Go through the template manual and check whether we use those templates."""
        templates_expected = [
            template
            for template in METIS_TemplateManual.templates.values()
            if template.ttype in ["Calibration", "Observing"]
        ]
        templates_used = {
            template.lower()
            for recipe in METIS_DataReductionLibraryDesign.recipes.values()
            for template in recipe.templates
        }
        templates_missing = [
            template.name
            for template in templates_expected
            if template.name.lower() not in templates_used
        ]
        assert not templates_missing


    def test_dataitems_sanity(self):
        """Do dataitems internal consistency check."""
        all_errors = []
        for dataitem in METIS_DataReductionLibraryDesign.dataitems.values():
            names_created_by_claimed = [recref.name.lower() for recref in dataitem.created_by if recref.name is not None and recref.name not in HACK_RECIPES_THAT_ARE_ALLOWED_TO_BE_MISSING]
            created_by = METIS_DataReductionLibraryDesign.get_created_by(dataitem.name)
            names_created_by = [recipe.name.lower() for recipe in created_by]
            if created_by:
                s_created_by = "\n".join(
                    [f"Created by:   & \\REC{{{created_by[0].name}}} \\\\"] +
                    [f"              & \\REC{{{rec.name}}} \\\\" for rec in created_by[1:]]
                )
            else:
                s_created_by = ""

            names_input_for_claimed = [
                recref.name.lower()
                for recref in dataitem.input_for
                if recref.name is not None
                and recref.name not in HACK_RECIPES_THAT_ARE_ALLOWED_TO_BE_MISSING
                and recref.name.lower() not in HACK_DATAITEMS_ALLOWED_TO_HAVE_BROKEN_USERS.get(dataitem.name, {})
            ]
            input_for = METIS_DataReductionLibraryDesign.get_input_for(dataitem.name)
            names_input_for = [
                recipe.name.lower()
                for recipe in input_for
            ]
            if input_for:
                s_input_for = "\n".join(
                    [f"Input for:    & \\REC{{{input_for[0].name}}} \\\\"] +
                    [f"              & \\REC{{{rec.name}}} \\\\" for rec in input_for[1:]]
                )
            else:
                s_input_for = ""

            possible_errors = [
                # Test the four times the name is repeated
                (
                    dataitem.name == dataitem.name_header,
                    f"{dataitem.name} uses {dataitem.name_header} as header",
                ),
                (
                    dataitem.do_catg == dataitem.name or dataitem.do_catg in ["n/a"],
                    f"{dataitem.name} uses {dataitem.do_catg} as DO.CATG",
                ),
                (
                    dataitem.pro_catg is None or dataitem.pro_catg == dataitem.name,
                    f"{dataitem.name} uses {dataitem.pro_catg} as PRO.CATG instead of {dataitem.name},"
                ),
                # And two more times in the label/hyperref
                (
                    dataitem.hyperref == f"dataitem:{dataitem.name.lower()}",
                    f"{dataitem.name} uses {dataitem.hyperref} as hyperref",
                ),
                (
                    dataitem.hyperref in dataitem.labels,
                    f"{dataitem.name} uses labels {dataitem.labels}",
                ),
                # More checks
                (
                    dataitem.dtype == dataitem.dtype_header,
                    f"{dataitem.name} has {dataitem.dtype} in the name and {dataitem.dtype_header} in the header",
                ),
                (
                    # If the dataitem is used as input for a recipe, it must have a DO.CATG set.
                    dataitem.do_catg not in ["n/a"] or not dataitem.input_for,
                    f"{dataitem.name} is used as input for {dataitem.input_for} but has {dataitem.do_catg} as DO.CATG",
                ),
                (
                    not (dataitem.pro_catg and (dataitem.dpr_catg or dataitem.dpr_type or dataitem.dpr_tech)),
                    f"{dataitem.name} has PRO.CATG {dataitem.pro_catg} and also some of the DPR keywords",
                ),
                (
                    sum([dataitem.dpr_catg is not None, dataitem.dpr_tech  is not None, dataitem.dpr_type is not None]) in (0, 3),
                    f"{dataitem.name} has only some of the DPR keywords defined",
                ),
                (
                    dataitem.dtype != "RAW" or dataitem.pro_catg is None,
                    f"{dataitem.name} is {dataitem.dtype} but has PRO.CATG defined as {dataitem.pro_catg}",
                ),
                (
                    dataitem.dtype == "RAW" or dataitem.dpr_catg is None,
                    f"{dataitem.name} is {dataitem.dtype} but has DPR.CATG defined as {dataitem.dpr_catg}",
                ),
                (
                    dataitem.dtype == "RAW" or not dataitem.templates,
                    f"{dataitem.name} is not RAW but has templats {dataitem.templates}",
                ),
                (
                    dataitem.dtype != "RAW" or dataitem.templates,
                    f"{dataitem.name} is RAW but is not produced by any template",
                ),
                (
                    dataitem.dtype not in {"PROD", "STATCALIB"} or dataitem.created_by,
                    f"""{dataitem.name} is {dataitem.dtype} but is not produced by any recipe
{s_created_by}""",
                ),
                (
                    dataitem.dtype in {"RAW", "PROD", "STATCALIB", "EXTCALIB"},
                    f"{dataitem.name} has unknown dtype {dataitem.dtype}",
                ),
                # Now also some external checks.
                (
                    set(names_created_by_claimed) == set(names_created_by),
                    f"""{dataitem.name} claims to be created by {names_created_by_claimed}
{s_created_by}"""
                ),
                (
                    set(names_input_for_claimed) == set(names_input_for),
                    f"""{dataitem.name} claims to be input for {names_input_for_claimed}
{s_input_for}"""
                ),
            ]
            # TODO: Check created_by and input_for RecipeRefs actually have a name, or are HITRAN
            # TODO: Check OCA keywords
            # TODO: Check HDU headers
            all_errors += [errorstring for is_ok, errorstring in possible_errors if not is_ok]

        if all_errors:
            print()
            print()
            print("\n".join(all_errors))
        assert not all_errors, f"Found {len(all_errors)} problems with the dataitems internal consistency."


    def test_dataitems_refer_to_correct_recipes(self):
        """Check whether dataitems have the correct recipes."""
        allerrors = {
            dataitem.name: {
                "bad_created_by": [
                    reciperef.name
                    for reciperef in dataitem.created_by
                    if reciperef.name is not None and reciperef.name.lower() not in [
                        name.lower() for name in METIS_DataReductionLibraryDesign.recipes if name is not None
                    ] and reciperef.name not in HACK_RECIPES_THAT_ARE_ALLOWED_TO_BE_MISSING
                ],
                "bad_input_for": [
                    reciperef.name
                    for reciperef in dataitem.input_for
                    if reciperef.name is not None and  reciperef.name.lower() not in [
                        name.lower() for name in METIS_DataReductionLibraryDesign.recipes if name is not None
                    ] and reciperef.name not in HACK_RECIPES_THAT_ARE_ALLOWED_TO_BE_MISSING
                ],
            } for dataitem in METIS_DataReductionLibraryDesign.dataitems.values()
        }
        errors = False
        for (name, theerrors) in allerrors.items():
            if theerrors["bad_created_by"]:
                errors = True
                print(f"{name} claims to be created by recipes that do not exist: {theerrors['bad_created_by']}")
            if theerrors["bad_input_for"]:
                errors = True
                print(f"{name} claims to be input for recipes that do not exist: {theerrors['bad_input_for']}")
        assert not errors

    def test_templates(self):
        """Test whether all templates produce data."""
        errors = []
        for template in METIS_DataReductionLibraryDesign.template_names_used_normal:
            if template in HACK_TEMPLATES_ALLOWED_TO_TRIGGER_RECIPES_WITHOUT_RAW_DATA:
                continue
            dataitems = METIS_DataReductionLibraryDesign.get_raws_for_template(template)
            recipes = METIS_DataReductionLibraryDesign.get_recipes_for_template(template)
            if not dataitems:
                errors.append(f"{template} produces no raw data but triggers {recipes}")
        if errors:
            errors = set(errors)
            print()
            for error in errors:
                print(error)
        assert not errors, f"There are {len(errors)} templates that produce no data."

    def test_recipe_input(self):
        """Check whether input to recipes matches templates."""
        errors = []
        for recipe in METIS_DataReductionLibraryDesign.recipes.values():
            raws_unaccounted_for = []
            templates_unaccounted_for = set(recipe.templates)
            for dataitemref in recipe.input_data:
                dataitem = METIS_DataReductionLibraryDesign.dataitems[dataitemref.name]
                if dataitem.templates is None:
                    continue
                if not set(dataitem.templates).union(set(recipe.templates)):
                    # There is no overlap between templates, so this dataitem cannot be used as input
                    raws_unaccounted_for.append(dataitem)
                templates_unaccounted_for -= set(dataitem.templates)
            # if raws_unaccounted_for:
            #     errors.append(f"{recipe.name} has {dataitem.name} as input, but none of its templates {dataitem.templates}")
            if templates_unaccounted_for:
                for template in templates_unaccounted_for:
                    if template in HACK_TEMPLATES_ALLOWED_TO_TRIGGER_RECIPES_WITHOUT_RAW_DATA:
                        continue
                    data = METIS_DataReductionLibraryDesign.get_raws_for_template(template)
                    errors.append(f"{recipe.name} is triggered by {template}, but none of its data {data} is used as input")
        if errors:
            print()
            for error in errors:
                print(error)
        assert not errors, f"The input_data and templates of {len(errors)} recipes is inconsistent."


class TestFindLatexInputs:
    def test_find_latex_inputs(self):
        fns_expected = {
            "CalDB_data_items.tex",
            "LMS_data_items.tex",
            "IMG_data_items.tex",
            "LSS_data_items.tex",
            "ADI_data_items.tex",
        }
        path = (
            METIS_DataReductionLibraryDesign.path_drld / "09_0-DRL-Data-Structures.tex"
        )
        paths_input = find_latex_inputs(path)
        filenames_input = {pp.name for pp in paths_input}
        assert (
            filenames_input == fns_expected
        ), f"Found more dataitems: {filenames_input - fns_expected}, or less: {fns_expected - filenames_input}"


class TestParseDataItemReference:
    def test_parse_dataitem_reference(self):
        diref = DataItemReference.from_recipe_line(
            r"\hyperref[dataitem:nlsssciobjmap]{\PROD{N_LSS_SCI_OBJ_MAP}}: Pixel map of object pixels"
        )
        assert diref.name == "N_LSS_SCI_OBJ_MAP"
        assert diref.dtype == "PROD"
        assert diref.hyperref == "dataitem:nlsssciobjmap"
        assert diref.description == "Pixel map of object pixels"

        diref = DataItemReference.from_recipe_line(
            r"\hyperref[dataitem:nlsswaveguess]{\STATCALIB{N_LSS_WAVE_GUESS}}"
        )
        assert diref.name == "N_LSS_WAVE_GUESS"
        assert diref.dtype == "STATCALIB"
        assert diref.hyperref == "dataitem:nlsswaveguess"
        assert diref.description is None

        diref = DataItemReference.from_recipe_line(r"\PROD{MF\_BEST\_FIT\_TAB}")
        assert diref.name == "MF_BEST_FIT_TAB"
        assert diref.dtype == "PROD"
        assert diref.hyperref is None
        assert diref.description is None

        diref = DataItemReference.from_recipe_line(
            r"\PROD{N_DIST_REDUCED} (reduced grid mask images)"
        )
        assert diref.name == "N_DIST_REDUCED"
        assert diref.dtype == "PROD"
        assert diref.hyperref is None
        assert diref.description == "reduced grid mask images"

        diref = DataItemReference.from_recipe_line(
            "Chopped/nodded science or standard images"
        )
        assert diref.name is None
        assert diref.dtype == "PROD"
        assert diref.hyperref is None
        assert diref.description == "Chopped/nodded science or standard images"

        diref = DataItemReference.from_recipe_line(
            "$N\\times$ \\hyperref[dataitem:nlssrsrfpinhraw]{\\RAW{N_LSS_RSRF_PINH_RAW}}"
        )
        assert diref.name == "N_LSS_RSRF_PINH_RAW"
        assert diref.dtype == "RAW"
        assert diref.hyperref == "dataitem:nlssrsrfpinhraw"
        assert diref.description == "$N\\times$"

        diref = DataItemReference.from_recipe_line(
            "Calibrated science images (\\PROD{LM_SCI_CALIBRATED})"
        )
        assert diref.name == "LM_SCI_CALIBRATED"
        assert diref.dtype == "PROD"
        assert diref.hyperref is None
        assert diref.description == "Calibrated science images"


def test_parse_dataitem_from_paragraph():
    """Test parsing of dataitem."""

    stable = r"""\paragraph{\hyperref[dataitem:master_n_lss_rsrf]{\PROD{MASTER_N_LSS_RSRF}}}\label{dataitem:master_n_lss_rsrf}
\begin{recipedef}
\textbf{\ac{FITS} file structure:}\\
Name: & \hyperref[dataitem:master_n_lss_rsrf]{\PROD{MASTER_N_LSS_RSRF}}\\[0.3cm]
Description: & LM-band \ac{LSS} Master \ac{RSRF}.\\[0.3cm]
\hyperref[fits:pro.catg]{\FITS{PRO.CATG}}: & \FITS{MASTER_N_LSS_RSRF}\\
OCA keywords: & \hyperref[fits:pro.catg]{\FITS{PRO.CATG}},  \hyperref[fits:ins.opti12.name]{\FITS{INS.OPTI12.NAME}}, \hyperref[fits:ins.opti13.name]{\FITS{INS.OPTI13.NAME}}, \hyperref[fits:ins.opti14.name]{\FITS{INS.OPTI14.NAME}}\\
\FITS{DPR.CATG}: & \FITS{HELLO}\\[0.3cm]
\FITS{DPR.TYPE}: & \FITS{WORLD}\\[0.3cm]
\FITS{DPR.TECH}: & \FITS{HOWRU}\\[0.3cm]
\FITS{PRO.CATG}: & \FITS{MASTER_N_LSS_RSRF}\\[0.3cm]
\FITS{DO.CATG}: & \FITS{MASTER_N_LSS_RSRF}\\[0.3cm]
Created by: & \hyperref[rec:metis_n_lss_rsrf]{\REC{metis_n_lss_rsrf}}\\
Input for recipes: & \hyperref[rec:metis_n_lss_trace]{\REC{metis_n_lss_trace}}\\
                   & \hyperref[rec:metis_n_lss_std]{\REC{metis_n_lss_std}}\\
                   & \hyperref[rec:metis_n_lss_sci]{\REC{metis_n_lss_sci}}\\
Processing \ac{FITS} Keywords: & provided at \ac{PAE}\\
Templates:             & \TPL{METIS_ifu_vc_obs_FixedSkyOffset} \\
                       & \TPL{METIS_ifu_ext_vc_obs_FixedSkyOffset} \\
\end{recipedef}
%\paragraph{\hyperref[dataitem:lm_rsrf_raw]{\PROD{LM_RSRF_RAW}}}\label{drsstructure:LM_RSRF_RAW}
\begin{datastructdef}
\textbf{Corresponding \ac{CPL} structure:}
\begin{enumerate}
    \item \texttt{cpl\_propertylist * keywords: Primary keywords (\hyperref[fits:pro.catg]{\FITS{PRO.CATG}},  \hyperref[fits:ins.opti12.name]{\FITS{INS.OPTI12.NAME}}, \hyperref[fits:ins.opti13.name]{\FITS{INS.OPTI13.NAME}}, \hyperref[fits:ins.opti14.name]{\FITS{INS.OPTI14.NAME}})}
    \item \texttt{hdrl\_imagelist * image: Three image layers (data, error, mask)}
    \item \texttt{cpl\_propertylist * plistarray[]: Extension keywords}
\end{enumerate}
\end{datastructdef}"""
    dataitem = DataItem.from_paragraph(stable)
    assert dataitem.templates == ["METIS_ifu_vc_obs_FixedSkyOffset".lower(), "METIS_ifu_ext_vc_obs_FixedSkyOffset".lower()]
    assert [recref.name for recref in dataitem.input_for] == ["metis_n_lss_trace", "metis_n_lss_std", "metis_n_lss_sci"]
    assert [recref.name for recref in dataitem.created_by] == ["metis_n_lss_rsrf"]
    assert dataitem.name == "MASTER_N_LSS_RSRF"
    assert dataitem.hyperref == "dataitem:master_n_lss_rsrf"
    assert dataitem.labels == ["dataitem:master_n_lss_rsrf"]
    assert dataitem.dtype == "PROD"
    assert dataitem.name_header =="MASTER_N_LSS_RSRF"
    assert dataitem.dtype_header == "PROD"
    assert dataitem.pro_catg == "MASTER_N_LSS_RSRF"
    assert dataitem.do_catg == "MASTER_N_LSS_RSRF"
    assert dataitem.dpr_catg == "HELLO"
    assert dataitem.dpr_tech == "HOWRU"
    assert dataitem.dpr_type == "WORLD"

    stable = r"""\paragraph{\hyperref[dataitem:badpix_map_2rg]{\PROD{BADPIX_MAP_2RG}}}\label{dataitem:badpix_map_2rg}
See \hyperref[dataitem:badpix_map_det]{\PROD{BADPIX_MAP_det}}.
"""
    dataitem = DataItem.from_paragraph(stable)
    assert dataitem.name_header == "BADPIX_MAP_2RG"
    assert dataitem.name is None


def test_tikz():
    """Test whether the names used in the tikz figures exist."""


# TODO: Order of input in recipes, primary input should go first!
# TODO: the raw dark was an EXTCALIB, should not happen!
# TODO: Check whether LM data is created with LM templates and processed with LM recipes, similar for N
