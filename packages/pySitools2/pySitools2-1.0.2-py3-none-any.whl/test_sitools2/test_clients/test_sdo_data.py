#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__author__ = "Nima TRAORE"

from datetime import datetime
import pytest

from sitools2.clients.sdo_data import SdoData


class TestSdoData:
    """Tests the class SdoData methods.

    """
    def setup_method(self):
        """Setup method"""
        self.data = {'get': 'https://sdo.ias.u-psud.fr/SDO/...1230681651',
                     'recnum': 171963897,
                     'sunum': 775321065,
                     'series_name': 'aia.lev1',
                     'date__obs': datetime(2016, 1, 1, 0, 0, 13, 627),
                     'wavelnth': 335,
                     'ias_location': '/SUM12/D775321065',
                     'exptime': 2.9008089999999997,
                     't_rec_index': 1230681651,
                     'ias_path': 'https://idoc-medoc.ias.u-psud.fr//s.../S00000'}
        self.sdd = SdoData(self.data)

    def test_compute_attributes(self):
        """Tests compute_attributes()"""
        data = self.data
        sdd = self.sdd
        assert data['get'] == sdd.url
        assert data['recnum'] == sdd.recnum
        assert data['sunum'] == sdd.sunum
        assert data['series_name'] == sdd.series_name
        assert data['date__obs'] == sdd.date_obs
        assert data['wavelnth'] == sdd.wave
        assert data['exptime'] == sdd.exptime
        assert data['t_rec_index'] == sdd.t_rec_index
        assert data['ias_location'] == sdd.ias_location

    def test_compute_attributes_1(self):
        """Tests compute_attributes()"""
        new_data = {'recnum': 171963898,
                    'sunum': 775321066,
                    'date__obs': datetime(2000, 1, 1, 0, 0, 0, 000),
                    'wavelnth': 335,
                    't_rec_index': 1230681651}
        new_sdd = SdoData(new_data)
        assert '' == new_sdd.url
        assert '' == new_sdd.series_name
        assert '' == new_sdd.ias_location
        assert '' == new_sdd.ias_path
        assert 0 == new_sdd.exptime
        assert 0 == new_sdd.harpnum

    def test_get_ias_path(self):
        """Tests get_ias_path()"""
        sdd = self.sdd
        assert 'https://idoc-medoc.ias.u-psud.fr//s.../S00000' == sdd.get_ias_path()

    def test_get_ias_path_1(self):
        """Tests get_ias_path()"""
        sdd = self.sdd
        sdd.ias_path = 'https://idoc-medoc.ias.u-psud.fr//s.../S00000/image_lev1.fits'
        assert 'https://idoc-medoc.ias.u-psud.fr//s.../S00000' == sdd.get_ias_path()

    def test_get_ias_path_2(self):
        """Tests get_ias_path()"""
        sdd = self.sdd
        sdd.ias_path = 'idoc-medoc.ias.u-psud.fr//s.../S00000/image_lev1.fits'
        assert 'https://idoc-medoc.ias.u-psud.fr//s.../S00000' == sdd.get_ias_path()

    def test_get_filename_and_create_target_dir(self):
        """Tests get_filename_and_create_target_dir()"""
        sdd = self.sdd
        assert 'aia.lev1_335A_2016-01-01T00-00-13_171963897.' == sdd.get_filename_and_create_target_dir(None, None)

    def test_get_filename_and_create_target_dir_1(self):
        """Tests get_filename_and_create_target_dir()"""
        sdd = self.sdd
        assert 'my_dir/toto' == sdd.get_filename_and_create_target_dir('toto', 'my_dir/')

    def test_get_filename_and_create_target_dir_2(self):
        """Tests get_filename_and_create_target_dir()"""
        sdd = self.sdd
        sdd.series_name = 'hmi.sharp_720s'
        sdd.wave = 6173
        sdd.harpnum = 1331
        assert 'hmi.sharp_720s_6173A_2016-01-01T00-00-13_1331.' == sdd.get_filename_and_create_target_dir(None, None)

    def test_get_filename_and_create_target_dir_3(self):
        """Tests get_filename_and_create_target_dir()"""
        sdd = self.sdd
        sdd.series_name = 'hmi.m_720s'
        sdd.wave = 6173
        assert 'hmi.m_720s_6173A_2016-01-01T00-00-13.' == sdd.get_filename_and_create_target_dir(None, None)

    def test_load_url_build_seg(self):
        """Tests load_url_build_seg()"""
        sdd = self.sdd
        url_build_seg = 'https://idoc-medoc.ias.u-psud.fr//sitools/datastorage/user/SUM12/D775321065/S00000/?media=json'
        segment = ['image_lev1']
        segment_allowed = []
        assert ['image_lev1'], ['image_lev1', 'spikes'] == sdd.load_url_build_seg(
            url_build_seg, segment, segment_allowed)

    def test_scan_segment(self):
        """Tests scan_segment()"""
        sdd = self.sdd
        assert (['image_lev1'],
                ['image_lev1', 'spikes'],
                'https://sdo.ias.u-psud.fr/SDO/...1230681651;segment=image_lev1') == sdd.scan_segment(None, None, None)

    def test_scan_segment_1(self):
        """Tests scan_segment()"""
        sdd = self.sdd
        assert (['SDO_IAS_file'],
                [],
                'https://sdo.ias.u-psud.fr/SDO/...1230681651;segment=SDO_IAS_file') == \
               sdd.scan_segment(None, 'SDO_IAS_file', None)

    def test_scan_segment_2(self):
        """Tests scan_segment()"""
        sdd = self.sdd
        assert (['image_lev1'],
                ['image_lev1', 'spikes', 'image_lev1', 'spikes'],
                'https://sdo.ias.u-psud.fr/SDO/...1230681651;segment=image_lev1') == \
            sdd.scan_segment(['image_lev1'],
                             None,
                             'https://idoc-medoc.ias.u-psud.fr//sitools/datastorage/user/SUM12/D775321065/S00000')

    def test_scan_segment_3(self):
        """Tests scan_segment()"""
        sdd = self.sdd
        sdd.series_name = 'hmi.ic_720s'
        sdd.wave = 6173
        assert (['continuum'],
                ['continuum'],
                'https://sdo.ias.u-psud.fr/SDO/...12306816510;segment=continuum') == sdd.scan_segment(None, None, None)

    def test_scan_segment_4(self):
        """Tests scan_segment()"""
        sdd = self.sdd
        sdd.series_name = 'hmi.m_720s'
        sdd.wave = 6173

        assert (['magnetogram'],
                ['magnetogram'],
                'https://sdo.ias.u-psud.fr/SDO/...12306816510;segment=magnetogram') == \
               sdd.scan_segment(None, None, None)

    def test_scan_segment_5(self):
        """Tests scan_segment()"""
        sdd = self.sdd
        sdd.series_name = 'hmi.sharp_720s'
        sdd.wave = 6173
        sdd.url = 'https://sdo.ias.u-psud.fr/SDO/ias_export_hmi.cgi?series='\
                  'hmi.sharp_720s;record=6173_1008001-1008001;harpnum=6205'
        segment_list = ['Dopplergram', 'alpha_err', 'alpha_mag', 'azimuth',
                        'azimuth_alpha_err', 'azimuth_err', 'bitmap', 'chisq',
                        'conf_disambig', 'confid_map', 'continuum', 'conv_flag',
                        'damping', 'disambig', 'dop_width', 'eta_0', 'field',
                        'field_alpha_err', 'field_az_err', 'field_err',
                        'field_inclination_err', 'inclin_azimuth_err',
                        'inclination', 'inclination_alpha_err',
                        'inclination_err', 'info_map', 'magnetogram',
                        'src_continuum', 'src_grad', 'vlos_err', 'vlos_mag']
        sdd.ias_path = 'https://idoc-medoc.ias.u-psud.fr/sitools/datastorage/user/SUM12/D785084767/S00000'
        assert (segment_list,
                segment_list,
                'https://sdo.ias.u-psud.fr/SDO/ias_export_hmi.cgi?series='
                'hmi.sharp_720s;record=6173_1008001-1008001;harpnum=6205;media=json') == \
            sdd.scan_segment(None, None, sdd.ias_path)

    def test_scan_segment_6(self):
        """Tests scan_segment()"""
        sdd = self.sdd
        sdd.series_name = 'hmi.sharp_720s'
        sdd.wave = 6173
        sdd.url = 'https://sdo.ias.u-psud.fr/SDO/ias_export_hmi.cgi?series='\
                  'hmi.sharp_720s;record=6173_1008001-1008001;harpnum=6205'
        segment_list = ['Dopplergram', 'alpha_err', 'alpha_mag', 'azimuth',
                        'azimuth_alpha_err', 'azimuth_err', 'bitmap', 'chisq',
                        'conf_disambig', 'confid_map', 'continuum', 'conv_flag',
                        'damping', 'disambig', 'dop_width', 'eta_0', 'field',
                        'field_alpha_err', 'field_az_err', 'field_err',
                        'field_inclination_err', 'inclin_azimuth_err',
                        'inclination', 'inclination_alpha_err',
                        'inclination_err', 'info_map', 'magnetogram',
                        'src_continuum', 'src_grad', 'vlos_err', 'vlos_mag']
        sdd.ias_path = 'https://idoc-medoc.ias.u-psud.fr/sitools/datastorage/user/SUM12/D785084767/S00000'
        assert ('Dopplergram',
                segment_list,
                'https://sdo.ias.u-psud.fr/SDO/ias_export_hmi.cgi?series='
                'hmi.sharp_720s;record=6173_1008001-1008001;harpnum=6205;'
                'segment=D%2Co%2Cp%2Cp%2Cl%2Ce%2Cr%2Cg%2Cr%2Ca%2Cm') == \
               sdd.scan_segment('Dopplergram', None, sdd.ias_path)

    def test_is_keywords(self):
        """Tests is_keywords()"""
        sdd = self.sdd
        with pytest.raises(ValueError):
            assert sdd.is_keywords('')
        with pytest.raises(TypeError):
            assert sdd.is_keywords('QUALITY')
        assert sdd.is_keywords(['QUALITY']) is True
