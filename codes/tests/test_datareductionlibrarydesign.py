import glob
import re

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
    AssociationMatrix,
)
from ..drld_parser.hacks import (
    TEMPLATE_IN_DRLD_BUT_NOT_IN_OPERATIONS_WIKI,
    HACK_RECIPES_THAT_ARE_ALLOWED_TO_HAVE_BAD_OUTPUT,
    HACK_RECIPES_THAT_ARE_ALLOWED_TO_BE_MISSING,
    HACK_DATAITEMS_ALLOWED_TO_HAVE_BROKEN_USERS,
    HACK_TEMPLATES_ALLOWED_TO_TRIGGER_RECIPES_WITHOUT_RAW_DATA,
    HACK_RECIPES_THAT_DO_NOT_NEED_A_FIGURE,
    HACK_RECIPES_THAT_WERE_NOT_GOING_TO_CHECK_TIKZ_FOR,
)
from ..drld_parser.template_manual import METIS_TemplateManual


class TestDataReductionLibraryDesign:
    def test_number_of_recipes_extracted_is_not_none(self):
        assert len(METIS_DataReductionLibraryDesign.recipes) > 0

    def test_number_of_dataitems_extracted_is_not_none(self):
        assert len(METIS_DataReductionLibraryDesign.dataitems) > 0

    def test_dataitem_extraction(self):
        """Another way to find the dataitems.

        This test directly checks the paragraph headers in all tex files for
        data items.
        This check is rather fragile, so it will probably break at some point.
        """
        sglob = str(METIS_DataReductionLibraryDesign.path_drld / "*.tex")
        paths_tex = glob.glob(sglob)
        lines1 = [
            line
            for path in paths_tex
            for line in open(path).readlines()
        ]
        lines2 = [
            # Some paragraph headers have their label on the next line.
            l1 + (l2 if "label" in l2 else "") 
            for l1, l2 in zip(lines1, lines1[1:])
            if "paragraph" in l1
        ]
        lines_single1 = [
            line
            for line in lines2
            if "paragraph" in line and "dataitem" in line and not line.startswith("%")
        ]
        # Prevent paragraphs after labels.
        lines_single2 = [
            line
            for line in lines_single1
            if line.index("paragraph") < line.index("dataitem")
        ]
        lines_full = []
        for line in lines_single2:
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
                    for line in lines_single2
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
            for linesingle, linefull, used in zip(lines_single2, lines_full, is_used)
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

    @staticmethod
    def all_templates_used_also_exist(hard=True):
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
        rason="['METIS_spec_lmn_obs_AutoChopNodOnSlit', 'METIS_img_lm_cal_platescale', 'METIS_img_n_cal_platescale', "
              "'METIS_ifu_cal_platescale']"
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
            names_created_by_claimed = [
                recref.name.lower()
                for recref in dataitem.created_by
                if recref.name is not None
                and recref.name not in HACK_RECIPES_THAT_ARE_ALLOWED_TO_BE_MISSING
            ]
            created_by = METIS_DataReductionLibraryDesign.get_created_by(dataitem.name)
            names_created_by = [recipe.name.lower() for recipe in created_by]
            if created_by:
                s_created_by = "\n".join(
                    [f"Created by:   & \\REC{{{created_by[0].name}}} \\\\"]
                    + [
                        f"              & \\REC{{{rec.name}}} \\\\"
                        for rec in created_by[1:]
                    ]
                )
            else:
                s_created_by = ""

            names_input_for_claimed = [
                recref.name.lower()
                for recref in dataitem.input_for
                if recref.name is not None
                and recref.name not in HACK_RECIPES_THAT_ARE_ALLOWED_TO_BE_MISSING
                and recref.name.lower()
                not in HACK_DATAITEMS_ALLOWED_TO_HAVE_BROKEN_USERS.get(
                    dataitem.name, {}
                )
            ]
            input_for = METIS_DataReductionLibraryDesign.get_input_for(dataitem.name)
            names_input_for = [recipe.name.lower() for recipe in input_for]
            if input_for:
                s_input_for = "\n".join(
                    [f"Input for:    & \\REC{{{input_for[0].name}}} \\\\"]
                    + [
                        f"              & \\REC{{{rec.name}}} \\\\"
                        for rec in input_for[1:]
                    ]
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
                    f"{dataitem.name} uses {dataitem.pro_catg} as PRO.CATG instead of {dataitem.name},",
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
                    not (
                        dataitem.pro_catg
                        and (
                            dataitem.dpr_catg or dataitem.dpr_type or dataitem.dpr_tech
                        )
                    ),
                    f"{dataitem.name} has PRO.CATG {dataitem.pro_catg} and also some of the DPR keywords",
                ),
                (
                    sum(
                        [
                            dataitem.dpr_catg is not None,
                            dataitem.dpr_tech is not None,
                            dataitem.dpr_type is not None,
                        ]
                    )
                    in (0, 3),
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
{s_created_by}""",
                ),
                (
                    set(names_input_for_claimed) == set(names_input_for),
                    f"""{dataitem.name} claims to be input for {names_input_for_claimed}
{s_input_for}""",
                ),
            ]
            # TODO: Check created_by and input_for RecipeRefs actually have a name, or are HITRAN
            # TODO: Check OCA keywords
            # TODO: Check HDU headers
            all_errors += [
                errorstring for is_ok, errorstring in possible_errors if not is_ok
            ]

        if all_errors:
            print()
            print()
            print("\n".join(all_errors))
        assert (
            not all_errors
        ), f"Found {len(all_errors)} problems with the dataitems internal consistency."

    def test_dataitems_refer_to_correct_recipes(self):
        """Check whether dataitems have the correct recipes."""
        allerrors = {
            dataitem.name: {
                "bad_created_by": [
                    reciperef.name
                    for reciperef in dataitem.created_by
                    if reciperef.name is not None
                    and reciperef.name.lower()
                    not in [
                        name.lower()
                        for name in METIS_DataReductionLibraryDesign.recipes
                        if name is not None
                    ]
                    and reciperef.name
                    not in HACK_RECIPES_THAT_ARE_ALLOWED_TO_BE_MISSING
                ],
                "bad_input_for": [
                    reciperef.name
                    for reciperef in dataitem.input_for
                    if reciperef.name is not None
                    and reciperef.name.lower()
                    not in [
                        name.lower()
                        for name in METIS_DataReductionLibraryDesign.recipes
                        if name is not None
                    ]
                    and reciperef.name
                    not in HACK_RECIPES_THAT_ARE_ALLOWED_TO_BE_MISSING
                ],
            }
            for dataitem in METIS_DataReductionLibraryDesign.dataitems.values()
        }
        errors = False
        for name, theerrors in allerrors.items():
            if theerrors["bad_created_by"]:
                errors = True
                print(
                    f"{name} claims to be created by recipes that do not exist: {theerrors['bad_created_by']}"
                )
            if theerrors["bad_input_for"]:
                errors = True
                print(
                    f"{name} claims to be input for recipes that do not exist: {theerrors['bad_input_for']}"
                )
        assert not errors

    def test_templates(self):
        """Test whether all templates produce data."""
        errors = []
        for template in METIS_DataReductionLibraryDesign.template_names_used_normal:
            if template in HACK_TEMPLATES_ALLOWED_TO_TRIGGER_RECIPES_WITHOUT_RAW_DATA:
                continue
            dataitems = METIS_DataReductionLibraryDesign.get_raws_for_template(template)
            recipes = METIS_DataReductionLibraryDesign.get_recipes_for_template(
                template
            )
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
                if not dataitem.templates:
                    continue
                if not set(dataitem.templates).union(set(recipe.templates)):
                    # There is no overlap between templates, so this dataitem cannot be used as input
                    raws_unaccounted_for.append(dataitem)
                templates_unaccounted_for -= set(dataitem.templates)
                if raws_unaccounted_for:
                    errors.append(
                        f"{recipe.name} has {dataitem.name} as input, but none of its templates {dataitem.templates}"
                    )
            if templates_unaccounted_for:
                for template in templates_unaccounted_for:
                    if (
                        template
                        in HACK_TEMPLATES_ALLOWED_TO_TRIGGER_RECIPES_WITHOUT_RAW_DATA
                    ):
                        continue
                    data = METIS_DataReductionLibraryDesign.get_raws_for_template(
                        template
                    )
                    errors.append(
                        f"{recipe.name} is triggered by {template}, but none of its data {data} is used as input"
                    )
        if errors:
            print()
            for error in errors:
                print(error)
        assert (
            not errors
        ), f"The input_data and templates of {len(errors)} recipes is inconsistent."

    def test_recipes_first_input_is_from_template(self):
        """The first input of the recipes should be from the templates."""
        recipes_with_raw_data = [
            recipe
            for recipe in METIS_DataReductionLibraryDesign.recipes.values()
            if recipe.templates
        ]
        problems = []
        for recipe in recipes_with_raw_data:
            dataitemref = recipe.input_data[0]
            input_first = METIS_DataReductionLibraryDesign.dataitems[dataitemref.name]
            if input_first.dtype != "RAW":
                problems.append(
                    f"{recipe} has {input_first.name} as input, but this is {input_first.dtype} instead of RAW"
                )

        if problems:
            print()
            for problem in problems:
                print(problem)

        assert (
            not problems
        ), f"There are {len(problems)} recipe where the the first input is not RAW"

    def test_recipes_input_different_templates(self):
        """Check whether we can make DPR keywords easily.

        It would be the easiest if each recipe has input from one specific
        set of raw data. That is, that if other recipes have the same input,
        then it should be exactly the same.
        """
        recipes_with_raw_data = [
            recipe
            for recipe in METIS_DataReductionLibraryDesign.recipes.values()
            if recipe.templates
        ]
        problem = 0
        for recipe1 in recipes_with_raw_data:
            templates1 = set(recipe1.templates)
            for recipe2 in recipes_with_raw_data:
                if recipe1.input_data[0].name != recipe2.input_data[0].name:
                    # Different input data, so it is fine
                    continue
                templates2 = set(recipe2.templates)
                union = templates1.union(templates2)
                in1notin2 = templates1.difference(templates2)
                in2notin1 = templates1.difference(templates2)
                if templates1 == templates2 or union == {}:
                    continue
                problem += 1
                print(
                    f"{recipe1.name} and {recipe2.name} share templates, but not exactly"
                )
                print(f"{templates1=}")
                print(f"{templates2=}")
                print(f"{union=}")
                print(f"{in1notin2=}")
                print(f"{in2notin1=}")

        assert not problem, f"{problem} recipes have partially overlapping templates"

    def test_dpr_keywords(self):
        """Check whether DPR keywords are uniq."""
        dataitems_with_dpr = [
            dataitem
            for dataitem in METIS_DataReductionLibraryDesign.dataitems.values()
            if dataitem.templates
        ]
        problems = []
        dprs = {}
        for dataitem in dataitems_with_dpr:
            if "IFU" in dataitem.name and "IFU" not in dataitem.dpr_tech:
                problems.append(
                    f"{dataitem.name} has {dataitem.dpr_tech} as DPR.TECH instead of IFU"
                )
            if "IFU" in dataitem.dpr_tech and "IFU" not in dataitem.name:
                problems.append(
                    f"{dataitem.name} has {dataitem.dpr_tech} as DPR.TECH but is not IFU"
                )
            if "SCI" in dataitem.name and "SCIENCE" not in dataitem.dpr_catg:
                problems.append(
                    f"{dataitem.name} has {dataitem.dpr_catg} as DPR.CATG instead of SCIENCE"
                )
            if "SCI" not in dataitem.name and "SCIENCE" in dataitem.dpr_catg:
                problems.append(
                    f"{dataitem.name} has {dataitem.dpr_catg} as DPR.CATG but is not SCIENCE"
                )

            dpr_key = (dataitem.dpr_catg, dataitem.dpr_tech, dataitem.dpr_type)
            if dpr_key not in dprs:
                dprs[dpr_key] = set()
            dprs[dpr_key].add(dataitem.name)

        for dpr_key, dataitems in dprs.items():
            if len(dataitems) > 1:
                problems.append(
                    f"{len(dataitems)} have DPR keys {dpr_key}: {dataitems}"
                )

        pprint(sorted(dprs.items()))

        if problems:
            print()
            for problem in problems:
                print(problem)

        assert not problems, f"There are {len(problems)} with the DPR keywords."

        recipes_from_docatg = {
            docatg: METIS_DataReductionLibraryDesign.get_recipes_for_dataitem(docatg)
            for (docatg,) in dprs.values()
        }
        lenrecipes = max(
            len(recipe)
            for recipes in recipes_from_docatg.values()
            for recipe in recipes
        )

        lencatg = max(len(catg) for catg, _, _ in dprs)
        lentech = max(len(tech) for _, tech, _ in dprs)
        lentype = max(len(typp) for _, _, typp in dprs)
        lendocatg = max(len(docatg) for (docatg,) in dprs.values())
        idem = '"'
        print(
            "┏━"
            + "━" * lencatg
            + "━┯━"
            + "━" * lentech
            + "━┯━"
            + "━" * lentype
            + "━┯━"
            + "━" * lendocatg
            + "━┯━"
            + "━" * lenrecipes
            + "━┓"
        )
        print(
            f"┃ {'DPR.CATG':<{lencatg}} │ {'DPR.TECH':<{lentech}} │ {'DPR.TYPE':<{lentype}} │"
            f" {'DO.CATG':<{lendocatg}} │ {'recipes':<{lenrecipes}} ┃"
        )
        print(
            "┣━"
            + "━" * lencatg
            + "━┿━"
            + "━" * lentech
            + "━┿━"
            + "━" * lentype
            + "━┿━"
            + "━" * lendocatg
            + "━┿━"
            + "━" * lenrecipes
            + "━┫"
        )
        for (catg, tech, typp), (docatg,) in sorted(dprs.items()):
            for ri, recipe in enumerate(recipes_from_docatg[docatg]):
                if ri == 0:
                    print(
                        f"┃ {catg:<{lencatg}} │ {tech:<{lentech}} │ {typp:<{lentype}} │"
                        f" {docatg:<{lendocatg}} │ {recipe:<{lenrecipes}} ┃"
                    )
                else:
                    print(
                        f"┃ {idem:<{lencatg}} │ {idem:<{lentech}} │ {idem:<{lentype}} │"
                        f" {idem:<{lendocatg}} │ {recipe:<{lenrecipes}} ┃"
                    )
        print(
            "┗━"
            + "━" * lencatg
            + "━┷━"
            + "━" * lentech
            + "━┷━"
            + "━" * lentype
            + "━┷━"
            + "━" * lendocatg
            + "━┷━"
            + "━" * lenrecipes
            + "━┛"
        )


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
        assert diref.description == "$N times$"

        diref = DataItemReference.from_recipe_line(
            "Calibrated science images (\\PROD{LM_SCI_CALIBRATED})"
        )
        assert diref.name == "LM_SCI_CALIBRATED"
        assert diref.dtype == "PROD"
        assert diref.hyperref is None
        assert diref.description == "Calibrated science images"


def test_parse_dataitem_from_paragraph():
    """Test parsing of dataitem."""
    stable = r"""\paragraph{\PROD{MASTER_N_LSS_RSRF}}\label{dataitem:master_n_lss_rsrf}
    \begin{recipedef}
    \textbf{\ac{FITS} file structure:}\\
    Name: & \PROD{MASTER_N_LSS_RSRF}\\[0.3cm]
    Description: & LM-band \ac{LSS} Master \ac{RSRF}.\\[0.3cm]
    \FITS{PRO.CATG}: & \FITS{MASTER_N_LSS_RSRF}\\
    OCA keywords: & \FITS{PRO.CATG},  \FITS{INS.OPTI12.NAME}, \FITS{INS.OPTI13.NAME}, \FITS{INS.OPTI14.NAME}\\
    \FITS{DPR.CATG}: & \FITS{HELLO}\\[0.3cm]
    \FITS{DPR.TYPE}: & \FITS{WORLD}\\[0.3cm]
    \FITS{DPR.TECH}: & \FITS{HOWRU}\\[0.3cm]
    \FITS{PRO.CATG}: & \FITS{MASTER_N_LSS_RSRF}\\[0.3cm]
    \FITS{DO.CATG}: & \FITS{MASTER_N_LSS_RSRF}\\[0.3cm]
    Created by: & \REC{metis_n_lss_rsrf}\\
    Input for recipes: & \REC{metis_n_lss_trace}\\
                       & \REC{metis_n_lss_std}\\
                       & \REC{metis_n_lss_sci}\\
    Processing \ac{FITS} Keywords: & provided at \ac{PAE}\\
    Templates:             & \TPL{METIS_ifu_vc_obs_FixedSkyOffset} \\
                           & \TPL{METIS_ifu_ext_vc_obs_FixedSkyOffset} \\
    \end{recipedef}
    \begin{datastructdef}
    \textbf{Corresponding \ac{CPL} structure:}
    \begin{enumerate}
        \item \texttt{cpl\_propertylist * keywords: Primary keywords (\FITS{PRO.CATG},  \FITS{INS.OPTI12.NAME},"""
    r"""\FITS{INS.OPTI13.NAME}, \FITS{INS.OPTI14.NAME})}
        \item \texttt{hdrl\_imagelist * image: Three image layers (data, error, mask)}
        \item \texttt{cpl\_propertylist * plistarray[]: Extension keywords}
    \end{enumerate}
    \end{datastructdef}"""
    dataitem = DataItem.from_paragraph(stable)
    assert dataitem.templates == [
        "METIS_ifu_vc_obs_FixedSkyOffset".lower(),
        "METIS_ifu_ext_vc_obs_FixedSkyOffset".lower(),
    ]
    assert [recref.name for recref in dataitem.input_for] == [
        "metis_n_lss_trace",
        "metis_n_lss_std",
        "metis_n_lss_sci",
    ]
    assert [recref.name for recref in dataitem.created_by] == ["metis_n_lss_rsrf"]
    assert dataitem.name == "MASTER_N_LSS_RSRF"
    assert dataitem.hyperref == "dataitem:master_n_lss_rsrf"
    assert dataitem.labels == ["dataitem:master_n_lss_rsrf"]
    assert dataitem.dtype == "PROD"
    assert dataitem.name_header == "MASTER_N_LSS_RSRF"
    assert dataitem.dtype_header == "PROD"
    assert dataitem.pro_catg == "MASTER_N_LSS_RSRF"
    assert dataitem.do_catg == "MASTER_N_LSS_RSRF"
    assert dataitem.dpr_catg == "HELLO"
    assert dataitem.dpr_tech == "HOWRU"
    assert dataitem.dpr_type == "WORLD"

    stable = r"""\paragraph{\PROD{BADPIX_MAP_2RG}}\label{dataitem:badpix_map_2rg}
    See \PROD{BADPIX_MAP_det}.
    """
    dataitem = DataItem.from_paragraph(stable)
    assert dataitem.name_header == "BADPIX_MAP_2RG"
    assert dataitem.name is None


def test_associationmatrices():
    """Regular association matrix test."""
    check_associationmatrices(check_input=False)


# @pytest.mark.xfail(reason="Many input is still missing from association matrices."
#                           "This test also complains about non-linearity and gain"
#                           "which we are still considering to combine."
#                           "So test_associationmatrices_input_ignore_nonlin should"
#                           "probably be fixed first, as that is simpler.")
def test_associationmatrices_input():
    """Test to also check whether all the recipe input is present in the matrix"""
    check_associationmatrices(check_input=True, ignore_nonlinearity=False)


# @pytest.mark.xfail(reason="Some input is still missing from association matrices.")
def test_associationmatrices_input_ignore_nonlin():
    """Test to also check whether all the recipe input is present in the matrix

    But ignore the non-linearity, gain, flat, rsrf, as we are still discussing
    whether to combine them.
    """
    check_associationmatrices(check_input=True, ignore_nonlinearity=True)


def check_associationmatrices(check_input=False, ignore_nonlinearity=True):
    """Some tests for the association matrices. This code is horrible.

    With check_input=True, it is checked whether all input that is listed in
    the recipe is also included in the association matrix.
    """
    asso_lm = AssociationMatrix(fn="tikz/IMG_LM_assomap_tikz.tex")
    asso_n = AssociationMatrix(fn="tikz/IMG_N_assomap_tikz.tex")
    asso_ifu = AssociationMatrix(fn="tikz/IFU_assomap_tikz.tex")

    problems_all = []
    for asso in [asso_lm, asso_n, asso_ifu]:
        # print()
        # print(asso.filename)
        problems = []
        for recipecolumn in asso.matrix:
            problems_recipe = []

            # Get the recipe
            recipecell = recipecolumn[0]
            reciperef = recipecell.recipe
            raw_dataitemref = recipecell.dataitems[0] if recipecell.dataitems else None
            if reciperef is None:
                # can happen if there is calibration data on the left
                assert str(recipecell) == "(empty)"
                continue
            recipe_name = reciperef.name
            recipe_name2 = "metis_" + recipe_name
            recipe = None
            if recipe_name in METIS_DataReductionLibraryDesign.recipes:
                recipe = METIS_DataReductionLibraryDesign.recipes[recipe_name]
            elif recipe_name2 in METIS_DataReductionLibraryDesign.recipes:
                problems_recipe.append(
                    f"{recipe_name} does not exist but {recipe_name2} does"
                )
                recipe = METIS_DataReductionLibraryDesign.recipes[recipe_name2]
            else:
                problems_recipe.append(f"{recipe_name} does not exist")

            if raw_dataitemref is not None:
                assert recipe_name
                # TODO: Support other organizations of the matrix?
                # TODO: E.g. now the LM and N band show data products there too
                # assert raw_dataitemref.dtype == "RAW"
                if (
                    raw_dataitemref.name
                    not in METIS_DataReductionLibraryDesign.dataitems
                ):
                    problems_recipe.append(
                        f"{recipe_name} is triggered by {raw_dataitemref.name} which does not exist"
                    )

            if not recipe:
                problems.append((recipe_name, problems_recipe))
                continue

            # Get the first dataitem(s)
            if recipecell.dataitems is not None:
                for input_primary in recipecell.dataitems:
                    input_primary_real = recipe.input_data[0]
                    # The input_primary does not have to be the first,
                    # e.g. metis_det_dark only lists the GEO one as first input.
                    is_input_primary_really_input = any(
                        input_primary.name == inp.name for inp in recipe.input_data
                    )
                    if not is_input_primary_really_input:
                        problems_recipe.append(
                            f"{recipe.name} should not have {input_primary.name}"
                            f" as primary input but {input_primary_real.name}"
                        )
            else:
                # There is not really a way to get to the primary data item
                # because then it would be necessary to follow the lines, e.g. for IFU.
                # TODO: Perhaps follow those lines anyway?
                ...

            # Try to see whether input listed in the matrix is also listed
            # as input in the recipe table itself.
            dataitems_found = []
            for icell, cell in enumerate(recipecolumn):
                if cell.connection:
                    # Find out what it is.
                    # TODO: Use the path? But cannot always do that.
                    # Needs to be in reverse order because occasionally there
                    # are multiple products on one row.
                    for cell2 in [col[icell] for col in asso.matrix][::-1]:
                        if cell2.dataitems:
                            # found it
                            thedataitems = cell2.dataitems
                            break
                    else:
                        raise ValueError
                    dataitems_found += thedataitems
                    is_input_really_input = any(
                        thedataitem.name == inp.name
                        for inp in recipe.input_data
                        for thedataitem in thedataitems
                    )
                    if not is_input_really_input:
                        sthedataitem = "+".join(td.name for td in thedataitems)
                        problems_recipe.append(
                            f"{recipe.name} has {sthedataitem} as input in the"
                            f" association matrix, but not in the recipe table"
                        )
                        assert sthedataitem, ValueError(
                            "sthedataitem should never be empty"
                        )

            primary_input_names_according_to_matrix = [
                input_primary.name
                for input_primary in recipecell.dataitems
            ]
            if check_input:
                # Vice-versa, check whether all input in the recipe table is
                # also in the association matrix. This is harder, because some
                # might be optional.
                input_names_according_to_matrix = [di.name for di in dataitems_found]
                # Skip the first input according to the recipe, because that should
                # always be the primary input, which is checked above.
                input_names_according_to_recipe = [diref.name for diref in recipe.input_secondary]

                input_names_missing_from_matrix = [
                    name
                    for name in input_names_according_to_recipe
                    if name not in input_names_according_to_matrix
                    and name not in primary_input_names_according_to_matrix
                    and name not in [
                        # These are part of the input raw data:
                        "LM_WCU_OFF_RAW",
                        "N_WCU_OFF_RAW",
                        "IFU_WCU_OFF_RAW",
                        "IFU_SKY_RAW",
                    ] + ([
                        "GAIN_MAP_2RG",
                        "GAIN_MAP_GEO",
                        "GAIN_MAP_IFU",
                        "LINEARITY_2RG",
                        "LINEARITY_GEO",
                        "LINEARITY_IFU",
                    ] if ignore_nonlinearity else [])
                ]

                # For metis_det_dark, this holds:
                #   input_names_according_to_recipe ==
                #     ['LINEARITY_2RG', 'LINEARITY_GEO', 'LINEARITY_IFU', 'PERSISTENCE_MAP']
                #   input_names_according_to_matrix == ['LINEARITY_2RG', 'PERSISTENCE_MAP']
                #   input_names_missing_from_matrix == ['LINEARITY_GEO', 'LINEARITY_IFU']
                # So we check whether e.g. for 'LINEARITY_GEO' it happens that
                # all three _det combinations are actually in the input
                # according to the recipe, and then whether at least one
                # of them is in the matrix.
                import itertools
                names_missing_correctly = []
                for name1 in input_names_missing_from_matrix:
                    for ext1, ext2, ext3 in itertools.permutations(["GEO", "IFU", "2RG"]):
                        name2 = name1.replace(ext1, ext2)
                        name3 = name1.replace(ext1, ext3)
                        names = (name1, name2, name3)
                        if all(n in input_names_according_to_recipe for n in names):
                            if name2 in input_names_according_to_matrix:
                                names_missing_correctly.append(name1)
                input_names_missing_from_matrix = [
                    name for name in input_names_missing_from_matrix
                    if name not in names_missing_correctly
                ]

                if input_names_missing_from_matrix:
                    problems_recipe.append(
                        f"{recipe.name} has {input_names_missing_from_matrix} as"
                        f" input in the recipe, but they are missing in the"
                        f" association matrix."
                    )

            # Try to see whether the output is correct.
            # Skip the first cell, as that is the raw data which is checked elsewhere.
            recipe_output = (
                [do.name for do in recipe.output_data] if recipe is not None else []
            )
            for icell, cell in enumerate(recipecolumn[1:], 1):
                if cell.dataitems is None:
                    continue
                for diref in cell.dataitems:
                    if diref.name in {"FLUXSTD_CATALOG", "PERSISTENCE_MAP"}:
                        # FLUXSTD_CATALOG is an external file, and listed above another calibration file for convenience
                        continue
                    if diref.name not in METIS_DataReductionLibraryDesign.dataitems:
                        problems_recipe.append(
                            f"{recipe_name} claims to produce {diref.name}, which does not exist"
                        )
                    elif diref.name not in recipe_output:
                        problems_recipe.append(
                            f"{recipe_name} listed as producing {diref.name}, but it doesn't, only {recipe_output}"
                        )

            if problems_recipe:
                problems.append((recipe_name, problems_recipe))

        if problems:
            problems_all.append(problems)
            print()
            print("Problems with", asso.filename)
            for recipe_name, problems_recipe in problems:
                print(" " + recipe_name)
                for problem in problems_recipe:
                    print("   " + problem)

    assert not problems_all


def test_tikz():
    """Test whether the names used in the tikz figures exist."""
    problems = {}
    dir_tikz = METIS_DataReductionLibraryDesign.path_drld / "tikz"
    dir_figures = METIS_DataReductionLibraryDesign.path_drld / "figures"
    for name_recipe, recipe in METIS_DataReductionLibraryDesign.recipes.items():
        problems_recipe = []
        name_recipe_lower = name_recipe.lower()
        if name_recipe == name_recipe_lower:
            names = [name_recipe]
        else:
            names = [name_recipe, name_recipe_lower]
        fns_that_exist = [
            fn
            for name in names
            for fn in list(dir_tikz.glob(f"{name}*.tex"))
            + list(dir_figures.glob(f"{name}*.pdf"))
            + list(dir_figures.glob(f"{name}*.png"))
        ]
        if len(fns_that_exist) != 1:
            if name_recipe in HACK_RECIPES_THAT_DO_NOT_NEED_A_FIGURE:
                continue
            problems_recipe.append(
                f"There there should be exactly one figure for {name_recipe} , not {fns_that_exist}"
            )

        # If there are no figures, bail
        if not fns_that_exist:
            continue

        fn_to_use = fns_that_exist[0]
        # If there is no tikz figure, bail.
        if fn_to_use.suffix != ".tex":
            continue

        # Let's skip some of the ADI for now
        if name_recipe in HACK_RECIPES_THAT_WERE_NOT_GOING_TO_CHECK_TIKZ_FOR:
            continue

        # This is a tikz figure, lets see whether it makes sense.
        data1 = fn_to_use.read_text(encoding="utf-8")
        data2 = [
            line for line in data1.splitlines() if not line.strip().startswith("%")
        ]
        data = "\n".join(data2)

        if "black_style" not in data:
            problems_recipe.append(
                f"The figure for {name_recipe} does not set black_style"
            )
        if "normal_style" not in data:
            problems_recipe.append(
                f"The figure for {name_recipe} does not set normal_style back"
            )

        # pattern = r"\\(RAW|PROD|EXTCALIB|STATCALIB){(.*?)}"
        pattern = r"\\(RAW|PROD|EXTCALIB|STATCALIB|TPL|REC){(.*?)}"
        matches = re.findall(pattern, data)
        names_in_figure = [
            name.lower() if name.startswith("METIS_") else name
            for _dtype, name in matches
        ]
        names_in_table = (
            [diref.name for diref in recipe.input_data + recipe.output_data]
            + recipe.templates
            + [name_recipe]
        )

        # Check for duplicate names. This was used to find BADPIX_MAP_det input,
        # which is not necessary since all data products have a data quality
        # layer. Nevertheless, we decided to add a BADPIX_MAP_det input to
        # recipes dealing with raw data anyway.
        duplicates = [
            name for name in names_in_figure
            if names_in_figure.count(name) > 1
               and not name.startswith("BADPIX_MAP_")
        ]
        if duplicates:
            problems_recipe.append(
                f"{name_recipe} mentions some names multiple times: {duplicates}"
            )

        for name_di in names_in_figure:
            names_di_expanded = [
                name_di.replace("det", lmn)
                for lmn in ["LM", "N", "IFU", "2RG", "GEO", "det"]
            ]
            is_name_used = any(name in names_in_table for name in names_di_expanded)
            if not is_name_used:
                problems_recipe.append(
                    f"The figure for {name_recipe} has {name_di} as"
                    f" input/output/template/recipe, but the table doesn't!"
                )

        # Vice-versa, does the recipe use dataitems that are not in the figures?
        for name_di in names_in_table:
            names_di_expanded = [
                name_di.replace(lmn, "det")
                for lmn in ["LM", "N", "IFU", "2RG", "GEO", "det"]
            ]
            is_name_used = any(name in names_in_figure for name in names_di_expanded)
            if not is_name_used:
                problems_recipe.append(
                    f"The table for {name_recipe} has {name_di} as"
                    f" input/output/template/recipe, but it is not in the figure!"
                )

        if problems_recipe:
            problems_recipe.append(f"{names_in_table=}")
            problems_recipe.append(f"{names_in_figure=}")
            problems[name_recipe] = problems_recipe

    for name_recipe, problems_recipe in problems.items():
        print()
        print(name_recipe)
        for problem in problems_recipe:
            print("  " + problem)

    assert not problems


@pytest.mark.skip(reason="We decided we want bad pixel maps")
def test_badpixinput():
    """The imaging and IFU pipelines do not need a bad pixel map as input.

    Every calibration product has a data quality layer that is propagated
    to the data being processed.

    Nevertheless, we decided to add the bad pixel map as input anyway,
    so this check is not necessary anymore.

    TODO: Perhaps ensure each recipe dealing with raw data actually has
          an (optional) BADPIX_MAP_det as input?
    """
    problems = []
    for name_recipe, recipe in METIS_DataReductionLibraryDesign.recipes.items():
        if any(toskip in name_recipe.lower() for toskip in {"lss", "adc"}):
            continue
        names_input = [diref.name.upper() for diref in recipe.input_data]
        input_bp = [name for name in names_input if "BADPIX" in name]
        if input_bp:
            problems.append(
                f"{name_recipe} has {input_bp} as input, which is not necessary"
            )

    for problem in problems:
        print(problem)
    assert not problems


# TODO: Order of input in recipes, primary input should go first!
# TODO: the raw dark was an EXTCALIB, should not happen!
# TODO: Check whether LM data is created with LM templates and processed with LM recipes, similar for N
