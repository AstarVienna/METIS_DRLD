import re
import os
import glob
from pathlib import Path

from codes.drld_parser.base_classes import FitsHeader, Template, Recipe

PATH_HERE = Path(__file__).parent
PATH_OPERATIONS = PATH_HERE / "operations"

HACK_TEMPLATE_NAMES_IN_WIKI = {
    # Should just not be there:
    ("fits_keywords", "METIS_all_dark"): "metis_gen_cal_dark",
    # Probably typo?
    (
        "metis_ifu_cal_platescale",
        "METIS_img_ifu_cal_platescale",
    ): "metis_ifu_cal_platescale",
    ("ifu_discussion", "METIS_obs_IFU_FixedSkyOffset"): "metis_ifu_obs_fixedskyoffset",
    ("cal_slitloss_adc", "METIS_spec_lm_cal_slit_adc"): "metis_spec_lm_cal_slitadc",
    # all -> gen
    ("cal_dark", "METIS_all_cal_dark"): "METIS_gen_cal_dark",
    # all -> gen for lampoff, but lampoff not in Template Manual
    ("cal_rsrf_slit", "metis_all_cal_lampoff"): "metis_gen_cal_lampoff",
    ("cal_flat_lamp", "metis_all_cal_lampoff"): "metis_gen_cal_lampoff",
    ("cal_rsrf_lms", "metis_all_cal_lampoff"): "metis_gen_cal_lampoff",
    # lamp
    ("cal_flat_lamp", "METIS_img_lm_cal_LampFlat"): "metis_img_lm_cal_internalflat",
    # Should not be a template? # Not in Template Manual
    ("cal_det_bias", "METIS_all_cal_bias"): "",
    # Twilight flats, are TwilightFlat in Template Manual, not flat_twilight
    # ("metis_img_lm_cal_twilightflat", "METIS_img_lm_cal_flat_twilight"): "metis_img_lm_cal_twilightflat",
    ("cal_flat_twilight", "METIS_all_cal_TwilightFlat"): "metis_img_n_cal_twilightflat",
    ("cal_flat_twilight", "METIS_all_cal_twilightflat"): "metis_img_n_cal_twilightflat",
    # ("metis_img_n_cal_twilightflat", "METIS_img_n_cal_flat_twilight"): "metis_img_n_cal_twilightflat",
    # Not a problem, picked up by accident
    ("ifu_discussion", "METIS_CM"): "",
    ("start", "metis_templates"): "",
    # NQ. NQ mentioned twice in Template Manual though
    ("img_nq_app", "METIS_obs_APP_N_AutoChop"): "metis_img_n_obs_autochopnod",
    ("img_nq_app", "METIS_acq_APP_N"): "metis_img_lm_app_acq",
    ("cal_flux", "METIS_spec_nq_cal_standard"): "metis_img_n_obs_autochopnod",
    ("cal_flux", "METIS_spec_nq_cal_standard"): "metis_spec_n_cal_standard",
    ("cal_flux", "METIS_img_nq_cal_standard"): "metis_img_n_cal_standard",
    ("img_n_discussion", "METIS_obs_IMG_NQ_AutoChop"): "metis_img_n_obs_autochopnod",
    ("cal_distortion", "METIS_img_nq_cal_distortion"): "metis_img_n_cal_distortion",
    ("cal_flat_lamp", "METIS_img_nq_cal_LampFlat"): "",
    ("cal_det_linearity", "METIS_img_nq_cal_DetLin"): "metis_img_n_cal_detlin",
    ("cal_slitloss_adc", "METIS_spec_nq_cal_slit_adc"): "metis_spec_n_cal_slit",
    # Seems to be only discussion item
    (
        "img_n_cvc_discussion",
        "METIS_obs_RAVC_N_AutoChop",
    ): "metis_img_n_cvc_obs_autochop",
    ("spec_n_discussion", "METIS_ACQ_LSS_N_LR"): "metis_acq_lss_n_mr",
    # to investigate
    ("cal_wavelength_telluric", "METIS_all_cal_wave_telluric"): "",
}


