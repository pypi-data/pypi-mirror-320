|License| |Python Version| |Downloads|

.. |License| image:: https://img.shields.io/badge/license-GPL2.0+-blue.svg
   :target: https://github.com/jas02/dependency-track-python/LICENSE.md

.. |Python Version| image:: https://img.shields.io/badge/python-3.6%2C3.7%2C3.8-blue?logo=python
   :target: https://www.python.org/doc/versions/
   
.. |Downloads| image:: https://pypip.in/download/dependency-track/badge.svg?period=week
    :target: https://pypi.python.org/pypi/dependency-track-ng/
    
A simple wrapper for the Dependency Track REST API. This is fork based on original work of Alvin Chen and his `dependency-track library <https://github.com/alvinchchen/dependency-track-python>`_.

Usage
=====

Installation
------------

   This project is available as `Python package on PyPi.org <https://pypi.org/project/dependency-track-client/>`_.

-  Install DependencyTrack and required dependencies:

   .. code:: shell

      pip install dependency-track-client

Using the API
-------------

-  Get a REST API key from the DependencyTrack server under "Administration-> Access Management-> Teams":

   .. code:: Python

		from dependencytrack_client import DependencyTrack

		url = 'http://10.0.0.1:8080'

		api_key = 'YRlAeOAb0uXT7dTGrfsvnGxjxZSF0XbO'

		dt = DependencyTrack(url, api_key)

		dt.list_projects()
		
		dt.get_project_property('ab36ead0-c7b0-47f5-89ac-7f92a0bbe12e')
		
		dt.list_components()

		dt.get_project_dependency('ab36ead0-c7b0-47f5-89ac-7f92a0bbe12e')
		
		dt.get_component_dependency('db6157c2-f0a3-447c-902d-aecd360958bd')
		
		dt.list_concise_licenses()[0]
		
		dt.get_license('MIT')

		dt.search('dnsmasq-2.0')


Versioning
----------

Major Version is following [DependencyTrack Major Version](https://github.com/DependencyTrack/dependency-track/releases).