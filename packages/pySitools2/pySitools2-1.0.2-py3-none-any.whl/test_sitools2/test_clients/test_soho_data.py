#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__author__ = "Nima TRAORE"

from datetime import datetime

from sitools2.clients.soho_data import SohoData


class TestSohoData:
    """Tests the class SohoData methods.

    """
    def test_compute_attributes(self):
        """Tests compute_attributes()"""
        data = {'download_path': 'http://idoc-medoc.ias.u-psud.fr/...fts',
                'instrument': 'LASCO',
                'detector': 'LASCO/C2',
                'date_obs': datetime(2014, 1, 1, 0, 0, 6),
                'date_end': datetime(2014, 1, 1, 0, 0, 31),
                'wavemin': 0.0,
                'wavemax': 0.0,
                'obs_mode': 'Normal',
                'xcen': 0.0,
                'ycen': 0.0,
                'datatype': 'IMG',
                'id_sitools_view': '15587299',
                'filesize': 2108160}
        sd = SohoData(data)
        assert data['download_path'] == sd.download
        assert data['instrument'] == sd.instrument
        assert data['detector'] == sd.detector
        assert data['date_obs'] == sd.date_obs
        assert data['date_end'] == sd.date_end
        assert data['wavemin'] == sd.wavemin
        assert data['wavemax'] == sd.wavemax
        assert data['obs_mode'] == sd.obs_mode
        assert data['xcen'] == sd.xcen
        assert data['ycen'] == sd.ycen
        assert data['datatype'] == sd.datatype
        assert data['filesize'] == sd.filesize
        # assert data['id_sitools_view'] == sd.id_sitools_view
