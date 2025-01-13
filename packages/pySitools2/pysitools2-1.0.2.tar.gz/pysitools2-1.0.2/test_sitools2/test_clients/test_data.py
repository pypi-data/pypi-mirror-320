#!/usr/bin/env python3
# -*- coding:utf-8 -*-

__author__ = "Nima TRAORE"

from datetime import datetime
import pytest

from sitools2.clients.data import Data


class TestData:
    """Tests the class Data methods.

    """
    def setup_method(self):
        """Setup method"""
        self.d1 = datetime(2020, 1, 1, 0, 0, 0)
        self.d2 = datetime(2020, 1, 1, 2, 12, 0)
        self.dt = Data()
        self.params_list = ['DATES', 'WAVES', 'SERIES',
                            'DETECTORS', 'NB_RES_MAX']

    def test_check_kwargs(self):
        """Tests scan_kwargs()"""
        kwargs = {'DATES': [self.d1, self.d2],
                  'WAVES': ['94', '131', '304'],
                  'NB_RES_MAX': 4}

        kwgs_dict = self.dt.check_kwargs(self.params_list, kwargs)
        assert [self.d1, self.d2] == kwgs_dict['dates']
        assert ['94', '131', '304'] == kwgs_dict['waves']
        assert 4 == kwgs_dict['nb_res_max']

    def test_check_kwargs_bis(self):
        """Tests scan_kwargs()"""
        kwargs = {'TIMES': [self.d1, self.d2],
                  'WAVES': ['94', '131', '304'],
                  'NB_RES_MAX': 4}

        # TIMES not in params_list: so an exception is raised
        with pytest.raises(ValueError):
            assert self.dt.check_kwargs(self.params_list, kwargs)
