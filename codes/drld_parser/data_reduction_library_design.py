"""The Data Reduction Library Design."""

import dataclasses
import glob
import hashlib
import itertools
import os
from pathlib import Path
import re
from typing import List

from codes.drld_parser.hacks import (
    HACK_BAD_NAMES,
    HACK_INCORRECT_INPUT_DATA,
    HACK_RECIPE_TEMPLATES,
)

PATTERN_TEX_COMMENT = re.compile(r"(?<!\\)%[^\n]*")
# Anything that is: not a backslash, then a percent, then anything not a newline


def guess_postfixes(name):
    """Try to guess what _det_ means in name."""
    postfixes_hardware = ["2RG", "GEO", "IFU"]
    postfixes_mode = ["LM", "N", "IFU"]
    postfixes_adiimg = ["LM", "N"]
    nameparts_hardware = ["master", "linearity", "persistence", "gain", "badpix", "detlin", "dark"]
    nameparts_adiimg = [
        a.lower()
        for a in [
            # These have their IFU counterpart explicitly written down
            "_cgrph_SCI_CALIBRATED",
            "_cgrph_SCI_CENTRED",
            "_cgrph_CENTROID_TAB",
            "_cgrph_SCI_SPECKLE",
            "_cgrph_SCI_DEROTATED_PSFSUB",
            "_cgrph_SCI_DEROTATED",
            "_cgrph_SCI_CONTRAST_RAW",
            "_cgrph_SCI_CONTRAST_ADI",
            "_cgrph_SCI_THROUGHPUT",
            "_cgrph_SCI_SNR",
            "_cgrph_SCI_COVERAGE",
        ]
    ]
    if any(namepart in name.lower() for namepart in nameparts_hardware):
        return postfixes_hardware
    if any(namepart in name.lower() for namepart in nameparts_adiimg):
        return postfixes_adiimg
    return postfixes_mode


def guess_dataitem_type(name, raise_exception=False):
    """Guess the dataitem type from DataItemReferences.

    However, it is not uniquely defined, because in different context
    a DataItem can have a different type. In particular, it could be a PROD
    for the recipe that produces it, but a STATCALIB for the recipes that
    use it. More importantly, it could be that a STATCALIB data product is
    used in the same workflow as it is produced, then it should be a PROD also
    as input.

    For now this function assumes that the type of a DataItem as input is
    always identical."""
    direfs_output = [
        (recipe, diref)
        for recipe in METIS_DataReductionLibraryDesign.recipes.values()
        for diref in recipe.output_data
        if diref.name is not None and diref.name.lower() == name.lower()
    ]
    direfs_input = [
        (recipe, diref)
        for recipe in METIS_DataReductionLibraryDesign.recipes.values()
        for diref in recipe.input_data
        if diref.name is not None and diref.name.lower() == name.lower()
    ]
    datatypes_input = [diref.dtype for _, diref in direfs_input]
    datatypes_output = [diref.dtype for _, diref in direfs_output]
    datatypes = [diref.dtype for _, diref in direfs_input + direfs_output]
    if not datatypes:
        return "PROD"

    if len(set(datatypes_input)) > 1 or len(set(datatypes_output)) > 1:
        print()
        print(name)
        print(datatypes_input)
        print([rec.name for rec, _ in direfs_input])
        print(datatypes_output)
        print([rec.name for rec, _ in direfs_output])
        assert not raise_exception

    return (datatypes_input + datatypes_output)[0]


def find_latex_inputs(path):
    """Flatten a tex file."""
    lines = open(path).readlines()
    lines_with_input = [line for line in lines if line.strip() and line.strip().startswith(r"\input{")]
    paths_inputted = [
        path.parent / (ll + ".tex")
        for line in lines_with_input
        for ll in re.findall(r"\\input{(.*?)}", line)
    ]
    paths_to_return = [fn for fn in paths_inputted]
    for fn in paths_inputted:
        paths_to_return + find_latex_inputs(fn)

    return paths_to_return


