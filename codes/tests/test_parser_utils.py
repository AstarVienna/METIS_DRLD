import os.path as p
from pathlib import Path

import pytest
from ..drld_parser import parser_utils as pu
from ..drld_parser.base_classes import METIS_TemplateManual

PATH_ROOT = Path(__file__).parent.parent.parent


class TestGetRecipes:
    def test_number_of_recipes_extracted_is_not_none(self):
        assert len(pu.get_recipes(PATH_ROOT)) > 0


class TestGetTemplateSummaries:
    def test_number_of_templates_extracted_is_not_none(self):

        assert len(METIS_TemplateManual.templates) > 0
