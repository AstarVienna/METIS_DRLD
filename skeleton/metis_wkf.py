"""
DO NOT EDIT, THIS FILE IS GENERATED!
"""

from edps import SCIENCE, QC1_CALIB, QC0, CALCHECKER
from edps import task, ReportInput
from edps import data_source
from edps import classification_rule
from edps import match

# HEADER KEYWORDS USED FOR CLASSIFICATION, GROUPING, AND ASSOCIATION.
instrume = "instrume"
pro_catg = "pro.catg"
dpr_type = "dpr.type"
dpr_catg = "dpr.catg"
dpr_tech = "dpr.tech"
tpl_nexp = "tpl.nexp"
obs_id = "obs.id"
tpl_start = "tpl.start"
ins_mode = "ins.mode"
arcfile = "arcfile"
mjd_obs = "mjd-obs"

ifu_wave_raw_class = classification_rule('IFU_WAVE_RAW', {dpr_catg: 'CALIB', dpr_tech: 'IFU', dpr_type: 'WAVE'})
ifu_rsrf_raw_class = classification_rule('IFU_RSRF_RAW', {dpr_catg: 'CALIB', dpr_tech: 'IFU', dpr_type: 'RSRF'})
ifu_distortion_raw_class = classification_rule('IFU_DISTORTION_RAW', {dpr_catg: 'CALIB', dpr_tech: 'IFU', dpr_type: 'DISTORTION'})
ifu_std_raw_class = classification_rule('IFU_STD_RAW', {dpr_catg: 'CALIB', dpr_tech: 'IFU', dpr_type: 'STD'})
ifu_sci_raw_class = classification_rule('IFU_SCI_RAW', {dpr_catg: 'SCIENCE', dpr_tech: 'IFU', dpr_type: 'OBJECT'})
ifu_sky_raw_class = classification_rule('IFU_SKY_RAW', {dpr_catg: 'CALIB', dpr_tech: 'IFU', dpr_type: 'SKY'})
lm_image_sci_raw_class = classification_rule('LM_IMAGE_SCI_RAW', {dpr_catg: 'SCIENCE', dpr_tech: 'IMAGE,LM', dpr_type: 'OBJECT'})
lm_image_std_raw_class = classification_rule('LM_IMAGE_STD_RAW', {dpr_catg: 'CALIB', dpr_tech: 'IMAGE,LM', dpr_type: 'STD'})
n_image_sci_raw_class = classification_rule('N_IMAGE_SCI_RAW', {dpr_catg: 'SCIENCE', dpr_tech: 'IMAGE,N', dpr_type: 'OBJECT'})
n_image_std_raw_class = classification_rule('N_IMAGE_STD_RAW', {dpr_catg: 'CALIB', dpr_tech: 'IMAGE,N', dpr_type: 'OBJECT'})
lm_chopperhome_raw_class = classification_rule('LM_CHOPPERHOME_RAW', {dpr_catg: 'CALIB', dpr_tech: 'IMAGE,LM', dpr_type: 'CHOPHOME'})
detlin_2rg_raw_class = classification_rule('DETLIN_2RG_RAW', {dpr_catg: 'CALIB', dpr_tech: 'IMAGE,LM', dpr_type: 'DETLIN'})
detlin_geo_raw_class = classification_rule('DETLIN_GEO_RAW', {dpr_catg: 'CALIB', dpr_tech: 'IMAGE,N', dpr_type: 'DETLIN'})
detlin_ifu_raw_class = classification_rule('DETLIN_IFU_RAW', {dpr_catg: 'CALIB', dpr_tech: 'IFU', dpr_type: 'DETLIN'})
dark_2rg_raw_class = classification_rule('DARK_2RG_RAW', {dpr_catg: 'CALIB', dpr_tech: 'IMAGE,LM', dpr_type: 'DARK'})
dark_geo_raw_class = classification_rule('DARK_GEO_RAW', {dpr_catg: 'CALIB', dpr_tech: 'IMAGE,N', dpr_type: 'DARK'})
dark_ifu_raw_class = classification_rule('DARK_IFU_RAW', {dpr_catg: 'CALIB', dpr_tech: 'IFU', dpr_type: 'DARK'})
lm_wcu_off_raw_class = classification_rule('LM_WCU_OFF_RAW', {dpr_catg: 'CALIB', dpr_tech: 'IMAGE,LM', dpr_type: 'DARK,WCUOFF'})
n_wcu_off_raw_class = classification_rule('N_WCU_OFF_RAW', {dpr_catg: 'CALIB', dpr_tech: 'IMAGE,N', dpr_type: 'DARK,WCUOFF'})
ifu_wcu_off_raw_class = classification_rule('IFU_WCU_OFF_RAW', {dpr_catg: 'CALIB', dpr_tech: 'IFU', dpr_type: 'DARK,WCUOFF'})
lm_flat_lamp_raw_class = classification_rule('LM_FLAT_LAMP_RAW', {dpr_catg: 'CALIB', dpr_tech: 'IMAGE,LM', dpr_type: 'FLAT,LAMP'})
lm_flat_twilight_raw_class = classification_rule('LM_FLAT_TWILIGHT_RAW', {dpr_catg: 'CALIB', dpr_tech: 'IMAGE,LM', dpr_type: 'FLAT,TWILIGHT'})
n_flat_lamp_raw_class = classification_rule('N_FLAT_LAMP_RAW', {dpr_catg: 'CALIB', dpr_tech: 'IMAGE,N', dpr_type: 'FLAT,LAMP'})
n_flat_twilight_raw_class = classification_rule('N_FLAT_TWILIGHT_RAW', {dpr_catg: 'CALIB', dpr_tech: 'IMAGE,N', dpr_type: 'FLAT,TWILIGHT'})
lm_distortion_raw_class = classification_rule('LM_DISTORTION_RAW', {dpr_catg: 'CALIB', dpr_tech: 'IMAGE,LM', dpr_type: 'DISTORTION'})
n_distortion_raw_class = classification_rule('N_DISTORTION_RAW', {dpr_catg: 'CALIB', dpr_tech: 'IMAGE,N', dpr_type: 'DISTORTION'})
lm_pupil_raw_class = classification_rule('LM_PUPIL_RAW', {dpr_catg: 'TECHNICAL', dpr_tech: 'PUP,M', dpr_type: 'PUPIL'})
n_pupil_raw_class = classification_rule('N_PUPIL_RAW', {dpr_catg: 'TECHNICAL', dpr_tech: 'PUP,N', dpr_type: 'PUPIL'})
lm_slitlosses_raw_class = classification_rule('LM_SLITLOSSES_RAW', {dpr_catg: 'CALIB', dpr_tech: 'LSS,LM', dpr_type: 'SLITLOSS'})
n_slitlosses_raw_class = classification_rule('N_SLITLOSSES_RAW', {dpr_catg: 'CALIB', dpr_tech: 'LSS,N', dpr_type: 'SLITLOSS'})
lm_lss_rsrf_raw_class = classification_rule('LM_LSS_RSRF_RAW', {dpr_catg: 'CALIB', dpr_tech: 'LSS,LM', dpr_type: 'FLAT,LAMP'})
lm_lss_rsrf_pinh_raw_class = classification_rule('LM_LSS_RSRF_PINH_RAW', {dpr_catg: 'CALIB', dpr_tech: 'LSS,LM', dpr_type: 'FLAT,LAMP,PINH'})
lm_lss_wave_raw_class = classification_rule('LM_LSS_WAVE_RAW', {dpr_catg: 'CALIB', dpr_tech: 'LSS,LM', dpr_type: 'WAVE'})
lm_lss_std_raw_class = classification_rule('LM_LSS_STD_RAW', {dpr_catg: 'CALIB', dpr_tech: 'LSS,LM', dpr_type: 'STD'})
lm_lss_sci_raw_class = classification_rule('LM_LSS_SCI_RAW', {dpr_catg: 'SCIENCE', dpr_tech: 'LSS,LM', dpr_type: 'OBJECT'})
n_lss_rsrf_raw_class = classification_rule('N_LSS_RSRF_RAW', {dpr_catg: 'CALIB', dpr_tech: 'LSS,N', dpr_type: 'FLAT,LAMP'})
n_lss_wave_raw_class = classification_rule('N_LSS_WAVE_RAW', {dpr_catg: 'CALIB', dpr_tech: 'LSS,N', dpr_type: 'WAVE'})
n_lss_rsrf_pinh_raw_class = classification_rule('N_LSS_RSRF_PINH_RAW', {dpr_catg: 'CALIB', dpr_tech: 'LSS,N', dpr_type: 'FLAT,LAMP,PINH'})
n_lss_std_raw_class = classification_rule('N_LSS_STD_RAW', {dpr_catg: 'CALIB', dpr_tech: 'LSS,N', dpr_type: 'STD'})
n_lss_sci_raw_class = classification_rule('N_LSS_SCI_RAW', {dpr_catg: 'SCIENCE', dpr_tech: 'LSS,N', dpr_type: 'OBJECT'})
lm_off_axis_psf_raw_class = classification_rule('LM_OFF_AXIS_PSF_RAW', {dpr_catg: 'CALIB', dpr_tech: 'IMAGE,LM', dpr_type: 'PSF,OFFAXIS'})
n_off_axis_psf_raw_class = classification_rule('N_OFF_AXIS_PSF_RAW', {dpr_catg: 'CALIB', dpr_tech: 'IMAGE,N', dpr_type: 'PSF,OFFAXIS'})
ifu_off_axis_psf_raw_class = classification_rule('IFU_OFF_AXIS_PSF_RAW', {dpr_catg: 'CALIB', dpr_tech: 'IFU', dpr_type: 'PSF,OFFAXIS'})