@dataclasses.dataclass
class DataItem:
    """A Raw / Processed / External DataItem."""

    # TODO: Add at least DO.CATG / PRO.CATG, because those can be referenced too.

    name: str = None
    hyperref: str = None
    labels: List[str] = dataclasses.field(default_factory=list)
    description: str = None
    pro_catg: str = None
    dpr_catg: str = None
    dpr_type: str = None
    dpr_tech: str = None
    do_catg: str = None
    oca_keywords: str = None
    created_by: List["RecipeReference"] = dataclasses.field(default_factory=list)
    input_for: List["RecipeReference"] = dataclasses.field(default_factory=list)
    templates: List[str] = dataclasses.field(default_factory=list)
    dtype: str = None
    name_header: str = None
    dtype_header: str = None
    sparagraph: str = None

    @classmethod
    def from_paragraph(cls, sparagraph):
        """Parse a dataitem from a paragraph with a recipedef table."""
        lines1 = [line.strip() for line in sparagraph.splitlines() if not line.strip().startswith("%")]
        line_header = lines1[0]
        # E.g. \paragraph{\hyperref[dataitem:master_n_lss_rsrf]{\PROD{MASTER_N_LSS_RSRF}}}\label{dataitem:master_n_lss_rsrf}
        regex_header = re.compile(
            r"\\paragraph{\\hyperref\[(?P<hyperref>.*?)]{\\(?P<dtype>[A-Z]+){(?P<name>.*?)}}}\\label{(?P<label>.*?)}"
        )
        match = regex_header.match(line_header)
        group = match.groupdict()
        hyperref = group["hyperref"]
        dtype_header = group["dtype"]
        name_header = group["name"]
        label = group["label"]
        assert hyperref == label
        assert label.startswith("dataitem")
        assert hyperref == f"dataitem:{name_header.lower()}"

        lines2 = itertools.dropwhile(
            lambda line: not line.startswith(r"\begin{recipedef}"),
            lines1,
        )
        lines3 = itertools.takewhile(
            lambda line: not line.startswith(r"\end{recipedef}"),
            lines2,
        )

        rows1a = [line.replace("[0.3cm]", "") for line in list(lines3)[1:]]

        # The rest is based on Recipe.parse_recipe_from_table and therefore
        # just as horific

        # Some recipes start with
        # \begin{recipedef}\label{rec:metisimgchophome}\label{rec:metis_img_chophome}
        # So rows1a starts with
        # \label{rec:metisimgchophome}\label{rec:metis_img_chophome}
        # Remove that line
        # TODO: perhaps do something useful with the labels
        rows1b = [row for row in rows1a if not row.startswith(r"\label")]
        # Some recipes have the label in the name
        #   Name:                & \hyperref[rec:metis_ifu_adi_cgrph]{\REC{metis_ifu_adi_cgrph}}\label{rec:metis_ifu_adi_cgrph}                                        \\
        # So remove those as well.
        rows1c = [row.split(r"\label") for row in rows1b]
        rows1 = [row[0] if len(row) == 1 else row[0] + r"\\" for row in rows1c]

        # Concatenate lines.. Aargh
        rows2 = []
        thisline = ""
        for line in rows1:
            # Remove any trailing comments
            line2 = PATTERN_TEX_COMMENT.sub("", line).strip()
            thisline += line2
            if thisline.endswith("\\\\"):
                rows2.append(thisline)
                thisline = ""

        rows3 = [
            line.strip().strip("\\").strip().split("&")
            for line in rows2
            # TODO: Do something sensible if there is no &
            if "&" in line
        ]

        for row in rows3:
            msg = f"Wrong number of columns: {row}"
            assert len(row) == 2, msg

        # Placeholder is necessary for last item
        rows4 = [(aa.strip().strip(":").strip(), bb.strip()) for aa, bb in rows3] + [("placeholder", "")]

        to_skip = {
            r"processing_\ac{fits}_keywords",
            "purpose",
            "comment",
            "pro_tech",
            "qc_parameters",
            "processing_fits_keywords",
            "placeholder",
        }

        value = ""
        field_old = ""
        thedata = {
            "name_header": name_header,
            "dtype_header": dtype_header,
            "labels": [label],
            "hyperref": hyperref,
            "sparagraph": sparagraph,
        }
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
                            HACK_RECIPE_TEMPLATES.get((thedata["name"], vi.lower()), vi.lower())
                            for vi in value
                        ]
                    # There could be a * in one of the templates, e.g.
                    # "metis_img_lm_*_obs_*". However, it is not possible
                    # to expand those here, because there is no knowledge
                    # about which templates exist at this stage.
                elif field_old in ["pro_catg", "do_catg", "dpr_catg", "dpr_tech", "dpr_type"]:
                    value = re.sub("\\\\FITS{(.*?)}", " \\1 ", value)
                    value = value.strip()
                elif field_old in ["created_by", "input_for"]:
                    # These should all be \REC{something}
                    value1 = [
                        RecipeReference.from_line(val)
                        for val in value.split("\n")
                        if not val.startswith("(")
                    ]
                    # First, from the DRLD:
                    #   Where _det appears in FITS keywords of input or product files,
                    #   it is taken to mean _LM, N or _IFU
                    #   according to the detector array for which data are being processed.
                    # TODO: Perhaps we should go back to _2RG and _GEO for _LM and _N

                    value = value1

                thedata[field_old] = value

            field = HACK_BAD_NAMES.get(field1, field1)
            # if field1 in HACK_BAD_NAMES:
            #     print(f"{field1} should be renamed to {field}.")
            value = row[1]

            if "name" in field:
                dtype = re.match(r".*?\\([A-Z]+){.*?}", value).group(1)
                thedata["dtype"] = dtype
                value = re.sub(r"\\[A-Z]+{(.*?)}", "\\1", value)
                value = re.sub(r"\\hyperref\[.*?]{(.*?)}", "\\1", value)
                # print(field, ":::", value)

            if "fits:" in field:
                # E.g.
                # field: hyperref[fits:pro.catg]{\fits{pro.catg}}
                # value: \\FITS{MASTER_N_LSS_RSRF}
                field = re.sub(r"hyperref.*?\\fits{(.*?)}}", "\\1", field)
                field = field.replace(".", "_")
            elif "fits" in field:
                # E.g.
                # field: fits{do.catg}
                # value: \\FITS{MASTER_N_LSS_RSRF}
                field = field.replace("fits{", "").strip("}")
                field = field.replace(".", "_")

            # noinspection PyUnresolvedReferences
            assert (
                field in cls.__dataclass_fields__ or field in to_skip
            ), f"Field {field} cannot be found {row[0]}"

            # Cannot yet add the value to thedata dictionary because the value
            # might continue on other rows.
            field_old = field

        for field in to_skip:
            if field in thedata:
                thedata.pop(field)

        toreturn = cls(**thedata)
        toreturn.thedata = thedata
        return toreturn


