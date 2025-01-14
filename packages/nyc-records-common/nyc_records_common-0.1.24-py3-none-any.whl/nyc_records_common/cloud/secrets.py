"""Google Cloud Secret Manager utilities.

Provides functions for securely accessing secrets stored in Google Cloud Secret
Manager. Handles authentication and error cases with appropriate logging.
"""

import logging
import os

from google.api_core.exceptions import GoogleAPIError, NotFound
from google.cloud import secretmanager
from google.oauth2 import service_account

logger = logging.getLogger(__name__)


def get_secret_manager_client(keyfile_path: str = "/home/vscode/keyfile.json"):
    """Get authenticated Secret Manager client.

    Creates a Google Cloud Secret Manager client using either:
    - Service account credentials from keyfile
    - Default IAM credentials if keyfile not found

    Args:
        keyfile_path: Path to service account credentials JSON file

    Returns:
        SecretManagerServiceClient: Authenticated client instance

    Example:
        client = get_secret_manager_client("/path/to/keyfile.json")
        client = get_secret_manager_client()  # Uses default authentication
    """
    if os.path.exists(keyfile_path):
        # File-based authentication
        credentials = service_account.Credentials.from_service_account_file(
            keyfile_path, scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        return secretmanager.SecretManagerServiceClient(credentials=credentials)
    else:
        # Default IAM-based authentication
        return secretmanager.SecretManagerServiceClient()


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
