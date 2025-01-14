import requests
import json
from datetime import datetime
import re
import pandas as pd
from google.cloud import secretmanager
from google.cloud import bigquery
from .logger_init import Logger
from .slack_alert import SlackNotifier
from .alert_ops import AlertOpsNotifier
from .secret_manager import SecretManager


class MixpanelHandler:
    def __init__(self, mixpanel_token_secret_name, mixpanel_api_key, mixpanel_secret, logger, slack_notifier, alert_ops_notifier, secret_manager):
        """
        Initializes the MixpanelHandler.

        Args:
            mixpanel_token_secret_name (str): Secret name in Google Secret Manager for Mixpanel token.
            mixpanel_api_key (str): Mixpanel API key.
            mixpanel_secret (str): Mixpanel API secret.
            logger (Logger): Instance of Logger.
            slack_notifier (SlackNotifier): Instance of SlackNotifier for notifications.
            alert_ops_notifier (AlertOpsNotifier): Instance of AlertOpsNotifier for notifications.
            secret_manager (SecretManager): Instance of SecretManager to fetch secrets.
        """
        self.mixpanel_token_secret_name = mixpanel_token_secret_name
        self.mixpanel_api_key = mixpanel_api_key
        self.mixpanel_secret = mixpanel_secret
        self.logger = logger
        self.slack_notifier = slack_notifier
        self.alert_ops_notifier = alert_ops_notifier
        self.secret_manager = secret_manager
        self.mixpanel_token = self._get_mixpanel_token()

    def _get_mixpanel_token(self):
        """
        Retrieves the Mixpanel token from Google Secret Manager.

        Returns:
            str: Mixpanel token.
        """
        try:
            self.logger.info("Fetching Mixpanel token from Secret Manager...")
            token = self.secret_manager.get_secret(self.mixpanel_token_secret_name)
            if not token:
                raise ValueError("Mixpanel token is empty.")
            return token
        except Exception as e:
            error_msg = f"Error fetching Mixpanel token: {e}"
            self.logger.critical(error_msg)
            raise RuntimeError(error_msg)

    def fetch_mixpanel_data(self, mp_project_id, mp_workspace, mp_region, mp_bookmark, output_json):
        """
        Fetches data from Mixpanel API and saves it to a JSON file.

        Args:
            mp_project_id (str): Mixpanel project ID.
            mp_workspace (str): Mixpanel workspace ID.
            mp_region (str): Mixpanel region.
            mp_bookmark (str): Mixpanel bookmark ID.
            output_json (str): Path to save the output JSON file.
        """
        MIXPANEL_API_URL = f"https://{mp_region}.mixpanel.com/api/query/insights"
        try:
            self.logger.info(f"Fetching data from Mixpanel... {MIXPANEL_API_URL}")
            response = requests.get(
                MIXPANEL_API_URL,
                auth=(self.mixpanel_api_key, self.mixpanel_secret),
                params={
                    "project_id": mp_project_id,
                    "workspace_id": mp_workspace,
                    "bookmark_id": mp_bookmark
                }
            )
            response.raise_for_status()
            with open(output_json, "w") as f:
                json.dump(response.json(), f, indent=4)
            self.logger.info(f"Mixpanel data saved to: {output_json}")
            self.slack_notifier.success(f"Mixpanel data fetched and saved to {output_json}.")
        except Exception as e:
            error_msg = f"Error fetching Mixpanel data: {e}"
            self.logger.error(error_msg)
            self.slack_notifier.error(error_msg)
            self.alert_ops_notifier.send_notification(error_msg)

    def process_mixpanel_json(self, json_file, csv_file):
        """
        Processes Mixpanel JSON data and saves it to a structured CSV.

        Args:
            json_file (str): Path to the JSON file.
            csv_file (str): Path to the output CSV file.
        """
        try:
            self.logger.info(f"Processing Mixpanel JSON: {json_file}")
            with open(json_file, "r") as f:
                data = json.load(f)

            date_range = data.get("date_range", {})
            date_dim = datetime.fromisoformat(date_range.get("from_date")).strftime("%Y-%m-%d")
            series_data = data.get("series", {})

            rows = []
            for metric, platforms in series_data.items():
                cleaned_metric = re.sub(r"^[A-Z]\.\s*", "", metric).lower().replace(" ", "_")
                for platform, values in platforms.items():
                    if platform == "$overall":
                        continue
                    row = {"date_dim": date_dim, "platform": platform, cleaned_metric: values.get("all", 0)}
                    rows.append(row)

            df = pd.DataFrame(rows)
            df.to_csv(csv_file, index=False)
            self.logger.info(f"CSV file saved to: {csv_file}")
            self.slack_notifier.success(f"Mixpanel JSON processed and saved to {csv_file}.")
        except Exception as e:
            error_msg = f"Error processing Mixpanel JSON: {e}"
            self.logger.error(error_msg)
            self.slack_notifier.error(error_msg)
            self.alert_ops_notifier.send_notification(error_msg)

    def upload_to_bigquery(self, project_id, dataset_name, table_name, csv_file, unique_keys):
        """
        Appends data from a CSV file to BigQuery with deduplication.

        Args:
            project_id (str): BigQuery project ID.
            dataset_name (str): BigQuery dataset name.
            table_name (str): BigQuery table name.
            csv_file (str): Path to the CSV file.
            unique_keys (list): List of unique key columns for deduplication.
        """
        client = bigquery.Client(project=project_id)
        table_id = f"{project_id}.{dataset_name}.{table_name}"
        temp_table_id = f"{table_id}_temp"

        try:
            self.logger.info(f"Uploading data to temporary BigQuery table: {temp_table_id}")
            job_config = bigquery.LoadJobConfig(
                source_format=bigquery.SourceFormat.CSV,
                skip_leading_rows=1,
                autodetect=True,
                write_disposition="WRITE_TRUNCATE"
            )
            with open(csv_file, "rb") as source_file:
                load_job = client.load_table_from_file(source_file, temp_table_id, job_config=job_config)
            load_job.result()

            unique_condition = " AND ".join([f"target.{key} = source.{key}" for key in unique_keys])
            merge_query = f"""
            MERGE `{table_id}` AS target
            USING `{temp_table_id}` AS source
            ON {unique_condition}
            WHEN MATCHED THEN
              UPDATE SET target.* = source.*
            WHEN NOT MATCHED THEN
              INSERT ROW
            """
            client.query(merge_query).result()
            self.logger.info(f"Data merged into BigQuery table: {table_id}")
            self.slack_notifier.success(f"Data successfully uploaded to {table_id}.")
        except Exception as e:
            error_msg = f"Error uploading to BigQuery: {e}"
            self.logger.error(error_msg)
            self.slack_notifier.error(error_msg)
            self.alert_ops_notifier.send_notification(error_msg)

    def push_user_properties_batch(self, user_batches):
        """
        Push user properties to Mixpanel in batches.

        Args:
            user_batches (list): List of batches, where each batch is a list of user dictionaries.
        """
        MIXPANEL_ENGAGE_URL = "https://api.mixpanel.com/engage/"

        for batch in user_batches:
            try:
                self.logger.info(f"Pushing batch of {len(batch)} user properties to Mixpanel...")

                # Create the payload
                payload = {
                    "$token": self.mixpanel_token,
                    "batch": batch,
                }

                # Send the request
                response = requests.post(
                    MIXPANEL_ENGAGE_URL,
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(payload),
                )

                # Check response
                if response.status_code == 200:
                    result = response.json()
                    if result.get("status") == 1:
                        self.logger.info(f"Successfully updated batch of {len(batch)} user properties in Mixpanel.")
                        self.slack_notifier.success(f"Batch update successful for {len(batch)} users.")
                    else:
                        error_msg = f"Batch update failed. Mixpanel response: {result}"
                        self.logger.error(error_msg)
                        self.slack_notifier.error(error_msg)
                        self.alert_ops_notifier.send_notification(
                            source="MixpanelHandler", severity="Error", details=error_msg, priority="High"
                        )
                else:
                    error_msg = f"Failed to update batch. HTTP Status: {response.status_code}, Response: {response.text}"
                    self.logger.error(error_msg)
                    self.slack_notifier.error(error_msg)
                    self.alert_ops_notifier.send_notification(
                        source="MixpanelHandler", severity="Critical", details=error_msg, priority="High"
                    )

            except Exception as e:
                error_msg = f"Error updating batch: {e}"
                self.logger.error(error_msg)
                self.slack_notifier.error(error_msg)
                self.alert_ops_notifier.send_notification(
                    source="MixpanelHandler", severity="Critical", details=error_msg, priority="High"
                )

    def divide_users_into_batches(self, users, batch_size=2000):
        """
        Divides the user list into smaller batches.

        Args:
            users (list): List of user dictionaries.
            batch_size (int): Number of users per batch.

        Returns:
            list: List of user batches.
        """
        return [users[i:i + batch_size] for i in range(0, len(users), batch_size)]

    def update_users(self, users):
        """
        Updates user properties in Mixpanel for a large user list.

        Args:
            users (list): List of user dictionaries.
        """
        try:
            self.logger.info(f"Starting update for {len(users)} users...")
            user_batches = self.divide_users_into_batches(users)
            self.push_user_properties_batch(user_batches)
            self.logger.info(f"Completed update for {len(users)} users.")
        except Exception as e:
            error_msg = f"Error during user updates: {e}"
            self.logger.error(error_msg)
            self.slack_notifier.error(error_msg)
            self.alert_ops_notifier.send_notification(
                source="MixpanelHandler", severity="Critical", details=error_msg, priority="High"
            )