ifu_wave_raw = (data_source()
    .with_classification_rule(ifu_wave_raw_class)
    .build())


ifu_rsrf_raw = (data_source()
    .with_classification_rule(ifu_rsrf_raw_class)
    .build())


ifu_distortion_raw = (data_source()
    .with_classification_rule(ifu_distortion_raw_class)
    .build())


ifu_std_raw = (data_source()
    .with_classification_rule(ifu_std_raw_class)
    .build())


ifu_sci_raw = (data_source()
    .with_classification_rule(ifu_sci_raw_class)
    .build())


ifu_sky_raw = (data_source()
    .with_classification_rule(ifu_sky_raw_class)
    .build())


lm_image_sci_raw = (data_source()
    .with_classification_rule(lm_image_sci_raw_class)
    .build())


lm_image_std_raw = (data_source()
    .with_classification_rule(lm_image_std_raw_class)
    .build())


n_image_sci_raw = (data_source()
    .with_classification_rule(n_image_sci_raw_class)
    .build())


n_image_std_raw = (data_source()
    .with_classification_rule(n_image_std_raw_class)
    .build())


lm_chopperhome_raw = (data_source()
    .with_classification_rule(lm_chopperhome_raw_class)
    .build())


detlin_2rg_raw = (data_source()
    .with_classification_rule(detlin_2rg_raw_class)
    .build())


