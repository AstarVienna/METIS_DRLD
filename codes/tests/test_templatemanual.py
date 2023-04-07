from pathlib import Path

from ..drld_parser.template_manual import METIS_TemplateManual

PATH_ROOT = Path(__file__).parent.parent.parent


class TestTemplateManual:

    def test_number_of_templates_extracted_is_not_none(self):
        assert len(METIS_TemplateManual.templates) > 0

