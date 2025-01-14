import logging
import json

from .exceptions import AuthorizationError, DependencyTrackApiError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Violations():
    """Get the information about policy violations
    """
    def get_project_violations(self, uuid):
        """Returns a list of all policy violations for a specific project

        Parameters
        ----------
        uuid : str
            

        Returns
        -------
        _type_
            _description_

        Raises
        ------
        DependencyTrackApiError
            _description_
        """
        response = self.session.get(self.api + f"/violation/project/{uuid}", params=self.paginated_param_payload)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            description = f"Unable to get a Dependency Track policy violation for project"
            raise DependencyTrackApiError(description, response)