detlin_geo_raw = (data_source()
    .with_classification_rule(detlin_geo_raw_class)
    .build())


detlin_ifu_raw = (data_source()
    .with_classification_rule(detlin_ifu_raw_class)
    .build())


dark_2rg_raw = (data_source()
    .with_classification_rule(dark_2rg_raw_class)
    .build())


dark_geo_raw = (data_source()
    .with_classification_rule(dark_geo_raw_class)
    .build())


dark_ifu_raw = (data_source()
    .with_classification_rule(dark_ifu_raw_class)
    .build())


lm_wcu_off_raw = (data_source()
    .with_classification_rule(lm_wcu_off_raw_class)
    .build())


n_wcu_off_raw = (data_source()
    .with_classification_rule(n_wcu_off_raw_class)
    .build())


ifu_wcu_off_raw = (data_source()
    .with_classification_rule(ifu_wcu_off_raw_class)
    .build())


lm_flat_lamp_raw = (data_source()
    .with_classification_rule(lm_flat_lamp_raw_class)
    .build())


lm_flat_twilight_raw = (data_source()
    .with_classification_rule(lm_flat_twilight_raw_class)
    .build())


n_flat_lamp_raw = (data_source()
    .with_classification_rule(n_flat_lamp_raw_class)
    .build())


n_flat_twilight_raw = (data_source()
    .with_classification_rule(n_flat_twilight_raw_class)
    .build())


lm_distortion_raw = (data_source()
    .with_classification_rule(lm_distortion_raw_class)
    .build())


n_distortion_raw = (data_source()
    .with_classification_rule(n_distortion_raw_class)
    .build())


lm_pupil_raw = (data_source()
    .with_classification_rule(lm_pupil_raw_class)
    .build())


n_pupil_raw = (data_source()
    .with_classification_rule(n_pupil_raw_class)
    .build())


lm_slitlosses_raw = (data_source()
    .with_classification_rule(lm_slitlosses_raw_class)
    .build())


n_slitlosses_raw = (data_source()
    .with_classification_rule(n_slitlosses_raw_class)
    .build())


lm_lss_rsrf_raw = (data_source()
    .with_classification_rule(lm_lss_rsrf_raw_class)
    .build())


lm_lss_rsrf_pinh_raw = (data_source()
    .with_classification_rule(lm_lss_rsrf_pinh_raw_class)
    .build())


lm_lss_wave_raw = (data_source()
    .with_classification_rule(lm_lss_wave_raw_class)
    .build())


lm_lss_std_raw = (data_source()
    .with_classification_rule(lm_lss_std_raw_class)
    .build())


lm_lss_sci_raw = (data_source()
    .with_classification_rule(lm_lss_sci_raw_class)
    .build())


n_lss_rsrf_raw = (data_source()
    .with_classification_rule(n_lss_rsrf_raw_class)
    .build())


