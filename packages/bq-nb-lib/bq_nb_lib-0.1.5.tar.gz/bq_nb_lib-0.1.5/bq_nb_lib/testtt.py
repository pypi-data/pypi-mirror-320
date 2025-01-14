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
    def __init__(self, mixpanel_token_secret_name, logger, slack_notifier, alert_ops_notifier, secret_manager):
        """
        Initializes the MixpanelHandler.

        Args:
            mixpanel_token_secret_name (str): Secret name in Google Secret Manager for Mixpanel token.
            logger (Logger): Instance of Logger.
            slack_notifier (SlackNotifier): Instance of SlackNotifier for notifications.
            alert_ops_notifier (AlertOpsNotifier): Instance of AlertOpsNotifier for notifications.
            secret_manager (SecretManager): Instance of SecretManager to fetch secrets.
        """
        self.mixpanel_token_secret_name = mixpanel_token_secret_name
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
            self._handle_error(f"Error fetching Mixpanel token: {e}")

    def _handle_error(self, error_message):
        """
        Global error handler to log and notify.

        Args:
            error_message (str): Error message to handle.
        """
        self.logger.error(error_message)
        self.slack_notifier.error(error_message)
        self.alert_ops_notifier.send_notification(
            source="MixpanelHandler", severity="Critical", details=error_message, priority="High"
        )

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
                headers={"Authorization": f"Bearer {self.mixpanel_token}"},
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
            self._handle_error(f"Error fetching Mixpanel data: {e}")

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
            self._handle_error(f"Error processing Mixpanel JSON: {e}")

    def update_users(self, csv_file):
        """
        Updates user properties in Mixpanel based on a CSV file.

        Args:
            csv_file (str): Path to the CSV file containing user updates.
        """
        try:
            self.logger.info(f"Loading user updates from CSV: {csv_file}")
            df = pd.read_csv(csv_file)

            user_batches = self.divide_users_into_batches(df.to_dict(orient="records"))
            self.push_user_properties_batch(user_batches)
            self.logger.info(f"Completed user updates from {csv_file}.")
        except Exception as e:
            self._handle_error(f"Error updating users from CSV: {e}")

    def delete_user_properties(self, csv_file):
        """
        Deletes specified properties for users listed in a CSV file.

        Args:
            csv_file (str): Path to the CSV file containing user IDs and properties to delete.
        """
        try:
            self.logger.info(f"Loading user deletions from CSV: {csv_file}")
            df = pd.read_csv(csv_file)

            MIXPANEL_ENGAGE_URL = "https://api.mixpanel.com/engage/"

            user_batches = self.divide_users_into_batches(df.to_dict(orient="records"))

            for batch in user_batches:
                payload = []
                for user in batch:
                    payload.append({
                        "$token": self.mixpanel_token,
                        "$distinct_id": user.get("distinct_id"),
                        "$unset": user.get("properties_to_delete", []).split(",")
                    })

                response = requests.post(
                    MIXPANEL_ENGAGE_URL,
                    headers={"Content-Type": "application/json"},
                    data=json.dumps({"batch": payload}),
                )

                if response.status_code == 200:
                    self.logger.info(f"Successfully deleted properties for batch of users.")
                else:
                    self._handle_error(f"Failed to delete properties. HTTP Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self._handle_error(f"Error deleting user properties from CSV: {e}")

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

                payload = {"batch": [{"$token": self.mixpanel_token, **user} for user in batch]}

                response = requests.post(
                    MIXPANEL_ENGAGE_URL,
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(payload),
                )

                if response.status_code == 200:
                    result = response.json()
                    if result.get("status") == 1:
                        self.logger.info(f"Successfully updated batch of {len(batch)} user properties in Mixpanel.")
                        self.slack_notifier.success(f"Batch update successful for {len(batch)} users.")
                    else:
                        self._handle_error(f"Batch update failed. Mixpanel response: {result}")
                else:
                    self._handle_error(f"Failed to update batch. HTTP Status: {response.status_code}, Response: {response.text}")

            except Exception as e:
                self._handle_error(f"Error updating batch: {e}")

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