HACK_TEMPLATE_NAMES_IN_DRLD = {
    ("*", "METIS_img_nq_cal_DetLin"): "METIS_img_n_cal_DetLin",
    ("*", "METIS_all_cal_dark"): "METIS_gen_cal_dark",
    # ("*", "METIS_img_n_cal_LampFlat"): "",
    (
        "Recipes_Imaging_LM",
        "METIS_all_cal_TwilightFlat",
    ): "METIS_img_lm_cal_TwilightFlat",
    ("Recipes_Imaging_N", "METIS_all_cal_TwilightFlat"): "METIS_img_n_cal_TwilightFlat",
    ("metis_n_img_flat", "METIS_all_cal_TwilightFlat"): "METIS_img_n_cal_TwilightFlat",
    # Seems wrong in DRLD:
    (
        "Recipes_LSS_N",
        "METIS_spec_N_obs_AutoNodOnSlit",
    ): "metis_spec_n_obs_autochopnodonslit",
    ("Recipes_LSS_LM", "METIS_spec_lm_cal_slit_adc"): "metis_spec_lm_cal_slitadc",
    # Maybe should exist? # TODO: should be metis_spec_n_cal_slit ?
    # ("Recipes_LSS_N", "METIS_spec_N_cal_slit_adc"): "metis_spec_lm_cal_slitadc",
    ("Recipes_LSS_N", "METIS_spec_N_cal_slit_adc"): "metis_spec_n_cal_slit",
    # Maybe should exist?
    (
        "Recipadces_LSS_N",
        "METIS_spec_N_obs_GenericOffset",
    ): "metis_spec_lm_obs_genericoffset",
    # Which one?
    # ("Recipes_Technical", "METIS_spec_n_cal_SlitAdc"): "metis_spec_lm_cal_slitadc",
    ("Recipes_Technical", "METIS_spec_n_cal_SlitAdc"): "metis_spec_n_cal_slit",
    (
        "Recipes_IFU_LM",
        "METIS_ifu_app_obs_GenericOffset",
    ): "metis_ifu_obs_genericoffset",
    # Pinhole is internal wave?
    ("LSS_data_items", "METIS_spec_lm_cal_rsrfpinh"): "metis_spec_lm_cal_internalwave",
    ("LSS_data_items", "METIS_spec_n_cal_rsrfpinh"): "metis_spec_n_cal_internalwave",
    ("Recipes_LSS_LM", "METIS_spec_lm_cal_rsrfpinh"): "metis_spec_lm_cal_internalwave",
    ("Recipes_LSS_N", "METIS_spec_n_cal_rsrfpinh"): "metis_spec_n_cal_internalwave",
    # and these as well?
    ("Recipes_IFU_LM", "METIS_ifu_cal_LampWave"): "metis_ifu_cal_internalwave",
    ("metis_ifu_wavecal", "METIS_ifu_cal_LampWave"): "metis_ifu_cal_internalwave",
    # Unknown
    ("metis_n_img_flat", "METIS_img_n_cal_LampFlat"): "metis_img_n_cal_internalflat",
    (
        "metis_lm_img_flat",
        "METIS_all_cal_TwilightFlat",
    ): "metis_img_lm_cal_twilightflat",
    ("metis_lm_img_flat", "METIS_img_lm_cal_LampFlat"): "metis_img_lm_cal_internalflat",
    # App stuff
    (
        "Recipes_IFU_LM",
        "METIS_ifu_ext_app_obs_GenericOffset",
    ): "metis_ifu_ext_obs_genericoffset",
    ("Recipes_Imaging_N", "METIS_img_nq_cal_standard"): "metis_img_n_cal_standard",
    # Investigate
}


TEMPLATE_IN_DRLD_BUT_NOT_IN_OPERATIONS_WIKI = [
    "METIS_spec_lm_cal_rsrfpinh",
    "METIS_spec_n_cal_rsrfpinh",
    "METIS_img_nq_cal_DetLin",
]


HACK_BAD_NAMES = {
    "recipe_name": "name",
    "observing_templates": "templates",
    "recipe_parameters": "parameters",
    "hdrl_function": "hdrl_functions",
    "requirement": "requirements",
    "template": "templates",
}


def hack_rename_template(name_template):
    # The filename is considered the correct one.
    # TODO: Check whether there are files for all these.
    hack_dict = {
        # "metis_img_n_cal_flat_twilight": "METIS_img_n_cal_TwilightFlat"
    }
    return hack_dict.get(name_template.lower(), name_template)


