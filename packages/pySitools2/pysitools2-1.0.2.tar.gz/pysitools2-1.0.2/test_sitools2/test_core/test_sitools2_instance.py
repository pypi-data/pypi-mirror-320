#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Nima TRAORE"

from simplejson import load
from future.moves.urllib.request import urlopen

from sitools2.clients import medoc_config as cfg
from sitools2.core.sitools2_instance import Sitools2Instance


class TestSitools2Instance:
    """Tests the class Sitools2Instance methods.

    """
    def setup_method(self):
        """Method called before one of the current class tests."""
        self.s2i = Sitools2Instance(cfg.SITOOLS2_URL)

    def test_url(self):
        """Tests the base url of Sitools2Instance."""
        f = urlopen(self.s2i.instance_url)
        assert 200 == f.getcode()

    def test_sitools_portal(self):
        """Tests url+'sitools/portal'."""
        result = load(urlopen(self.s2i.instance_url+"/sitools/portal"))
        assert isinstance(result, dict)
        assert 3 == len(result)
        assert 1 == result['total']
        assert isinstance(result['data'], list)
        assert result['success'] is True

    def test_list_project(self):
        """Tests list_project()"""
        data = self.s2i.list_project()
        assert isinstance(data, list)
        assert 1 == len(data)
