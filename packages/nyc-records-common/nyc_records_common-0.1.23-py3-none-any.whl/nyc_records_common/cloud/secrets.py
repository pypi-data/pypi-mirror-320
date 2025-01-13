"""Google Cloud Secret Manager utilities.

Provides functions for securely accessing secrets stored in Google Cloud Secret
Manager. Handles authentication and error cases with appropriate logging.
"""

import logging

from google.api_core.exceptions import GoogleAPIError, NotFound
from google.cloud import secretmanager

logger = logging.getLogger(__name__)


def load_secret(secret_name: str) -> str | None:
    """Load secret value from Google Cloud Secret Manager.

    Args:
        secret_name: Full secret path in format 'projects/*/secrets/*/versions/*'

    Returns:
        Secret value as string if successful, None if failed

    Example:
        secret = load_secret('projects/123/secrets/api-key/versions/latest')
    """
    try:
        client = secretmanager.SecretManagerServiceClient()
        secret_path = f"{secret_name}/versions/latest"
        response = client.access_secret_version(name=secret_path)
        return response.payload.data.decode("UTF-8")
    except NotFound:
        logger.error("Secret not found: %s", secret_name)
        return None
    except (GoogleAPIError, ValueError) as e:
        logger.error("Error loading secret %s: %s", secret_name, str(e))
        return None
