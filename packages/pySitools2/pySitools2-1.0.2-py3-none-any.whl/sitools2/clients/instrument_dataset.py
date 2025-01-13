#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Nima TRAORE"

import datetime
from future.moves.urllib.error import HTTPError
from future.utils import viewitems
from os import path, mkdir
from sys import stdout

from sitools2.clients import medoc_config as cfg
from sitools2.core.dataset import Dataset


class SdoDataset(Dataset):
    """Class getting instance of the SDO (AIA and HMI) datasets.

    This class is inherited from the class Dataset which is a set of instances. The class SdoDataset is specially used
    to have an instance of the IDOC/MEDOC client dataset for the SDO (AIA and HMI) series.

    """
    def __init__(self, url):
        Dataset.__init__(self, url)


class InstrumentDataset(Dataset):
    """Class getting instance of the IDOC/MEDOC clients datasets.

    Data files are provided as a (TAR, ZIP or Tar.gz) file in the user current directory. If a downloading directory is
    specified by the user, then the (TAR, ZIP or Tar.gz) file is placed in that directory.

    This class is inherited from the class Dataset which is a set of instances. The class InstrumentDataset is specially
    used to have an instance of the IDOC/MEDOC client dataset such as: GAIA-DEM, EUV-SYN, SOHO and STEREO etc.

    Attributes defined here:
        download_type: downloading type
        filename: name of the (TAR, ZIP or Tar.gz) file
        target_dir: downloading directory

    Methods defined here:
        check_kwargs(): initializes some attributes of the class if a dictionary is provided as named parameters
        __getSelection__(): get a selection of data

    """
    def __init__(self, url):
        Dataset.__init__(self, url)
        self.filename = None
        self.target_dir = None
        self.download_type = "TAR"

    def check_kwargs(self, kwargs):
        """Initializes some attributes of the class.

        When a dictionary is provided as named parameters to the function, the method checks if each value of the given
        dictionary is in an allowed parameters list, then initializes some attributes of the class.

        Args:
            kwargs: a dictionary

        """
        params = getattr(cfg, 'INST_DATASET_ALLOWED_GETSELECTION_PARAMS')
        for key, value in viewitems(kwargs):
            if key not in params:
                raise ValueError("Error in search:\n%s entry for the __getSelection__ function is not allowed\n" % key)
            else:
                setattr(self, key.lower(), value)

    def __getSelection__(self, primary_key_list=None, filename=None, target_dir=None, dataset_id='', get_plugin_id=None,
                         **kwargs):
        """Gets a selection of data.

        If the argument filename is None, a default file name is defined.
        If the argument target_dir is None, then the user current directory is used as default output.
        If the argument target_dir is not a directory , a new directory is created with the target_dir value.

        Args:
            primary_key_list: list of primaries keys
            filename: name of the (TAR, ZIP or Tar.gz) file
            target_dir: downloading directory
            dataset_id: IDOC/MEDOC client datatset ID
            get_plugin_id: method returning IDOC/MEDOC client pluging ID
            kwargs: optional parameters

        Returns:
            (TAR, ZIP or Tar.gz) file

         """
        if primary_key_list is None:
            primary_key_list = []
        if filename is not None:
            self.filename = filename
        if target_dir is not None:
            self.target_dir = target_dir

        if self.download_type is None:
            self.download_type = "TAR"
        if self.download_type.upper() not in cfg.DOWNLOAD_TYPE_LIST:
            stdout.write("Error get_selection(): %s type not allowed\nOnly TAR, ZIP or Tar.gz is allowed for parameter "
                         "download_type" % self.download_type)

        self.check_kwargs(kwargs)

        if self.filename is None:
            self.filename = ("IAS_" + dataset_id + "_export_" +
                             datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H-%M-%S") + "." +
                             self.download_type.lower())
        if self.target_dir is not None:
            if not path.isdir(self.target_dir):
                stdout.write("Get file:\n'%s' directory does not exist.\nCreation directory in progress ...\n" %
                             self.target_dir)
                mkdir(self.target_dir)
            if self.target_dir[-1].isalnum():
                self.filename = self.target_dir + '/' + self.filename
            elif self.target_dir[-1] == '/':
                self.filename = self.target_dir + self.filename
            else:
                stdout.write("Error get_file():\nCheck the param target_dir, special char %s at the end of target_dir "
                             "is not allowed." % self.target_dir[-1])

        plugin_id = get_plugin_id(download_type=self.download_type)
        stdout.write("Download %s file in progress ...\n" % self.download_type.lower())

        try:
            Dataset.execute_plugin(self, plugin_name=plugin_id, pkey_values_list=primary_key_list,
                                   filename=self.filename)
        except HTTPError:
            stdout.write("Error downloading selection %s " % self.filename)
        else:
            stdout.write("Download selection %s completed\n" % self.filename)
