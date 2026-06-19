"""
DO NOT EDIT, THIS FILE IS GENERATED!
"""from generate_recipe import generate_recipe

recipe_metis_LM_lss_rsrf = generate_recipe(
    name="metis_LM_lss_rsrf",
    catg_input="LM_LSS_RSRF_RAW",
    catg_output="MASTER_LM_LSS_RSRF",
)

recipe_metis_LM_lss_trace = generate_recipe(
    name="metis_LM_lss_trace",
    catg_input="LM_LSS_RSRF_PINH_RAW",
    catg_output="LM_LSS_TRACE",
)

recipe_metis_LM_lss_wave = generate_recipe(
    name="metis_LM_lss_wave",
    catg_input="LM_LSS_WAVE_RAW",
    catg_output="LM_LSS_CURVE",
)

recipe_metis_LM_lss_std = generate_recipe(
    name="metis_LM_lss_std",
    catg_input="LM_LSS_STD_RAW",
    catg_output="n/a",
)

recipe_metis_LM_lss_sci = generate_recipe(
    name="metis_LM_lss_sci",
    catg_input="LM_LSS_SCI_RAW",
    catg_output="n/a",
)

recipe_metis_LM_lss_mf_model = generate_recipe(
    name="metis_LM_lss_mf_model",
    catg_input="LM_LSS_SCI_FLUX_1D",
    catg_output="MF_BEST_FIT_TAB",
)

recipe_metis_LM_lss_mf_calctrans = generate_recipe(
    name="metis_LM_lss_mf_calctrans",
    catg_input="MF_BEST_FIT_TAB",
    catg_output="LM_LSS_SYNTH_TRANS",
)

recipe_metis_LM_lss_mf_correct = generate_recipe(
    name="metis_LM_lss_mf_correct",
    catg_input="LM_LSS_SCI_FLUX_1D",
    catg_output="LM_LSS_SCI_FLUX_TELLCORR_1D",
)

recipe_metis_N_lss_rsrf = generate_recipe(
    name="metis_N_lss_rsrf",
    catg_input="N_LSS_RSRF_RAW",
    catg_output="MASTER_N_LSS_RSRF",
)

recipe_metis_N_lss_trace = generate_recipe(
    name="metis_N_lss_trace",
    catg_input="N_LSS_RSRF_PINH_RAW",
    catg_output="N_LSS_TRACE",
)

recipe_metis_N_lss_std = generate_recipe(
    name="metis_N_lss_std",
    catg_input="N_LSS_STD_RAW",
    catg_output="n/a",
)

recipe_metis_N_lss_sci = generate_recipe(
    name="metis_N_lss_sci",
    catg_input="N_LSS_SCI_RAW",
    catg_output="n/a",
)

recipe_metis_N_lss_mf_model = generate_recipe(
    name="metis_N_lss_mf_model",
    catg_input="N_LSS_SCI_FLUX_1D",
    catg_output="MF_BEST_FIT_TAB",
)

recipe_metis_N_lss_mf_calctrans = generate_recipe(
    name="metis_N_lss_mf_calctrans",
    catg_input="MF_BEST_FIT_TAB",
    catg_output="N_LSS_SYNTH_TRANS",
)

recipe_metis_N_lss_mf_correct = generate_recipe(
    name="metis_N_lss_mf_correct",
    catg_input="N_LSS_SCI_FLUX_1D",
    catg_output="N_LSS_SCI_FLUX_TELLCORR_1D",
)

recipe_metis_pupil_imaging = generate_recipe(
    name="metis_pupil_imaging",
    catg_input="LM_PUPIL_RAW",
    catg_output="LM_PUPIL_REDUCED",
)

recipe_metis_lm_adc_slitloss = generate_recipe(
    name="metis_lm_adc_slitloss",
    catg_input="LM_SLITLOSSES_RAW",
    catg_output="LM_ADC_SLITLOSS",
)

recipe_metis_n_adc_slitloss = generate_recipe(
    name="metis_n_adc_slitloss",
    catg_input="N_SLITLOSSES_RAW",
    catg_output="N_ADC_SLITLOSS",
)

recipe_metis_img_adi_cgrph = generate_recipe(
    name="metis_img_adi_cgrph",
    catg_input="LM_SCI_CALIBRATED",
    catg_output="det_cgrph_SCI_CALIBRATED",
)

recipe_metis_lm_adi_app = generate_recipe(
    name="metis_lm_adi_app",
    catg_input="LM_SCI_CALIBRATED",
    catg_output="LM_APP_SCI_CALIBRATED",
)

recipe_metis_ifu_adi_cgrph = generate_recipe(
    name="metis_ifu_adi_cgrph",
    catg_input="IFU_SCI_CUBE_CALIBRATED",
    catg_output="IFU_cgrph_SCI_CALIBRATED",
)

