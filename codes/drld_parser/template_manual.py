import dataclasses
import os
from pathlib import Path
import re
from typing import Dict, Set

from codes.drld_parser.fits_header import FitsHeader
from codes.drld_parser.hacks import (
    hack_rename_template_header,
    HACK_TEMPLATE_NAMES_ONLY_IN_WIKI_SUMMARY_BUT_NOT_ACTUALLY_ON_WIKI,
)


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

        if not path_template.exists():
            if name in HACK_TEMPLATE_NAMES_ONLY_IN_WIKI_SUMMARY_BUT_NOT_ACTUALLY_ON_WIKI:
                print(f"WARNING: {name} is mentioned in the wiki summary but does not have its own wiki page.")
                return None
            else:
                raise FileNotFoundError(f"Cannot find template {name}")

        datatt = open(path_template, encoding="utf8").read()
        used_template_names = set(
            hack_rename_template_header(name, ttt) for ttt in re.findall("METIS_[a-zA-Z_]*", datatt)
        )
        used_template_names_headers = set(
            hack_rename_template_header(name, ttt) for ttt in re.findall("=.*(METIS_[a-zA-Z_]*)", datatt)
        )
        # print(name_template, used_template_names_headers)
        # TODO: Remove these .lower()s.
        assert set(name.lower() for name in used_template_names_headers) == {name.lower()}
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
        data = open(os.path.join(self.path_operations, "metis_templates.txt"), encoding="utf8").read()
        sections = [section.strip() for section in data.split("++++")[1:] if section.strip()]
        if len(sections) != 4:
            print(f"WARNING: Expected 4 sections, found {len(sections)}")
        # There should be 4 sections: Acquisition, Observing, Calibration, and Engineering.
        # However, the Calibration section header was broken in #326 so now
        # there are only 3. And we might add a new section for AIT templates,
        # meaning there could also be 5.
        # These asserts are in here because a failure usually means something
        # else is wrong too, so it is fine to relax or remove them, if done
        # consciously.
        assert 3 <= len(sections) <= 5

        template_summaries = {}
        for section in sections:
            lines = section.splitlines()
            type_template = lines[0].split()[1]
            # print(type_template)
            lines_with_template = [line for line in lines if "METIS_" in line]
            template_list = {}
            for line_with_template in lines_with_template:
                # print(line_with_template)
                line_splitted = line_with_template.strip().split("|")
                if len(line_splitted) == 5:
                    # Original lines from Kora, e.g.
                    # ['', '[[METIS_gen_cal_detchar', 'METIS_gen_cal_detchar]]', 'Detector characterisation (e.g. bias voltage)', '']
                    _, name_a, name_b, description, _ = line_with_template.strip().split("|")
                elif len(line_splitted) > 5:
                    # New lines by Yannis
                    _, _aitid, name_a, name_b, description, *_rest = line_with_template.strip().split("|")
                else:
                    raise ValueError(f"Unexpected template line {len(line_splitted)} {line_with_template}")

                name_a = name_a.strip().strip("[").strip("]").strip()
                name_b = name_b.strip().strip("[").strip("]").strip()
                assert name_a == name_b, f"{name_a} {name_b}"
                template_list[name_a] = description
            template_summaries[type_template] = template_list

        type_from_template_name = {
            tt.lower(): type_tt for type_tt, tps in template_summaries.items() for tt in tps
        }

        templates_all_true = [tt for tpslist in template_summaries.values() for tt in tpslist]
        assert len(templates_all_true) == len(set(templates_all_true))
        assert len(type_from_template_name) == len(templates_all_true)
        return template_summaries

    def __init__(self):
        """Initialize by reading the wiki data."""
        path_here = Path(__file__).parent
        self.path_operations = path_here / "operations"

        template_summaries = self.get_template_summaries()

        self.templates = {
            name_template: temp
            for type_template, names_descs in template_summaries.items()
            for name_template, description in names_descs.items()
            if (temp := Template.from_wiki_file(
                name=name_template,
                ttype=type_template,
                description=description,
            )) is not None
        }

    def get_template(self, name):
        """Get a template even if the capitalization is wrong, or None."""
        templatesd = {tn.lower(): template for tn, template in self.templates.items()}
        return templatesd.get(name.lower(), None)

    def expand_wildcards(self, name):
        """Expand wildcards in template names.

        E.g., the DRLD can refer to e.g. metis_img_lm_*_obs_* in
        metis_lm_img_basic_reduce and metis_lm_img_background. This should
        expand to (ignoring capitalization):
        - METIS_img_lm_obs_AutoJitter
        - METIS_img_lm_obs_FixedSkyOffset
        - METIS_img_lm_obs_GenericOffset
        - METIS_img_lm_app_obs_FixedOffset
        - METIS_img_lm_vc_obs_FixedSkyOffset

        Note that the first three have only one underscore between the 'lm'
        and the 'obs', but the given template name has two, and these should
        not match:
        - METIS_img_lmn_obs_AutoChopNod
        - METIS_img_lmn_obs_GenericChopNod

        TODO: Maybe those *should* match in this particular case?
        """
        if "*" not in name:
            return [name]

        # Replace the second _; on the basis that that works.
        name2 = name.replace("*_", "*").replace("*", ".*").lower()
        pattern = re.compile(name2)

        return [tn for tn in METIS_TemplateManual.templates if re.match(pattern, tn.lower())]


METIS_TemplateManual = TemplateManual()
