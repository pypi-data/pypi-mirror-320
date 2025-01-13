#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Nima TRAORE"

from sitools2.clients import medoc_config as cfg
from sitools2.core.project import Project


class TestProject:
    """Tests the class Project methods.

    """
    def setup_method(self):
        """Method called before one of the current class tests."""
        self.pj = Project(cfg.SITOOLS2_URL + '/project/solar')

    def test_project_attributes(self):
        """Tests the class Project attributes after initialisation."""
        assert 'Medoc-Solar-Portal' == self.pj.name
        assert 'Solar datasets' == self.pj.description
        assert 15 == len(self.pj.resources_target)

    def test_dataset_list(self):
        """Tests dataset_list() method."""
        data = self.pj.dataset_list()
        assert isinstance(data, list)
        assert 75 == len(data)
