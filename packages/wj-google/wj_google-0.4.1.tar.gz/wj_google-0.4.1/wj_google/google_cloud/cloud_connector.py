import ast
import os
import json
from google.oauth2.service_account import Credentials

import time
from typing import List, Any, Tuple, Dict, Optional
from google.cloud import storage
from google.cloud.storage import Bucket
from google.cloud import bigquery

from dotenv import load_dotenv

load_dotenv()


class GoogleCloud:

    def __init__(
        self, service: str, credentials: Optional[str] = None, scopes: Optional[List[str]] = None
    ) -> None:
        if not credentials:
            credentials = self._get_credentials_from_env()
        if service == "STORAGE":
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials
            self.storage_client = storage.Client()
        elif service == "BIGQUERY":
            credentials_s = Credentials.from_service_account_file(
                credentials, scopes=scopes
            )
            self.bigquery_client = bigquery.Client(credentials=credentials_s)
        else:
            messege = "Undefined the service {}".format(service)
            raise Exception(messege)
    
    def _get_credentials_from_env(self) -> str:
        """
        Reads the Google application credentials from the JSON file specified by the
        GCP_CREDENTIALS environment variable and returns the path to the JSON file.
        """
        credentials_value = os.getenv('GCP_CREDENTIALS')
        if not credentials_value:
            raise EnvironmentError("GCP_CREDENTIALS environment variable not set")

        try:
            credential_dict = ast.literal_eval(credentials_value)
            temp_credentials_path = 'temp_credentials.json'
            with open(temp_credentials_path, 'w') as temp_file:
                json.dump(credential_dict, temp_file)
            return temp_credentials_path
        except FileNotFoundError:
            raise FileNotFoundError(f"Credentials file not found at path: {temp_credentials_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Error decoding JSON from the credentials file at path: {credential_dict}")


class GoogleStorage(GoogleCloud):

    def create_bucket(
        self, bucket_name: str, storage_class="STANDARD", location="us-central1"
    ) -> Bucket:
        try:
            bucket = self.storage_client.bucket(bucket_name)
            bucket.storage_class = storage_class

            bucket = self.storage_client.create_bucket(bucket, location)
            return bucket
        except Exception as e:
            print(e)

            return None

    def upload_file(
        self, bucket_name: str, source_file_name: str, destination_file_name: str
    ) -> bool:
        try:
            bucket = self.storage_client.bucket(bucket_name)

            blob = bucket.blob(destination_file_name)
            blob.upload_from_filename(source_file_name)

            return True
        except Exception as e:
            print(e)

            return False

    def download_file(
        self, bucket_name: str, file_name: str, destination_file: str
    ) -> bool:
        try:
            bucket = self.storage_client.bucket(bucket_name)

            blob = bucket.blob(file_name)
            blob.download_to_filename(destination_file)

            return True
        except Exception as e:
            print(e)

            return False

    def list_files(self, bucket_name: str) -> List[str]:
        try:
            file_list = self.storage_client.list_blobs(bucket_name)
            return [file.name for file in file_list]
        except Exception as e:
            print(e)

            return []


class GoogleBigQuery(GoogleCloud):

    def sql_query(self, query: str):  # TODO: See type of object
        return self.bigquery_client.query(query)

    def table_reference(self, dataset_name: str, table_name: str) -> Tuple[Any, Any]:
        data_reference = bigquery.DatasetReference(
            self.bigquery_client.project, dataset_name
        )
        table_reference = bigquery.TableReference(data_reference, table_name)

        return data_reference, table_reference

    def add_table_labels(self, labels: Dict, dataset_name: str, table_name: str) -> Any:
        _, table_reference = self.table_reference(
            dataset_name=dataset_name, table_name=table_name
        )
        table = self.bigquery_client.get_table(table_reference)
        table.labels = labels
        return self.bigquery_client.update_table(table, ["labels"])

    def delete_table_labels(self, dataset_name: str, table_name: str) -> Any:
        _, table_reference = self.table_reference(
            dataset_name=dataset_name, table_name=table_name
        )
        table = self.bigquery_client.get_table(table_reference)
        labels = table.labels
        table.labels = {k: None for k, v in labels.items()}
        return self.bigquery_client.update_table(table, ["labels"])

    def save_query_as_table(
        self, query: str, destination_dataset_name: str, destination_table_name: str
    ):
        destination_dataset_reference = self.bigquery_client.dataset(
            destination_dataset_name, self.bigquery_client.project
        )
        destination_dataset = self.bigquery_client.get_dataset(
            destination_dataset_reference
        )

        destination_table_reference = destination_dataset_reference.table(
            destination_table_name
        )

        query_job_config = bigquery.QueryJobConfig()
        query_job_config.destination = destination_table_reference

        query_job = self.bigquery_client.query(
            query=query,
            location=destination_dataset.location,
            job_config=query_job_config,
        )

        while query_job.state != "DONE":
            time.sleep(1)
            query_job.reload()

    #TODO: Expand params
    def insert_row_in_table(self, table_id: str, rows: List[Dict]):
         #TODO: Verify table schema and rows list
         errors = self.bigquery_client.insert_rows_json(table=table_id, json_rows=rows)
         return errors

    #TODO: def export_queries_to_excel(self, queries: List[str]):
