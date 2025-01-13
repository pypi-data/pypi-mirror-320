#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Nima TRAORE"

from sitools2.clients import medoc_config as cfg
from sitools2.core.dataset import Dataset
from sitools2.core.query import Query


class TestQuery:
    """Tests the class Query methods.

    """
    def setup_method(self):
        """Method called before one of the current class tests."""
        ds = Dataset(cfg.SITOOLS2_URL + '/' + cfg.AIA_LEV1_DATASET_ID)
        param_list = [[ds.fields_list[4]],
                      ['2012-08-10T00:00', '2012-08-10T01:00'],
                      'DATE_BETWEEN']
        self.q1 = Query(param_list)

    def test_query_attributes(self):
        """Tests the class Query attributes after initialisation."""
        assert ['sessionns'] == self.q1.name_list
        assert ['2012-08-10T00:00', '2012-08-10T01:00'] == self.q1.value_list
        assert 'DATE_BETWEEN' == self.q1.operation
        assert isinstance(self.q1.fields_list, list)
