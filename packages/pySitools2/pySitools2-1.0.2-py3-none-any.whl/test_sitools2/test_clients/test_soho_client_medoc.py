#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__author__ = "Nima TRAORE"

from datetime import datetime
import os
import pytest

from sitools2.clients.soho_client_medoc import SohoClientMedoc


class TestSohoClientMedoc:
    """Tests the class SohoClientMedoc methods.

    """

    def setup_method(self):
        """Setup method."""
        d1 = datetime(2014, 1, 1, 0, 0, 0)
        d2 = datetime(2014, 1, 1, 0, 30, 0)
        self.sh = SohoClientMedoc()
        self.soho_data_list = self.sh.search(dates=[d1, d2], nb_res_max=12)

    def test_get_class_name(self):
        """Tests get_class_name()"""
        assert 'SohoClientMedoc' == self.sh.get_class_name()

    def test_check_wave(self):
        """Tests check_wave()"""
        with pytest.raises(TypeError):
            assert self.sh.check_wave(waves=[{0: '193'}, {1: '335'}])
        with pytest.raises(ValueError):
            assert self.sh.check_wave(waves=['10', '11'])

    def test_check_detector(self):
        """Tests check_detector()"""
        detector_default_list = [
            'CDS/NIS', 'CDS/GIS', 'CELIAS/CTOF', 'CELIAS/DPU',
            'CELIAS/HSTOF', 'CELIAS/MTOF', 'CELIAS/PM', 'CELIAS/SEM',
            'CELIAS/STOF', 'COSTEP/EPHIN', 'COSTEP/LION', 'COSTEP/N/A',
            'EIT/EIT', 'ERNE/HED', 'ERNE/LED', 'ERNE/N/A', 'GOLF',
            'LASCO/C1', 'LASCO/C2', 'LASCO/C3', 'LASCO/N/A', 'MDI/MDI',
            'SUMER/A', 'SUMER/B', 'SUMER/N/A', 'SUMER/RSC', 'SWAN/N/A',
            'SWAN/-Z', 'SWAN/+Z', 'SWAN/+Z-Z', 'UVCS/LYA', 'UVCS/OVI',
            'UVCS/VLD', 'VIRGO/DIARAD', 'VIRGO/LOI', 'VIRGO/N/A',
            'VIRGO/PMOD', 'VIRGO/SPM'
        ]
        assert detector_default_list == self.sh.check_detector()

    def test_check_detector1(self):
        """Tests check_detector()"""
        detector_list = ['CELIAS/CTOF', 'LASCO/C3', 'VIRGO/LOI']
        assert detector_list == self.sh.check_detector(detectors=['CELIAS/CTOF', 'LASCO/C3', 'VIRGO/LOI'])

    def test_get_plugin_id(self):
        """Tests get_plugin_id()"""
        assert 'pluginSOHOtar' == self.sh.get_plugin_id(download_type='tar')

    def test_get_plugin_id1(self):
        """Tests get_plugin_id()"""
        assert '' == self.sh.get_plugin_id(download_type='')

    def test_search(self):
        """Tests search()"""
        soho_data_list = self.soho_data_list
        assert 5 == len(soho_data_list)
        assert datetime(2014, 1, 1, 0, 0, 6) == soho_data_list[0].date_obs
        assert datetime(2014, 1, 1, 0, 0, 31) == soho_data_list[0].date_end
        assert 'LASCO' == soho_data_list[0].instrument
        assert 'LASCO/C2' == soho_data_list[0].detector
        assert 2108160 == soho_data_list[0].filesize

        assert 0.0 == soho_data_list[0].slitwidth
        assert 0.0 == soho_data_list[0].wavemax
        assert 0.0 == soho_data_list[0].wavemin
        assert 0.0 == soho_data_list[0].xcen
        assert 0.0 == soho_data_list[0].ycen

        assert datetime(2014, 1, 1, 0, 18, 5) == soho_data_list[3].date_obs
        assert datetime(2014, 1, 1, 0, 18, 22) == soho_data_list[3].date_end
        assert 'LASCO' == soho_data_list[3].instrument
        assert 'LASCO/C3' == soho_data_list[3].detector
        assert 2108160 == soho_data_list[3].filesize

        assert 0.0 == soho_data_list[3].slitwidth
        assert 0.0 == soho_data_list[3].wavemin
        assert 0.0 == soho_data_list[3].wavemax
        assert 0.0 == soho_data_list[3].xcen
        assert 0.0 == soho_data_list[3].ycen

    def test_get(self, tmp_path):
        """Tests get() """
        d = tmp_path / "results"
        d.mkdir()
        path = d / ""

        soho_data_list = self.soho_data_list
        self.sh.get(data_list=soho_data_list, download_type="tar", target_dir=str(path))

        tmp_dir = str(path) + '/'
        tmp_file_list = os.listdir(tmp_dir)
        assert 1 == len(tmp_file_list)
