#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = ["Pablo ALINGERY, Nima TRAORE"]


class Field:
    """Definition of an item from a dataset

    Attributes defined here:
        behavior: apply special behavior on field like dataset link
        component: list of the components of the field
        ffilter: stands if the field is filtered or not
        ftype: type of the field
        name: name of the field
        sort: stands if the field is sorted or not

    Methods defined here:
        compute_attributes(): computes attributes from web service dataset description

    """
    def __init__(self, dictionary):
        """Initializes class Field."""
        self.name = ""
        self.component = ""
        self.ftype = ""
        self.ffilter = False
        self.sort = False
        self.behavior = ""
        self.compute_attributes(dictionary)

    def compute_attributes(self, dictionary):
        """Computes attribute from web service dataset description"""
        if 'columnAlias' in dictionary:
            self.name = dictionary['columnAlias']
        if 'dataIndex' in dictionary:
            self.component = dictionary['dataIndex']
        if 'sqlColumnType' in dictionary:
            self.ftype = dictionary['sqlColumnType']
        if 'filter' in dictionary:
            self.ffilter = dictionary['filter']
        if 'sortable' in dictionary:
            self.sort = dictionary['sortable']
        if 'columnRenderer' in dictionary:
            self.behavior = dictionary['columnRenderer']['behavior']

    def display(self):
        """Displays a representation of the data"""
        print(self.__repr__())

    def __repr__(self):
        return ("Field object display() :\n\t%s\n\t\tftype : %s\n\t\tffilter : %s\n\t\tsort : %s\n\t\tbehavior : %s" %
                (self.name, self.ftype, self.ffilter, self.sort, self.behavior))
