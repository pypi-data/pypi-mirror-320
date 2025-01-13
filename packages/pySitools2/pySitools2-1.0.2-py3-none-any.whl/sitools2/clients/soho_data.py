#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Nima TRAORE"

from sitools2.clients import medoc_config as cfg
from sitools2.clients.data import Data


class SohoData(Data):
    """Class SohoData.

    Attributes defined here:
        datatype: type of the data
        date_end: end of observation in UTC
        date_obs: observation date in UTC
        detector: detector name
        download: URL of the data in the IDOC/MEDOC server
        filesize: size of the file
        id_sitools_view: ID of the sitools view
        instrument: instrument name
        jop: JOP
        obs_mode: mode of observation
        sci_obj: SCI obj
        slitwidth: width of the slit
        xcen: X cen
        ycen: Y cen
        wavemax: wave max
        wavemin: wave min
        wavetype: type of wave


    Methods defined here:
        compute_attributes(): computes attributes

    """
    def __init__(self, data, server=cfg.SITOOLS2_URL):
        Data.__init__(self, server)
        self.download = ''
        self.instrument = ''
        self.detector = ''
        self.date_obs = ''
        self.date_end = ''
        self.wavemin = 0.
        self.wavemax = 0.
        self.wavetype = ''
        self.sci_obj = ''
        self.obs_mode = ''
        self.jop = 0
        self.xcen = 0.
        self.ycen = 0.
        self.datatype = ''
        self.filesize = 0
        self.slitwidth = 0.
        self.id_sitools_view = ''
        self.compute_attributes(data)

    def compute_attributes(self, data):
        self.download = data['download_path']
        self.instrument = data['instrument']
        self.detector = data['detector']
        self.date_obs = data['date_obs']
        self.date_end = data['date_end']
        self.wavemin = data['wavemin']
        self.wavemax = data['wavemax']
        self.xcen = data['xcen']
        self.ycen = data['ycen']
        self.datatype = data['datatype']
        self.filesize = data['filesize']
        self.id_sitools_view = data['id_sitools_view']
        if 'obs_mode' in data:
            self.obs_mode = data['obs_mode']

    def display(self):
        print(self.__repr__())

    def __repr__(self):
        return ("download : %s, instrument : %s, detector : %s, date_obs : %s, date_end : %s, wavemin : %d, "
                "wavemax : %d, obs_mode : %s, xcen : %d, ycen : %d, datatype : %s, filesize : %d" %
                (self.download, self.instrument, self.detector, self.date_obs, self.date_end, self.wavemin,
                 self.wavemax, self.obs_mode, self.xcen, self.ycen, self.datatype, self.filesize))
