import boto3
from .secret_manager import SecretManager
from .logger_init import Logger  # Import your custom Logger class


class S3Handler:
    """
    Utility class for managing AWS S3 interactions and notifications.
    """

    def __init__(
        self,
        s3_bucket_name: str,
        s3_region: str,
        access_key_id_secret_name: str,
        secret_key_secret_name: str,
        secret_manager: SecretManager,
        slack_notifier,
        alert_ops_notifier,
        logger: Logger,  # Explicitly specify Logger type
        send_to_s3: bool = True,
        alert_to_alert_ops: bool = True,
        alert_to_slack: bool = True,
    ):
        """
        Initializes S3Handler with configurations for AWS S3 and notifications.

        Args:
            s3_bucket_name (str): AWS S3 bucket for data uploads.
            bucket_name (str): GCP bucket for logs (used for notifications).
            s3_region (str): AWS S3 region.
            access_key_id_secret_name (str): Name of the secret for AWS access key ID.
            secret_key_secret_name (str): Name of the secret for AWS secret key.
            secret_manager (SecretManager): Instance of the new SecretManager class.
            slack_notifier (SlackNotifier): Instance for sending Slack notifications.
            alert_ops_notifier (AlertOpsNotifier): Instance for sending AlertOps notifications.
            logger (Logger): Instance of your custom Logger class.
            send_to_s3 (bool): Flag to enable/disable S3 uploads.
            alert_to_alert_ops (bool): Flag to enable/disable AlertOps notifications.
            alert_to_slack (bool): Flag to enable/disable Slack notifications.
        """
        self.s3_bucket_name = s3_bucket_name
        self.s3_region = s3_region
        self.access_key_id_secret_name = access_key_id_secret_name
        self.secret_key_secret_name = secret_key_secret_name
        self.secret_manager = secret_manager
        self.send_to_s3 = send_to_s3
        self.alert_to_alert_ops = alert_to_alert_ops
        self.alert_to_slack = alert_to_slack
        self.logger = logger
        self.slack_notifier = slack_notifier
        self.alert_ops_notifier = alert_ops_notifier
        self.s3_client = None

        # Initialize S3 client
        self.init_s3()

    def init_s3(self):
        """
        Initializes the S3 client with AWS credentials fetched from Secret Manager.
        """
        try:
            # Fetch AWS credentials
            self.logger.info("Fetching AWS credentials from Secret Manager.")
            aws_access_key_id = self.secret_manager.get_secret(self.access_key_id_secret_name)
            aws_secret_access_key = self.secret_manager.get_secret(self.secret_key_secret_name)

            if not aws_access_key_id or not aws_secret_access_key:
                raise ValueError("Failed to retrieve AWS credentials from Secret Manager.")

            # Initialize S3 client
            self.s3_client = boto3.client(
                "s3",
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=self.s3_region,
            )
            self.logger.info("S3 client initialized successfully.")
        except Exception as e:
            self.handle_error(
                error_message=f"Error initializing S3 client: {e}",
                failing_step="Init S3",
            )

    def upload_to_s3(self, file_path: str, s3_key_prefix: str = "daily_kpi_report"):
        """
        Uploads a file to S3.

        Args:
            file_path (str): Path to the local file to upload.
            s3_key_prefix (str): Prefix for the file in the S3 bucket.
        """
        if not self.send_to_s3:
            self.logger.info(f"Simulating S3 upload for testing: {file_path}")
            return

        s3_key = f"{s3_key_prefix}/{file_path.split('/')[-1]}"  # Generate S3 key

        try:
            self.s3_client.upload_file(file_path, self.s3_bucket_name, s3_key)
            self.logger.info(f"File successfully uploaded to S3: s3://{self.s3_bucket_name}/{s3_key}")
        except Exception as e:
            self.handle_error(
                error_message=f"S3 upload failed: {e}",
                failing_step="Upload to S3",
            )

    def handle_error(self, error_message: str, failing_step: str):
        """
        Handles errors by logging and sending notifications to Slack and AlertOps.

        Args:
            error_message (str): The error message to log and send.
            failing_step (str): The step where the error occurred.
        """
        self.logger.error(f"Error in step '{failing_step}': {error_message}")

        # Notify Slack
        if self.alert_to_slack and self.slack_notifier:
            try:
                self.slack_notifier.error(error_message, failing_step)
            except Exception as e:
                self.logger.error(f"Failed to send Slack notification: {e}")

        # Notify AlertOps
        if self.alert_to_alert_ops and self.alert_ops_notifier:
            try:
                self.alert_ops_notifier.send_notification(
                    message=error_message,
                    source=failing_step,
                    severity="Critical",
                    details=error_message,
                    priority="High",
                )
            except Exception as e:
                self.logger.error(f"Failed to send AlertOps notification: {e}")
