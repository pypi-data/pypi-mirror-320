#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Nima TRAORE"

from future.moves.urllib.request import urlopen
from simplejson import load

from sitools2.clients import medoc_config as cfg
from sitools2.core.field import Field


class TestField:
    """Tests the class Field methods.

    """
    def setup_method(self):
        """Method called before one of the current class tests."""
        result = load(urlopen(cfg.SITOOLS2_URL + '/' +
                              cfg.AIA_LEV1_DATASET_ID))
        column_dict = result['dataset']['columnModel']
        self.fd0 = Field(column_dict[0])
        self.fd1 = Field(column_dict[1])

    def test_field_attributes(self):
        """Tests the class Field attributes after initialisation."""
        assert 'recnum' == self.fd0.name
        assert 'int8' == self.fd0.ftype
        assert self.fd0.ffilter is True
        assert self.fd0.sort is True
        assert '' == self.fd0.behavior

        assert 'sunum' == self.fd1.name
        assert 'int8' == self.fd1.ftype
        assert self.fd1.ffilter is True
        assert self.fd1.sort is True
        assert '' == self.fd1.behavior
