import logging
import json

from .exceptions import AuthorizationError, DependencyTrackApiError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Version():
    """Get the version of the Dependency Track instance"""
    def version(self) -> str:
        """Returns string with current Dependency Track version

        API Endpoint: GET /version

        Returns
        -------
        str
            String with Dependency Track version

        Raises
        ------
        DependencyTrackApiError
            Raise an error
        """
        response = self.session.get(f"{self.host}/api/version")
        if response.status_code == 200:
            return json.loads(response.text)['version']
        else:
            description = f"Unable to get a Dependency Track version"
            raise DependencyTrackApiError(description, response)