n_lss_wave_raw = (data_source()
    .with_classification_rule(n_lss_wave_raw_class)
    .build())


n_lss_rsrf_pinh_raw = (data_source()
    .with_classification_rule(n_lss_rsrf_pinh_raw_class)
    .build())


n_lss_std_raw = (data_source()
    .with_classification_rule(n_lss_std_raw_class)
    .build())


n_lss_sci_raw = (data_source()
    .with_classification_rule(n_lss_sci_raw_class)
    .build())


lm_off_axis_psf_raw = (data_source()
    .with_classification_rule(lm_off_axis_psf_raw_class)
    .build())


n_off_axis_psf_raw = (data_source()
    .with_classification_rule(n_off_axis_psf_raw_class)
    .build())


ifu_off_axis_psf_raw = (data_source()
    .with_classification_rule(ifu_off_axis_psf_raw_class)
    .build())



master_dark_2rg = (task('MASTER_DARK_2RG')
    .with_recipe('metis_det_dark')
    .with_main_input(dark_2rg_raw)
    #.with_associated_input()
    .build())


master_dark_geo = (task('MASTER_DARK_GEO')
    .with_recipe('metis_det_dark')
    .with_main_input(dark_2rg_raw)
    #.with_associated_input()
    .build())


master_dark_ifu = (task('MASTER_DARK_IFU')
    .with_recipe('metis_det_dark')
    .with_main_input(dark_2rg_raw)
    #.with_associated_input()
    .build())


lm_distortion_table = (task('LM_DISTORTION_TABLE')
    .with_recipe('metis_lm_img_distortion')
    .with_main_input(lm_distortion_raw)
    #.with_associated_input()
    .build())


lm_distortion_map = (task('LM_DISTORTION_MAP')
    .with_recipe('metis_lm_img_distortion')
    .with_main_input(lm_distortion_raw)
    #.with_associated_input()
    .build())


lm_dist_reduced = (task('LM_DIST_REDUCED')
    .with_recipe('metis_lm_img_distortion')
    .with_main_input(lm_distortion_raw)
    #.with_associated_input()
    .build())


n_distortion_table = (task('N_DISTORTION_TABLE')
    .with_recipe('metis_n_img_distortion')
    .with_main_input(n_distortion_raw)
    #.with_associated_input()
    .build())


n_distortion_map = (task('N_DISTORTION_MAP')
    .with_recipe('metis_n_img_distortion')
    .with_main_input(n_distortion_raw)
    #.with_associated_input()
    .build())


n_dist_reduced = (task('N_DIST_REDUCED')
    .with_recipe('metis_n_img_distortion')
    .with_main_input(n_distortion_raw)
    #.with_associated_input()
    .build())


lm_pupil_reduced = (task('LM_PUPIL_REDUCED')
    .with_recipe('metis_pupil_imaging')
    .with_main_input(lm_pupil_raw)
    #.with_associated_input()
    .build())


n_pupil_reduced = (task('N_PUPIL_REDUCED')
    .with_recipe('metis_pupil_imaging')
    .with_main_input(lm_pupil_raw)
    #.with_associated_input()
    .build())


master_img_flat_twilight_lm = (task('MASTER_IMG_FLAT_TWILIGHT_LM')
    .with_recipe('metis_lm_img_flat')
    .with_main_input(lm_flat_lamp_raw)
    #.with_associated_input()
    .build())


master_img_flat_lamp_lm = (task('MASTER_IMG_FLAT_LAMP_LM')
    .with_recipe('metis_lm_img_flat')
    .with_main_input(lm_flat_lamp_raw)
    #.with_associated_input()
    .build())


master_lm_lss_rsrf = (task('MASTER_LM_LSS_RSRF')
    .with_recipe('metis_LM_lss_rsrf')
    .with_main_input(lm_lss_rsrf_raw)
    #.with_associated_input()
    .build())


median_lm_lss_rsrf_img = (task('MEDIAN_LM_LSS_RSRF_IMG')
    .with_recipe('metis_LM_lss_rsrf')
    .with_main_input(lm_lss_rsrf_raw)
    #.with_associated_input()
    .build())


mean_lm_lss_rsrf_img = (task('MEAN_LM_LSS_RSRF_IMG')
    .with_recipe('metis_LM_lss_rsrf')
    .with_main_input(lm_lss_rsrf_raw)
    #.with_associated_input()
    .build())


master_img_flat_lamp_n = (task('MASTER_IMG_FLAT_LAMP_N')
    .with_recipe('metis_n_img_flat')
    .with_main_input(n_flat_lamp_raw)
    #.with_associated_input()
    .build())


