#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Nima TRAORE"

from collections import Counter
from future.moves.urllib.error import HTTPError
from sys import stdout

from sitools2.clients import medoc_config as cfg
from sitools2.clients.client_medoc import ClientMedoc
from sitools2.clients.sdo_data import SdoData
from sitools2.clients.instrument_dataset import SdoDataset
from sitools2.clients.instrument_dataset import InstrumentDataset
from sitools2.core.query import Query


class SdoClientMedoc(ClientMedoc):
    """Class giving easy way to interrogate IDOC/MEDOC sitools interface.

    SdoClientMedoc inherits from the ClientMedoc class which provides
    some generic methods to interact with sitools interface:
        - search() method is called to recover the (AIA or HMI) data list
            (the list of output data is defined in the configuration file
            as SDO_OUTPUT_OPTION_LIST: each element of the list can be
            commented or uncommented in order to customize the output)
        - get() method is called to download data files as TAR, ZIP or Tar.gz

    Attributes defined here:
        cadence: SDO (AIA or HMI) cadence
        dataset_data_class: name of the class defining the client data
        dataset_id: ID of the IDOC/MEDOC client
        dataset_uri: dataset URI
        keywords: list of keywords from the metadata to be outputted
        primary_key: dataset primary key
        series: SDO (AIA or HMI) series name
        recnum_list: list of recnums identifiers for given series

    Methods defined here:
        check_cadence(): check that the cadence is allowed
        check_keywords(): check that keywords are allowed
        check_series(): check that the series name is allowed
        check_wave(): check that the wavelengths are allowed
        get_class_name(): return the class name
        get_data_primary_key_list(): return primary key list
        get_dataset_target(): defines metadata dataset target
        get_item_file(): downloads files for each dataset object
        get_metadata_output(): get metadata output for given datataset keyword
        get_plugin_id(): return plugin ID
        metadata_info(): displays information concerning the dataset
        scan_datalist_server_and_recnum_list(): scan datalist, series, server and recnum_list
        sdo_metadata_search(): provides metadata information from IDOC/MEDOC server
        search(): return dataset objects

    Examples:
        >>> from sitools2 import SdoClientMedoc
        >>> from datetime import datetime
        >>> d1 = datetime(2020, 1, 15, 0, 0, 0)
        >>> d2 = datetime(2020, 1, 15, 2, 0, 0)
        >>> sdo = SdoClientMedoc()
        >>> sdo_data_list = sdo.search(DATES=[d1, d2],NB_RES_MAX=10)
        >>> sdo.get(DATA_LIST=sdo_data_list, TARGET_DIR='results', DOWNLOAD_TYPE='TAR')
        >>> keyword_list = ['recnum', 'sunum', 'date__obs', 'quality', 'cdelt1', 'cdelt2', 'crval1']
        >>> metadata_search = sdo.sdo_metadata_search(DATA_LIST=sdo_data_list, KEYWORDS=keyword_list)
        >>> for data in sdo_data_list:
        ...     data.get_file(target_dir='results_dir', segment=['image_lev1'])
        ...

    """
    def __init__(self, server=cfg.SITOOLS2_URL):
        """Constructor of the class SdoClientMedoc."""
        ClientMedoc.__init__(self, server)
        self.dataset_uri = ''
        self.dataset_id = "SDO"
        self.dataset_data_class = SdoData
        self.series = None
        self.cadence = None
        self.keywords = None
        self.recnum_list = None
        self.primary_key = ["recnum", "series_name"]

    @staticmethod
    def get_class_name():
        """Return the class name in string format."""
        return 'SdoClientMedoc'

    def check_wave(self, waves=None, series=cfg.SDO_SERIE_NAME["aia_lev1"]):
        """Checks that the wavelengths are allowed.

        When waves=None and series is equal one of the SDO(AIA or HMI)
        series, then SDO (AIA or HMI) default wavelengths list is
        returned. If waves=None and series!=None and series is different
        to SDO (AIA or HMI) series, then an error message is occurred.

        Args:
            waves: wavelengths
            series: series name

        Returns:
            [waves]

        """
        if waves is not None:
            self.waves = waves
        out_msg = "waves parameter not specified, %s default value is set : waves = %s\n"
        if self.waves is None:
            if series.startswith('hmi'):
                self.waves = cfg.HMI_ALLOWED_WAVE_LIST
                stdout.write(out_msg % ('hmi', cfg.HMI_ALLOWED_WAVE_LIST))
            else:
                self.waves = cfg.AIA_ALLOWED_WAVE_LIST
                stdout.write(out_msg % (cfg.SDO_SERIE_NAME["aia_lev1"], cfg.AIA_ALLOWED_WAVE_LIST))

        self.is_waves_int_xor_list_type()

        for wave in self.waves:
            if type(wave).__name__ != 'str':
                error_msg = ("Error in search():\nEntry type for waves element is %s\nlist element for waves "
                             "must be a string or int type" % type(wave).__name__)
                raise TypeError(error_msg)

            if wave not in cfg.AIA_ALLOWED_WAVE_LIST and wave not in cfg.HMI_ALLOWED_WAVE_LIST:
                error_msg = ("Error in search():\nwaves = %s not allowed\nwaves must be in list %s" %
                             (self.waves, cfg.AIA_ALLOWED_WAVE_LIST + cfg.HMI_ALLOWED_WAVE_LIST))
                raise ValueError(error_msg)

        return self.waves

    def check_series(self, series, waves):
        """Checks that the series is allowed.

        Args:
            series: SDO (AIA or HMI) series name
            waves: wavelengths of the series

        Returns:
            series

        """
        self.series = series
        if self.series is None:
            if '6173' in waves:
                raise ValueError("series parameter must be specified")
            else:
                self.series = cfg.SDO_SERIE_NAME["aia_lev1"]
                stdout.write("series parameter not specified, default "
                             "value is set : series = '%s'\n" % cfg.SDO_SERIE_NAME["aia_lev1"])
        if type(self.series).__name__ != 'str':
            raise TypeError("Error in search():\nentry type for series "
                            "is : %s\nseries must be a str type" % type(self.series).__name__)
        if self.series not in cfg.SDO_SERIE_NAME.values():
            raise ValueError("Error in search():\nseries = %s not allowed\nseries must be in list %s" %
                             (self.series, cfg.SDO_SERIE_NAME.values()))
        if self.series.startswith('hmi'):
            if waves != ['6173']:
                raise ValueError("waves value %s does not correspond to the series specified : %s " %
                                 (",".join(waves), self.series))
            if self.server.startswith('https://medoc-sdo'):
                raise ValueError("server %s only for %s data\n" % self.server, cfg.SDO_SERIE_NAME["aia_lev1"])

        return self.series

    def check_cadence(self, cadence):
        """Check that the cadence is allowed.

        Args:
            cadence: SDO (AIA or HMI) cadence value

        Returns:
            [cadence]

        """
        if cadence is not None:
            self.cadence = cadence

        if self.cadence is None:
            if self.series.startswith(cfg.SDO_SERIE_NAME["aia_lev1"]):
                self.cadence = ['1m']
                stdout.write(f"cadence parameter not specified, default value for {self.series} is set: cadence=[1m]\n")
            elif self.series.startswith('hmi'):
                self.cadence = ['12m']
                stdout.write(f"cadence parameter not specified, default value for {self.series} is set: cadence=[12m]\n"
                             )
        if type(self.cadence).__name__ == 'str':
            self.cadence = [self.cadence]
        if type(self.cadence).__name__ != 'list':
            raise ValueError("Entry type for cadence is : %s\ncadence must be a list or a string type" %
                             type(cadence).__name__)
        if len(self.cadence) != 1:
            raise ValueError("Error in search():\n%d elements specified for cadence\ncadence param must be "
                             "specified and be a list of only one element" % len(self.cadence))
        for cad_item in self.cadence:
            if cad_item not in cfg.ALLOWED_CADENCE_DICT.keys() and cad_item not in cfg.ALLOWED_CADENCE_DICT.values():
                raise ValueError("Error in search():\ncadence = %s not allowed\ncadence for %s must be in list:\n%s\n" %
                                 (cad_item, self.series, cfg.ALLOWED_CADENCE_DICT))
            elif cad_item in cfg.ALLOWED_CADENCE_DICT.values():
                self.cadence = [cad_item]
            else:
                cadence_value = cfg.ALLOWED_CADENCE_DICT[str(cad_item)]
                self.cadence = [cadence_value]

        return self.cadence

    def search(self, dates=None, waves=None,
               series=cfg.SDO_SERIE_NAME["aia_lev1"],
               cadence=None, nb_res_max=-1, **kwargs):
        """Search dataset objects.

        Uses the generic search() from PySitools2 library for Sitools2
        dataset instance located at IAS.

        Args:
            dates: interval dates for the research
            waves: wavelengths
            series: SDO (AIA or HMI) series name
            cadence: cadence of the SDO(AIA or HMI) series
            nb_res_max: maximum number of the result to be returned

        Returns:
             self.get_data_list(data_result)

        """
        self.series = series
        self.scan_kwargs(kwargs)
        self.check_server()
        dates_optim = self.get_dates_optim(dates)
        nb_res_max = self.check_nb_res_max(nb_res_max)
        wave_list = self.check_wave(waves, self.series)
        serie_name = self.check_series(self.series, wave_list)
        cadence_list = self.check_cadence(cadence)
        dataset = self.get_dataset_server(serie_name)

        dates_params = [[dataset.fields_dict['date__obs']], dates_optim, 'DATE_BETWEEN']
        waves_params = [[dataset.fields_dict['wavelnth']], wave_list, 'IN']
        serie_params = [[dataset.fields_dict['series_name']], [serie_name], 'IN']
        cadence_params = [[dataset.fields_dict['mask_cadence']], cadence_list, 'cadence']

        q1 = Query(dates_params)
        q2 = Query(waves_params)
        q3 = Query(serie_params)
        q4 = Query(cadence_params)
        query_list = [q1, q2, q3, q4]

        sort_options = [[dataset.fields_dict['date__obs'], 'ASC'], [dataset.fields_dict['wavelnth'], 'ASC']]

        out_opt_list = getattr(cfg, self.dataset_id + '_OUTPUT_OPTION_LIST')
        if serie_name.startswith('hmi.sharp'):
            out_opt_list.append('harpnum')
        output_options = [dataset.fields_dict[out_opt] for out_opt in out_opt_list]

        result = dataset.search(query_list, output_options, sort_options, limit_to_nb_res_max=nb_res_max)

        return self.get_data_list(result)

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
            if item.ias_location != '':
                item.get_file(target_dir=target_dir, **kwargs)
            else:
                stdout.write("The data for recnum %s is not at IAS\n" % str(item.recnum))

    def get_data_primary_key_list(self, data_list):
        """Return dataset objects primary key list.

        Args:
            data_list: list of dataset objects

        Returns:
            data_primary_key_list

        """
        data_primary_key_list = []
        for item in data_list:
            if item.ias_location != '':
                data_primary_key_list.append(getattr(item, self.primary_key[0]))
                data_primary_key_list.append(getattr(item, self.primary_key[1]))
            else:
                stdout.write("the data for recnum %s is not at IAS\n" % str(item.recnum))
        return data_primary_key_list

    def get_plugin_id(self, download_type=None):
        """return plugin ID

        Args:
            download_type: downloading type

        """
        if download_type.upper() in cfg.DOWNLOAD_TYPE_LIST:
            if self.series.startswith('aia'):
                self.plugin_id = 'pluginAIAtar'
            elif self.series.startswith('hmi'):
                self.plugin_id = 'pluginHMIIAS'

        return self.plugin_id

    def check_keywords(self):
        """Check that keywords are allowed"""
        if len(self.keywords) == 0:
            raise ValueError("keywords must be specified")
        if type(self.keywords).__name__ != 'list':
            raise TypeError("Error in metadata_search():\nentry type for keywords is: %s\nkeywords must be a list type"
                            % type(self.keywords).__name__)

        return 0

    def scan_datalist_server_and_recnum_list(self):
        """Scan datalist, series, server and recnum_list"""
        result = []
        if len(self.data_list) != 0:
            series_list = [item.series_name for item in self.data_list]
            count_series_list = Counter(series_list)
            if len(count_series_list.keys()) > 1:
                stdout.write("Several series_name detected in data_list\n")
                result = [item.metadata_search(self.keywords) for item in self.data_list]
            else:
                self.recnum_list = [item.recnum for item in self.data_list]
                self.series = self.data_list[0].series_name

        if self.series is None and len(self.data_list) == 0:
            raise ValueError("Error in sdo_metadata_search():\nseries parameter must be specified\n")

        self.check_server()

        if len(self.recnum_list) == 0:
            raise ValueError("Error in sdo_metadata_search():\nNo recnum_list provided\nPlease check your request\n")

        return result

    def get_dataset_target(self):
        """Defines metadata dataset target"""
        metadata_ds = None
        if self.server.startswith('https://idoc-medoc'):
            if self.series == cfg.SDO_SERIE_NAME["aia_lev1"]:
                metadata_ds = SdoDataset(self.server + "/" + cfg.AIA_LEV1_DATASET_ID)
            elif self.series.startswith('hmi'):
                metadata_ds = SdoDataset(self.server + "/webs_" + self.series + "_dataset")
        elif self.server.startswith('https://medoc-sdo'):
            metadata_ds = SdoDataset(self.server + "/" + cfg.SDO_AIA_LEV1_DATASET_ID)
        
        return metadata_ds

    def get_metadata_output(self, metadata_ds):
        """Get metadata output for given datataset keyword"""
        output_sdo = []
        for key in self.keywords:
            if key in metadata_ds.fields_dict:
                output_sdo.append(metadata_ds.fields_dict[key])
            else:
                error_msg = f"Error metadata_search(): {key} keyword does not exist for series : {self.series}\n"
                raise ValueError(error_msg)
        return output_sdo

    def sdo_metadata_search(self, data_list=None, series=None,
                            keywords=None, recnum_list=None, **kwargs):
        """Provides metadata information from IDOC/MEDOC server.

        Args:
            data_list: list of dataset objects
            series: SDO (AIA or HMI) series name
            keywords: list of keywords from the metadata to be outputted
            recnum_list: list of recnums identifiers for given series
            **kwargs: optional parameters

        Returns:
            {metadata}

        """
        if data_list is not None:
            self.data_list = data_list
        if series is not None:
            self.series = series
        if keywords is not None:
            self.keywords = keywords
        if recnum_list is not None:
            self.recnum_list = recnum_list

        self.scan_kwargs(
            kwargs, allowed_params=cfg.SDO_ALLOWED_METADATA_SEARCH_PARAMS)
        self.check_keywords()
        
        result = self.scan_datalist_server_and_recnum_list()
        if len(result) > 0:
            return result

        metadata_ds = self.get_dataset_target()
        output_sdo = self.get_metadata_output(metadata_ds)
        sort_sdo = [[metadata_ds.fields_dict['date__obs'], 'ASC']]

        result = []
        i = 0
        # Make a request for each 500 recnum
        if len(self.recnum_list) > 500:
            while i < len(self.recnum_list):
                recnum_sublist = self.recnum_list[i:i + 499]
                recnum_sublist = list(map(str, recnum_sublist))
                param_query_aia = [[metadata_ds.fields_dict['recnum']], recnum_sublist, 'IN']
                q_sdo = Query(param_query_aia)
                try:
                    result += metadata_ds.search([q_sdo], output_sdo, sort_sdo)
                except HTTPError:
                    print("\nmetadata_ds.search() failed please send an email to medoc-contact@ias.u-psud.fr")
                    raise
                i = i + 499
        else:
            recnum_sublist = list(map(str, self.recnum_list))
            param_query_aia = [[metadata_ds.fields_dict['recnum']], recnum_sublist, 'IN']
            q_sdo = Query(param_query_aia)
            try:
                result += metadata_ds.search([q_sdo], output_sdo, sort_sdo)
            except HTTPError:
                print("\nmetadata_ds.search() failed please send an email to medoc-contact@ias.u-psud.fr")
                raise

        return result

    def metadata_info(self, series=cfg.SDO_SERIE_NAME["aia_lev1"]):
        """Displays information concerning the specified dataset.

        Default value for the series parameter is 'aia.lev1'

        Args:
            series: SDO (AIA or HMI) series name

        """
        self.check_server()
        metadata_ds = None
        if self.server == 'https://idoc-medoc.ias.u-psud.fr' or self.server == 'https://idoc-medoc-test.ias.u-psud.fr':
            metadata_ds = InstrumentDataset(self.server + "/webs_" + series + "_dataset")
        elif self.server == 'https://medoc-sdo.ias.u-psud.fr' or self.server == 'https://medoc-sdo-test.ias.u-psud.fr':
            metadata_ds = InstrumentDataset(self.server + "/" + cfg.SDO_AIA_LEV1_DATASET_ID)

        return metadata_ds.display()
