#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration file for IDOC/MEDOC specialized clients

"""

__author__ = "Nima TRAORE"

# Default name of the IDOC/MEDOC server
SITOOLS2_URL = "https://idoc-medoc.ias.u-psud.fr"

# Allowed servers list of IDOC/MEDOC web interface
ALLOWED_SERVER_LIST = ['https://idoc-medoc.ias.u-psud.fr',
                       'https://idoc-medoc-test.ias.u-psud.fr',
                       'https://localhost:8184',
                       'https://medoc-sdo.ias.u-psud.fr',
                       'https://medoc-sdo-test.ias.u-psud.fr']

# Type of the download to be used
DOWNLOAD_TYPE_LIST = ['TAR', 'ZIP', 'TAR.GZ']

# Allowed series name for SDO (AIA and HMI) client
SDO_SERIE_NAME = {"aia_lev1": 'aia.lev1',
                  "hmi_ic_720s": 'hmi.ic_720s',
                  "hmi_ic_nolimbdark_720s": 'hmi.ic_nolimbdark_720s',
                  "hmi_ic_nolimbdark_720s_nrt": 'hmi.ic_nolimbdark_720s_nrt',
                  "hmi_m_720s": 'hmi.m_720s',
                  "hmi_m_720s_nrt": 'hmi.m_720s_nrt',
                  "hmi_sharp_720s": 'hmi.sharp_720s',
                  "hmi_sharp_720s_nrt": 'hmi.sharp_720s_nrt',
                  "hmi_sharp_cea_720s": 'hmi.sharp_cea_720s',
                  "hmi_sharp_cea_720s_nrt": 'hmi.sharp_cea_720s_nrt'}

# Allowed cadence values for SDO (AIA and HMI) client
ALLOWED_CADENCE_DICT = {'12s': '12 sec', '1m': '1 min', '2m': '2 min', '10m': '10 min', '12m': '12 min',
                        '30m': '30 min', '1h': '1 h', '2h': '2 h', '6h': '6 h', '12h': '12 h', '1d': '1 day'}

# Allowed waves list for SDO AIA series ('aia.lev1')
AIA_ALLOWED_WAVE_LIST = ['94', '131', '171', '193', '211', '304', '335', '1600', '1700']

# Allowed waves list for SDO HMI series
HMI_ALLOWED_WAVE_LIST = ['6173']

# Allowed waves list for EUV-SYN
EUVSYN_ALLOWED_WAVE_LIST = ['171', '195', '284', '304']

# Allowed waves list for SOHO EIT instrument
SOHO_ALLOWED_WAVE_LIST = ['171', '195', '284', '304']

# Allowed waves list for STEREO EUVI instrument
STEREO_ALLOWED_WAVE_LIST = ['171', '195', '284', '304']

# Allowed detectors list for SOHO client
SOHO_ALLOWED_DETECTOR_LIST = ['CDS/NIS', 'CDS/GIS', 'CELIAS/CTOF', 'CELIAS/DPU', 'CELIAS/HSTOF', 'CELIAS/MTOF',
                              'CELIAS/PM', 'CELIAS/SEM', 'CELIAS/STOF', 'COSTEP/EPHIN', 'COSTEP/LION', 'COSTEP/N/A',
                              'EIT/EIT', 'ERNE/HED', 'ERNE/LED', 'ERNE/N/A', 'GOLF', 'LASCO/C1', 'LASCO/C2', 'LASCO/C3',
                              'LASCO/N/A', 'MDI/MDI', 'SUMER/A', 'SUMER/B', 'SUMER/N/A', 'SUMER/RSC', 'SWAN/N/A',
                              'SWAN/-Z', 'SWAN/+Z', 'SWAN/+Z-Z', 'UVCS/LYA', 'UVCS/OVI', 'UVCS/VLD', 'VIRGO/DIARAD',
                              'VIRGO/LOI', 'VIRGO/N/A', 'VIRGO/PMOD', 'VIRGO/SPM']

# Allowed detectors list for STEREO client
STEREO_ALLOWED_DETECTOR_LIST = ['SECCHI/HI1', 'SECCHI/HI2', 'SECCHI/COR1', 'SECCHI/COR2', 'SECCHI/EUVI']

# Allowed parameters which can be given as args in search() method
# for EUV-SYN client
EUVSYN_ALLOWED_SEARCH_PARAMS = ['DATES', 'WAVES', 'NB_RES_MAX']

# Allowed parameters which can be given as args in search() method
# for GAIA-DEM client
GAIA_ALLOWED_SEARCH_PARAMS = ['DATES', 'NB_RES_MAX']

# Allowed parameters which can be given as args in search() method
# for SDO client
SDO_ALLOWED_SEARCH_PARAMS = ['SERIES', 'DATES', 'WAVES', 'CADENCE', 'NB_RES_MAX']

# Allowed parameters which can be given as args in search() method
# for SOHO client
SOHO_ALLOWED_SEARCH_PARAMS = ['DATES', 'WAVES', 'DETECTORS', 'NB_RES_MAX']

# Allowed parameters which can be given as args in search() method
# for STEREO client
STEREO_ALLOWED_SEARCH_PARAMS = ['DATES', 'WAVES', 'DETECTORS', 'NB_RES_MAX']

# Allowed parameters which can be given as args in get() method
# for all clients
ALLOWED_GET_PARAMS = ['DATA_LIST', 'TARGET_DIR', 'DOWNLOAD_TYPE']

# Allowed parameters which can be given as args in getSelection() method
# for all clients
ALLOWED_GET_SELECTION_PARAMS = ['DATA_LIST', 'TARGET_DIR', 'DOWNLOAD_TYPE']

# Allowed parameters which can be given as args in sdo_metadata_search()
# method for SDO clients
SDO_ALLOWED_METADATA_SEARCH_PARAMS = ['KEYWORDS', 'RECNUM_LIST', 'SERIES', 'DATA_LIST']

# Allowed parameters which can be given as args in __getSelection__()
# method for all clients
INST_DATASET_ALLOWED_GETSELECTION_PARAMS = ['FILENAME', 'TARGET_DIR', 'DOWNLOAD_TYPE']

# List of output options for the EUV-SYN dataset
EUVSYN_OUTPUT_OPTION_LIST = ['preview', 'download', 'obs_date', 'wavelength', 'index', 'filename', 'crea_date']

# List of output options for the GAIA-DEM dataset
GAIA_OUTPUT_OPTION_LIST = ['download', 'date_obs', 'sunum_193', 'filename',
                           'temp_fits_rice', 'em_fits_rice',
                           'width_fits_rice', 'chi2_fits_rice']

# List of output options for the SDO dataset
SDO_OUTPUT_OPTION_LIST = ['get', 'recnum', 'sunum', 'series_name',
                          'date__obs', 'wavelnth', 'ias_location',
                          'exptime', 't_rec_index', 'ias_path']

# List of output options for the SOHO dataset
SOHO_OUTPUT_OPTION_LIST = ['download_path', 'instrument', 'detector', 'date_obs', 'date_end', 'wavemin', 'wavemax',
                           'obs_mode', 'xcen', 'ycen', 'datatype', 'filesize', 'id_sitools_view']

# List of output options for the STEREO dataset
STEREO_OUTPUT_OPTION_LIST = ['download_path', 'instrument', 'detector', 'secchisata', 'secchisatb', 'twin', 'date_obs',
                             'date_end', 'wavemin', 'wavemax', 'wavetype', 'xcen', 'ycen', 'filesize', 'id_sitools_view'
                             ]

# Dataset ID (URI) for the IDOC/MEDOC specialized clients
AIA_LEV1_DATASET_ID = 'webs_aia.lev1_dataset'
CORONAS_F_DATASET_ID = 'webs_CORONAS-F_dataset'
EUV_SYN_DATASET_ID = 'webs_EUV-SYN_dataset'
GAIA_DEM_DATASET_ID = 'webs_GAIA-DEM_dataset'
PICARD_DATASET_ID = 'webs_PICARD_dataset'
SDO_AIA_DATASET_ID = 'webs_IAS_SDO_AIA_dataset'
SDO_HMI_DATASET_ID = 'webs_IAS_SDO_HMI_dataset'
SOHO_DATASET_ID = 'webs_SOHO_dataset'
STEREO_DATASET_ID = 'webs_STEREO_dataset'
TRACE_DATASET_ID = 'webs_TRACE_dataset'

# medoc-sdo.ias.u-psud.fr old interface
SDO_AIA_LEV1_DATASET_ID = 'webs_aia_dataset'
SDO_DATASET_ID = 'webs_IAS_SDO_dataset'
