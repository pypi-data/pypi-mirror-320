#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Nima TRAORE"

from sitools2.clients import medoc_config as cfg
from sitools2.clients.client_medoc import ClientMedoc
from sitools2.clients.gaia_data import GaiaData


class GaiaClientMedoc(ClientMedoc):
    """Class giving easy way to interrogate IDOC/MEDOC sitools interface.

    GaiaClientMedoc inherits from the ClientMedoc class which provides
    some generic methods to interact with sitools interface:
        - search() method is called to recover the data list (the list of output data is defined in the configuration
            file as GAIA_OUTPUT_OPTION_LIST: each element of the list can be commented or uncommented in order to
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
        get_item_file(): downloads files for each dataset object

    Examples:
        >>> from sitools2 import GaiaClientMedoc
        >>> from datetime import datetime
        >>> d1 = datetime(2019, 9, 2, 0, 0, 0)
        >>> d2 = datetime(2019, 9, 3, 0, 0, 0)
        >>> gaia = GaiaClientMedoc()
        >>> gaia_data_list = gaia.search(DATES=[d1, d2], NB_RES_MAX=10)
        >>> gaia.get(DATA_LIST=gaia_data_list, TARGET_DIR='results', DOWNLOAD_TYPE='TAR')
        >>> for data in gaia_data_list:
        ...     data.get_file(TARGET_DIR='results1')
        ...

    """
    def __init__(self, server=cfg.SITOOLS2_URL):
        """Constructor of the class GaiaClientMedoc."""
        ClientMedoc.__init__(self, server)
        self.dataset_uri = cfg.GAIA_DEM_DATASET_ID
        self.dataset_id = "GAIA"
        self.dataset_data_class = GaiaData
        self.primary_key = 'sunum_193'
        self.plugin_id = "pluginGAIAtar"

    @staticmethod
    def get_class_name():
        """Return the class name in string format"""
        return 'GaiaClientMedoc'

    def get_item_file(self, data_list=None, target_dir=None, **kwargs):
        """Downloads files for each dataset object.

        Args:
            data_list: dataset objects list
            target_dir: downloading directory
            **kwargs: optional args

        Returns:
            files

        """
        for item in data_list:
            item.get_file(target_dir=target_dir, **kwargs)
