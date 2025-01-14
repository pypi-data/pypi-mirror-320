# Copyright 2020 Alvin Chen sonoma001@gmail.com
# SPDX-License-Identifier: GPL-2.0+

import logging
import json

from .exceptions import AuthorizationError, DependencyTrackApiError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Projects:
    """Class dedicated to all "projects" related endpoints"""

    def list_projects(self):
        """List all projects accessible to the authenticated user

        API Endpoint: GET /project

        :return: a list of projects
        :rtype: list()
        :raises DependencyTrackApiError: if the REST call failed
        """
        response = self.session.get(self.api + "/project", params=self.paginated_param_payload)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            description = f"Unable to get a list of projects"
            raise DependencyTrackApiError(description, response)

    def get_project_property(self, uuid):
        """Get details of project.

        API Endpoint: GET /project/{uuid}/property

        :param uuid: the ID of the project to be analysed
        :type uuid: uuid string
        :return: the requested project property
        :rtype: list()
        :raises DependencyTrackApiError: if the REST call failed
        """
        response = self.session.get(self.api + f"/project/{uuid}/property", params=self.paginated_param_payload)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            description = f"Error while getting property for project {uuid}"
            raise DependencyTrackApiError(description, response)

    def get_project_dependency(self, uuid):
        """Get details of project dependency.
    
        API Endpoint: GET /dependency/project/{uuid}
    
        :param uuid: the ID of the project to be analysed
        :type uuid: uuid string
        :return: the requested project
        :rtype: project dependency dict
        :raises DependencyTrackApiError: if the REST call failed
        """
        
        response = self.session.get(self.api + f"/dependency/project/{uuid}", params=self.paginated_param_payload)
        print(response.url)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            description = f"Error while getting dependency for project {uuid}"
            raise DependencyTrackApiError(description, response)
            
    def get_project(self, uuid):
        """Get details of project.
    
        API Endpoint: GET /project/{uuid}/property
    
        :param uuid: the ID of the project to be analysed
        :type uuid: uuid string
        :return: the requested project property
        :rtype: list()
        :raises DependencyTrackApiError: if the REST call failed
        """
        response = self.session.get(self.api + f"/project/{uuid}/", params=self.paginated_param_payload)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            description = f"Error while getting project {uuid}"
            raise DependencyTrackApiError(description, response)
    
    def project_lookup(self, name, version):
        """Returns specific project by its name and version
        
        API Endpoint: GET /project/lookup?name=test&version=0.1.2
        
        Parameters
        ----------
        name : str
            Project Name
        version : str
            Project Version
        
        Returns
        -------
        """
        query = f"?name={name}&version={version}"
        response = self.session.get(self.api + f"/project/lookup{query}", params=self.paginated_param_payload)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            description = f"Error while lookup the project by name and version"
            raise DependencyTrackApiError(description, response)