def hack_rename_template_header(name_template_file, name_template_header):
    # The filename is considered the correct one.
    # TODO: Check whether there are files for all these.
    hack_dict = {
        (
            "metis_img_lmn_obs_autochopnod",
            "METIS_img_n_obs_AutoChopNod".lower(),
        ): "METIS_img_lmn_obs_AutoChopNod",
        (
            "metis_img_n_cal_twilightflat",
            "metis_img_n_cal_flat_twilight",
        ): "METIS_img_n_cal_TwilightFlat",
        ("metis_spec_lmn_acq", "METIS_spec_lm_acq".lower()): "METIS_spec_lmn_acq",
        (
            "metis_img_lm_cal_chopperhome",
            "METIS_img_lm_cal_InternalFlat".lower(),
        ): "METIS_img_lm_cal_ChopperHome",
        (
            "metis_img_lmn_obs_genericchopnod",
            "METIS_img_n_obs_GenericChopNod".lower(),
        ): "METIS_img_lmn_obs_GenericChopNod",
        (
            "metis_img_lm_cal_twilightflat",
            "METIS_img_lm_cal_flat_twilight".lower(),
        ): "metis_img_lm_cal_twilightflat",
        (
            "metis_ifu_cal_platescale",
            "METIS_img_ifu_cal_platescale".lower(),
        ): "metis_ifu_cal_platescale",
        ("metis_pup_n", "METIS_pup_lm".lower()): "metis_pup_n",
    }
    return hack_dict.get(
        (name_template_file.lower(), name_template_header.lower()), name_template_header
    )


def parse_fits_header(line):
    _, parameter, hidden, therange, label, _ = [
        cell.strip() for cell in line.split("|")
    ]
    return FitsHeader(
        parameter=parameter,
        hidden=hidden,
        range=therange,
        label=label,
    )


def parse_file_template(filename, template_types_dict):
    """Parse a Template file."""
    name_template = hack_rename_template(Path(filename).stem).lower()
    datatt = open(filename, encoding="utf8").read()
    used_template_names = set(
        hack_rename_template_header(name_template, ttt)
        for ttt in re.findall("METIS_[a-zA-Z_]*", datatt)
    )
    used_template_names_headers = set(
        hack_rename_template_header(name_template, ttt)
        for ttt in re.findall("=.*(METIS_[a-zA-Z_]*)", datatt)
    )
    # print(name_template, used_template_names_headers)
    assert set(name.lower() for name in used_template_names_headers) == {name_template}
    templates_referenced = used_template_names - used_template_names_headers

    lines_param = [
        line.strip() + ("" if line.strip().endswith("|") else "|")
        for line in datatt.split("^Parameter")[-1].splitlines()
        if line.startswith("|")
    ]

    parameters = [parse_fits_header(line) for line in lines_param]
    fitsheaders = {param.parameter: param for param in parameters}
    return Template(
        name=name_template,
        ttype=template_types_dict.get(name_template, "Unknown"),
        headers=fitsheaders,
        references=templates_referenced,
    )


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


def hack_rename_template_names_drld(filename, name_template):
    filenamestem = Path(filename).stem
    return HACK_TEMPLATE_NAMES_IN_DRLD.get(
        (filenamestem, name_template),
        HACK_TEMPLATE_NAMES_IN_DRLD.get(("*", name_template), name_template),
    )


def get_template_summaries():
    data = open(
        os.path.join(PATH_OPERATIONS, "metis_templates.txt"), encoding="utf8"
    ).read()
    sections = [
        section.strip() for section in data.split("++++")[1:] if section.strip()
    ]
    assert len(sections) == 4

    templates_true = {}
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
        templates_true[type_template] = template_list

    return templates_true


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


def parse_recipes(filenames):
    # Just concatenate all the contents
    # 12_0-QC_parameters.tex uses recipedef for QC params
    # CalDB_data_items.tex uses recipedef for dataitems
    # IMG_drl_functions.tex uses recipedef for functions
    filenames_ok = [
        fni
        for fni in filenames
        if "12_0-QC_parameters" not in fni
        and "CalDB_data_items" not in fni
        and "LSS_data_items" not in fni
        and "IMG_drl_functions" not in fni
    ]
    data_all = "\n\n".join(open(fni, encoding="utf8").read() for fni in filenames_ok)
    # TODO: Assure we don't miss the first recipe by accident.
    srecipes = [
        dd.split("\\end{recipedef}")[0]
        for dd in data_all.split("\\begin{recipedef}")
        if "recipe parameters" in dd.lower() or "qc1" in dd.lower()
    ][1:]
    return [parse_recipe_from_table(stable) for stable in srecipes]


def get_recipes(drld_path):
    files_drld = glob.glob(os.path.join(drld_path, "*.tex")) + glob.glob(
        os.path.join(drld_path, "**/*.tex")
    )
    return parse_recipes(files_drld)
