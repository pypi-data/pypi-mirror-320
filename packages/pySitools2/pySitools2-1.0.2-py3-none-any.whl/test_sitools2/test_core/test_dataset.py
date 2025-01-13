#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Nima TRAORE"

import pytest

from sitools2.clients import medoc_config as cfg
from sitools2.core.dataset import Dataset
from sitools2.core.field import Field


class TestDataset:
    """Tests the class Dataset methods.

    """
    def setup_method(self):
        """Method called before one of the current class tests."""
        self.ds = Dataset(cfg.SITOOLS2_URL+'/'+cfg.AIA_LEV1_DATASET_ID)

    def test_constructor(self):
        """Tests __init__()"""
        url = 'https://tototitixxxx'
        with pytest.raises(Exception):
            self.ds = Dataset(url)

    def test_dataset_attributes(self):
        """Tests the class Dataset attributes after initialisation."""
        assert 'aia.lev1' == self.ds.name
        assert 'access to all metadata info' == self.ds.description
        assert 188 == len(self.ds.fields_list)
        assert 188 == len(self.ds.fields_dict)
        assert 188 == len(self.ds.filter_list)
        assert 188 == len(self.ds.sort_list)
        assert 21 == len(self.ds.resources_target)

    def test_optimize_operation(self):
        """Tests optimize_operation()"""
        assert 'GTE' == self.ds.optimize_operation('GE')
        assert 'LTE' == self.ds.optimize_operation('LE')

    def test_get_result_count(self):
        """Tests get_result_count(): raises exception when URL not good"""
        url_count = 'https://xxxyyy/webs_IAS_SDO_AIA_dataset/count?xxxyyy'
        with pytest.raises(Exception):
            assert self.ds.get_result_count(url_count)

    def test_get_pk_item_component(self):
        """Tests get_pk_item_component()"""
        pk_item = Field({})
        pk_item.component = 'index'
        assert ['index'] == self.ds.get_pk_item_component(pk_item)
        pk_item.component = 'recnum||\',\'||series_name'
        assert ['recnum', 'series_name'] == self.ds.get_pk_item_component(pk_item)
        pk_item.component = 'recnum||\'/\'||series_name'
        assert ['recnum', 'series_name'] == self.ds.get_pk_item_component(pk_item)

    def test_execute_plugin(self):
        """Tests execute_plugin()"""
        # plugin_name is None
        with pytest.raises(ValueError):
            assert self.ds.execute_plugin(plugin_name=None,
                                          pkey_values_list=[171963897, 'aia.lev1'])
        # plugin_name is wrong
        with pytest.raises(ValueError):
            assert self.ds.execute_plugin(plugin_name='Tototitixxx',
                                          pkey_values_list=[171963897, 'aia.lev1'])
        # len(pkey_values_list) = 0
        with pytest.raises(ValueError):
            assert self.ds.execute_plugin(plugin_name='pluginAIAtar',
                                          pkey_values_list=[])
        # filename is None
        with pytest.raises(ValueError):
            assert self.ds.execute_plugin(plugin_name='pluginAIAtar',
                                          pkey_values_list=[171963897, 'aia.lev1'],
                                          filename=None)
