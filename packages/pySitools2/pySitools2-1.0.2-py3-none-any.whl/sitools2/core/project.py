#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = ["Pablo ALINGERY, Nima TRAORE"]

from future.moves.urllib.error import HTTPError
from future.moves.urllib.parse import urlencode
from future.moves.urllib.request import urlopen
from simplejson import load
from sys import stderr
from xml.dom.minidom import parseString


from sitools2.core.dataset import Dataset


class Project:
    """Class giving details about a project of sitools2.

    Attributes defined here:
        description: description of the project
        name: name of the project
        resources_target: list of resources target
        uri: URI of the project
        url: URL of the project

    Methods defined here:
        compute_attributes(): computes attributes from project instance
        resources_list(): explores the project resources
        dataset_list(): returns list of available datasets

    """
    def __init__(self, url):
        """Initializes Project"""
        self.name = ""
        self.description = ""
        self.uri = "/" + url.split("/")[-1]
        self.url = url
        self.resources_target = []
        self.compute_attributes()
        self.resources_list()

    def compute_attributes(self, **kwargs):
        """Computes attributes from a project instance"""
        kwargs.update({'media': 'json'})
        url = self.url + '?' + urlencode(kwargs)
        result = load(urlopen(url))
        self.name = result['project']['name']
        self.description = result['project']['description']

    def resources_list(self):
        """Explores a project resources.

        method=options should be allowed

        """
        url = urlopen(self.url + '?method=OPTIONS')
        wadl = url.read()
        try:
            dom_wadl = parseString(wadl)
        except HTTPError:
            stderr.write("Project %s : project.resources_list() not allowed\nPlease contact "
                         "medoc-contacts@ias.u-psud.fr and report that issue\n" % self.name)
            raise
        else:
            resources = dom_wadl.getElementsByTagName('resource')
            for i in range(len(resources)):
                self.resources_target.append(self.url + "/" + resources[i].getAttribute('path'))

    def display(self):
        """Output Project attributes"""
        print(self.__repr__())

    def __repr__(self):
        """Representation of Project instance.

        Returns:
            name, description, uri, url

        """
        phrase = ""
        phrase += ("\n\nProject object display() :\n\t%s\n\t\tdescription : %s\n\t\turi : %s\n\t\turl : %s" %
                   (self.name, self.description, self.uri, self.url))
        phrase += "\n\t\tresources list :"
        if len(self.resources_target) != 0:
            for i, res in enumerate(self.resources_target):
                phrase += "\n\t\t\t%d) %s" % (i, res)
        return phrase

    def dataset_list(self, **kwargs):
        """Gives relevant information concerning the project datasets.

        Lists all datasets in the Project instance and creates the
        dataset objects.

        """
        sitools_url = self.url.split("/")[0] + "//" + self.url.split("//")[1].split("/")[0]
        kwargs.update({'media': 'json'})
        url = self.url + '/datasets' + '?' + urlencode(kwargs)
        data = []
        try:
            result = load(urlopen(url))
            if len(result['data']) != 0:
                for i, dataset in enumerate(result['data']):
                    dataset_url = sitools_url + dataset['url']
                    data.append(Dataset(dataset_url))
        except HTTPError:
            stderr.write("Error in Project.dataset_list() :\nCannot access dataset list %s\nContact "
                         "medoc-contacts@ias.u-psud.fr and report that issue\n" % url)
            raise
        return data
