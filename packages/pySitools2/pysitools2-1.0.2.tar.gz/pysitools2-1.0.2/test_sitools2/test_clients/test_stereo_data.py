#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__author__ = "Nima TRAORE"

from datetime import datetime

from sitools2.clients.stereo_data import StereoData


class TestStereoData:
    """Tests the class StereoData methods.

    """
    def test_compute_attributes(self):
        """Tests compute_attributes()"""
        data = {'download_path': 'http://idoc-medoc-test.ias.u-psud.fr/...fts',
                'instrument': 'SECCHI',
                'detector': 'SECCHI/COR1',
                'secchisata': 't',
                'secchisatb': 'f',
                'twin': 't',
                'date_obs': datetime(2014, 2, 20, 0, 5),
                'date_end': datetime(2014, 2, 20, 0, 5, 1),
                'wavemin': 0.0,
                'wavetype': '',
                'xcen': -50.1502260538,
                'ycen': 76.8023088158,
                'filesize': 547200,
                'id_sitools_view': '5437501',
                'wavemax': 0.0}
        strd = StereoData(data)
        assert data['download_path'] == strd.download
        assert data['instrument'] == strd.instrument
        assert data['detector'] == strd.detector
        assert data['secchisata'] == strd.secchisata
        assert data['secchisatb'] == strd.secchisatb
        assert data['twin'] == strd.twin
        assert data['date_obs'] == strd.date_obs
        assert data['date_end'] == strd.date_end
        assert data['wavemin'] == strd.wavemin
        assert data['wavetype'] == strd.wavetype
        assert data['xcen'] == strd.xcen
        assert data['ycen'] == strd.ycen
        assert data['filesize'] == strd.filesize
        # assert data['id_sitools_view'] == strd.id_sitools_view
        assert data['wavemax'] == strd.wavemax
