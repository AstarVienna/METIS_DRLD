import dataclasses
import os
from pathlib import Path
import re
from typing import Dict, Set

from codes.drld_parser.fits_header import FitsHeader
from codes.drld_parser.hacks import hack_rename_template_header


@dataclasses.dataclass
class Template:
    name: str
    ttype: str
    headers: Dict[str, FitsHeader]
    references: Set[str]
    description: str

    @staticmethod
    def from_wiki_file(
        name: str,
        ttype: str,
        description: str,
    ):
        """Parse a Template file.

        name, ttype, and description from metis_templates.txt
        """
        path_here = Path(__file__).parent
        path_template = path_here / "operations" / f"{name.lower()}.txt"

        datatt = open(path_template, encoding="utf8").read()
        used_template_names = set(
            hack_rename_template_header(name, ttt)
            for ttt in re.findall("METIS_[a-zA-Z_]*", datatt)
        )
        used_template_names_headers = set(
            hack_rename_template_header(name, ttt)
            for ttt in re.findall("=.*(METIS_[a-zA-Z_]*)", datatt)
        )
        # print(name_template, used_template_names_headers)
        # TODO: Remove these .lower()s.
        assert set(name.lower() for name in used_template_names_headers) == {
            name.lower()
        }
        templates_referenced = used_template_names - used_template_names_headers

        lines_param = [
            line.strip() + ("" if line.strip().endswith("|") else "|")
            for line in datatt.split("^Parameter")[-1].splitlines()
            if line.startswith("|")
        ]

        parameters = [FitsHeader.from_wiki_line(line) for line in lines_param]
        fitsheaders = {param.parameter: param for param in parameters}
        return Template(
            name=name,
            ttype=ttype,
            headers=fitsheaders,
            references=templates_referenced,
            description=description,
        )


class TemplateManual:
    """The templates as written on the operations wiki."""

    def get_template_summaries(self):
        """Get a dictionary of template types, names, and descriptions.

        The wiki defines many templates, but most are not used (anymore). The
        templates in "metis_templates.txt" are the ones that are actually included
        in the Template Manual.

        The names in this list also have the canonical capitalisation.

        E.g.
        {
            "Acquisition": {
                "METIS_ifu_acq": "acquisition of nominal IFU spectroscopy ",
                "METIS_ifu_app_acq": "acquisition of nominal IFU spectroscopy with APP coronagraph",
                "METIS_ifu_ext_acq": "acquisition of extended IFU " "spectroscopy ",
                ...
            },
            "Calibration": {
                "METIS_gen_cal_InsDark": "Series of dark frames (instrument dark)",
                "METIS_gen_cal_dark": "Series of dark frames (imager dark)",
                ...
            },
            "Engineering": {
                "METIS_pup_lm": "Pupil imaging in LM ",
                "METIS_pup_n": "Pupil imaging in N ",
            },
            "Observing": {
                "METIS_ifu_app_obs_Stare": " Nominal IFU spectroscopy with APP coronagraph",
                "METIS_ifu_ext_app_obs_Stare": " Extended IFU spectroscopy with APP coronagraph",
                ...
            },
        }
        """
        data = open(
            os.path.join(self.path_operations, "metis_templates.txt"), encoding="utf8"
        ).read()
        sections = [
            section.strip() for section in data.split("++++")[1:] if section.strip()
        ]
        assert len(sections) == 4

        template_summaries = {}
        for section in sections:
            lines = section.splitlines()
            type_template = lines[0].split()[1]
            # print(type_template)
            lines_with_template = [line for line in lines if "METIS_" in line]
            template_list = {}
            for line_with_template in lines_with_template:
                # print(line_with_template)
                _, name_a, name_b, description, _ = line_with_template.strip().split(
                    "|"
                )
                name_a = name_a.strip().strip("[").strip("]").strip()
                name_b = name_b.strip().strip("[").strip("]").strip()
                assert name_a == name_b, f"{name_a} {name_b}"
                template_list[name_a] = description
            template_summaries[type_template] = template_list

        type_from_template_name = {
            tt.lower(): type_tt
            for type_tt, tps in template_summaries.items()
            for tt in tps
        }

        templates_all_true = [
            tt for tpslist in template_summaries.values() for tt in tpslist
        ]
        assert len(templates_all_true) == len(set(templates_all_true))
        assert len(type_from_template_name) == len(templates_all_true)
        return template_summaries

    def __init__(self):
        """Initialize by reading the wiki data."""
        path_here = Path(__file__).parent
        self.path_operations = path_here / "operations"

        template_summaries = self.get_template_summaries()

        self.templates = {
            name_template: Template.from_wiki_file(
                name=name_template,
                ttype=type_template,
                description=description,
            )
            for type_template, names_descs in template_summaries.items()
            for name_template, description in names_descs.items()
        }

    def get_template(self, name):
        """Get a template even if the capitalization is wrong, or None."""
        templatesd = {tn.lower(): template for tn, template in self.templates.items()}
        return templatesd.get(name, None)


METIS_TemplateManual = TemplateManual()
