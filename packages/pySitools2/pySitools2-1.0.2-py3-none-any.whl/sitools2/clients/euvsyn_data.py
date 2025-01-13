#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Nima TRAORE"

from sitools2.clients import medoc_config as cfg
from sitools2.clients.data import Data


class EuvsynData(Data):
    """Class EuvsynData.

    Attributes defined here:
        crea_date: creation date
        date_obs: observation date in UTC
        download: URL of the data in the IDOC/MEDOC server
        filename: file name
        index: index
        preview: data preview
        wave: wavelength

    Methods defined here:
        compute_attributes(): computes attributes

    """
    def __init__(self, data, server=cfg.SITOOLS2_URL):
        Data.__init__(self, server)
        self.preview = ''
        self.download = ''
        self.date_obs = ''
        self.wave = 0
        self.index = 0
        self.filename = ''
        self.crea_date = ''
        self.compute_attributes(data)

    def compute_attributes(self, data):
        self.preview = data['preview']
        self.download = data['download']
        self.date_obs = data['obs_date']
        self.wave = data['wavelength']
        self.index = data['index']
        self.filename = data['filename']
        self.crea_date = data['crea_date']

    def display(self):
        print(self.__repr__())

    def __repr__(self):
        return ("preview : %s, download : %s, date_obs : %s, wave : %d, "
                % (self.preview, self.download, self.date_obs, self.wave))