@dataclasses.dataclass
class DataItemReference:
    """A DataItem as referenced in a Recipe.

    Has to be a separate class as DataItem, because the point is to check
    whether the Recipes properly refer to existing DataItems."""

    name: str = None
    dtype: str = "PROD"
    hyperref: str = None
    description: str = None

    def fake_hash(self):
        """Create a reproducible hash.

        Python __hash__ cannot be used because it is not reproducible
        by design.
        """
        s_all = f"{self.name} {self.dtype} {self.hyperref} {self.description}"
        h_all = hashlib.sha256(s_all.encode("utf-8"))
        return h_all.hexdigest()

    def get_name(self):
        return self.name if self.name else f"UNKNOWN_{str(self.fake_hash())[-8:]}"

    def __post_init__(self):
        # TODO: perhaps use pydantic?
        if self.name is not None:
            self.name = self.name.replace("\\", "")
            self.name = HACK_INCORRECT_INPUT_DATA.get(self.name, self.name)

    @staticmethod
    def from_recipe_line(line):
        r"""Parse a line from a Recipe definition.

        Example lines:

        \hyperref[dataitem:nlsssciobjmap]{\PROD{N_LSS_SCI_OBJ_MAP}}: Pixel map of object pixels
        "$N\\times$ \\hyperref[dataitem:nlssrsrfpinhraw]{\\RAW{N_LSS_RSRF_PINH_RAW}}"
        \hyperref[dataitem:nlsswaveguess]{\STATCALIB{N_LSS_WAVE_GUESS}}
        Calibrated science images (\\PROD{LM_SCI_CALIBRATED})
        \PROD{N_DIST_REDUCED} (reduced grid mask images)
        \PROD{MF\_BEST\_FIT\_TAB}
        Chopped/nodded science or standard images
        """
        patterns_to_test = [
            re.compile(pp)
            # Patterns are ordered from most specific to least specific.
            for pp in [
                r"\\hyperref\[(?P<hyperref>.*?)]{\\(?P<dtype>[A-Z]+){(?P<name>.*?)}}: (?P<description>.*)",
                r"(?P<description>.*?) \\hyperref\[(?P<hyperref>.*?)]{\\(?P<dtype>[A-Z]+){(?P<name>.*?)}}",
                r"\\hyperref\[(?P<hyperref>.*?)]{\\(?P<dtype>[A-Z]+){(?P<name>.*?)}}",
                r"(?P<description>.*?) \(\\(?P<dtype>[A-Z]+){(?P<name>.*?)}\)",
                r"\\(?P<dtype>[A-Z]+){(?P<name>.*?)} \((?P<description>.*?)\)",
                r"\\(?P<dtype>[A-Z]+){(?P<name>.*?)}",
                r"(?P<description>.*)",
            ]
        ]
        for pattern in patterns_to_test:
            match = re.match(pattern, line)
            if match:
                return DataItemReference(**match.groupdict())

        return DataItemReference


