from google.cloud import secretmanager
from google.auth.exceptions import DefaultCredentialsError
from google.oauth2 import service_account
import os
from .logger_init import Logger

class SecretManager:
    """
    A utility class for managing secrets from Google Secret Manager with flexible authentication methods.
    """

    def __init__(self, project_id: str, logger: Logger, service_account_json: str = None):
        """
        Initialize the SecretManager.

        Args:
            project_id (str): Google Cloud Project ID.
            logger (Logger): Your custom logger instance.
            service_account_json (str, optional): Path to a service account JSON key file.
        """
        self.project_id = project_id
        self.logger = logger
        self.client = self._init_secret_manager(service_account_json)

    def _init_secret_manager(self, service_account_json: str = None) -> secretmanager.SecretManagerServiceClient:
        """
        Initializes the Secret Manager client with flexible authentication.

        Args:
            service_account_json (str, optional): Path to a service account JSON key file.

        Returns:
            SecretManagerServiceClient: Initialized client instance.
        """
        try:
            if service_account_json:
                self.logger.info(f"Authenticating with service account JSON: {service_account_json}")
                credentials = service_account.Credentials.from_service_account_file(service_account_json)
                client = secretmanager.SecretManagerServiceClient(credentials=credentials)
            else:
                self.logger.info("Authenticating with application default credentials (ADC) or current user.")
                client = secretmanager.SecretManagerServiceClient()
            self.logger.info("Google Secret Manager client initialized successfully.")
            return client
        except FileNotFoundError:
            self.logger.critical(f"Service account JSON file not found: {service_account_json}")
            raise
        except DefaultCredentialsError as e:
            self.logger.critical(f"Authentication failed: {e}")
            raise RuntimeError("Could not authenticate with Google Secret Manager.") from e

    def get_secret(self, secret_name: str, fallback_env_var: str = None) -> str:
        """
        Retrieve a secret from Google Secret Manager or fallback to an environment variable.

        Args:
            secret_name (str): The name of the secret in Secret Manager.
            fallback_env_var (str): Optional environment variable as a fallback.

        Returns:
            str: The secret value.

        Raises:
            ValueError: If the secret cannot be retrieved.
        """
        try:
            self.logger.info(f"Fetching secret from Secret Manager: {secret_name}")
            name = f"projects/{self.project_id}/secrets/{secret_name}/versions/latest"
            response = self.client.access_secret_version(request={"name": name})
            secret = response.payload.data.decode("UTF-8")
            self.logger.info(f"Successfully retrieved secret: {secret_name}")
            return secret
        except Exception as e:
            self.logger.error(f"Error fetching secret '{secret_name}': {e}")
            if fallback_env_var:
                self.logger.warning(f"Attempting to fetch secret from environment variable: {fallback_env_var}")
                secret = os.getenv(fallback_env_var)
                if secret:
                    self.logger.info(f"Successfully retrieved secret from environment variable: {fallback_env_var}")
                    return secret
                self.logger.error(f"Environment variable '{fallback_env_var}' not set.")
            raise ValueError(f"Failed to retrieve secret: {secret_name}")

    @staticmethod
    def mask_secret(secret: str) -> str:
        """
        Mask a secret to protect it in logs.

        Args:
            secret (str): The secret value to mask.

        Returns:
            str: Masked secret.
        """
        if len(secret) > 8:
            return secret[:4] + "*" * (len(secret) - 8) + secret[-4:]
        return "*" * len(secret)
