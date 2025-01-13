#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Nima TRAORE"

from sitools2.clients import medoc_config as cfg
from sitools2.clients.data import Data


class StereoData(Data):
    """Class StereoData.

    Attributes defined here:
        datatype: type of the data
        date_end: end of observation in UTC
        date_obs: observation date in UTC
        detector: detector name
        download: URL of the data in the IDOC/MEDOC server
        filesize: size of the file
        id_sitools_view: ID of the sitools view
        instrument: instrument name
        secchisata: state of SECCHISATA (TRUE or FALSE)
        secchisatb: state of SECCHISATB (TRUE or FALSE)
        slitwidth: width of the slit
        twin: (TRUE or FALSE)
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
        self.secchisata = False
        self.secchisatb = False
        self.twin = False
        self.date_obs = ''
        self.date_end = ''
        self.wavemin = 0.
        self.wavemax = 0.
        self.wavetype = ''
        self.xcen = 0.
        self.ycen = 0.
        self.filesize = 0
        self.id_sitools_view = ''
        self.compute_attributes(data)

    def compute_attributes(self, data):
        self.download = data['download_path']
        self.instrument = data['instrument']
        self.detector = data['detector']
        self.secchisata = data['secchisata']
        self.secchisatb = data['secchisatb']
        self.twin = data['twin']
        self.date_obs = data['date_obs']
        self.date_end = data['date_end']
        self.wavemin = data['wavemin']
        self.wavemax = data['wavemax']
        self.wavetype = data['wavetype']
        self.xcen = data['xcen']
        self.ycen = data['ycen']
        self.filesize = data['filesize']
        self.id_sitools_view = data['id_sitools_view']

    def display(self):
        print(self.__repr__())

    def __repr__(self):
        return ("download : %s, instrument : %s, detector : %s, secchisata : %s, secchisatb : %s, twin : %s, "
                "date_obs : %s, date_end : %s, wavemin : %d, wavemax : %d, wavetype : %s, xcen : %d, ycen : %d, "
                "filesize : %d" %
                (self.download, self.instrument, self.detector, self.secchisata, self.secchisatb, self.twin,
                 self.date_obs, self.date_end, self.wavemin, self.wavemax, self.wavetype, self.xcen, self.ycen,
                 self.filesize))
