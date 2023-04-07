"""Hacks to make parsing the Operations Wiki or the DRLD work.

These are currently necessary, but should in due time be removed.
"""


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
        ("metis_gen_cal_insdark", "METIS_gen_cal_InsDark".lower()): "METIS_gen_cal_InsDark"
    }
    return hack_dict.get(
        (name_template_file.lower(), name_template_header.lower()), name_template_header
    )
