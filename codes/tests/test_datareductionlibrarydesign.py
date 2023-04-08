import pytest

from ..drld_parser.data_reduction_library_design import METIS_DataReductionLibraryDesign
from ..drld_parser.template_manual import METIS_TemplateManual


class TestDataReductionLibraryDesign:
    def test_number_of_recipes_extracted_is_not_none(self):
        assert len(METIS_DataReductionLibraryDesign.recipes) > 0

    def test_template_and_recipe_names_do_not_overlap(self):
        names_recipes = {
            name.lower() for name in METIS_DataReductionLibraryDesign.recipes.keys()
        }
        names_templates = {
            name.lower() for name in METIS_TemplateManual.templates.keys()
        }
        assert not (names_recipes & names_templates)

    @pytest.mark.xfail(
        reason="There are several recipes mentioned that do not exist..."
    )
    def test_all_recipe_names_used_also_exist(self):
        names_existing = METIS_DataReductionLibraryDesign.recipes.keys()
        names_used = METIS_DataReductionLibraryDesign.recipe_names_used
        names_existing_lower = [name.lower() for name in names_existing]
        names_not_existing = [
            name
            for name in names_used
            if name not in names_existing and name.lower() not in names_existing_lower
        ]

        assert (
            not names_not_existing
        ), f"Non existing recipe names: {names_not_existing}"

    @pytest.mark.xfail(
        reason="There are many references to recipes with incorrect capitalization, in particular in LSS_data_items.tex."
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
        reason="There are many references to templates that do not exits."
    )
    def test_all_templates_used_also_exist(self):
        # TODO: hack_rename_template_names_drld and
        #  TEMPLATE_IN_DRLD_BUT_NOT_IN_OPERATIONS_WIKI are currently not
        #  used anymore.
        names_existing = METIS_TemplateManual.templates.keys()
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
