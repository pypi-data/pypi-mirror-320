#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Nima TRAORE"

from future.moves.urllib.error import HTTPError
from future.moves.urllib.parse import urlencode
from future.moves.urllib.request import urlopen, urlretrieve
from os import path, mkdir
from simplejson import load
from sys import stdout

from sitools2.clients import medoc_config as cfg
from sitools2.clients.data import Data
from sitools2.clients.instrument_dataset import SdoDataset
from sitools2.core.query import Query


class SdoData(Data):
    """Class SdoData.

    Attributes defined here:
        date_obs: observation date in UTC
        exptime: exposure time
        harpnum: active region patch number for HMI sharp data
        ias_location: location of the data at IAS disks
        ias_path: URL of the data for SDO (AIA and HMI) series
        recnum: record number
        series_name: series name
        sunum: storage unit number
        t_rec_index: index of T_REC in database
        url: URL of the data from IDOC/MEDOC server
        wave: wavelength of the record

    Methods defined here:
        compute_attributes(): computes attributes
        get_file(): download AIA and HMI data from IDOC/MEDOC server
        get_filename_and_create_target_dir(): get filename and create downloading directory if it does not exist
        get_ias_path(): return ias_path
        get_metadata_dataset(): get dataset of the metadata regard to the server name
        is_keywords(): check that keywords is allowed
        load_url_build_seg(): loads url_build_seg and updates segment and segment_allowed values
        metadata_search(): provides metadata information from IDOC/MEDOC server
        scan_segment(): scans and defines segment if it does not exist

    """
    def __init__(self, data, server=cfg.SITOOLS2_URL):
        Data.__init__(self, server)
        self.url = ''
        self.recnum = 0
        self.sunum = 0
        self.date_obs = None
        self.series_name = ''
        self.wave = 0
        self.ias_location = ''
        self.ias_path = ''
        self.exptime = 0
        self.t_rec_index = 0
        self.harpnum = 0
        self.compute_attributes(data)

    def compute_attributes(self, data):
        if 'get' in data:
            self.url = data['get']
        elif 'ias_path' in data:
            self.url = data['ias_path']
        else:
            self.url = ''
        self.recnum = data['recnum']
        self.sunum = data['sunum']
        self.date_obs = data['date__obs']
        if 'series_name' in data:
            self.series_name = data['series_name']
        else:
            self.series_name = ''

        self.wave = data['wavelnth']
        if 'ias_location' in data:
            self.ias_location = data['ias_location']
        else:
            self.ias_location = ''
        if 'ias_path' in data:
            self.ias_path = data['ias_path']
        else:
            self.ias_path = ''
        if 'exptime' in data:
            self.exptime = data['exptime']
        else:
            self.exptime = 0
        self.t_rec_index = data['t_rec_index']
        if 'harpnum' in data:
            self.harpnum = data['harpnum']
        else:
            self.harpnum = 0

    def display(self):
        """Display a representation of SDO data from IDOC/MEDOC server

        Returns:
            print __repr__()

        """
        print(self.__repr__())

    def __repr__(self):
        if self.series_name.startswith('hmi.sharp'):
            return ("url : %s,recnum : %d, sunum : %d, series_name : %s, date_obs : %s, wave : %d, ias_location : %s, "
                    "exptime : %s, t_rec_index : %d, harpnum : %d, ias_path : %s\n" %
                    (self.url, self.recnum, self.sunum, self.series_name, self.date_obs, self.wave, self.ias_location,
                     self.exptime, self.t_rec_index, self.harpnum, self.ias_path))
        else:
            return ("url : %s,recnum : %d, sunum : %d, series_name : %s, date_obs : %s, wave : %d, ias_location : %s, "
                    "exptime : %s, t_rec_index : %d, ias_path : %s\n" %
                    (self.url, self.recnum, self.sunum, self.series_name, self.date_obs, self.wave, self.ias_location,
                     self.exptime, self.t_rec_index, self.ias_path))

    def get_ias_path(self):
        """Gets ias_path"""
        ias_path = ''

        if self.ias_path.endswith("/image_lev1.fits"):
            ias_path += self.ias_path.split("/image_lev1.fits")[0]
        else:
            ias_path = self.ias_path

        if not self.ias_path.startswith('https://'):
            ias_path = 'https://' + ias_path

        return ias_path

    def get_filename_and_create_target_dir(self, filename, target_dir):
        """Get filename and create downloading dir if does not exist"""
        filename_pre = ""
        str_date_format = '%Y-%m-%dT%H-%M-%S'
        if filename is None:
            if self.series_name == cfg.SDO_SERIE_NAME["aia_lev1"]:
                filename_pre = self.series_name + "_" + str(self.wave) + "A_" + self.date_obs.strftime(
                    str_date_format + '_' + str(self.recnum) + ".")
            elif self.series_name.startswith('hmi.shar'):
                filename_pre = self.series_name + "_" + str(self.wave) + "A_" + self.date_obs.strftime(
                    str_date_format + '_') + str(self.harpnum) + "."
            elif self.series_name.startswith('hmi'):
                filename_pre = self.series_name + "_" + str(self.wave) + "A_" + self.date_obs.strftime(
                    str_date_format + '.')
        else:
            stdout.write("filename defined by user : %s\n" % filename)
            filename_pre = path.splitext(filename)[0]
        
        if target_dir is not None:
            if not path.isdir(target_dir):
                stdout.write("Warning get_file(): '%s' directory does not exist.\nCreation of directory in "
                             "progress ... \n" % target_dir)
                mkdir(target_dir)
            if target_dir[-1].isalnum():
                filename_pre = target_dir + '/' + filename_pre
            elif target_dir[-1] == '/':
                filename_pre = target_dir + filename_pre
            else:
                raise ValueError("Error get_file()\nCheck the parameter target_dir, special char %s at the end "
                                 "of the target_dir is not allowed.\n" % target_dir[-1])

        return filename_pre

    @staticmethod
    def load_url_build_seg(url_build_seg, segment, segment_allowed, flag=False):
        """Load url_build_seg and update segment and segment_allowed"""
        fits_ext = ".fits"
        try:
            result = load(urlopen(url_build_seg))
        except HTTPError:
            stdout.write("HttpError exception unable to load url :\n %s" % url_build_seg)
        else:
            if result['items']:
                for item in result['items']:
                    if flag:
                        segment.append(item['name'].split(fits_ext)[0])
                        segment_allowed.append(item['name'].split(fits_ext)[0])
                    else:
                        segment_allowed.append(item['name'].split(fits_ext)[0])
            else:
                print("No key 'items' found for %s " % url_build_seg)
        return segment, segment_allowed

    def scan_segment(self, segment, filename, ias_path):
        """Scans and defines segment if it does not exist"""
        segment_allowed = []
        kwargs = {}
        url = ""
        str_hmi_sharp = 'hmi.sharp'
        if segment is None and filename is None:
            if self.series_name == cfg.SDO_SERIE_NAME["aia_lev1"]:
                segment = ['image_lev1']
                kwargs.update({'segment': ','.join(segment)})
                url = self.url + ';' + urlencode(kwargs)
                segment_allowed += ['image_lev1', "spikes"]
            elif self.series_name.startswith(str_hmi_sharp):
                segment = []
                kwargs.update({'media': 'json'})
                url = self.url + ';' + urlencode(kwargs)
                url_build_seg = ias_path + '/?' + urlencode(kwargs)
                segment, segment_allowed = self.load_url_build_seg(url_build_seg, segment, segment_allowed, flag=True)
            elif self.series_name.startswith('hmi.ic'):
                segment = ['continuum']
                kwargs.update({'segment': ",".join(segment)})
                url = self.url + str(self.harpnum) + ";" + urlencode(kwargs)
                segment_allowed.append('continuum')
            elif self.series_name.startswith('hmi.m'):
                segment = ['magnetogram']
                kwargs.update({'segment': ",".join(segment)})
                url = self.url + str(self.harpnum) + ";" + urlencode(kwargs)
                segment_allowed.append('magnetogram')
        elif segment is not None and filename is None:
            if self.series_name == cfg.SDO_SERIE_NAME["aia_lev1"]:
                kwargs.update({'segment': ','.join(segment)})
                segment_allowed += ['image_lev1', "spikes"]
                url = self.url + ';' + urlencode(kwargs)
                url_build_seg = ias_path + "/?" + "media=json"
                segment, segment_allowed = self.load_url_build_seg(url_build_seg, segment, segment_allowed)
            elif self.series_name.startswith(str_hmi_sharp):
                kwargs.update({'segment': ','.join(segment)})
                url = self.url + ';' + urlencode(kwargs)
                url_build_seg = ias_path + "/?" + "media=json"
                segment, segment_allowed = self.load_url_build_seg(url_build_seg, segment, segment_allowed)
        elif filename is not None:
            segment = [filename]
            kwargs.update({'segment': ','.join(segment)})
            url = self.url + ';' + urlencode(kwargs)

        return segment, segment_allowed, url

    def get_file(self, decompress=False, filename=None, target_dir=None, segment=None, **kwargs):
        """Download AIA and HMI data from IDOC/MEDOC server"""
        params_list = ['DECOMPRESS', 'FILENAME', 'TARGET_DIR', 'SEGMENT']
        kwg = self.check_kwargs(params_list, kwargs)
        if 'decompress' in kwg.keys():
            decompress = kwg['decompress']
        if 'filename' in kwg.keys():
            filename = kwg['filename']
        if 'target_dir' in kwg.keys():
            target_dir = kwg['target_dir']
        if 'segment' in kwg.keys():
            segment = kwg['segment']

        ias_path = self.get_ias_path()
        filename_pre = self.get_filename_and_create_target_dir(filename, target_dir)
        segment, segment_allowed, url = self.scan_segment(segment, filename, ias_path)

        # Specification for aia.lev1 and COMPRESS param
        if not decompress and self.series_name == cfg.SDO_SERIE_NAME["aia_lev1"]:
            url += ";compress=rice"

        fits_ext = ".fits"
        for seg in segment:
            if seg not in segment_allowed and filename is None:
                error_msg = ("%s segment value not allowed\nSegment allowed :%s" % (seg, segment_allowed))
                raise ValueError(error_msg)
            if filename is None:
                filename_path = filename_pre + seg + fits_ext
            else:
                filename_path = filename_pre + fits_ext

            try:
                urlretrieve(url, filename_path)
            except HTTPError:
                stdout.write("Error downloading %s\n" % filename_path)
                raise
            stdout.write("Download file %s completed\n" % filename_path)
            stdout.flush()

    @staticmethod
    def is_keywords(keywords):
        """Check that keywords is allowed"""
        if len(keywords) == 0:
            raise ValueError("keywords must be specified")
        if type(keywords).__name__ != 'list':
            raise TypeError("Error in metadata_search():\nentry type for keywords is: %s\nkeywords must be a list type"
                            % type(keywords).__name__)
        return True
    
    def get_metadata_dataset(self, server_url):
        """Get dataset of the metadata regard to the server name"""
        if server_url.startswith('https://idoc-medoc') or server_url.startswith('https://localhost'):
            metadata_ds = SdoDataset(server_url + "/webs_" + self.series_name + "_dataset")
        elif server_url.startswith('https://medoc-sdo'):
            metadata_ds = SdoDataset(server_url + "/" + cfg.SDO_AIA_LEV1_DATASET_ID)
        else:
            raise ValueError("metadata_ds is not valid, please check your server param\n")
        return metadata_ds

    def metadata_search(self, keywords=None, **kwargs):
        """Provides metadata information from IDOC/MEDOC server"""
        params_list = ['KEYWORDS']
        kwg = self.check_kwargs(params_list, kwargs)
        if 'keywords' in kwg.keys():
            keywords = kwg['keywords']

        server_url = cfg.SITOOLS2_URL
        if server_url not in cfg.ALLOWED_SERVER_LIST:
            raise ValueError("Server %s is not allowed \nServers available : %s\n" %
                             (server_url, cfg.ALLOWED_SERVER_LIST))

        self.is_keywords(keywords)
        metadata_ds = self.get_metadata_dataset(server_url)
        recnum_list = [str(self.recnum)]

        param_query = [[metadata_ds.fields_dict['recnum']], recnum_list, 'IN']
        query1 = Query(param_query)
        output1 = []
        for key in keywords:
            if key in metadata_ds.fields_dict:
                output1.append(metadata_ds.fields_dict[key])
            else:
                raise ValueError("Error metadata_search(): %s keyword does not exist for %s" % (key, metadata_ds.name))
        sort1 = [[metadata_ds.fields_dict['date__obs'], 'ASC']]

        if len(metadata_ds.search([query1], output1, sort1)) != 0:
            return metadata_ds.search([query1], output1, sort1)[0]
        else:
            raise ValueError("No data found for your request\nCheck your parameters")