recipe_metis_det_lingain = generate_recipe(
    name="metis_det_lingain",
    catg_input="DETLIN_2RG_RAW",
    catg_output="GAIN_MAP_det",
)

recipe_metis_det_dark = generate_recipe(
    name="metis_det_dark",
    catg_input="DARK_2RG_RAW",
    catg_output="MASTER_DARK_2RG",
)

recipe_metis_ifu_wavecal = generate_recipe(
    name="metis_ifu_wavecal",
    catg_input="IFU_WAVE_RAW",
    catg_output="IFU_WAVECAL",
)

recipe_metis_ifu_rsrf = generate_recipe(
    name="metis_ifu_rsrf",
    catg_input="IFU_RSRF_RAW",
    catg_output="MASTER_FLAT_IFU",
)

recipe_metis_ifu_reduce = generate_recipe(
    name="metis_ifu_reduce",
    catg_input="IFU_SCI_RAW",
    catg_output="IFU_SCI_REDUCED",
)

recipe_metis_ifu_telluric = generate_recipe(
    name="metis_ifu_telluric",
    catg_input="IFU_SCI_COMBINED",
    catg_output="IFU_TELLURIC",
)

recipe_metis_ifu_calibrate = generate_recipe(
    name="metis_ifu_calibrate",
    catg_input="IFU_SCI_REDUCED",
    catg_output="IFU_SCI_CUBE_CALIBRATED",
)

recipe_metis_ifu_postprocess = generate_recipe(
    name="metis_ifu_postprocess",
    catg_input="IFU_SCI_CUBE_CALIBRATED",
    catg_output="IFU_SCI_COADD",
)

recipe_metis_ifu_distortion = generate_recipe(
    name="metis_ifu_distortion",
    catg_input="IFU_DISTORTION_RAW",
    catg_output="IFU_DISTORTION_TABLE",
)

recipe_metis_lm_img_flat = generate_recipe(
    name="metis_lm_img_flat",
    catg_input="LM_FLAT_LAMP_RAW",
    catg_output="MASTER_IMG_FLAT_LAMP_LM",
)

recipe_metis_lm_img_basic_reduce = generate_recipe(
    name="metis_lm_img_basic_reduce",
    catg_input="LM_IMAGE_SCI_RAW",
    catg_output="LM_SCI_BASIC_REDUCED",
)

recipe_metis_lm_img_background = generate_recipe(
    name="metis_lm_img_background",
    catg_input="LM_SCI_BASIC_REDUCED",
    catg_output="LM_SCI_BKG",
)

recipe_metis_lm_img_std_process = generate_recipe(
    name="metis_lm_img_std_process",
    catg_input="LM_STD_BKG_SUBTRACTED",
    catg_output="LM_STD_COMBINED",
)

recipe_metis_lm_img_calibrate = generate_recipe(
    name="metis_lm_img_calibrate",
    catg_input="LM_SCI_BKG_SUBTRACTED",
    catg_output="LM_SCI_CALIBRATED",
)

recipe_metis_lm_img_sci_postprocess = generate_recipe(
    name="metis_lm_img_sci_postprocess",
    catg_input="LM_SCI_CALIBRATED",
    catg_output="LM_SCI_COADD",
)

recipe_metis_lm_img_distortion = generate_recipe(
    name="metis_lm_img_distortion",
    catg_input="LM_DISTORTION_RAW",
    catg_output="LM_DISTORTION_TABLE",
)

recipe_metis_n_img_flat = generate_recipe(
    name="metis_n_img_flat",
    catg_input="N_FLAT_LAMP_RAW",
    catg_output="MASTER_IMG_FLAT_LAMP_N",
)

recipe_metis_n_img_chopnod = generate_recipe(
    name="metis_n_img_chopnod",
    catg_input="N_IMAGE_SCI_RAW",
    catg_output="N_SCI_BKG_SUBTRACTED",
)

recipe_metis_n_img_std_process = generate_recipe(
    name="metis_n_img_std_process",
    catg_input="N_STD_BKG_SUBTRACTED",
    catg_output="FLUXCAL_TAB",
)

recipe_metis_n_img_calibrate = generate_recipe(
    name="metis_n_img_calibrate",
    catg_input="N_SCI_BKG_SUBTRACTED",
    catg_output="N_SCI_CALIBRATED",
)

recipe_metis_n_img_restore = generate_recipe(
    name="metis_n_img_restore",
    catg_input="N_SCI_CALIBRATED",
    catg_output="N_SCI_RESTORED",
)

recipe_metis_n_img_distortion = generate_recipe(
    name="metis_n_img_distortion",
    catg_input="N_DISTORTION_RAW",
    catg_output="N_DISTORTION_TABLE",
)
