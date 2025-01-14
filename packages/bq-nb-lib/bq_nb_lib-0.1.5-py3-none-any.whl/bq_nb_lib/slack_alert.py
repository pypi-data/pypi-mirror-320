import requests
import json
from datetime import datetime
from .secret_manager import SecretManager  # Import the SecretManager class
from .logger_init import Logger


class SlackNotifier:
    """
    A class for sending notifications to Slack using webhooks retrieved from Google Secret Manager or provided directly.
    """

    def __init__(
        self,
        logger: Logger,
        secret_manager: SecretManager,
        slack_channel_secret_list: list = None,
        direct_webhook_urls: list = None,
        slack_channel_secret_prefix: str = None,
        bucket_name: str = "default-bucket",
        webhook_url_prefix: str = "https://hooks.slack.com/services/",
        is_test: bool = False,
    ):
        """
        Initializes the SlackNotifier.

        Args:
            logger (object): Logger instance for logging.
            secret_manager (SecretManager): Instance of SecretManager.
            slack_channel_secret_list (list): List of specific secret names in Google Secret Manager for partial links.
            direct_webhook_urls (list): List of full or partial Slack webhook URLs provided directly.
            slack_channel_secret_prefix (str): Prefix for Slack channel secrets in Google Secret Manager.
            bucket_name (str): Name of the bucket for storing logs.
            webhook_url_prefix (str): Prefix for Slack webhook URLs.
            is_test (bool): Flag to indicate if messages are test messages (default: False).

        """
        self.logger = logger
        self.secret_manager = secret_manager
        self.slack_channel_secret_prefix = slack_channel_secret_prefix
        #self.bucket_name = bucket_name
        self.webhook_url_prefix = webhook_url_prefix
        self.is_test = is_test
        # Retrieve and combine URLs from secrets and direct input
        self.webhook_urls = self._retrieve_and_combine_webhook_urls(
            slack_channel_secret_list, direct_webhook_urls
        )

    def _is_partial_url(self, url: str) -> bool:
        """
        Checks if a URL is partial (does not include the full Slack webhook prefix).

        Args:
            url (str): The URL to check.

        Returns:
            bool: True if the URL is partial, False if it's full.
        """
        return not url.startswith(self.webhook_url_prefix)

    def _retrieve_and_combine_webhook_urls(self, secret_list: list, direct_urls: list) -> list:
        """
        Retrieves Slack webhook URLs from provided secret names and direct URLs, combines them uniquely.

        Args:
            secret_list (list): List of secret names to fetch from Secret Manager.
            direct_urls (list): List of full or partial webhook URLs provided directly.

        Returns:
            list: Unique Slack webhook URLs.
        """
        webhook_urls = set()  # Use a set to ensure uniqueness

        # Retrieve URLs from secrets
        if secret_list:
            self.logger.info(f"Fetching Slack webhook channels from Secret Manager.")
            for secret_name in secret_list:
                try:
                    partial_url = self.secret_manager.get_secret(secret_name)
                    full_url = (
                        f"{self.webhook_url_prefix}{partial_url}"
                        if self._is_partial_url(partial_url)
                        else partial_url
                    )
                    webhook_urls.add(full_url)
                except Exception as e:
                    self.logger.error(f"Error retrieving secret '{secret_name}': {e}")

        # Add direct URLs
        if direct_urls:
            self.logger.info(f"Adding provided direct webhook URLs.")
            for url in direct_urls:
                full_url = (
                    f"{self.webhook_url_prefix}{url}" if self._is_partial_url(url) else url
                )
                webhook_urls.add(full_url)

        # Convert to list for further use
        combined_webhook_urls = list(webhook_urls)
        self.logger.info(f"Combined Slack webhook URLs: {combined_webhook_urls}")
        return combined_webhook_urls

    def _send_message(self, message: str) -> None:
        """
        Sends the message to all Slack webhook URLs.

        Args:
            message (str): The message to send.
        """
        if self.is_test:
            message = f"🧪 *TEST MESSAGE* 🧪\n{message}"
        for webhook_url in self.webhook_urls:
            try:
                payload = {"text": message}
                headers = {"Content-Type": "application/json"}
                response = requests.post(webhook_url, data=json.dumps(payload), headers=headers)

                if response.status_code == 200:
                    self.logger.info(f"Slack message sent successfully to {webhook_url}.")
                else:
                    self.logger.error(f"Failed to send Slack message to {webhook_url}. Status code: {response.status_code}")
            except Exception as e:
                self.logger.error(f"Error sending Slack message to {webhook_url}: {e}")

    def _format_message(self, message: str) -> str:
        """
        Formats a message by adding a line break and a tab before each new line.

        Args:
            message (str): The message to format.

        Returns:
            str: The formatted message.
        """
        return "\n".join(f"\n\t{line.strip()}" for line in message.split("\n"))

    def success(self, success_message: str) -> None:
        """
        Sends a success message to Slack.

        Args:
            success_message (str): The success message content.
        """
        message = (
            f"✅ *Process Successful!*\n"
            f"📅 *Date*: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n"
            f"🔍 *Message*: ```{self._format_message(success_message)}```"
        )
        self._send_message(message)

    def error(self, error_message: str, failing_step: str = 'Not Provided') -> None:
        """
        Sends an error message to Slack.

        Args:
            error_message (str): The error message content.
            failing_step (str): The step where the error occurred.
        """
        message = (
            f"❌ *Process Failed!*\n"
            f"📅 *Date*: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n"
            f"🔍 *Error*: ```{self._format_message(error_message)}```\n"
            f"📄 *Step*: `{failing_step}`\n"
            #f"🔗 *Logs*: [View Logs](https://console.cloud.google.com/storage/browser/{self.bucket_name}/)\n"
            f"💡 *Note*: Please review and take necessary action."
        )
        self._send_message(message)

    def warning(self, warning_message: str, affected_step: str = 'Not Provided') -> None:
        """
        Sends a warning message to Slack.

        Args:
            warning_message (str): The warning message content.
            affected_step (str): The step where the warning occurred.
        """
        message = (
            f"⚠️ *Process Warning!*\n"
            f"📅 *Date*: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`\n"
            f"🔍 *Warning*: {self._format_message(warning_message)}\n"
            f"📄 *Step*: `{affected_step}`\n"
            #f"🔗 *Logs*: [View Logs](https://console.cloud.google.com/storage/browser/{self.bucket_name}/)\n"
            f"💡 *Note*: Please review and take necessary action."
        )
        self._send_message(message)
