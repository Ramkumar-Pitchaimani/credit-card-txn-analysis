from datetime import datetime, timedelta
import uuid
from airflow import DAG
from airflow.providers.google.cloud.operators.dataproc import DataprocCreateBatchOperator
from airflow.providers.google.cloud.sensors.gcs import GCSObjectsWithPrefixExistenceSensor
from airflow.providers.google.cloud.transfers.gcs_to_gcs import GCSToGCSOperator
from airflow.utils.trigger_rule import TriggerRule

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
    'start_date': datetime(2025, 5, 30),
}

with DAG(
    dag_id="credit_card_transactions_dataproc_dag",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:

    gcs_bucket = "credit-card-data-analysis-dir"
    file_pattern = "transactions/transactions_"
    source_prefix = "transactions/"
    archive_prefix = "archive/"

    file_sensor = GCSObjectsWithPrefixExistenceSensor(
        task_id="check_json_file_arrival",
        bucket=gcs_bucket,
        prefix=file_pattern,
        timeout=600,
        poke_interval=30,
        mode="poke",
    )

    batch_id = f"credit-card-batch-{str(uuid.uuid4())[:8]}"

    batch_details = {
        "pyspark_batch": {
            "main_python_file_uri": "gs://credit-card-data-analysis-dir/spark_job/spark_job.py",
            #"jar_file_uris": [
            #    "gs://spark-lib/bigquery/spark-bigquery-with-dependencies_2.13-0.40.0.jar"
            #],
            # <-- Option-1: folder only, no wildcard
            "args": [
                "gs://credit-card-data-analysis-dir/transactions/"
            ],
        },
        "runtime_config": {
            "version": "2.2",
        },
        "environment_config": {
            "execution_config": {
                "service_account": "p101-473210@appspot.gserviceaccount.com",
                "network_uri": "projects/p101-473210/global/networks/default",
                "subnetwork_uri": "projects/p101-473210/regions/us-central1/subnetworks/default",
            }
        },
    }

    pyspark_task = DataprocCreateBatchOperator(
        task_id="run_credit_card_processing_job",
        batch=batch_details,
        batch_id=batch_id,
        project_id="p101-473210",
        region="us-central1",
        gcp_conn_id="google_cloud_default",
    )

    move_files_to_archive = GCSToGCSOperator(
        task_id="move_files_to_archive",
        source_bucket=gcs_bucket,
        source_object=source_prefix,
        destination_bucket=gcs_bucket,
        destination_object=archive_prefix,
        move_object=True,
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )

    file_sensor >> pyspark_task >> move_files_to_archive