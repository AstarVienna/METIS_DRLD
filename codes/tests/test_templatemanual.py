from pathlib import Path

from ..drld_parser.template_manual import METIS_TemplateManual

PATH_ROOT = Path(__file__).parent.parent.parent


class TestTemplateManual:
    def test_number_of_templates_extracted_is_not_none(self):
        assert len(METIS_TemplateManual.templates) > 0

    def test_template_types(self):
        for template in METIS_TemplateManual.templates.values():
            assert template.ttype in [
                "Calibration",
                "Observing",
                "Acquisition",
                "Engineering",
            ]