master_img_flat_twilight_n = (task('MASTER_IMG_FLAT_TWILIGHT_N')
    .with_recipe('metis_n_img_flat')
    .with_main_input(n_flat_lamp_raw)
    #.with_associated_input()
    .build())


master_n_lss_rsrf = (task('MASTER_N_LSS_RSRF')
    .with_recipe('metis_N_lss_rsrf')
    .with_main_input(n_lss_rsrf_raw)
    #.with_associated_input()
    .build())


median_n_lss_rsrf_img = (task('MEDIAN_N_LSS_RSRF_IMG')
    .with_recipe('metis_N_lss_rsrf')
    .with_main_input(n_lss_rsrf_raw)
    #.with_associated_input()
    .build())


mean_n_lss_rsrf_img = (task('MEAN_N_LSS_RSRF_IMG')
    .with_recipe('metis_N_lss_rsrf')
    .with_main_input(n_lss_rsrf_raw)
    #.with_associated_input()
    .build())


ifu_dist_reduced = (task('IFU_DIST_REDUCED')
    .with_recipe('metis_ifu_distortion')
    .with_main_input(ifu_distortion_raw)
    #.with_associated_input()
    .build())


ifu_distortion_table = (task('IFU_DISTORTION_TABLE')
    .with_recipe('metis_ifu_distortion')
    .with_main_input(ifu_distortion_raw)
    #.with_associated_input()
    .build())


lm_adc_slitloss = (task('LM_ADC_SLITLOSS')
    .with_recipe('metis_lm_adc_slitloss')
    .with_main_input(lm_slitlosses_raw)
    #.with_associated_input()
    .build())


lm_std_basic_reduced = (task('LM_STD_BASIC_REDUCED')
    .with_recipe('metis_lm_img_basic_reduce')
    .with_main_input(lm_image_sci_raw)
    #.with_associated_input()
    .build())


lm_sci_basic_reduced = (task('LM_SCI_BASIC_REDUCED')
    .with_recipe('metis_lm_img_basic_reduce')
    .with_main_input(lm_image_sci_raw)
    #.with_associated_input()
    .build())


lm_lss_trace = (task('LM_LSS_TRACE')
    .with_recipe('metis_LM_lss_trace')
    .with_main_input(lm_lss_rsrf_pinh_raw)
    #.with_associated_input()
    .build())


n_adc_slitloss = (task('N_ADC_SLITLOSS')
    .with_recipe('metis_n_adc_slitloss')
    .with_main_input(n_slitlosses_raw)
    #.with_associated_input()
    .build())


n_std_bkg_subtracted = (task('N_STD_BKG_SUBTRACTED')
    .with_recipe('metis_n_img_chopnod')
    .with_main_input(n_image_sci_raw)
    #.with_associated_input()
    .build())


n_sci_bkg_subtracted = (task('N_SCI_BKG_SUBTRACTED')
    .with_recipe('metis_n_img_chopnod')
    .with_main_input(n_image_sci_raw)
    #.with_associated_input()
    .build())


n_lss_trace = (task('N_LSS_TRACE')
    .with_recipe('metis_N_lss_trace')
    .with_main_input(n_lss_rsrf_pinh_raw)
    #.with_associated_input()
    .build())


ifu_wavecal = (task('IFU_WAVECAL')
    .with_recipe('metis_ifu_wavecal')
    .with_main_input(ifu_wave_raw)
    #.with_associated_input()
    .build())


lm_std_bkg_subtracted = (task('LM_STD_BKG_SUBTRACTED')
    .with_recipe('metis_lm_img_background')
    .with_main_input(lm_sci_basic_reduced)
    #.with_associated_input()
    .build())


lm_sci_bkg = (task('LM_SCI_BKG')
    .with_recipe('metis_lm_img_background')
    .with_main_input(lm_sci_basic_reduced)
    #.with_associated_input()
    .build())


lm_std_bkg = (task('LM_STD_BKG')
    .with_recipe('metis_lm_img_background')
    .with_main_input(lm_sci_basic_reduced)
    #.with_associated_input()
    .build())


lm_sci_bkg_subtracted = (task('LM_SCI_BKG_SUBTRACTED')
    .with_recipe('metis_lm_img_background')
    .with_main_input(lm_sci_basic_reduced)
    #.with_associated_input()
    .build())


lm_std_object_cat = (task('LM_STD_OBJECT_CAT')
    .with_recipe('metis_lm_img_background')
    .with_main_input(lm_sci_basic_reduced)
    #.with_associated_input()
    .build())


lm_sci_object_cat = (task('LM_SCI_OBJECT_CAT')
    .with_recipe('metis_lm_img_background')
    .with_main_input(lm_sci_basic_reduced)
    #.with_associated_input()
    .build())