@dataclasses.dataclass
class RecipeReference:
    """A Recipe as referenced in a DataItem.

    Has to be a separate class as Recipe, because the point is to check
    whether the DataItems properly refer to existing Recipes."""

    name: str = None
    dtype: str = "REC"
    hyperref: str = None
    description: str = None

    def fake_hash(self):
        """Create a reproducible hash.

        Python __hash__ cannot be used because it is not reproducible
        by design.
        """
        s_all = f"{self.name} {self.dtype} {self.hyperref} {self.description}"
        h_all = hashlib.sha256(s_all.encode("utf-8"))
        return h_all.hexdigest()

    def get_name(self):
        return self.name if self.name else f"UNKNOWN_{str(self.fake_hash())[-8:]}"

    def __post_init__(self):
        # TODO: perhaps use pydantic?
        if self.name is not None:
            self.name = self.name.replace("\\", "")
            self.name = HACK_INCORRECT_INPUT_DATA.get(self.name, self.name)

    @staticmethod
    def from_line(line):
        r"""Parse a line from a DataItem definition.

        Example lines:

        \\hyperref[rec:metis_n_lss_trace]{\\REC{metis_n_lss_trace}}
        """
        patterns_to_test = [
            re.compile(pp)
            # Patterns are ordered from most specific to least specific.
            for pp in [
                r"\\hyperref\[(?P<hyperref>.*?)]{\\(?P<dtype>[A-Z]+){(?P<name>.*?)}}: (?P<description>.*)",
                r"(?P<description>.*?) \\hyperref\[(?P<hyperref>.*?)]{\\(?P<dtype>[A-Z]+){(?P<name>.*?)}}",
                r"\\hyperref\[(?P<hyperref>.*?)]{\\(?P<dtype>[A-Z]+){(?P<name>.*?)}}",
                r"(?P<description>.*?) \(\\(?P<dtype>[A-Z]+){(?P<name>.*?)}\)",
                r"\\(?P<dtype>[A-Z]+){(?P<name>.*?)} \((?P<description>.*?)\)",
                r"\\(?P<dtype>[A-Z]+){(?P<name>.*?)}",
                r"(?P<description>.*)",
            ]
        ]
        for pattern in patterns_to_test:
            match = re.match(pattern, line)
            if match:
                return RecipeReference(**match.groupdict())

        return RecipeReference


