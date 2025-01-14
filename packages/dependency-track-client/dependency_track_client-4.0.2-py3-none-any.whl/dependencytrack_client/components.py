# Copyright 2020 Alvin Chen sonoma001@gmail.com
# SPDX-License-Identifier: GPL-2.0+

import logging
import json

from .exceptions import AuthorizationError, DependencyTrackApiError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Components:
    """Class dedicated to all "folders" related endpoints"""

    def list_components(self):
        """List all components accessible to the authenticated user

        API Endpoint: GET /component

        :return: a list of components
        :rtype: list()
        :raises DependencyTrackApiError: if the REST call failed
        """
        response = self.session.get(self.api + "/component", params=self.paginated_param_payload)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            description = f"Unable to get a list of components"
            raise DependencyTrackApiError(description, response)

    def get_component_dependency(self, uuid):
        """Get details of project dependency.
    
        API Endpoint: GET /dependency/project/{uuid}
    
        :param id: the ID of the project to be analysed
        :type id: int
        :return: the requested project dependency
        :rtype: dist
        :raises DependencyTrackApiError: if the REST call failed
        """
        response = self.session.get(self.api + f"/dependency/component/{uuid}", params=self.paginated_param_payload)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            description = f"Error while getting dependency for component {uuid}"
            raise DependencyTrackApiError(description, response)


    def get_project_components(self, uuid):
        """Returns a list of components for given project
        
        API Endpoint: GET /component/project/{uuid}

        Parameters
        ----------
        uuid : str
            The UUID of the project to retrieve components for

        Returns
        -------

        """
        response = self.session.get(self.api + f"/component/project/{uuid}", params=self.paginated_param_payload)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            description = f"Error while getting dependency for component {uuid}"
            raise DependencyTrackApiError(description, response)

    def get_component(self, uuid):
        """Returns a specific component

        API Endpoint: GET /component/{uuid}

        Parameters
        ----------
        uuid : str
            The UUID of the component to retrieve
        """
        response = self.session.get(self.api + f"/component/{uuid}", params=self.paginated_param_payload)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            description = f"Error while getting component {uuid}"
            raise DependencyTrackApiError(description, response)