lm_lss_curve = (task('LM_LSS_CURVE')
    .with_recipe('metis_LM_lss_wave')
    .with_main_input(lm_lss_wave_raw)
    #.with_associated_input()
    .build())


lm_lss_dist_sol = (task('LM_LSS_DIST_SOL')
    .with_recipe('metis_LM_lss_wave')
    .with_main_input(lm_lss_wave_raw)
    #.with_associated_input()
    .build())


lm_lss_wave_guess = (task('LM_LSS_WAVE_GUESS')
    .with_recipe('metis_LM_lss_wave')
    .with_main_input(lm_lss_wave_raw)
    #.with_associated_input()
    .build())


n_lss_std_obj_map = (task('N_LSS_STD_OBJ_MAP')
    .with_recipe('metis_N_lss_std')
    .with_main_input(n_lss_std_raw)
    #.with_associated_input()
    .build())


n_lss_std_sky_map = (task('N_LSS_STD_SKY_MAP')
    .with_recipe('metis_N_lss_std')
    .with_main_input(n_lss_std_raw)
    #.with_associated_input()
    .build())


n_lss_std_1d = (task('N_LSS_STD_1D')
    .with_recipe('metis_N_lss_std')
    .with_main_input(n_lss_std_raw)
    #.with_associated_input()
    .build())


master_n_response = (task('MASTER_N_RESPONSE')
    .with_recipe('metis_N_lss_std')
    .with_main_input(n_lss_std_raw)
    #.with_associated_input()
    .build())


rsrf_ifu = (task('RSRF_IFU')
    .with_recipe('metis_ifu_rsrf')
    .with_main_input(ifu_rsrf_raw)
    #.with_associated_input()
    .build())


master_flat_ifu = (task('MASTER_FLAT_IFU')
    .with_recipe('metis_ifu_rsrf')
    .with_main_input(ifu_rsrf_raw)
    #.with_associated_input()
    .build())


fluxcal_tab = (task('FLUXCAL_TAB')
    .with_recipe('metis_lm_img_std_process')
    .with_main_input(lm_std_bkg_subtracted)
    #.with_associated_input()
    .build())


lm_std_combined = (task('LM_STD_COMBINED')
    .with_recipe('metis_lm_img_std_process')
    .with_main_input(lm_std_bkg_subtracted)
    #.with_associated_input()
    .build())


lm_lss_std_obj_map = (task('LM_LSS_STD_OBJ_MAP')
    .with_recipe('metis_LM_lss_std')
    .with_main_input(lm_lss_std_raw)
    #.with_associated_input()
    .build())


lm_lss_std_sky_map = (task('LM_LSS_STD_SKY_MAP')
    .with_recipe('metis_LM_lss_std')
    .with_main_input(lm_lss_std_raw)
    #.with_associated_input()
    .build())


lm_lss_std_1d = (task('LM_LSS_STD_1D')
    .with_recipe('metis_LM_lss_std')
    .with_main_input(lm_lss_std_raw)
    #.with_associated_input()
    .build())


std_transmission = (task('STD_TRANSMISSION')
    .with_recipe('metis_LM_lss_std')
    .with_main_input(lm_lss_std_raw)
    #.with_associated_input()
    .build())


master_lm_response = (task('MASTER_LM_RESPONSE')
    .with_recipe('metis_LM_lss_std')
    .with_main_input(lm_lss_std_raw)
    #.with_associated_input()
    .build())


lm_lss_std_wave = (task('LM_LSS_STD_WAVE')
    .with_recipe('metis_LM_lss_std')
    .with_main_input(lm_lss_std_raw)
    #.with_associated_input()
    .build())


n_lss_sci_obj_map = (task('N_LSS_SCI_OBJ_MAP')
    .with_recipe('metis_N_lss_sci')
    .with_main_input(n_lss_sci_raw)
    #.with_associated_input()
    .build())


n_lss_sci_sky_map = (task('N_LSS_SCI_SKY_MAP')
    .with_recipe('metis_N_lss_sci')
    .with_main_input(n_lss_sci_raw)
    #.with_associated_input()
    .build())


n_lss_sci_2d = (task('N_LSS_SCI_2D')
    .with_recipe('metis_N_lss_sci')
    .with_main_input(n_lss_sci_raw)
    #.with_associated_input()
    .build())


n_lss_sci_1d = (task('N_LSS_SCI_1D')
    .with_recipe('metis_N_lss_sci')
    .with_main_input(n_lss_sci_raw)
    #.with_associated_input()
    .build())


n_lss_sci_flux_2d = (task('N_LSS_SCI_FLUX_2D')
    .with_recipe('metis_N_lss_sci')
    .with_main_input(n_lss_sci_raw)
    #.with_associated_input()
    .build())


