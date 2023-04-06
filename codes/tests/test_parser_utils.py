import os.path as p
import pytest
from ..drld_parser import parser_utils as pu

# Test run relative to parent directory of ./tests -> METIS_DRLD/codes/

class TestGetRecipes:
    def test_number_of_recipes_extracted_is_not_none(self):
        drld_path = p.abspath("../")
        assert len(pu.get_recipes(drld_path)) > 0


class TestGetTemplateSummaries:
    def test_number_of_templates_extracted_is_not_none(self):
        operations_path = p.abspath("codes/drld_parser/operations/")
        assert len(pu.get_template_summaries(operations_path)) > 0
