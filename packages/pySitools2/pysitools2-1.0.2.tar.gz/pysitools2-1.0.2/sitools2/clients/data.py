#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Nima TRAORE"

from future.utils import viewitems

from sitools2.clients import medoc_config as cfg


class Data:
    """Class Data.

    Data is designed to be a parent class for clients data objects (like GaiaData, SdoData classes...)

    Attributes defined here:
        server = server name

    Methods defined here:
        check_kwargs(): initialize some attributes provided in args

    """
    def __init__(self, server=cfg.SITOOLS2_URL):
        """Constructor of the class Data"""
        self.server = server

    @staticmethod
    def check_kwargs(params, kwargs):
        """Initializes some attributes provided in kwargs.

        When a dictionary is provided as named parameters to the function, the method checks if each value of the given
        dictionary is in an allowed parameters list, then initializes an empty dictionary with allowed attributes.

        Args:
            params: list of allowed parameters to be checked
            kwargs: a dictionary

        Returns:
            dictionary

        """
        kwg_dict = {}
        for key, value in viewitems(kwargs):
            if key not in params:
                raise ValueError("Error in search:\n%s entry for the function is not allowed\n" % key)
            else:
                kwg_dict[key.lower()] = value

        return kwg_dict
