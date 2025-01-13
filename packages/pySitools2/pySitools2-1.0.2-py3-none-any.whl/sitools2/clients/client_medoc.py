#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Nima TRAORE"

from collections import Counter
from future.moves.urllib.error import HTTPError
from future.utils import viewitems
from sys import stdout

from sitools2.clients import medoc_config as cfg
from sitools2.clients.instrument_dataset import SdoDataset
from sitools2.clients.instrument_dataset import InstrumentDataset
from sitools2.core.query import Query


class ClientMedoc:
    """Class giving easy way to interrogate IDOC/MEDOC sitools interface.

    ClientMedoc is designed to be a parent class for IDOC/MEDOC clients:
    EUV-SYN, GAIA-DEM, SDO, SOHO, STEREO etc. This class should not be
    instantiated but only its children ones. Depending on the client,
    the children class will 'None' some attributes and methods defined below.

    IDOC/MEDOC default server name is set when any server name is not provided by the user.

    Attributes defined here:
        data_list: list of the client data (dataset objects)
        dataset_data_class: name of the class defining the client data
        dataset_id: ID of the IDOC/MEDOC client
        dataset_uri: dataset URI
        dates: interval dates for the research
        detectors: instrument detectors of the client
        download_type: type of the download to be used (TAR, ZIP or Tar.gz)
        nb_res_max: maximum number of results to be returned
        plugin_id: client plugin ID to be used for downloading
        primary_key: dataset primary key
        server: name of the IDOC/MEDOC server
        target_dir: downloading directory (created if it doesn't exist yet)
        waves: wavelengths of the client

    Methods defined here:
        check_detector(): check that the detectors are allowed
        check_nb_res_max(): check that the provided number is allowed
        check_server(): check that the server name is allowed
        check_wave(): check that the wavelengths are allowed
        get_class_name(): return the class name
        get_data_list(): return data list (dataset objects)
        get_data_primary_key_list(): return primary key list
        get_dataset_server(): return dataset server name
        get_dates_optim(): return dates in format ['YYYY-MM-DDTHH:MN:SS.000', 'YYYY-MM-DDTHH:MN:SS.000']
        get_item_file(): virtual method
        get_plugin_id(): return plugin ID
        get_selection(): download a selection from IDOC/MEDOC server (TAR, ZIP or Tar.gz) file
        get(): downloads the researched dataset files
        is_waves_int_xor_list_type(): Checks that the wavelengths are an int or a list type
        scan_kwargs(): initialize some attributes of the class if a dictionary is provided as named parameters
        search(): return dataset objects


    """
    def __init__(self, server=cfg.SITOOLS2_URL):
        """Constructor of the class ClientMedoc"""
        self.server = server
        self.dataset_uri = ''
        self.dataset_id = None
        self.dataset_data_class = None
        self.dates = None
        self.waves = None
        self.nb_res_max = -1
        self.detectors = None
        self.data_list = None
        self.target_dir = None
        self.download_type = None
        self.primary_key = None
        self.plugin_id = ""

    @staticmethod
    def get_class_name():
        """Return the class name in string format"""
        return 'ClientMedoc'

    def scan_kwargs(self, kwargs, allowed_params=None):
        """Initializes some attributes of the class.

        When a dictionary is provided as named parameters to the function, the method checks if each value of the given
        dictionary is in an allowed parameters list, then initializes some attributes of the class.

        If the argument allowed_params is not provided, then default values of each client method is used.

        Args:
            kwargs: a dictionary
            allowed_params: allowed parameters list

        """
        if allowed_params is not None:
            params = allowed_params
        else:
            params = getattr(cfg, self.dataset_id+'_ALLOWED_SEARCH_PARAMS')
        for key, value in viewitems(kwargs):
            if key not in params:
                raise ValueError("Error in search:\n%s entry for the given function is not allowed\n" % key)
            else:
                setattr(self, key.lower(), value)

    def check_server(self, server=None):
        """Check that the server name is allowed.

        Args:
            server: server name

        Returns:
             0

        """
        if server is not None:
            self.server = server
        if self.server not in cfg.ALLOWED_SERVER_LIST:
            raise ValueError(f"Server {self.server} is not allowed\nAvailable servers: {cfg.ALLOWED_SERVER_LIST}\n")
        return 0

    def get_dates_optim(self, dates=None):
        """Reformat dates.

        Args:
            dates: interval dates for the research

        Returns:
            ['YYYY-MM-DDTHH:MN:SS.000', 'YYYY-MM-DDTHH:MN:SS.000']

        """
        dates_optim = []
        if dates is not None:
            self.dates = dates
        if self.dates is None:
            raise ValueError("Error in search():\ndates entry must be specified")
        if type(self.dates).__name__ != 'list':
            raise TypeError("Error in search():\nentry type for dates is : %s\ndates must be a list type" %
                            type(self.dates).__name__)
        if len(self.dates) != 2:
            raise ValueError("Error in search() : %d elements specified for dates\ndates param must be specified "
                             "and be a list of 2 elements" % len(self.dates))

        str_date_format = '%Y-%m-%dT%H:%M:%S'
        for date in self.dates:
            if type(date).__name__ != 'datetime':
                raise TypeError("Error in search() : type for dates element is %s\ndates list element must "
                                "be a datetime type" % type(date).__name__)
            else:
                if self.server.startswith('https://medoc-sdo'):
                    dates_optim.append(str(date.strftime(str_date_format)))
                else:
                    dates_optim.append(str(date.strftime(str_date_format)) + ".000")
        if self.dates[1] <= self.dates[0]:
            raise ValueError("Error in search():\nd1=%s\nd2=%s\nfor dates = [d1,d2], d2 should be > d1" %
                             (self.dates[1].strftime(str_date_format), self.dates[2].strftime(str_date_format)))
        return dates_optim

    def check_nb_res_max(self, nb_res_max=-1):
        """Check that the provided number is allowed.

        Args:
            nb_res_max: maximum number of results to be returned

        Returns:
            nb_res_max

        """
        if nb_res_max != -1:
            self.nb_res_max = nb_res_max
        if type(self.nb_res_max).__name__ != 'int':
            raise TypeError("Error in search():\nentry type for nb_res_max is : %s\nnb_res_max must be an int type" %
                            type(self.nb_res_max).__name__)
        if self.nb_res_max != -1 and self.nb_res_max < 0:
            raise ValueError(f"Error in search():\nnb_res_max = {self.nb_res_max} not allowed\nnb_res_max must be > 0")
        return self.nb_res_max

    def is_waves_int_xor_list_type(self, waves=None):
        """Checks that the wavelengths are an int or a list type"""
        if waves is not None:
            self.waves = waves

        if type(self.waves).__name__ == 'int':
            self.waves = [str(self.waves)]
        elif type(self.waves).__name__ == 'list':
            wave_type_list = [type(wave).__name__ for wave in self.waves]
            counter_wave_type_list = list(Counter(wave_type_list))
            if len(counter_wave_type_list) == 1 and counter_wave_type_list[0] == 'int':  # same type
                self.waves = [str(wave) for wave in self.waves]
            elif len(counter_wave_type_list) > 1:
                raise ValueError("waves parameter must have same type !\n")
        else:
            raise TypeError("Error in search():\nentry type for waves is: %s\nwaves must be a list or int type " %
                            type(self.waves).__name__)
        return True

    def check_wave(self, waves=None):
        """Checks that the wavelengths are allowed.

        When waves=None, then None is returned.

        Args:
            waves: wavelengths

        Returns:
            [waves]

        """
        if waves is not None:
            self.waves = waves

        if self.waves is None:
            return self.waves
        else:
            self.is_waves_int_xor_list_type()
            for wave in self.waves:
                if type(wave).__name__ != 'str':
                    raise TypeError("Error in search():\nEntry type for waves element is %s\nlist element for waves "
                                    "must be a string or int type" % type(wave).__name__)
                ds_wave = getattr(cfg, self.dataset_id + '_ALLOWED_WAVE_LIST')
                if wave not in ds_wave:
                    raise ValueError(f"Error in search():\nwaves= {wave} not allowed\nwaves must be in list {ds_wave}")
            return self.waves

    def check_detector(self, detectors=None):
        """Checks that the detectors are allowed.

        When detectors=None, then the client default detectors list is
        returned.

        Args:
            detectors: detectors of the instrument

        Returns:
            [detectors]

        """
        if detectors is not None:
            self.detectors = detectors
        if self.detectors is None:
            ds_adl = getattr(cfg, self.dataset_id + '_ALLOWED_DETECTOR_LIST')
            self.detectors = ds_adl
            stdout.write("detectors parameter not specified, default value is set : detectors = %s\n" % ds_adl)
        if type(self.detectors).__name__ == 'str':
            self.detectors = [self.detectors]
        elif type(self.detectors).__name__ == 'list':
            dt = [type(detector).__name__ for detector in self.detectors]
            counter_detectors_type_list = list(Counter(dt))
            if len(counter_detectors_type_list) > 1:
                raise ValueError("detectors parameter must have same type !\n")
        else:
            raise TypeError("Error in search():\nentry type for detectors is : %s\ndetectors must be a list type " %
                            type(self.detectors).__name__)

        for detector in self.detectors:
            if type(detector).__name__ != 'str':
                raise TypeError("Error in search():\nEntry type for detectors element is %s\nlist element "
                                "for detectors must be a string type" % type(detector).__name__)
            else:
                ds_adl = getattr(cfg, self.dataset_id + '_ALLOWED_DETECTOR_LIST')
                if detector not in ds_adl:
                    raise ValueError("Error in search():\ndetector = %s not allowed\ndetectors must be in list %s" %
                                     detectors, ds_adl)

        return self.detectors

    def get_dataset_server(self, series=None):
        """return name of the dataset server"""
        stdout.write(f"Loading client : {self.server}\n")
        if series is not None:
            if self.server.startswith('https://idoc-medoc'):
                if series.startswith('aia'):
                    self.dataset_uri = cfg.SDO_AIA_DATASET_ID
                    return SdoDataset(self.server + "/" + self.dataset_uri)
                elif series.startswith('hmi'):
                    self.dataset_uri = cfg.SDO_HMI_DATASET_ID
                    return SdoDataset(self.server + "/" + self.dataset_uri)
            elif self.server.startswith('https://localhost'):
                if series.startswith('aia'):
                    self.dataset_uri = cfg.AIA_LEV1_DATASET_ID
                    return SdoDataset(self.server + "/" + self.dataset_uri)
                elif series.startswith('hmi'):
                    self.dataset_uri = cfg.SDO_HMI_DATASET_ID
                    return SdoDataset(self.server + "/" + self.dataset_uri)
            elif self.server.startswith('https://medoc-sdo'):
                self.dataset_uri = cfg.SDO_DATASET_ID
                return InstrumentDataset(self.server + "/" + self.dataset_uri)
            else:
                raise ValueError(self.server + " is unknown")
        else:
            return InstrumentDataset(self.server+"/"+self.dataset_uri)

    def get_data_list(self, data_result):
        """Returns dataset objects list.

        Args:
            data_result: list of dataset objects

        Returns:
            data_list

        """
        data_list = []
        if len(data_result) != 0:
            for i, data in enumerate(data_result):
                data_list.append(self.dataset_data_class(data, self.server))
        stdout.write("%s results returned\n" % len(data_list))

        return data_list

    def search(self, dates=None, waves=None, detectors=None, nb_res_max=-1, **kwargs):
        """Search dataset objects.

        Uses the generic search() from PySitools2 library for Sitools2
        dataset instance located at IAS.

        Args:
            dates: interval dates for the research
            waves: wavelengths
            detectors: client instrument detectors list
            nb_res_max: maximum number of the result to be returned

        Returns:
             self.get_data_list(data_result)

        """
        self.scan_kwargs(kwargs)
        self.check_server()
        dates_optim = self.get_dates_optim(dates)
        nb_res_max = self.check_nb_res_max(nb_res_max)

        if self.get_class_name() == 'EuvsynClientMedoc':
            wave_list = self.check_wave(waves)
            dataset = self.get_dataset_server()

            dates_params = [[dataset.fields_dict['obs_date']], dates_optim, 'DATE_BETWEEN']
            waves_params = [[dataset.fields_dict['wavelength']], wave_list, 'IN']

            q1 = Query(dates_params)
            q2 = Query(waves_params)
            query_list = [q1, q2]

            sort_options = [[dataset.fields_dict['obs_date'], 'ASC'], [dataset.fields_dict['wavelength'], 'ASC']]
        elif self.get_class_name() == 'GaiaClientMedoc':
            dataset = self.get_dataset_server()
            dates_params = [[dataset.fields_dict['date_obs']], dates_optim, 'DATE_BETWEEN']

            q1 = Query(dates_params)
            query_list = [q1]

            sort_options = [[dataset.fields_dict['date_obs'], 'ASC']]
        elif self.get_class_name() == 'SohoClientMedoc' or self.get_class_name() == 'StereoClientMedoc':
            wave_list = self.check_wave(waves)
            detector_list = self.check_detector(detectors)
            dataset = self.get_dataset_server()

            dates_params = [[dataset.fields_dict['date_obs']], dates_optim, 'DATE_BETWEEN']
            detectors_params = [[dataset.fields_dict['detector']], detector_list, 'IN']

            if wave_list is not None:
                waves_params = [[dataset.fields_dict['wavemin']], wave_list, 'IN']
                q1 = Query(dates_params)
                q2 = Query(detectors_params)
                q3 = Query(waves_params)
                query_list = [q1, q2, q3]
            else:
                q1 = Query(dates_params)
                q2 = Query(detectors_params)
                query_list = [q1, q2]

            sort_options = [[dataset.fields_dict['date_obs'], 'ASC']]
        else:
            raise ValueError("Error calling the client: wrong Medoc client name.\n")

        out_opt_list = getattr(cfg, self.dataset_id + '_OUTPUT_OPTION_LIST')
        output_options = [dataset.fields_dict[out_opt] for out_opt in out_opt_list]

        result = dataset.search(query_list, output_options, sort_options, limit_to_nb_res_max=nb_res_max)

        return self.get_data_list(result)

    def get_data_primary_key_list(self, data_list):
        """Return dataset objects primary key list.

        Args:
            data_list: list of dataset objects

        Returns:
            data_primary_key_list

        """
        data_primary_key_list = []
        for item in data_list:
            data_primary_key_list.append(getattr(item, self.primary_key))

        return data_primary_key_list

    def get_plugin_id(self, download_type=None):
        """return plugin ID when download_type=='TAR' else return '' """
        if download_type.upper() in cfg.DOWNLOAD_TYPE_LIST:
            return self.plugin_id
        else:
            return ""

    def get_item_file(self, data_list=None, target_dir=None, **kwargs):
        """Virtual method (used by children class)"""
        pass

    def get(self, data_list=None, target_dir=None, download_type=None, **kwargs):
        """Downloads instrument data from IDOC/MEDOC server.

        Args:
            data_list: list of data objects
            target_dir: downloading directory
            download_type: type of the downloading (TAR, ZIP or Tar.gz)

        Returns:
            TAR, ZIP or Tar.gz file

        """
        if data_list is not None:
            self.data_list = data_list
        if target_dir is not None:
            self.target_dir = target_dir
        self.scan_kwargs(kwargs, allowed_params=cfg.ALLOWED_GET_PARAMS)
        if 'DATA_LIST' in kwargs:
            del kwargs['DATA_LIST']
        if len(self.data_list) == 0:
            raise ValueError('Nothing to download\n')
        if download_type is None:
            self.get_item_file(data_list=self.data_list, target_dir=self.target_dir, **kwargs)
        else:
            self.get_selection(data_list=self.data_list, target_dir=self.target_dir, download_type=download_type,
                               **kwargs)

    def get_selection(self, data_list=None, target_dir=None, download_type="TAR", **kwargs):
        """Downloads a selection from IDOC/MEDOC server TAR, ZIP or Tar.gz file.

        By default, the download_type is 'TAR'.

        Args:
            data_list : list of data objects
            target_dir : downloading directory
            download_type : type of the downloading (TAR, ZIP or Tar.gz)

        """
        if data_list is not None:
            self.data_list = data_list
        if target_dir is not None:
            self.target_dir = target_dir
        if download_type is not None:
            self.download_type = download_type
        self.scan_kwargs(kwargs, allowed_params=cfg.ALLOWED_GET_SELECTION_PARAMS)
        if 'DATA_LIST' in kwargs:
            del kwargs['DATA_LIST']
        if self.server not in cfg.ALLOWED_SERVER_LIST:
            raise ValueError("Server %s is not allowed for get_selection()\nAvailable servers %s :" %
                             (self.server, cfg.ALLOWED_SERVER_LIST))
        try:
            dataset = InstrumentDataset(self.server+"/"+self.dataset_uri)
        except HTTPError:
            raise HTTPError
        else:
            if len(self.data_list) == 0:
                raise ValueError("Nothing to download\n")
            data_pk_list = self.get_data_primary_key_list(self.data_list)
            dataset.download_type = self.download_type
            dataset.__getSelection__(primary_key_list=data_pk_list, target_dir=self.target_dir,
                                     dataset_id=self.dataset_id, get_plugin_id=self.get_plugin_id, **kwargs)
