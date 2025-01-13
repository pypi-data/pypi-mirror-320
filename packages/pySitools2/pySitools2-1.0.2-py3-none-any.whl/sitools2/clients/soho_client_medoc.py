#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Nima TRAORE"

from sitools2.clients import medoc_config as cfg
from sitools2.clients.client_medoc import ClientMedoc
from sitools2.clients.soho_data import SohoData


class SohoClientMedoc(ClientMedoc):
    """Class giving easy way to interrogate IDOC/MEDOC sitools interface.

    SohoClientMedoc inherits from the ClientMedoc class which provides
    some generic methods to interact with sitools interface:
        - search() method is called to recover the data list (the list of output data is defined in the configuration
            file as SOHO_OUTPUT_OPTION_LIST: each element of the list can be commented or uncommented in order to
            customize the output)
        - get() method is called to download data files as TAR, ZIP or Tar.gz

    Attributes defined here:
        dataset_data_class: name of the class defining the client data
        dataset_id: ID of the IDOC/MEDOC client
        dataset_uri: dataset URI
        plugin_id: client plugin ID to be used for downloading
        primary_key: dataset primary key

    Methods defined here:
        get_class_name(): return the class name

    Examples:
        >>> from sitools2 import SohoClientMedoc
        >>> from datetime import datetime
        >>> d1 = datetime(2015, 3, 31, 0, 0, 0)
        >>> d2 = datetime(2015, 4, 1, 0, 0, 0)
        >>> soho = SohoClientMedoc()
        >>> soho_data_list = soho.search(DATES=[d1, d2], NB_RES_MAX=12)
        >>> soho.get(DATA_LIST=soho_data_list, TARGET_DIR='soho_results', DOWNLOAD_TYPE='TAR')

    """
    def __init__(self, server=cfg.SITOOLS2_URL):
        """Constructor of the class SohoClientMedoc"""
        ClientMedoc.__init__(self, server)
        self.dataset_uri = cfg.SOHO_DATASET_ID
        self.dataset_id = "SOHO"
        self.dataset_data_class = SohoData
        self.primary_key = 'id_sitools_view'
        self.plugin_id = "pluginSOHOtar"

    @staticmethod
    def get_class_name():
        """Return the class name in string format"""
        return 'SohoClientMedoc'
