"""Hacks to make parsing the Operations Wiki or the DRLD work.

These are currently necessary, but should in due time be removed.
"""
from pathlib import Path

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


# TODO: HACK_TEMPLATE_NAMES_IN_DRLD is now less necessary, as all templates
#  referenced in the Recipes are dealt with in HACK_RECIPE_TEMPLATES.
HACK_TEMPLATE_NAMES_IN_DRLD = {
    # ("*", "METIS_img_nq_cal_DetLin"): "METIS_img_n_cal_DetLin",
    # ("*", "METIS_all_cal_dark"): "METIS_gen_cal_dark",
    # ("*", "METIS_img_n_cal_LampFlat"): "",
    # (
    #     "Recipes_Imaging_LM",
    #     "METIS_all_cal_TwilightFlat",
    # ): "METIS_img_lm_cal_TwilightFlat",
    # ("Recipes_Imaging_N", "METIS_all_cal_TwilightFlat"): "METIS_img_n_cal_TwilightFlat",
    # ("metis_n_img_flat", "METIS_all_cal_TwilightFlat"): "METIS_img_n_cal_TwilightFlat",
    # Seems wrong in DRLD:
    # (
    #     "Recipes_LSS_N",
    #     "METIS_spec_N_obs_AutoNodOnSlit",
    # ): "metis_spec_n_obs_autochopnodonslit",
    # ("Recipes_LSS_LM", "METIS_spec_lm_cal_slit_adc"): "metis_spec_lm_cal_slitadc",
    # Maybe should exist? # TODO: should be metis_spec_n_cal_slit ?
    # ("Recipes_LSS_N", "METIS_spec_N_cal_slit_adc"): "metis_spec_lm_cal_slitadc",
    # ("Recipes_LSS_N", "METIS_spec_N_cal_slit_adc"): "metis_spec_n_cal_slit",
    # Maybe should exist?
    # (
    #     "Recipadces_LSS_N",
    #     "METIS_spec_N_obs_GenericOffset",
    # ): "metis_spec_lm_obs_genericoffset",
    # Which one?
    # ("Recipes_Technical", "METIS_spec_n_cal_SlitAdc"): "metis_spec_lm_cal_slitadc",
    # ("Recipes_Technical", "METIS_spec_n_cal_SlitAdc"): "metis_spec_n_cal_slit",
    # (
    #     "Recipes_IFU_LM",
    #     "METIS_ifu_app_obs_GenericOffset",
    # ): "metis_ifu_obs_genericoffset",
    # Pinhole is internal wave? No apparently this template should be added
    # ("LSS_data_items", "METIS_spec_lm_cal_rsrfpinh"): "metis_spec_lm_cal_internalwave",
    # ("LSS_data_items", "METIS_spec_n_cal_rsrfpinh"): "metis_spec_n_cal_internalwave",
    # ("Recipes_LSS_LM", "METIS_spec_lm_cal_rsrfpinh"): "metis_spec_lm_cal_internalwave",
    # ("Recipes_LSS_N", "METIS_spec_n_cal_rsrfpinh"): "metis_spec_n_cal_internalwave",
    # and these as well?
    # ("Recipes_IFU_LM", "METIS_ifu_cal_LampWave"): "metis_ifu_cal_internalwave",
    # ("metis_ifu_wavecal", "METIS_ifu_cal_LampWave"): "metis_ifu_cal_internalwave",
    # Unknown
    # ("metis_n_img_flat", "METIS_img_n_cal_LampFlat"): "metis_img_n_cal_internalflat",
    # (
    #     "metis_lm_img_flat",
    #     "METIS_all_cal_TwilightFlat",
    # ): "metis_img_lm_cal_twilightflat",
    # ("metis_lm_img_flat", "METIS_img_lm_cal_LampFlat"): "metis_img_lm_cal_internalflat",
    # App stuff
    # (
    #     "Recipes_IFU_LM",
    #     "METIS_ifu_ext_app_obs_GenericOffset",
    # ): "metis_ifu_ext_obs_genericoffset",
    # ("Recipes_Imaging_N", "METIS_img_nq_cal_standard"): "metis_img_n_cal_standard",
    # Investigate
}