n_lss_sci_flux_1d = (task('N_LSS_SCI_FLUX_1D')
    .with_recipe('metis_N_lss_sci')
    .with_main_input(n_lss_sci_raw)
    #.with_associated_input()
    .build())


ifu_std_background = (task('IFU_STD_BACKGROUND')
    .with_recipe('metis_ifu_reduce')
    .with_main_input(ifu_sci_raw)
    #.with_associated_input()
    .build())


ifu_std_reduced = (task('IFU_STD_REDUCED')
    .with_recipe('metis_ifu_reduce')
    .with_main_input(ifu_sci_raw)
    #.with_associated_input()
    .build())


ifu_std_reduced_cube = (task('IFU_STD_REDUCED_CUBE')
    .with_recipe('metis_ifu_reduce')
    .with_main_input(ifu_sci_raw)
    #.with_associated_input()
    .build())


ifu_sci_combined = (task('IFU_SCI_COMBINED')
    .with_recipe('metis_ifu_reduce')
    .with_main_input(ifu_sci_raw)
    #.with_associated_input()
    .build())


ifu_std_combined = (task('IFU_STD_COMBINED')
    .with_recipe('metis_ifu_reduce')
    .with_main_input(ifu_sci_raw)
    #.with_associated_input()
    .build())


ifu_sci_reduced = (task('IFU_SCI_REDUCED')
    .with_recipe('metis_ifu_reduce')
    .with_main_input(ifu_sci_raw)
    #.with_associated_input()
    .build())


ifu_sci_background = (task('IFU_SCI_BACKGROUND')
    .with_recipe('metis_ifu_reduce')
    .with_main_input(ifu_sci_raw)
    #.with_associated_input()
    .build())


ifu_sci_reduced_cube = (task('IFU_SCI_REDUCED_CUBE')
    .with_recipe('metis_ifu_reduce')
    .with_main_input(ifu_sci_raw)
    #.with_associated_input()
    .build())


lm_sci_calibrated = (task('LM_SCI_CALIBRATED')
    .with_recipe('metis_lm_img_calibrate')
    .with_main_input(lm_sci_bkg_subtracted)
    #.with_associated_input()
    .build())


n_sci_calibrated = (task('N_SCI_CALIBRATED')
    .with_recipe('metis_n_img_calibrate')
    .with_main_input(n_sci_bkg_subtracted)
    #.with_associated_input()
    .build())


lm_lss_sci_obj_map = (task('LM_LSS_SCI_OBJ_MAP')
    .with_recipe('metis_LM_lss_sci')
    .with_main_input(lm_lss_sci_raw)
    #.with_associated_input()
    .build())


lm_lss_sci_sky_map = (task('LM_LSS_SCI_SKY_MAP')
    .with_recipe('metis_LM_lss_sci')
    .with_main_input(lm_lss_sci_raw)
    #.with_associated_input()
    .build())


lm_lss_sci_2d = (task('LM_LSS_SCI_2D')
    .with_recipe('metis_LM_lss_sci')
    .with_main_input(lm_lss_sci_raw)
    #.with_associated_input()
    .build())


lm_lss_sci_1d = (task('LM_LSS_SCI_1D')
    .with_recipe('metis_LM_lss_sci')
    .with_main_input(lm_lss_sci_raw)
    #.with_associated_input()
    .build())


lm_lss_sci_flux_2d = (task('LM_LSS_SCI_FLUX_2D')
    .with_recipe('metis_LM_lss_sci')
    .with_main_input(lm_lss_sci_raw)
    #.with_associated_input()
    .build())


lm_lss_sci_flux_1d = (task('LM_LSS_SCI_FLUX_1D')
    .with_recipe('metis_LM_lss_sci')
    .with_main_input(lm_lss_sci_raw)
    #.with_associated_input()
    .build())


ifu_std_reduced_1d = (task('IFU_STD_REDUCED_1D')
    .with_recipe('metis_ifu_telluric')
    .with_main_input(ifu_sci_combined)
    #.with_associated_input()
    .build())


ifu_telluric = (task('IFU_TELLURIC')
    .with_recipe('metis_ifu_telluric')
    .with_main_input(ifu_sci_combined)
    #.with_associated_input()
    .build())


ifu_sci_reduced_1d = (task('IFU_SCI_REDUCED_1D')
    .with_recipe('metis_ifu_telluric')
    .with_main_input(ifu_sci_combined)
    #.with_associated_input()
    .build())


lm_sci_coadd = (task('LM_SCI_COADD')
    .with_recipe('metis_lm_img_sci_postprocess')
    .with_main_input(lm_sci_calibrated)
    #.with_associated_input()
    .build())


