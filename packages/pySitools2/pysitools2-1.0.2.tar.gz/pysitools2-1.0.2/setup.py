#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#    SITools2 client for Python
#    Copyright (C) 2025 - Institut d'Astrophysique Spatiale
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages

import sitools2

__author__ = sitools2.__author__
__date__ = sitools2.__date__

setup(
    # Name of the project as it appears on PyPi
    name='pySitools2',

    # The code version
    version=sitools2.__version__,

    # List of packages to be inserted to the distribution
    packages=find_packages(),

    # List of the packages' dependencies here, for eg:
    install_requires=['pytest', 'pytest-cov', 'simplejson', 'future', 'astropy', 'matplotlib', 'sunpy'],

    # This is a one-line description
    description='A generic python Sitools2 client with IDOC/MEDOC clients',

    # Get the long description from the README file
    long_description=open("README.md").read(),

    # Denotes that long_description is in Markdown
    long_description_content_type='text/markdown',

    # Author with email
    author='Nima TRAORE',
    author_email='nima.traore@ias.u-psud.fr',

    # Give a homepage URL for the project
    url='https://git.ias.u-psud.fr/medoc/PySitools2',

    # Licence
    license='GPLv3',

    # Classifiers help users find the project by categorizing it
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
    ],

    # Additional URLs that are relevant to the project
    project_urls={
        'MEDOC/IAS Web Interface': 'https://idoc-medoc.ias.u-psud.fr',
        'Source': 'https://git.ias.u-psud.fr/medoc/PySitools2',
    },

    # Can be called with setup.py (with no arguments) to run unit tests
    test_suite="test_sitools2")
