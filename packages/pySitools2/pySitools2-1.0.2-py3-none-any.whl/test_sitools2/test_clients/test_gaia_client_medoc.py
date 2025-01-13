#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__author__ = "Nima TRAORE"

from datetime import datetime
import os

from sitools2.clients.gaia_client_medoc import GaiaClientMedoc


class TestGaiaClientMedoc:
    """Tests the class GaiaClientMedoc methods.

    """
    def setup_method(self):
        """Setup method"""
        d1 = datetime(2012, 8, 10, 0, 0, 0)
        d2 = datetime(2012, 8, 11, 0, 0, 0)
        self.gaia = GaiaClientMedoc()
        self.gaia_data_list = self.gaia.search(dates=[d1, d2], nb_res_max=2)

    def test_get_class_name(self):
        """Tests get_class_name()"""
        assert 'GaiaClientMedoc' == self.gaia.get_class_name()

    def test_get_plugin_id(self):
        """Tests get_plugin_id()"""
        assert 'pluginGAIAtar' == self.gaia.get_plugin_id(download_type='tar')

    def test_get_plugin_id1(self):
        """Tests get_plugin_id()"""
        assert '' == self.gaia.get_plugin_id(download_type='')

    def test_search(self):
        """Tests search()"""
        gaia_data_list = self.gaia_data_list
        assert 2 == len(gaia_data_list)
        assert 349340243 == gaia_data_list[0].sunum_193
        assert datetime(2012, 8, 10, 0, 5, 1, 875) == gaia_data_list[0].date_obs
        assert 'DEM_aia_2012-08-10T00_05_' == gaia_data_list[0].filename

        assert 349344872 == gaia_data_list[1].sunum_193
        assert datetime(2012, 8, 10, 1, 5, 1, 877) == gaia_data_list[1].date_obs
        assert 'DEM_aia_2012-08-10T01_05_' == gaia_data_list[1].filename

    def test_get_item_file(self, tmp_path):
        """Tests get_item_file() """
        d = tmp_path / "results"
        d.mkdir()
        path = d / ""

        gaia_data_list = self.gaia_data_list
        self.gaia.get_item_file(data_list=gaia_data_list, target_dir=str(path))

        tmp_dir = str(path) + '/'
        tmp_file_list = os.listdir(tmp_dir)
        assert 8 == len(tmp_file_list)

    def test_get(self, tmp_path):
        """Tests get() """
        d = tmp_path / "results"
        d.mkdir()
        path = d / ""

        gaia_data_list = self.gaia_data_list
        self.gaia.get(data_list=gaia_data_list, download_type="tar", target_dir=str(path))

        tmp_dir = str(path) + '/'
        tmp_file_list = os.listdir(tmp_dir)
        assert 1 == len(tmp_file_list)
