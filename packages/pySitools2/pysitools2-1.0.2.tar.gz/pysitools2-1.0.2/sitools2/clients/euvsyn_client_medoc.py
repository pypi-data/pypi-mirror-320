#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Nima TRAORE"

from sys import stdout

from sitools2.clients import medoc_config as cfg
from sitools2.clients.client_medoc import ClientMedoc
from sitools2.clients.euvsyn_data import EuvsynData


class EuvsynClientMedoc(ClientMedoc):
    """Class giving easy way to interrogate IDOC/MEDOC sitools interface.

    EuvsynClientMedoc inherits from the ClientMedoc class which provides
    some generic methods to interact with sitools interface:
        - search() method is called to recover the data list (the list of output data is defined in the configuration
            file as EUVSYN_OUTPUT_OPTION_LIST: each element of the list can be commented or uncommented in order to
            customize the output)
        - get() method is called to download data files as TAR, ZIP or Tar.gz

    Attributes defined here:
        dataset_data_class: name of the class defining the client data
        dataset_id: ID of the IDOC/MEDOC client
        dataset_uri: dataset URI
        plugin_id: client plugin ID to be used for downloading
        primary_key: dataset primary key

    Methods defined here:
        check_wave(): checks that the wavelengths are allowed
        get_class_name(): return the class name

    Examples:
        >>> from sitools2 import EuvsynClientMedoc
        >>> from datetime import datetime
        >>> d1 = datetime(2009, 7, 6, 0, 0, 0)
        >>> d2 = datetime(2009, 7, 10, 0, 0, 0)
        >>> euvsyn = EuvsynClientMedoc()
        >>> euvsyn_data_list = euvsyn.search(DATES=[d1, d2], NB_RES_MAX=10)
        >>> euvsyn.get(DATA_LIST=euvsyn_data_list, TARGET_DIR='results', DOWNLOAD_TYPE='TAR')

    """
    def __init__(self, server=cfg.SITOOLS2_URL):
        """Constructor of the class EuvsynClientMedoc."""
        ClientMedoc.__init__(self, server)
        self.dataset_uri = cfg.EUV_SYN_DATASET_ID
        self.dataset_id = "EUVSYN"
        self.dataset_data_class = EuvsynData
        self.primary_key = 'index'
        self.plugin_id = "pluginEITSYNtar"

    @staticmethod
    def get_class_name():
        """Return the class name in string format."""
        return 'EuvsynClientMedoc'

    def check_wave(self, waves=None):
        """Checks that the wavelengths are allowed.

        When waves=None, then default wavelengths list is returned.

        Args:
            waves: wavelengths

        Returns:
            [waves]

        """
        if waves is not None:
            self.waves = waves

        if self.waves is None:
            ds_wave = getattr(cfg, self.dataset_id+'_ALLOWED_WAVE_LIST')
            self.waves = ds_wave
            stdout.write("waves parameter not specified, %s default value is set : waves = %s\n" %
                         (self.dataset_id, ds_wave))

        self.is_waves_int_xor_list_type()

        for wave in self.waves:
            if type(wave).__name__ != 'str':
                raise TypeError("Error in search():\nEntry type for waves element is %s\nlist element for waves "
                                "must be a string or int type" % type(wave).__name__)
            ds_wave = getattr(cfg, self.dataset_id + '_ALLOWED_WAVE_LIST')
            if wave not in ds_wave:
                raise ValueError(f"Error in search():\nwaves = {wave} not allowed\nwaves must be in list {ds_wave}")

        return self.waves
