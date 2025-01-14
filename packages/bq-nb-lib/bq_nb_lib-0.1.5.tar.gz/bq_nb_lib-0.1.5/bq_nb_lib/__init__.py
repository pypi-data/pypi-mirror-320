from .logger_init import Logger
from .slack_alert import SlackNotifier
from .alert_ops import AlertOpsNotifier
from .s3_handler import S3Handler  # Updated class name
from .secret_manager import SecretManager


def initialize_components (
    secret_project_name: str,
    bucket_name: str,
    s3_bucket_name: str,
    s3_region: str,
    access_key_id_secret_name: str,
    secret_key_secret_name: str,
    slack_channel_secret_list: list = None,
    direct_slack_webhook_urls: list = None,
    alert_ops_api_key_secret_name: str = None,
    log_file_prefix: str = "bigquery_notebook_logs",
    send_to_s3: bool = True,
    alert_to_slack: bool = True,
    alert_to_alert_ops: bool = True,
    alert_closure_time: int = 300,
    is_test : bool = False,
) -> dict:
    """
    Centralized initialization for Logger, SlackNotifier, AlertOpsNotifier, and S3Handler.

    Args:
        secret_project_name (str): GCP project containing secrets.
        bucket_name (str): Logging bucket name.
        s3_bucket_name (str): AWS S3 bucket for uploads.
        s3_region (str): AWS S3 region.
        access_key_id_secret_name (str): Secret name for AWS access key ID.
        secret_key_secret_name (str): Secret name for AWS secret key.
        slack_channel_secret_list (list, optional): List of Slack channel secrets in Secret Manager.
        direct_slack_webhook_urls (list, optional): List of direct Slack webhook URLs.
        alert_ops_api_key_secret_name (str, optional): Secret name for AlertOps API key.
        log_file_prefix (str, optional): Log file prefix (default: "bigquery_notebook_logs").
        send_to_s3 (bool): Flag to enable/disable S3 uploads.
        alert_to_slack (bool): Flag to enable/disable Slack notifications.
        alert_to_alert_ops (bool): Flag to enable/disable AlertOps notifications.
        alert_closure_time (int): Time (in seconds) to wait before closing alerts.

    Returns:
        dict: Initialized components (logger, slack_notifier, alert_ops_notifier, s3_handler).
    """
    # Initialize Logger
    logger = Logger(log_file_prefix=log_file_prefix)

    # Initialize SecretManager
    secret_manager = SecretManager(project_id=secret_project_name, logger=logger)
    

    # Initialize SlackNotifier
    slack_notifier = SlackNotifier(
        logger=logger,
        secret_manager=secret_manager,
        slack_channel_secret_list=slack_channel_secret_list,
        direct_webhook_urls=direct_slack_webhook_urls,
        bucket_name=bucket_name,
        is_test= is_test
    )

    # Initialize S3Handler
    s3_handler = S3Handler(
        s3_bucket_name=s3_bucket_name,
        s3_region=s3_region,
        access_key_id_secret_name=access_key_id_secret_name,
        secret_key_secret_name=secret_key_secret_name,
        secret_manager=secret_manager,
        slack_notifier=slack_notifier,
        alert_ops_notifier=None,  # Will be added later
        logger=logger,
        send_to_s3=send_to_s3,
        alert_to_slack=alert_to_slack,
        alert_to_alert_ops=alert_to_alert_ops,
    )

    # Initialize AlertOpsNotifier
    alert_ops_notifier = AlertOpsNotifier(
        secret_name=alert_ops_api_key_secret_name,
        logger=logger,
        secret_manager=secret_manager,
        closure_time=alert_closure_time,
    )

    # Set the AlertOpsNotifier in S3Handler to complete the circular dependency
    s3_handler.alert_ops_notifier = alert_ops_notifier

    return {
        "logger": logger,
        "slack_notifier": slack_notifier,
        "alert_ops_notifier": alert_ops_notifier,
        "s3_handler": s3_handler,
    }


__all__ = [
    "Logger",
    "SlackNotifier",
    "AlertOpsNotifier",
    "S3Handler",
    "initialize_components",
]
