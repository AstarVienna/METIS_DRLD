from pathlib import Path

from ..drld_parser.base_classes import METIS_TemplateManual, METIS_DataReductionLibraryDesign

PATH_ROOT = Path(__file__).parent.parent.parent


class TestGetRecipes:
    def test_number_of_recipes_extracted_is_not_none(self):
        assert len(METIS_DataReductionLibraryDesign.recipes) > 0


class TestGetTemplateSummaries:
    def test_number_of_templates_extracted_is_not_none(self):

        assert len(METIS_TemplateManual.templates) > 0