@dataclasses.dataclass
class Recipe:
    name: str = None
    purpose: str = None
    type: str = None
    templates: List[str] = dataclasses.field(default_factory=list)
    input_data: List[DataItemReference] = dataclasses.field(default_factory=list)
    parameters: List[str] = dataclasses.field(default_factory=list)
    algorithm: str = None
    output_data: List[DataItemReference] = dataclasses.field(default_factory=list)
    expected_accuracies: str = None
    qc1_parameters: List[str] = None
    hdrl_functions: List[str] = None
    requirements: List[str] = None
    matched_keywords: List[str] = None

    @staticmethod
    def parse_recipe_from_table(stable):
        """Parse a Recipe from a table"""
        rows1a = [
            line.strip()
            for line in stable.splitlines()
            if line.strip() and not line.strip().startswith("%")
        ]
        # Some recipes start with
        # \begin{recipedef}\label{rec:metisimgchophome}\label{rec:metis_img_chophome}
        # So rows1a starts with
        # \label{rec:metisimgchophome}\label{rec:metis_img_chophome}
        # Remove that line
        # TODO: perhaps do something useful with the labels
        rows1b = [row for row in rows1a if not row.startswith(r"\label")]
        # Some recipes have the label in the name
        #   Name:                & \hyperref[rec:metis_ifu_adi_cgrph]{\REC{metis_ifu_adi_cgrph}}\label{rec:metis_ifu_adi_cgrph}                                        \\
        # So remove those as well.
        rows1c = [row.split(r"\label") for row in rows1b]
        rows1 = [row[0] if len(row) == 1 else row[0] + r"\\" for row in rows1c]

        # Concatenate lines.. Aargh
        rows2 = []
        thisline = ""
        for line in rows1:
            # Remove any trailing comments
            line2 = PATTERN_TEX_COMMENT.sub("", line).strip()
            thisline += line2
            if thisline.endswith("\\\\"):
                rows2.append(thisline)
                thisline = ""

        rows3 = [
            line.strip().strip("\\").strip().split("&")
            for line in rows2
            # TODO: Do something sensible if there is no &
            if "&" in line
        ]

        for row in rows3:
            msg = f"Wrong number of columns: {row}"
            assert len(row) == 2, msg

        # Placeholder is necessary for last item
        rows4 = [(aa.strip().strip(":").strip(), bb.strip()) for aa, bb in rows3] + [("placeholder", "")]

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
                            HACK_RECIPE_TEMPLATES.get((thedata["name"], vi.lower()), vi.lower())
                            for vi in value
                        ]
                    # There could be a * in one of the templates, e.g.
                    # "metis_img_lm_*_obs_*". However, it is not possible
                    # to expand those here, because there is no knowledge
                    # about which templates exist at this stage.
                elif field_old in ["output_data", "input_data"]:
                    value1 = []
                    for val in value.split("\n"):
                        # Some are weird like
                        # (\FITS{PRO_CATG}: \FITS{LM_LSS_2d_coadd_wavecal})
                        if val.startswith("(") and "PRO_CATG" in val:
                            continue

                        # Some of these have " or " in them and need to be split
                        # \hyperref[dataitem:lm_cgrph_sci_speckle]{\PROD{LM_cgrph_SCI_SPECKLE}} or \hyperref[dataitem:n_cgrph_sci_speckle]{\PROD{N_cgrph_SCI_SPECKLE}}\\
                        if " or " in val and val.count("hyperref") == 2:
                            val_left, val_right = val.split(" or ")
                            assert "hyperref" in val_left, f"Can't understand {val}"
                            assert "hyperref" in val_right, f"Can't understand {val}"
                            value1.append(DataItemReference.from_recipe_line(val_left.strip()))
                            value1.append(DataItemReference.from_recipe_line(val_right.strip()))
                        else:
                            value1.append(DataItemReference.from_recipe_line(val))

                    # First, from the DRLD:
                    #   Where _det appears in FITS keywords of input or product files,
                    #   it is taken to mean _LM, N or _IFU
                    #   according to the detector array for which data are being processed.
                    # TODO: Perhaps we should go back to _2RG and _GEO for _LM and _N

                    # Second, split these:
                    #         Reduced science cubes (\PROD{IFU_SCI_REDUCED}, \PROD{IFU_SCI_REDUCED_TAC})
                    value = []
                    for val in value1:
                        if val.name and "det" in val.name:
                            #  det_APP_SCI_CALIBRATED or DETLIN_det_RAW
                            msg = f"There are too many or wrong 'det's in f{val.name}."
                            assert (
                                val.name.endswith("_det")
                                or val.name.startswith("det_")
                                or "_det_" in val.name
                            ), msg
                            assert val.name.count("det") == 1, msg
                            # for postfix in ["LM", "N", "IFU", "GEO", "2RG"]:
                            for postfix in guess_postfixes(val.name):
                                value.append(
                                    DataItemReference(
                                        name=val.name.replace("det", postfix),
                                        dtype=val.dtype,
                                        hyperref=val.hyperref,
                                        description=val.description,
                                    )
                                )
                        elif val.name and "PROD" in val.name:
                            # There is only one case of this it seems.
                            # Then the name becomes
                            #  'IFU_SCI_REDUCED}, PROD{IFU_SCI_REDUCED_TAC'
                            names_new = val.name.split("}, PROD{")
                            assert len(names_new) == 2
                            for name_new in names_new:
                                value.append(
                                    DataItemReference(
                                        name=name_new,
                                        dtype=val.dtype,
                                        hyperref=val.hyperref,
                                        description=val.description,
                                    )
                                )
                        else:
                            value.append(val)

                thedata[field_old] = value

            field = HACK_BAD_NAMES.get(field1, field1)
            if field1 in HACK_BAD_NAMES:
                print(f"{field1} should be renamed to {field}.")
            value = row[1]

            if "name" in field:
                value = re.sub(r"\\REC{(.*?)}", "\\1", value)
                value = re.sub(r"\\hyperref\[.*?]{(.*?)}", "\\1", value)
                # print(field, ":::", value)

            if field == "placeholder":
                continue

            # noinspection PyUnresolvedReferences
            assert field in Recipe.__dataclass_fields__, f"Field {field} cannot be found {row[0]}"

            # Cannot yet add the value to thedata dictionary because the value
            # might continue on other rows.
            field_old = field

        return Recipe(**thedata)


