import dataclasses
import glob
import os
from pathlib import Path
import re
from typing import Dict, Set, List, Tuple

from codes.drld_parser.hacks import hack_rename_template_header, HACK_BAD_NAMES, HACK_TEMPLATE_NAMES_IN_DRLD


@dataclasses.dataclass
class FitsHeader:
    parameter: str
    hidden: str
    range: str
    label: str

    @staticmethod
    def from_wiki_line(line):
        _, parameter, hidden, therange, label, _ = [
            cell.strip() for cell in line.split("|")
        ]
        return FitsHeader(
            parameter=parameter,
            hidden=hidden,
            range=therange,
            label=label,
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


@dataclasses.dataclass
class Recipe:
    name: str = None
    purpose: str = None
    type: str = None
    templates: List[str] = None
    input_data: List[str] = None
    parameters: List[str] = None
    algorithm: str = None
    output_data: List[Tuple[str, str]] = None
    expected_accuracies: str = None
    qc1_parameters: List[str] = None
    hdrl_functions: List[str] = None
    requirements: List[str] = None
    matched_keywords: List[str] = None

    @staticmethod
    def parse_recipe_from_table(stable):
        """Parse a Recipe from a table"""
        rows1 = [
            line.strip()
            for line in stable.splitlines()
            if line.strip() and not line.strip().startswith("%")
        ]

        # Concatenate lines.. Aargh
        rows2 = []
        thisline = ""
        for line in rows1:
            thisline += line
            if thisline.endswith("\\\\"):
                rows2.append(thisline)
                thisline = ""

        rows3 = [
            line.strip().strip("\\").strip().split("&")
            for line in rows2
            # TODO: Do something sensible if there is no &
            if "&" in line
        ]

        rows4 = [(aa.strip().strip(":").strip(), bb.strip()) for aa, bb in rows3]

        value = ""
        field_old = ""
        thedata = {}
        for row in rows4:
            field1 = row[0].lower().replace(" ", "_")
            field1 = re.sub("label{.*?}", "", field1)
            if field1 == "":
                value += "\n" + row[1]
                continue

            # Previous one must be finished
            if field_old:
                if field_old == "templates":
                    value = re.sub("\\\\TPL{(.*?)}", " \\1 ", value)
                    value = value.replace(",", " ")
                    if "tbd" in value.lower():
                        value = ["TBD"]
                    elif value.lower() == "none" or "--" in value:
                        value = []
                    else:
                        value = value.split()
                        value = [
                            HACK_TEMPLATE_NAMES_IN_DRLD.get(vi.lower(), vi.lower())
                            for vi in value
                        ]
                thedata[field_old] = value

            field = HACK_BAD_NAMES.get(field1, field1)
            value = row[1]

            if "name" in field:
                value = re.sub("\\\\REC{(.*?)}", "\\1", value)
                value = re.sub("\\\\hyperref[.*?]{(.*?)}", "\\1", value)
                # print(field, ":::", value)

            # noinspection PyUnresolvedReferences
            if field not in Recipe.__dataclass_fields__:
                print(field, field1, row[0])

            # Cannot yet add the value to thedata dictionary because the value
            # might continue on other rows.
            field_old = field

        return Recipe(**thedata)


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
                _, name_a, name_b, description, _ = line_with_template.strip().split("|")
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
            name_template: Template.from_wiki_file(
                name=name_template,
                ttype=type_template,
                description=description,
            )
            for type_template, names_descs in template_summaries.items()
            for name_template, description in names_descs.items()
        }


class DataReductionLibraryDesign:
    """The information from the DRLD"""
    # TODO: Check all tex files

    def __init__(self):
        path_here = Path(__file__).parent

        self.path_drld = path_here.parent.parent
        # The path of the DRLD

        self.filenames_tex = glob.glob(os.path.join(self.path_drld, "*.tex")) + glob.glob(
            os.path.join(self.path_drld, "**/*.tex")
        )
        # All tex files, need to check whether the templates and recipes etc.
        # they reference actually exists.

        self.recipes = self.get_recipes()
        # The recipes as defined in the DRLD.

    def get_recipes(self):
        """"""
        # TODO: Verify that there are no recipes defined in other tex files.
        files_drld = glob.glob(os.path.join(self.path_drld, "Recipes*.tex"))
        recipes = {}
        for filename in files_drld:
            data = open(filename, encoding="utf8").read()
            # TODO: Assure we don't miss the first recipe by accident.
            srecipes = [
                dd.split("\\end{recipedef}")[0]
                for dd in data.split("\\begin{recipedef}")
                if "recipe parameters" in dd.lower() or "qc1" in dd.lower()
            ][1:]
            for stable in srecipes:
                recipe = Recipe.parse_recipe_from_table(stable)
                recipes[recipe.name] = recipe

        return recipes

    @staticmethod
    def get_tpls_from_tex(filename, recipe_names):
        """
        Get templates from tex files
        """

        not_templates = [
            "METIS_IMAGE",
            "METIS_CUBE",
        ] + recipe_names
        datat = open(filename, encoding="utf8").read()
        # Using TPL macro
        # TODO: There are TPL macros that are not templates!!
        tpls_macro = [
            tsii.replace("\\", "")
            for tsii in re.findall("\\\\TPL{(M.*?)}", datat, re.IGNORECASE)
        ]
        # Normal LaTeX, includes tikzs
        tpls_latex = [
            tsii.replace("\\", "").replace("$ast$", "*")
            for tsii in
            # re.findall("metis\\\\_[iaogps][a-z_\\*\\\\]*", datat, re.IGNORECASE)
            re.findall("metis\\\\_[a-z_*\\\\ast$]*", datat, re.IGNORECASE)
        ]
        # TODO: does not work for tikz
        return [tsi for tsi in tpls_macro + tpls_latex if tsi not in not_templates]


METIS_TemplateManual = TemplateManual()
METIS_DataReductionLibraryDesign = DataReductionLibraryDesign()
