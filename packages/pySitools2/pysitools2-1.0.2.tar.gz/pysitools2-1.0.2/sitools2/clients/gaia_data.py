#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Nima TRAORE"

from future.moves.urllib.error import HTTPError
from future.moves.urllib.request import urlretrieve
from future.utils import viewitems
from os import path, mkdir
from sys import stdout

from sitools2.clients import medoc_config as cfg
from sitools2.clients.data import Data


class GaiaData(Data):
    """Class GaiaData.

    Attributes defined here:
        chi2_fits_rice_uri: URI of the Chi2 image preview
        date_obs: observation date in UTC
        download: URL of the data in the IDOC/MEDOC server
        em_fits_rice_uri: URI of the emission image preview
        filename: file name containing DEM_aia_$date_obs
        sunum_193: ID of the sunum to be build
        temp_fits_rice_uri: URI of the temperature image preview
        width_fits_rice_uri: URI of the width image preview

    Methods defined here:
        compute_attributes(): computes attributes
        download_file(): download files
        get_file(): download GAIA-DEM data from IDOC/MEDOC server
        get_filename_dict(): get file name in dictionary type
        optimize_target_dir(): optimize downloading directory name
        scan_filename(): scan the arg to get file name in dictionary type
        scan_filetype(): scan the arg to get file name in dictionary type

    """
    def __init__(self, data, server=cfg.SITOOLS2_URL):
        Data.__init__(self, server)
        self.download = ''
        self.sunum_193 = 0
        self.date_obs = ''
        self.filename = ''
        self.temp_fits_rice_uri = ''
        self.em_fits_rice_uri = ''
        self.width_fits_rice_uri = ''
        self.chi2_fits_rice_uri = ''
        self.compute_attributes(data)

        self.url_dict = {'temp': self.temp_fits_rice_uri,
                         'em': self.em_fits_rice_uri,
                         'width': self.width_fits_rice_uri,
                         'chi2': self.chi2_fits_rice_uri}

    def compute_attributes(self, data):
        self.download = data['download']
        self.sunum_193 = data['sunum_193']
        self.date_obs = data['date_obs']
        self.filename = data['filename']
        self.temp_fits_rice_uri = data['temp_fits_rice']
        self.em_fits_rice_uri = data['em_fits_rice']
        self.width_fits_rice_uri = data['width_fits_rice']
        self.chi2_fits_rice_uri = data['chi2_fits_rice']

    def display(self):
        print(self.__repr__())

    def __repr__(self):
        return ("sunum_193 : %d, date_obs : %s, download : %s, filename : %s,\ntemp_fits_rice : %s,\nem_fits_rice : %s,"
                "\nwidth_fits_rice : %s,\nchi2_fits_rice : %s\n" %
                (self.sunum_193, self.date_obs, self.download, self.filename, self.temp_fits_rice_uri,
                 self.em_fits_rice_uri, self.width_fits_rice_uri, self.chi2_fits_rice_uri))

    def get_filename_dict(self):
        """Gets filename in dictionary type"""
        filename_dict = {}
        for value in self.url_dict.values():
            key = value.split("/")[-1]
            value = self.server + value
            filename_dict[key] = value
        return filename_dict

    def scan_filetype(self, filetype):
        """Scan the given argument to get filename in dictionary type"""
        filename_dict = {}
        for t_spec in filetype:
            if t_spec not in self.url_dict.keys() and t_spec != 'all':
                raise ValueError("Error get_file():\nfilename = %s entry for the get function is not allowed\n"
                                 "filetype value should be in list: 'temp', 'em', 'width', 'chi2', 'all'\n" % filetype)
            elif t_spec == 'all':
                filename_dict = self.get_filename_dict()
            else:
                key = self.url_dict[t_spec].split("/")[-1]
                value = self.server + self.url_dict[t_spec]
                filename_dict[key] = value
        return filename_dict

    def scan_filename(self, filename):
        """Scan the given argument to get filename in dictionary type"""
        filename_dict = {}
        for key, value in viewitems(filename):
            if key not in self.url_dict.keys():
                raise ValueError("Error get_file():\nfiletype = %s entry for the get function is not allowed\n"
                                 "filetype value should be in list: 'temp', 'em','width','chi2'\n" % key)
            else:
                f_key = filename[key]
                f_value = self.server + self.url_dict[f_key]
                filename_dict[f_key] = f_value
        return filename_dict

    @staticmethod
    def optimize_target_dir(target_dir):
        """Optimizes downloading directory"""
        if target_dir is not None:
            if not path.isdir(target_dir):
                stdout.write("Error get_file():\n'%s' directory does not exist.\nCreation directory in progress ..." %
                             target_dir)
                mkdir(target_dir)
            if target_dir[-1].isalnum():
                target_dir = target_dir + '/'
            else:
                stdout.write("Error get_file():\nCheck the param target_dir, special char %s at the end of target_dir "
                             "is not allowed." % target_dir[-1])
        else:
            target_dir = ""
        return target_dir

    @staticmethod
    def download_file(filename_dict, target_dir):
        """Downloads files.

        Args:
            filename_dict: filename in dictionary type
            target_dir: downloading directory

        Returns:
            Downloads files into target_dir

        """
        for (item, url) in viewitems(filename_dict):
            try:
                urlretrieve(url, "%s%s" % (target_dir, item))
            except HTTPError:
                stdout.write("Error downloading %s%s \n" % (target_dir, item))
            else:
                stdout.write("Download file %s%s completed\n" % (target_dir, item))
                stdout.flush()

    def get_file(self, filename=None, target_dir=None, filetype=None, **kwargs):
        """Download GAIA-DEM data from IDOC/MEDOC server"""
        params_list = ['FILENAME', 'TARGET_DIR', 'TYPE']
        kwg = self.check_kwargs(params_list, kwargs)
        if 'filename' in kwg.keys():
            filename = kwg['filename']
        if 'target_dir' in kwg.keys():
            target_dir = kwg['target_dir']
        if 'filetype' in kwg.keys():
            filetype = kwg['filetype']

        if filetype is not None and type(filetype).__name__ != 'list':
            raise ValueError("Error get_file():\nfiletype should be a list\n")

        if filename is None:
            if filetype is None:
                filename_dict = self.get_filename_dict()
            else:
                filename_dict = self.scan_filetype(filetype)
        else:
            if type(filename).__name__ != 'dict':
                raise ValueError("Error get_file():\nfilename should be a dictionary\n")
            elif filetype is not None:
                raise ValueError("Error get_file():\nfilename : %s\nfiletype : %s\nfilename and filetype are both "
                                 "specified at the same time\nNot allowed please remove one\n" % (filename, filetype))
            else:
                filename_dict = self.scan_filename(filename)

        target_dir = self.optimize_target_dir(target_dir)
        self.download_file(filename_dict, target_dir)
