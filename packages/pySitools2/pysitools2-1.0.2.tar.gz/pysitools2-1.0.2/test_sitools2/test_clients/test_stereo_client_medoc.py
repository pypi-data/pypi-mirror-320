#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__author__ = "Nima TRAORE"

from datetime import datetime
import os
import pytest

from sitools2.clients.stereo_client_medoc import StereoClientMedoc


class TestStereoClientMedoc:
    """Tests the class StereoClientMedoc methods.

    """
    def setup_method(self):
        """Setup method"""
        d1 = datetime(2014, 2, 20, 0, 0, 0)
        d2 = datetime(2014, 2, 20, 0, 6, 0)
        self.st = StereoClientMedoc()
        self.st_data_list = self.st.search(dates=[d1, d2], nb_res_max=12)

    def test_get_class_name(self):
        """Tests get_class_name()"""
        assert 'StereoClientMedoc' == self.st.get_class_name()

    def test_check_wave(self):
        """Tests check_wave()"""
        with pytest.raises(TypeError):
            assert self.st.check_wave(waves=[{0: '193'}, {1: '335'}])
        with pytest.raises(ValueError):
            assert self.st.check_wave(waves=['10', '11'])

    def test_check_detector(self):
        """Tests check_detector()"""
        detector_default_list = ['SECCHI/HI1', 'SECCHI/HI2', 'SECCHI/COR1', 'SECCHI/COR2', 'SECCHI/EUVI']
        assert detector_default_list == self.st.check_detector()

    def test_check_detector1(self):
        """Tests check_detector()"""
        detector_list = ['SECCHI/HI2', 'SECCHI/COR1', 'SECCHI/EUVI']
        assert detector_list == self.st.check_detector(detectors=['SECCHI/HI2', 'SECCHI/COR1', 'SECCHI/EUVI'])

    def test_get_plugin_id(self):
        """Tests get_plugin_id()"""
        assert 'pluginSTEREOtar' == self.st.get_plugin_id(download_type='tar')

    def test_get_plugin_id1(self):
        """Tests get_plugin_id()"""
        assert '' == self.st.get_plugin_id(download_type='')

    def test_search(self):
        """Tests search()"""
        st_data_list = self.st_data_list
        assert 9 == len(st_data_list)
        assert datetime(2014, 2, 20, 0, 5, 0) == st_data_list[0].date_obs
        assert datetime(2014, 2, 20, 0, 5, 1) == st_data_list[0].date_end
        assert 'SECCHI' == st_data_list[0].instrument
        assert 'SECCHI/COR1' == st_data_list[0].detector
        assert 547200 == st_data_list[0].filesize

        assert 't' == st_data_list[0].secchisata
        assert 'f' == st_data_list[0].secchisatb
        assert 't' == st_data_list[0].twin
        assert -50.1502260538 == st_data_list[0].xcen
        assert 76.8023088158 == st_data_list[0].ycen

        assert datetime(2014, 2, 20, 0, 5, 24) == st_data_list[5].date_obs
        assert datetime(2014, 2, 20, 0, 5, 25) == st_data_list[5].date_end
        assert 'SECCHI' == st_data_list[5].instrument
        assert 'SECCHI/COR1' == st_data_list[5].detector
        assert 54720 == st_data_list[5].filesize

        assert 't' == st_data_list[5].secchisata
        assert 'f' == st_data_list[5].secchisatb
        assert 'f' == st_data_list[5].twin
        assert -51.5174176022 == st_data_list[5].xcen
        assert 75.0328075059 == st_data_list[5].ycen

    def test_get(self, tmp_path):
        """Tests get() """
        d = tmp_path / "results"
        d.mkdir()
        path = d / ""

        st_data_list = self.st_data_list
        self.st.get(data_list=st_data_list, download_type="tar", target_dir=str(path))

        tmp_dir = str(path) + '/'
        tmp_file_list = os.listdir(tmp_dir)
        assert 1 == len(tmp_file_list)
