#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = ["Pablo ALINGERY, Nima TRAORE"]

from sys import stderr


class Query:
    """Definition of a request to be passed to the server.

    Attributes defined here:
        field_list: list of field objects
        name_list: list of field name attributes
        operation: name of the operation (ge, le, gte, lte, lt, eq, gt, lte, like, in, numeric_between, date_between or
        cadence)
        value_list: list of values of the field objects (values of field_list)

    Methods defined here:
        compute_attributes(): Computes attributes from client request

    """
    def __init__(self, param_list):
        """Initializes class Query"""
        self.fields_list = []
        self.name_list = []
        self.value_list = []
        self.operation = ""
        self.compute_attributes(param_list)

    def compute_attributes(self, param_list):
        """Computes attributes from client request"""
        if type(param_list[0]).__name__ != 'list':
            error_msg = ("Error in Query.compute_attributes() :\nQuery first argument type is : %s\nQuery first "
                         "argument type should be : list\n" % type(param_list[0]).__name__)
            stderr.write(error_msg)
            raise TypeError(error_msg)
        if type(param_list[1]).__name__ != 'list':
            error_msg = ("Error in Query.compute_attributes() :\nQuery second argument type is : %s\nQuery second "
                         "argument type should be : list\n\n\n" % type(param_list[1]).__name__)
            stderr.write(error_msg)
            raise TypeError(error_msg)
        for field in param_list[0]:
            self.name_list.append(str(field.name))
        self.fields_list = param_list[0]
        self.value_list = param_list[1]
        self.operation = param_list[2]

    def display(self):
        print(self.__repr__())

    def __repr__(self):
        return ("name : % s\nvalue : %s\nOperation : %s" %
                (", ".join(self.name_list), ", ".join(self.value_list), self.operation))
