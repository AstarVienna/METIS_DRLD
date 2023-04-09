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

    def test_expand_wildcards(self):
        expanded = METIS_TemplateManual.expand_wildcards("metis_img_lm_*_obs_*")
        expanded_lower = {tn.lower() for tn in expanded}
        expected = {
            "METIS_img_lm_obs_AutoJitter",
            "METIS_img_lm_obs_FixedSkyOffset",
            "METIS_img_lm_obs_GenericOffset",
            "METIS_img_lm_app_obs_FixedOffset",
            "METIS_img_lm_vc_obs_FixedSkyOffset",
        }
        expected_lower = {tn.lower() for tn in expected}
        assert expected_lower == expanded_lower
