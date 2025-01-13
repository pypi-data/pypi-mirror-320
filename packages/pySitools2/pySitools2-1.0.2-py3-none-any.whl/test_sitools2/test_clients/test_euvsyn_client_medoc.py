#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__author__ = "Nima TRAORE"

from datetime import datetime
import os
import pytest

from sitools2.clients.euvsyn_client_medoc import EuvsynClientMedoc


class TestEuvsynClientMedoc:
    """Tests the class EuvsynClientMedoc methods.

    """
    def setup_method(self):
        """Setup method"""
        d1 = datetime(2004, 3, 1, 0, 0, 0)
        d2 = datetime(2004, 3, 5, 0, 0, 0)
        self.euvs = EuvsynClientMedoc()
        self.euvsyn_data_list = self.euvs.search(dates=[d1, d2], nb_res_max=12)
    
    def test_get_class_name(self):
        """Tests get_class_name()"""
        assert 'EuvsynClientMedoc' == self.euvs.get_class_name()

    def test_check_wave(self):
        """Tests check_wave()"""
        with pytest.raises(TypeError):
            assert self.euvs.check_wave(waves=[{0: '193'}, {1: '335'}])
        with pytest.raises(ValueError):
            assert self.euvs.check_wave(waves=['193', '335'])

    def test_get_plugin_id(self):
        """Tests get_plugin_id()"""
        assert 'pluginEITSYNtar' == self.euvs.get_plugin_id(
            download_type='tar')

    def test_get_plugin_id1(self):
        """Tests get_plugin_id()"""
        assert '' == self.euvs.get_plugin_id(download_type='')
        
    def test_search(self):
        """Tests search()"""
        date_obs = datetime(2004, 3, 4, 0, 0, 0).strftime("%Y-%m-%dT%H:%M:%S.000")

        euvsyn_data_list = self.euvsyn_data_list
        assert ['171', '195', '284', '304'] == self.euvs.waves
        assert 12 == len(euvsyn_data_list)

        assert date_obs == euvsyn_data_list[10].date_obs
        assert 284 == euvsyn_data_list[10].wave

        assert date_obs == euvsyn_data_list[11].date_obs
        assert 304 == euvsyn_data_list[11].wave

    def test_get(self, tmp_path):
        """Tests get() """
        d = tmp_path / "results"
        d.mkdir()
        path = d / ""

        euvsyn_data_list = self.euvsyn_data_list
        self.euvs.get(data_list=euvsyn_data_list, download_type="tar", target_dir=str(path))

        tmp_dir = str(path) + '/'
        tmp_file_list = os.listdir(tmp_dir)
        assert 1 == len(tmp_file_list)