HACK_RECIPE_TEMPLATES = {
    # Pinhole is internal wave?
    # (
    #     "metis_LM_lss_trace",
    #     "metis_spec_lm_cal_rsrfpinh",
    # ): "METIS_spec_lm_cal_InternalWave",
    # ("metis_N_lss_trace", "metis_spec_n_cal_rsrfpinh"): "METIS_spec_n_cal_InternalWave",
    # and these as well?
    # ("metis_ifu_wavecal", "metis_ifu_cal_lampwave"): "METIS_ifu_cal_InternalWave",
    # app stuff, is that still relevant?
    # (
    #     "metis_ifu_sci_process",
    #     "metis_ifu_app_obs_genericoffset",
    # ): "METIS_ifu_obs_GenericOffset",
    # (
    #     "metis_ifu_sci_process",
    #     "metis_ifu_ext_app_obs_genericoffset",
    # ): "METIS_ifu_ext_obs_GenericOffset",
    # Why are these different? Renamed, TODO: discuss names
    # ("metis_LM_lss_sci", "metis_spec_lm_cal_slit_adc"): "METIS_spec_lm_cal_SlitAdc",
    # ("metis_N_lss_sci", "metis_spec_n_cal_slit_adc"): "METIS_spec_n_cal_slit",
    # ("metis_n_adc_slitloss", "metis_spec_n_cal_slitadc"): "METIS_spec_n_cal_slit",
    # Apparently not "all"
    # (
    #     "metis_lm_img_flat",
    #     "metis_all_cal_twilightflat",
    # ): "METIS_img_lm_cal_TwilightFlat",
    # ("metis_n_img_flat", "metis_all_cal_twilightflat"): "METIS_img_n_cal_TwilightFlat",
    # Typo?
    # (
    #     "metis_N_lss_sci",
    #     "metis_spec_n_obs_autonodonslit",
    # ): "METIS_spec_n_obs_AutoChopNodOnSlit",
    # No clue
    # ("metis_pupil_imaging", "TBD"): "",
    # To handle in some other way
    # ("metis_lm_img_basic_reduce", "metis_img_lm_*_obs_*"): "",
    # ("metis_lm_img_background", "metis_img_lm_*_obs_*"): "",
    # Maybe should exist?
    # ("metis_N_lss_sci", "metis_spec_n_obs_genericoffset"): "",
}

TEMPLATE_IN_DRLD_BUT_NOT_IN_OPERATIONS_WIKI = [
    # Should exist according to Wolfgang:
    "METIS_spec_lm_cal_rsrfpinh",
    "METIS_spec_n_cal_rsrfpinh",
    # Not sure:
    "METIS_spec_lm_obs_AutoChopNodOnSlit",
    # Should not be there according to WK:
    "METIS_spec_N_obs_GenericOffset",
]


# Bad labels in recipedef tables.
HACK_BAD_NAMES = {
    # E.g.
    # "recipe_name": "name",
    # "observing_templates": "templates",
    # "recipe_parameters": "parameters",
    # "hdrl_function": "hdrl_functions",
    # "requirement": "requirements",
    # "template": "templates",
    "source": "created_by",
    "input_for_recipes": "input_for",
    "input_for_recipe": "input_for",
    "template": "templates",
    "created_by_recipe": "created_by",
    "produced_by_recipe": "created_by",
    "input_for_recipe(s)": "input_for",
    "used_in_recipes": "input_for",
}

HACK_INCORRECT_INPUT_DATA = {
    # E.g.
    # "LM_SCI_REDUCED": "LM_SCI_BASIC_REDUCED",
    # "MASTER_FLAT_2RG": "MASTER_IMG_FLAT_2RG",
    # "MASTER_FLAT_GEO": "MASTER_IMG_FLAT_GEO",
    # "LM_SCI_BADPIX": "BADPIX_MAP_2RG",
}

HACK_RECIPES_THAT_ARE_ALLOWED_TO_HAVE_BAD_OUTPUT = {
    # Output of metis_img_chophome is to be used by the ICS.
    "metis_img_chophome",
}

HACK_RECIPES_THAT_ARE_ALLOWED_TO_BE_MISSING = {
    # We commented out the persistence recipe for now, because it is
    # not well-defined enough to include for the internal review.
    "metis_det_persistence",
}

HACK_DATAITEMS_ALLOWED_TO_HAVE_BROKEN_USERS = {
    # N_LSS_WAVE_RAW is only created during AIT and does not have its own recipe
    "N_LSS_WAVE_RAW": {"metis_lm_lss_wave"},
}

HACK_TEMPLATES_ALLOWED_TO_TRIGGER_RECIPES_WITHOUT_RAW_DATA = {
    "METIS_spec_lmn_acq",
    "METIS_spec_lm_acq",
    "METIS_spec_n_acq",
    # and lower
    "metis_spec_lmn_acq",
    "metis_spec_lm_acq",
    "metis_spec_n_acq",
}


def hack_rename_template_header(name_template_file, name_template_header):
    """Some template files on the wiki have incorrect headers.

    These headers should have the same name as the template file.
    """
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
        ): "METIS_img_lm_cal_TwilightFlat",
        (
            "metis_ifu_cal_platescale",
            "METIS_img_ifu_cal_platescale".lower(),
        ): "metis_ifu_cal_platescale",
        ("metis_pup_n", "METIS_pup_lm".lower()): "metis_pup_n",
        (
            "metis_gen_cal_insdark",
            "METIS_gen_cal_InsDark".lower(),
        ): "METIS_gen_cal_InsDark",
    }
    return hack_dict.get((name_template_file.lower(), name_template_header.lower()), name_template_header)


def hack_rename_template_names_drld(filename, name_template):
    filenamestem = Path(filename).stem
    return HACK_TEMPLATE_NAMES_IN_DRLD.get(
        (filenamestem, name_template),
        HACK_TEMPLATE_NAMES_IN_DRLD.get(("*", name_template), name_template),
    )
