#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__author__ = "Nima TRAORE"

from datetime import datetime
import pytest

from sitools2.clients.client_medoc import ClientMedoc
from sitools2.clients.instrument_dataset import InstrumentDataset


class TestClientMedoc:
    """Tests the class ClientMedoc methods.

    """
    def setup_method(self):
        """Setup method"""
        self.d1 = datetime(2020, 1, 1, 0, 0, 0)
        self.d2 = datetime(2020, 1, 1, 2, 12, 0)
        self.cm = ClientMedoc()

    def test_get_class_name(self):
        """Tests get_class_name()"""
        assert 'ClientMedoc' == self.cm.get_class_name()

    def test_scan_kwargs(self):
        """Tests scan_kwargs()"""
        params_list = ['DATES', 'WAVES', 'SERIES',
                       'DETECTORS', 'NB_RES_MAX']
        kwargs = {'DATES': [self.d1, self.d2],
                  'WAVES': ['94', '131', '304'],
                  'DETECTORS': ['TOTO/TITI1', 'TOTO/TITI2',
                                'TOTO/TITI3', 'TOTO/TITI4'],
                  'NB_RES_MAX': 4}

        self.cm.scan_kwargs(kwargs, allowed_params=params_list)

        assert [self.d1, self.d2] == self.cm.dates
        assert ['94', '131', '304'] == self.cm.waves
        assert ['TOTO/TITI1', 'TOTO/TITI2',
                'TOTO/TITI3', 'TOTO/TITI4'] == self.cm.detectors
        assert 4 == self.cm.nb_res_max

    def test_check_server(self):
        """Tests check_server()"""
        assert 0 == self.cm.check_server()

    def test_check_server1(self):
        """Tests check_server()"""
        with pytest.raises(ValueError):
            assert self.cm.check_server(server='toto')

    def test_get_dates_optim(self):
        """Tests get_dates_optim()"""
        date1 = self.d1.strftime("%Y-%m-%dT%H:%M:%S.000")
        date2 = self.d2.strftime("%Y-%m-%dT%H:%M:%S.000")

        assert [date1, date2] == self.cm.get_dates_optim(dates=[self.d1,
                                                                self.d2])
        assert [self.d1, self.d2] == self.cm.dates

    def test_check_nb_res_max(self):
        """Tests check_nb_res_max()"""
        assert 3 == self.cm.check_nb_res_max(nb_res_max=3)
        assert 3 == self.cm.nb_res_max

    def test_is_waves_int_xor_list_type(self):
        """Tests waves_is_int_or_list_type()"""
        assert self.cm.is_waves_int_xor_list_type(waves=94) is True
        assert self.cm.is_waves_int_xor_list_type(
            waves=['131', '304', '1700']) is True
        with pytest.raises(ValueError):
            assert self.cm.is_waves_int_xor_list_type(waves=[94, '131'])
        with pytest.raises(TypeError):
            assert self.cm.is_waves_int_xor_list_type(waves={131})

    def test_check_wave(self):
        """Tests check_wave()"""
        with pytest.raises(TypeError):
            assert self.cm.check_wave(waves=[{0: '193'}, {1: '335'}])
        with pytest.raises(TypeError):
            # A TypeError exception is raised here because ClientMedoc
            # dataset_id=None (and cfg allowed waves values are strings)
            assert self.cm.check_wave(waves=['193', '335'])

    def test_check_detector(self):
        """Tests check_detector()"""
        with pytest.raises(TypeError):
            assert self.cm.check_detector(detectors=['dtt', 'dt1'])

    def test_get_dataset_server(self):
        """Tests get_dataset_server()"""
        self.cm.dataset_uri = 'webs_STEREO_dataset'
        assert isinstance(self.cm.get_dataset_server(),
                          InstrumentDataset)

    def test_get_plugin_id(self):
        """Tests get_plugin_id()"""
        assert self.cm.get_plugin_id(download_type='tar') == ""

    def test_get_plugin_id1(self):
        """Tests get_plugin_id()"""
        assert '' == self.cm.get_plugin_id(download_type='')
