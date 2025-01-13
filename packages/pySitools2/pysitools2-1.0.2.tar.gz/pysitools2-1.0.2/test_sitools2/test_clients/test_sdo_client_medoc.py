#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__author__ = "Nima TRAORE"

from datetime import datetime
import os
import pytest

from sitools2.clients.sdo_client_medoc import SdoClientMedoc


class TestSdoClientMedoc:
    """Tests the class SdoClientMedoc methods.

    """
    def setup_method(self):
        """Setup method."""
        d1 = datetime(2016, 1, 1, 0, 0, 0)
        d2 = datetime(2016, 1, 1, 5, 12, 0)
        self.sdo = SdoClientMedoc()
        self.sdo_data_list = self.sdo.search(dates=[d1, d2], waves=[335, 193], cadence=['1m'], nb_res_max=2)

    def test_get_class_name(self):
        """Tests get_class_name()"""
        assert 'SdoClientMedoc' == self.sdo.get_class_name()

    def test_check_wave(self):
        """Tests check_wave()"""
        aia_wave_list = ['94', '131', '171', '193', '211', '304', '335', '1600', '1700']
        scm = SdoClientMedoc()
        assert aia_wave_list == scm.check_wave(series='aia.lev1')
        scm = SdoClientMedoc()
        assert aia_wave_list == scm.check_wave(waves=None, series='aia.lev1')
        scm = SdoClientMedoc()
        assert ['6173'] == scm.check_wave(series='hmi_720s')
        scm = SdoClientMedoc()
        assert ['6173'] == scm.check_wave(waves=None, series='hmi_720s')
        scm = SdoClientMedoc()
        assert ['193', '335'] == scm.check_wave(waves=['193', '335'])

        with pytest.raises(ValueError):
            assert scm.check_wave(waves=['15'])

    def test_check_series(self):
        """Tests check_series()"""
        assert 'aia.lev1' == self.sdo.check_series(None, '')

    def test_check_series1(self):
        """Tests check_series()"""
        assert 'hmi.m_720s' == self.sdo.check_series('hmi.m_720s', ['6173'])

    def test_check_cadence(self):
        """Tests check_cadence()"""
        self.sdo.series = 'aia.lev1'
        assert ['1 min'] == self.sdo.check_cadence(None)

    def test_check_cadence1(self):
        """Tests check_cadence()"""
        self.sdo = SdoClientMedoc()
        self.sdo.series = 'hmi.m_720s'
        assert ['12 min'] == self.sdo.check_cadence(None)

    def test_get_data_primary_key_list(self):
        """Tests get_data_primary_key_list()"""
        sdo_data_list = self.sdo_data_list
        assert [171963897, 'aia.lev1', 171963899, 'aia.lev1'] == self.sdo.get_data_primary_key_list(sdo_data_list)

    def test_get_plugin_id(self):
        """Tests get_plugin_id()"""
        self.sdo.series = 'aia.lev1'
        assert 'pluginAIAtar' == self.sdo.get_plugin_id(download_type='tar')

    def test_get_plugin_id1(self):
        """Tests get_plugin_id()"""
        self.sdo.series = 'hmi.m_720s'
        assert 'pluginHMIIAS' == self.sdo.get_plugin_id(download_type='tar')

    def test_get_plugin_id2(self):
        """Tests get_plugin_id()"""
        assert '' == self.sdo.get_plugin_id(download_type='')

    def test_search(self):
        """Tests search()"""
        sdo_data_list = self.sdo_data_list
        assert 2 == len(sdo_data_list)
        assert 'aia.lev1' == sdo_data_list[0].series_name
        assert 171963897 == sdo_data_list[0].recnum
        assert 775321065 == sdo_data_list[0].sunum
        assert datetime(2016, 1, 1, 0, 0, 13, 627) == sdo_data_list[0].date_obs
        assert 335 == sdo_data_list[0].wave
        assert '/SUM12/D775321065' == sdo_data_list[0].ias_location
        assert 2.900809 == pytest.approx(sdo_data_list[0].exptime)
        assert 1230681651 == sdo_data_list[0].t_rec_index

        assert 171963899 == sdo_data_list[1].recnum
        assert 775321055 == sdo_data_list[1].sunum
        assert datetime(2016, 1, 1, 0, 0, 17, 836) == sdo_data_list[1].date_obs
        assert 193 == sdo_data_list[1].wave

    def test_sdo_metadata_search(self):
        """Tests sdo_metadata_search()"""
        sdo_data_list = self.sdo_data_list
        my_meta_search = self.sdo.sdo_metadata_search(
            keywords=['date__obs', 'quality', 'cdelt1', 'cdelt2', 'crval1', 'sunum', 'recnum'],
            data_list=sdo_data_list)
        assert 171963897 == my_meta_search[0]['recnum']
        assert 775321065 == my_meta_search[0]['sunum']
        assert 1230681649.6275153 == my_meta_search[0]['date__obs']
        assert 0 == my_meta_search[0]['quality']
        assert 0.600737 == my_meta_search[0]['cdelt1']
        assert 0.600737 == my_meta_search[0]['cdelt2']
        assert 0.0 == my_meta_search[0]['crval1']

        assert 171963899 == my_meta_search[1]['recnum']
        assert 775321055 == my_meta_search[1]['sunum']
        assert 1230681653.8368313 == my_meta_search[1]['date__obs']

    def test_get(self, tmp_path):
        """Tests get() """
        d = tmp_path / "results"
        d.mkdir()
        path = d / ""

        sdo_data_list = self.sdo_data_list
        self.sdo.get(data_list=sdo_data_list, download_type="tar", target_dir=str(path))

        tmp_dir = str(path) + '/'
        tmp_file = os.listdir(tmp_dir)
        assert 1 == len(tmp_file)

    def test_get_item_file(self, tmp_path):
        """Tests get_item_file() """
        d = tmp_path / "results"
        d.mkdir()
        path = d / ""

        sdo_data_list = self.sdo_data_list
        self.sdo.get_item_file(data_list=sdo_data_list, target_dir=str(path), segment=['image_lev1'])

        tmp_dir = str(path) + '/'
        tmp_file = os.listdir(tmp_dir)
        assert 2 == len(tmp_file)
