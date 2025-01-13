#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__author__ = "Nima TRAORE"

from sitools2.clients.euvsyn_data import EuvsynData


class TestEuvsynData:
    """Tests the class EuvsynData methods.

    """
    def test_compute_attributes(self):
        """Tests compute_attributes()"""
        data = {'preview': 'http://idoc-medoc-test.ias.u-psud.fr/...fts.jpg',
                'download': 'http://idoc-medoc-test.ias.u-psud.fr/...fts',
                'index': 2635,
                'filename': 'syn171/syn171_20040302.005959_efz20040302.010014.fts',
                'crea_date': '2014-01-08T00:00:00.000',
                'obs_date': '2004-03-02T00:00:00.000',
                'wavelength': 171}
        esd = EuvsynData(data)
        assert data['preview'] == esd.preview
        assert data['download'] == esd.download
        assert data['index'] == esd.index
        assert data['filename'] == esd.filename
        assert data['crea_date'] == esd.crea_date
        assert data['obs_date'] == esd.date_obs
        assert data['wavelength'] == esd.wave