class DataReductionLibraryDesign:
    """The information from the DRLD"""

    # TODO: Check all tex files

    def __init__(self):
        path_here = Path(__file__).parent

        self.path_drld = path_here.parent.parent
        # The path of the DRLD

        self.templates_acquisition_used = {
            "METIS_spec_lm_acq",
            "METIS_spec_n_acq",
            "METIS_spec_lmn_acq",
        }
        # Apparently we do process some acquisition templates!

        self.filenames_tex = glob.glob(os.path.join(self.path_drld, "*.tex"))
        # Regular tex files.

        self.filenames_tikz = glob.glob(os.path.join(self.path_drld, "**/*.tex"))
        # Tikz figures.

        self.recipes = self.get_recipes()
        # The Recipes defined in the DRLD.

        self.dataitems = self.get_dataitems()
        # The DataItems defined in the DRLD.

        self.recipe_names_used = self.get_recipe_names_used()
        (
            self.template_names_used,
            self.template_names_used_normal,
            self.template_names_used_tikz,
        ) = self.get_template_names_used()

    def get_recipes(self):
        """"""
        # TODO: Verify that there are no recipes defined in other tex files.
        files_drld = glob.glob(os.path.join(self.path_drld, "Recipes*.tex"))
        recipes = {}
        for filename in files_drld:
            data = open(filename, encoding="utf8").read()
            # Remove comments
            data2 = PATTERN_TEX_COMMENT.sub("", data)
            srecipes = [
                dd.split("\\end{recipedef}")[0]
                for dd in data2.split("\\begin{recipedef}")
                if "recipe parameters" in dd.lower() or "qc1" in dd.lower()
            ]
            for stable in srecipes:
                recipe = Recipe.parse_recipe_from_table(stable)
                assert recipe.name is not None, f"Recipe has no name: {stable}"
                recipes[recipe.name] = recipe

        return recipes

    def get_dataitems_headers_only(self):
        r"""Read all DataItems defined in 'DRL DATA ITEMS AND STRUCTURES'.

        The DataItems are all defined in 09_0-DRL-Data-Structures.tex, which
        \input's all *_data_item.tex files. Those files have paragraphs like

        \paragraph{\hyperref[dataitem:lmlsssciflux2d]{\PROD{LM_LSS_SCI_FLUX_2D}}}\label{dataitem:lmlsssciflux2d}

        but some are

        '\\paragraph{\\hyperref[dataitem:masterdark2rg]{\\PROD{MASTER_DARK_2RG}} and \\hyperref[dataitem:masterdarkgeo]{\\PROD{MASTER_DARK_GEO}}}\\label{dataitem:masterdark}\\label{dataitem:masterdark2rg}\\label{dataitem:masterdarkgeo}'

        or

        \paragraph{\hyperref[dataitem:lsfkernel]{\STATCALIB{LSF_KERNEL}}}\label{dataitem:lsfkernel}

        """
        path_dataitems = self.path_drld / "09_0-DRL-Data-Structures.tex"
        paths_with_dataitems = find_latex_inputs(path_dataitems)

        data_all = (
            "\n"
            + "\n".join(
                "\n".join([ll for ll in open(pp).readlines() if not ll.strip().startswith("%")])
                for pp in [path_dataitems] + paths_with_dataitems
            )
            + "\n"
        )
        data_all = data_all.replace("\n", "\n\n")
        # All these \n's are there because HB doesn't know how to do proper
        # look-ahead or look-backwards in Python regular expressions.

        # TODO: differentiate between PROD, EXTCALIB, STATCALIB, and RAW
        # TODO: Add support for drlstructure
        dataitems1 = re.findall(
            r"[^%](\\paragraph{\\hyperref\[(.*?)]{\\[A-Z]+{(.*?)}}}\\label{(dataitem.*?)}.*)\n",
            data_all,
        )

        dataitems2 = []
        for line, hyperref, name, label in dataitems1:
            if " and " in name:
                # beware of ZA̡͊͠͝LGΌ
                mm = re.match(
                    r"\\paragraph{\\hyperref\[(.*?)]{\\PROD{(.*?)}} and \\hyperref\[(.*?)]{\\PROD{(.*?)}}}(\\label{.*?})$",
                    line,
                )
                hyperref1, name1, hyperref2, name2, labelsg = mm.groups()
                hyperref_common = "".join(
                    a[0] for a in itertools.takewhile(lambda a: a[0] == a[1], zip(hyperref1, hyperref2))
                )
                labels = re.findall(r"\\label{(.*?)}", labelsg)
                assert hyperref_common in labels
                assert hyperref2 in labels
                assert hyperref1 in labels
                dataitems2 += [
                    [name1, hyperref1, labels],
                    [name2, hyperref2, labels],
                ]
            else:
                assert (
                    hyperref == label
                ), f"Hyperref '{hyperref}' is not equal to label '{label}' for line '{line}'"
                # namel = name.lower().replace("_", "")
                # print(f"dataitem:{namel}" == hyperref, name, hyperref)
                dataitems2 += [[name, hyperref, [label]]]

        dataitems4 = []
        for [name, hyperref, labels] in dataitems2:
            if "det" in name:
                # TODO: Harmonize with the other one
                assert name.count("det") == 1, f"Too many 'det's in f{name}"
                # for name_det in ["LM", "N", "IFU", "2RG", "GEO", "det"]:
                for postfix in guess_postfixes(name):
                    dataitems4.append(
                        [
                            name.replace("det", postfix),
                            hyperref,
                            labels,
                        ]
                    )
                # Also add the one with placeholders.
                # TODO: Either only add the ones with placeholders, or the
                # ones with the placeholders filled in.
                dataitems4.append([name, hyperref, labels])
            else:
                dataitems4.append([name, hyperref, labels])

        dataitems3 = {}
        for name, hyperref, labels in dataitems4:
            # Check disable, because the _det_ dataitems can indeed have
            # more than one paragraph.
            # assert name not in dataitems3, f"Duplicate dataitem: {name}"
            dataitems3[name] = DataItem(
                name=name,
                hyperref=hyperref,
                labels=labels,
            )

        return dataitems3

    def get_dataitems_full(self):
        r"""Read all DataItems defined in 'DRL DATA ITEMS AND STRUCTURES'.

        The DataItems are all defined in 09_0-DRL-Data-Structures.tex, which
        \input's all *_data_item.tex files. Those files have paragraphs like

        \paragraph{\hyperref[dataitem:lmlsssciflux2d]{\PROD{LM_LSS_SCI_FLUX_2D}}}\label{dataitem:lmlsssciflux2d}

        but some are

        '\\paragraph{\\hyperref[dataitem:masterdark2rg]{\\PROD{MASTER_DARK_2RG}} and \\hyperref[dataitem:masterdarkgeo]{\\PROD{MASTER_DARK_GEO}}}\\label{dataitem:masterdark}\\label{dataitem:masterdark2rg}\\label{dataitem:masterdarkgeo}'

        or

        \paragraph{\hyperref[dataitem:lsfkernel]{\STATCALIB{LSF_KERNEL}}}\label{dataitem:lsfkernel}

        """
        path_dataitems = self.path_drld / "09_0-DRL-Data-Structures.tex"
        paths_with_dataitems = find_latex_inputs(path_dataitems)

        data_all = (
            "\n"
            + "\n".join(
                "".join([ll for ll in open(pp).readlines() if not ll.strip().startswith("%")])
                for pp in [path_dataitems] + paths_with_dataitems
            )
            + "\n"
        )

        dataitems1 = data_all.split("\\paragraph")

        dataitems3 = {}
        # dataitems[0] is the preamble of the section
        for sparagraph in dataitems1[1:]:
            if "drsstructure" in sparagraph:
                continue
            sparagraph = "\\paragraph" + sparagraph
            dataitem = DataItem.from_paragraph(sparagraph)
            if dataitem.name is None:
                continue

            name = dataitem.name
            dataitem_existing = dataitems3.get(name, None)
            # E.g. MASTER_DARK_2RG can be added while MASTER_DARK_det is there
            assert dataitem_existing is None or "det" in dataitem_existing.name
            dataitems3[dataitem.name] = dataitem

            if "det" in name:
                # TODO: Harmonize with the other one
                assert name.count("det") == 1, f"Too many 'det's in f{name}"
                for name_det in ["LM", "N", "IFU", "2RG", "GEO", "det"]:
                    dataitems3[name.replace("det", name_det)] = dataitem

        return dataitems3

    # get_dataitems = get_dataitems_headers_only
    get_dataitems = get_dataitems_full

    def get_template_names_used(self):
        """
        Get templates from tex files
        """

        not_templates = [
            "METIS_IMAGE",
            "METIS_CUBE",
        ] + list(self.recipes.keys())
        not_templates += [rec.lower() for rec in not_templates]
        template_names_normal = []
        for filename in self.filenames_tex:
            datat1 = open(filename, encoding="utf8").readlines()
            datat = "\n".join(line for line in datat1 if not line.strip().startswith("%"))
            tpls_macro = [
                tsii.replace("\\", "") for tsii in re.findall("\\\\TPL{(M.*?)}", datat, re.IGNORECASE)
            ]
            # Normal LaTeX, does not work for tikz?
            tpls_latex = [
                tsii.replace("\\", "").replace("$ast$", "*")
                for tsii in
                # re.findall("metis\\\\_[iaogps][a-z_\\*\\\\]*", datat, re.IGNORECASE)
                # Include negative lookbehind (<?![:{]) to exclude any possible
                # template name that has a : or { before it, because it is probably
                # e.g. drl:metis_derive_gain, or \DRL{metis_derive_gain}.
                # Any \TPL{metis_derive_gain} is caught in tpls_macro above
                re.findall("(?<![:{])metis\\\\_[a-z_*\\\\ast$]*", datat, re.IGNORECASE)
            ]
            template_names_normal += [
                tsi for tsi in tpls_macro + tpls_latex if tsi.lower() not in not_templates
            ]
        template_names_tikz = []
        for filename in self.filenames_tikz:
            # Only tikzs
            datat1 = open(filename, encoding="utf8").readlines()
            datat = "\n".join(line for line in datat1 if not line.strip().startswith("%"))
            tpls_latex = [
                tsii.replace("\\", "").replace("$ast$", "*")
                for tsii in
                # No negative lookbehind for tikz
                re.findall("metis\\\\_[a-z_*\\\\ast$]*", datat, re.IGNORECASE)
            ]
            template_names_tikz += [tsi for tsi in tpls_latex if tsi.lower() not in not_templates]

        return (
            template_names_normal + template_names_tikz,
            template_names_normal,
            template_names_tikz,
        )

    def get_recipe_names_used(self):
        """All recipes names used in the DRLD."""
        # TODO: Also search in the figures.

        # TODO: Ensure that these abbreviations are handled somehow:
        #       "The prefix ``\REC{metis_}'' has been
        #     omitted from the recipe names to improve clarity. The product
        #     names omit ``\PROD{LM_}''.}"

        # Everything starts with metis_ except detmon_ir_lg
        not_recipes = {"metis_do_stuff", "metis_", ""}
        recipe_names_u = [
            recname.replace("\\", "")
            for fn in self.filenames_tex
            for recname in re.findall("\\\\REC{(.*?)}", open(fn, encoding="utf8").read())
            if recname not in not_recipes
        ]
        return sorted(set(recipe_names_u))

    def get_created_by(self, name_dataitem):
        """Get recipes that create dataitems with this name."""
        return [
            recipe
            for recipe in self.recipes.values()
            if name_dataitem in [diref.name for diref in recipe.output_data]
            or any(
                name_dataitem.replace("det", postfix) in [diref.name for diref in recipe.output_data]
                for postfix in guess_postfixes(name_dataitem)
            )
        ]

    def get_raws_for_template(self, template: str):
        """Get raw data produced by template."""
        data = [
            di.name
            for di in self.dataitems.values()
            if template in di.templates or template.lower() in [tem.lower() for tem in di.templates]
        ]
        return data

    def get_recipes_for_template(self, template: str):
        """Get recipes triggered by template."""
        data = [
            recipe.name
            for recipe in self.recipes.values()
            if template in recipe.templates
            or template.lower() in [tem.lower() for tem in recipe.templates]
        ]
        return data

    def get_recipes_for_dataitem(self, dataitem: str):
        """Get recipes with dataitem as input."""
        data = [
            recipe.name
            for recipe in self.recipes.values()
            if dataitem.lower() in [dataitemref.name.lower() for dataitemref in recipe.input_data]
        ]
        return data

    def get_input_for(self, name_dataitem):
        """Get recipes that create dataitems with this name."""
        return [
            recipe
            for recipe in self.recipes.values()
            if name_dataitem in [diref.name for diref in recipe.input_data]
            or any(
                name_dataitem.replace("det", postfix) in [diref.name for diref in recipe.input_data]
                for postfix in guess_postfixes(name_dataitem)
            )
        ]


METIS_DataReductionLibraryDesign = DataReductionLibraryDesign()
