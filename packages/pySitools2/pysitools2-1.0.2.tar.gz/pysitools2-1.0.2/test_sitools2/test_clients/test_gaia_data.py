#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__author__ = "Nima TRAORE"

from datetime import datetime

from sitools2.clients.gaia_data import GaiaData


class TestGaiaData:
    """Tests the class GaiaData methods.

    """
    def setup_method(self):
        """Setup method"""
        self.data = {'download': '/sitools/.../DEM_aia_2012-08-10T00_05.tar',
                     'date_obs': datetime(2012, 8, 10, 0, 5, 1, 875),
                     'sunum_193': 349340243,
                     'filename': 'DEM_aia_2012-08-10T00_05_',
                     'temp_fits_rice': '/s.../DEM_aia_2012-08-10T00_05_temp.fits',
                     'em_fits_rice': '/s.../DEM_aia_2012-08-10T00_05_em.fits',
                     'width_fits_rice': '/s.../DEM_aia_2012-08-10T00_05_width.fits',
                     'chi2_fits_rice': '/s.../DEM_aia_2012-08-10T00_05_chi2.fits'}
        self.gd = GaiaData(self.data)

    def test_compute_attributes(self):
        """Tests compute_attributes()"""
        data = self.data
        gd = self.gd
        assert data['download'] == gd.download
        assert data['date_obs'] == gd.date_obs
        assert data['sunum_193'] == gd.sunum_193
        assert data['filename'] == gd.filename
        assert data['temp_fits_rice'] == gd.temp_fits_rice_uri
        assert data['em_fits_rice'] == gd.em_fits_rice_uri
        assert data['width_fits_rice'] == gd.width_fits_rice_uri
        assert data['chi2_fits_rice'] == gd.chi2_fits_rice_uri

    def test_optimize_target_dir(self):
        """Tests optimize_target_dir()"""
        gd = self.gd
        assert "" == gd.optimize_target_dir(None)

    def test_scan_filetype(self):
        """Tests scan_filetype()"""
        gd = self.gd
        file_dict = {'DEM_aia_2012-08-10T00_05_chi2.fits':
                     'https://idoc-medoc.ias.u-psud.fr/s.../DEM_aia_2012-08-10T00_05_chi2.fits'}

        assert file_dict == gd.scan_filetype(['chi2'])