lm_app_sci_calibrated = (task('LM_APP_SCI_CALIBRATED')
    .with_recipe('metis_lm_adi_app')
    .with_main_input(lm_sci_calibrated)
    #.with_associated_input()
    .build())


lm_app_sci_centred = (task('LM_APP_SCI_CENTRED')
    .with_recipe('metis_lm_adi_app')
    .with_main_input(lm_sci_calibrated)
    #.with_associated_input()
    .build())


lm_app_sci_speckle = (task('LM_APP_SCI_SPECKLE')
    .with_recipe('metis_lm_adi_app')
    .with_main_input(lm_sci_calibrated)
    #.with_associated_input()
    .build())


lm_app_sci_derotated_psfsub = (task('LM_APP_SCI_DEROTATED_PSFSUB')
    .with_recipe('metis_lm_adi_app')
    .with_main_input(lm_sci_calibrated)
    #.with_associated_input()
    .build())


lm_app_sci_derotated = (task('LM_APP_SCI_DEROTATED')
    .with_recipe('metis_lm_adi_app')
    .with_main_input(lm_sci_calibrated)
    #.with_associated_input()
    .build())


lm_app_sci_coverage = (task('LM_APP_SCI_COVERAGE')
    .with_recipe('metis_lm_adi_app')
    .with_main_input(lm_sci_calibrated)
    #.with_associated_input()
    .build())


lm_app_sci_snr = (task('LM_APP_SCI_SNR')
    .with_recipe('metis_lm_adi_app')
    .with_main_input(lm_sci_calibrated)
    #.with_associated_input()
    .build())


lm_app_sci_contrast_radprof = (task('LM_APP_SCI_CONTRAST_RADPROF')
    .with_recipe('metis_lm_adi_app')
    .with_main_input(lm_sci_calibrated)
    #.with_associated_input()
    .build())


lm_app_sci_contrast_adi = (task('LM_APP_SCI_CONTRAST_ADI')
    .with_recipe('metis_lm_adi_app')
    .with_main_input(lm_sci_calibrated)
    #.with_associated_input()
    .build())


lm_app_sci_throughput = (task('LM_APP_SCI_THROUGHPUT')
    .with_recipe('metis_lm_adi_app')
    .with_main_input(lm_sci_calibrated)
    #.with_associated_input()
    .build())


lm_app_centroid_tab = (task('LM_APP_CENTROID_TAB')
    .with_recipe('metis_lm_adi_app')
    .with_main_input(lm_sci_calibrated)
    #.with_associated_input()
    .build())


lm_app_psf_median = (task('LM_APP_PSF_MEDIAN')
    .with_recipe('metis_lm_adi_app')
    .with_main_input(lm_sci_calibrated)
    #.with_associated_input()
    .build())


n_sci_restored = (task('N_SCI_RESTORED')
    .with_recipe('metis_n_img_restore')
    .with_main_input(n_sci_calibrated)
    #.with_associated_input()
    .build())


mf_best_fit_tab = (task('MF_BEST_FIT_TAB')
    .with_recipe('metis_LM_lss_mf_model')
    .with_main_input(lm_lss_sci_flux_1d)
    #.with_associated_input()
    .build())


ifu_sci_cube_calibrated = (task('IFU_SCI_CUBE_CALIBRATED')
    .with_recipe('metis_ifu_calibrate')
    .with_main_input(ifu_sci_reduced)
    #.with_associated_input()
    .build())


lm_lss_synth_trans = (task('LM_LSS_SYNTH_TRANS')
    .with_recipe('metis_LM_lss_mf_calctrans')
    .with_main_input(mf_best_fit_tab)
    #.with_associated_input()
    .build())


n_lss_synth_trans = (task('N_LSS_SYNTH_TRANS')
    .with_recipe('metis_N_lss_mf_calctrans')
    .with_main_input(mf_best_fit_tab)
    #.with_associated_input()
    .build())


ifu_sci_coadd = (task('IFU_SCI_COADD')
    .with_recipe('metis_ifu_postprocess')
    .with_main_input(ifu_sci_cube_calibrated)
    #.with_associated_input()
    .build())


lm_lss_sci_flux_tellcorr_1d = (task('LM_LSS_SCI_FLUX_TELLCORR_1D')
    .with_recipe('metis_LM_lss_mf_correct')
    .with_main_input(lm_lss_sci_flux_1d)
    #.with_associated_input()
    .build())


n_lss_sci_flux_tellcorr_1d = (task('N_LSS_SCI_FLUX_TELLCORR_1D')
    .with_recipe('metis_N_lss_mf_correct')
    .with_main_input(n_lss_sci_flux_1d)
    #.with_associated_input()
    .build())


