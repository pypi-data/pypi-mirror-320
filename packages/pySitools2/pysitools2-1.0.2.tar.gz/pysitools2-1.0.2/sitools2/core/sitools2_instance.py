#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = ["Pablo ALINGERY, Nima TRAORE"]

from sys import stdout, stderr
from future.moves.urllib.parse import urlencode
from future.moves.urllib.request import urlopen
from future.moves.urllib.error import HTTPError
from simplejson import load

from sitools2.core.project import Project


class Sitools2Instance:
    """Define a server instance of Sitools2.

    Attributes defined here:
        instance_url: URL of the instance (URL of the IDOC/MEDOC server)

    Methods defined here:
        list_project(): list all projects available for sitools instance

    """
    def __init__(self, url):
        """Constructor of Sitools2Instance"""
        self.instance_url = url
        try:
            load(urlopen(self.instance_url + "/sitools/portal"))
        except HTTPError:
            stderr.write("Error in Sitools2Instance.__init__() :\nSitools2 instance %s not available please "
                         "contact admin for more info\n" % self.instance_url)
            raise

    def list_project(self, **kwargs):
        """List all projects available for the Sitools2 instance

        Args:
            kwargs: any optional parameters that can be useful for the function urlencode()

        Returns:
            list of objects (instances of the class Project)

        """
        data = []
        kwargs.update({'media': 'json'})
        url = self.instance_url + '/sitools/portal/projects' + '?' + urlencode(kwargs)

        result = load(urlopen(url))
        stdout.write("%s projects detected\n" % result['total'])
        stdout.flush()

        projects = result['data']
        for i, project in enumerate(projects):
            project_url = self.instance_url + project['sitoolsAttachementForUsers']
            try:
                data.append(Project(project_url))
            except HTTPError:
                stdout.write("Error in Sitools2Instance.list_project() :\nCannot create object project %s, %s protected"
                             "\nContact admin for more info\n" % (project['name'], project_url))
                stdout.flush()
                raise
        return data
