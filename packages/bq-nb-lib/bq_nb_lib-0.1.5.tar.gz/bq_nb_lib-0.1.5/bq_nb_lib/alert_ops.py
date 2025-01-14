import time
import requests
from .secret_manager import SecretManager  # Import the SecretManager class
from .logger_init import Logger  # Import your custom Logger class

class AlertOpsNotifier:
    """
    A class for sending notifications to AlertOps and managing alert lifecycle.
    """

    def __init__(
        self,
        secret_name: str,
        logger: Logger,
        secret_manager: SecretManager,
        closure_time: int = 300,
    ):
        """
        Initializes the AlertOpsNotifier.

        Args:
            secret_name (str): Secret name in Google Secret Manager for the API key.
            logger (object): Logger instance for logging.
            secret_manager (SecretManager): Instance of SecretManager.
            closure_time (int): Time (in seconds) to wait before closing alerts.
        """
        self.logger = logger
        self.closure_time = closure_time

        # Retrieve API key from SecretManager
        try:
            self.logger.info(f"Fetching AlertOps API key from Secret Manager: {secret_name}")
            self.api_key = secret_manager.get_secret(secret_name)
            self.alert_url = f"https://notify.alertops.com/POSTAlert/{self.api_key}/Custom"
        except Exception as e:
            self.logger.critical(f"Failed to retrieve AlertOps API key: {e}")
            raise

    def send_notification(
        self,
        source: str = "Unknown Source",
        severity: str = "Info",
        details: str = "No additional details provided.",
        priority: str = "High",
    ):
        """
        Sends a notification to AlertOps.

        Args:
            source (str, optional): The source of the issue (default: 'Unknown Source').
            severity (str, optional): The severity of the issue (default: 'Info').
            details (str, optional): Specific error message or description (default: 'No additional details provided.').
            priority (str, optional): The priority of the alert (default: 'High').
        """
        try:
            payload = {
                "message": f"{source}: {severity} issue reported",
                "priority": priority,
                "details": {
                    "source": source,
                    "severity": severity,
                    "description": details,
                },
            }
            headers = {"Content-Type": "application/json"}

            self.logger.info(f"Sending AlertOps notification: {payload}")
            response = requests.post(self.alert_url, headers=headers, json=payload)

            if response.status_code == 200:
                self.logger.info("AlertOps notification sent successfully.")
                token = token = response.json()
                if token:
                    self.schedule_alert_closure(token)
                else:
                    self.logger.warning("No token received in response.")
            else:
                self.logger.error(
                    f"Failed to send AlertOps notification. Status code: {response.status_code}\n"
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.logger.error(f"Error sending AlertOps notification: {e}")

    def schedule_alert_closure(self, token: str):
        """
        Schedules the alert closure after the configured delay.

        Args:
            token (str): The token of the alert to be closed.
        """
        try:
            self.logger.info(f"Scheduling alert closure for token: {token}")
            time.sleep(self.closure_time)  # Wait for the configured closure time
            self.close_alert(token)
        except Exception as e:
            self.logger.error(f"Error scheduling alert closure: {e}")

    def close_alert(self, token: str):
        """
        Closes the alert in AlertOps using the provided token.

        Args:
            token (str): The token of the alert to be closed.
        """
        try:
            payload = {
                "token": token,
                "status": "Closed",
            }
            headers = {"Content-Type": "application/json"}

            self.logger.info(f"Closing alert with token: {token}")
            response = requests.post(self.alert_url, headers=headers, json=payload)

            if response.status_code == 200:
                self.logger.info("Alert closed successfully.")
            else:
                self.logger.error(
                    f"Failed to close alert. Status code: {response.status_code}\n"
                    f"Response: {response.text}"
                )
        except Exception as e:
            self.logger.error(f"Error closing AlertOps notification: {e}")
