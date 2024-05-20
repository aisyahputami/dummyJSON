import json
import os
from airflow import DAG
from airflow.models import Variable
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateEmptyDatasetOperator, BigQueryInsertJobOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "airflow",
    "email_on_failure": False,
    "email_on_retry": False,
    "email": "admin@localhost.com",
    "retries": 1,
    "retry_delay": timedelta(minutes=5)
}

DATASET_NAME = os.environ.get("GCP_DATASET_NAME", 'week6')
RAW_USER_TABLE_NAME = os.environ.get("GCP_RAW_USER_TABLE_NAME", 'raw_users')
RAW_CART_TABLE_NAME = os.environ.get("GCP_RAW_CHART_TABLE_NAME", 'raw_carts')
RAW_POST_TABLE_NAME = os.environ.get("GCP_RAW_POST_TABLE_NAME", 'raw_posts')
RAW_TODO_TABLE_NAME = os.environ.get("GCP_RAW_TODO_TABLE_NAME", 'raw_todos')
LOCAL_SINK_PATH = '/opt/airflow/dags/output/'
last_users_row = Variable.get('last_users_row', default_var=0)
last_carts_row = Variable.get('last_carts_row', default_var=0)
last_posts_row = Variable.get('last_posts_row', default_var=0)
last_todos_row = Variable.get('last_todos_row', default_var=0)

def check_if_last_row(task_now, object, next_task, **kwargs):
    ti = kwargs['ti']
    response = ti.xcom_pull(task_ids=task_now)
    data = json.loads(response) # str to dict
    if len (data[object]) == 0: return
    return next_task

def store_object(task_name, object_name, object_variable_key, object_variable_value, **kwargs):
    ti = kwargs['ti']
    api_data = ti.xcom_pull(task_ids=task_name)
    data = json.loads(api_data) # str to dict
    objects = data[object_name]
    last_object_id = object_variable_value
    with open(f"{LOCAL_SINK_PATH}{object_name}.json", 'w', encoding='utf8') as f:
        for obj in objects:
            f.write(f'{json.dumps(obj)}\n')
            last_object_id = obj["id"]
            Variable.set(object_variable_key, last_object_id)

with DAG(
    "weekly_assignment",
    start_date=datetime(2024, 5 ,17),
    schedule_interval="0 23 * * *",
    default_args=default_args,
    catchup=False,
    tags=['iykra'],
    ) as dag:

    create_assignment_dataset = BigQueryCreateEmptyDatasetOperator(
    task_id="create_assignment_dataset", dataset_id=DATASET_NAME, dag=dag, gcp_conn_id="google_cloud_default"
    )

    is_users_api_available_task = HttpSensor(
        task_id="is_users_api_available",
        http_conn_id='dummyjson_conn',
        endpoint='/users',
        timeout=10,
        mode='poke',
        poke_interval=60,
        retries=5,
    )

    is_carts_api_available_task = HttpSensor(
        task_id="is_carts_api_available",
        http_conn_id='dummyjson_conn',
        endpoint='/carts',
        timeout=10,
        mode='poke',
        poke_interval=60,
        retries=5,
    )

    is_posts_api_available_task = HttpSensor(
        task_id="is_posts_api_available",
        http_conn_id='dummyjson_conn',
        endpoint='/posts',
        timeout=10,
        mode='poke',
        poke_interval=60,
        retries=5,
    )

    is_todos_api_available_task = HttpSensor(
        task_id="is_todos_api_available",
        http_conn_id='dummyjson_conn',
        endpoint='/todos',
        timeout=10,
        mode='poke',
        poke_interval=60,
        retries=5,
    )

    extract_users_task = SimpleHttpOperator(
        task_id="extract_users_task",
        http_conn_id='dummyjson_conn',
        method='GET',
        endpoint=f'/users',
        headers={"Content-Type":"application/json"},
        log_response=True,
        response_check=lambda response: True if response.status_code == 200 else False
    )

    extract_carts_task = SimpleHttpOperator(
        task_id="extract_carts_task",
        http_conn_id='dummyjson_conn',
        method='GET',
        endpoint=f'/carts',
        headers={"Content-Type":"application/json"},
        log_response=True,
        response_check=lambda response: True if response.status_code == 200 else False
    )

    extract_posts_task = SimpleHttpOperator(
        task_id="extract_posts_task",
        http_conn_id='dummyjson_conn',
        method='GET',
        endpoint=f'/posts',
        headers={"Content-Type":"application/json"},
        log_response=True,
        response_check=lambda response: True if response.status_code == 200 else False
    )

    extract_todos_task = SimpleHttpOperator(
        task_id="extract_todos_task",
        http_conn_id='dummyjson_conn',
        method='GET',
        endpoint=f'/todos',
        headers={"Content-Type":"application/json"},
        log_response=True,
        response_check=lambda response: True if response.status_code == 200 else False
    )

    check_for_new_users_task = BranchPythonOperator(
        task_id="check_for_new_users_task",
        python_callable=check_if_last_row,
        op_kwargs={'task_now': "extract_users_task", 'object': "users", 'next_task': "store_users_task"}
    )

    check_for_new_carts_task = BranchPythonOperator(
        task_id="check_for_new_carts_task",
        python_callable=check_if_last_row,
        op_kwargs={'task_now': "extract_carts_task", 'object': "carts", 'next_task': "store_carts_task"}
    )

    check_for_new_posts_task = BranchPythonOperator(
        task_id="check_for_new_posts_task",
        python_callable=check_if_last_row,
        op_kwargs={'task_now': "extract_posts_task", 'object': "posts", 'next_task': "store_posts_task"}
    )

    check_for_new_todos_task = BranchPythonOperator(
        task_id="check_for_new_todos_task",
        python_callable=check_if_last_row,
        op_kwargs={'task_now': "extract_todos_task", 'object': "todos", 'next_task': "store_todos_task"}
    )

    store_users_task = PythonOperator(
        task_id="store_users_task",
        python_callable=store_object,
        op_kwargs={'task_name':"extract_users_task",
                   'object_name': "users",
                   'object_variable_key': "last_users_row",
                   'object_variable_value': last_users_row}
    )

    store_carts_task = PythonOperator(
        task_id="store_carts_task",
        python_callable=store_object,
        op_kwargs={'task_name':"extract_carts_task",
                   'object_name': "carts",
                   'object_variable_key': "last_carts_row",
                   'object_variable_value': last_carts_row}
    )

    store_posts_task = PythonOperator(
        task_id="store_posts_task",
        python_callable=store_object,
        op_kwargs={'task_name':"extract_posts_task",
                   'object_name': "posts",
                   'object_variable_key': "last_posts_row",
                   'object_variable_value': last_posts_row}
    )

    store_todos_task = PythonOperator(
        task_id="store_todos_task",
        python_callable=store_object,
        op_kwargs={'task_name':"extract_todos_task",
                   'object_name': "todos",
                   'object_variable_key': "last_todos_row",
                   'object_variable_value': last_todos_row}
    )

    users_local_to_gcs_task = LocalFilesystemToGCSOperator(
        task_id='users_transfer_to_gcs',
        src='/opt/airflow/dags/output/users.json',
        dst=f'output/users.json',
        bucket='week-6',
        dag=dag,
    )

    carts_local_to_gcs_task = LocalFilesystemToGCSOperator(
        task_id='carts_transfer_to_gcs',
        src='/opt/airflow/dags/output/carts.json',
        dst=f'output/carts.json',
        bucket='week-6',
        dag=dag,
    )

    posts_local_to_gcs_task = LocalFilesystemToGCSOperator(
        task_id='posts_transfer_to_gcs',
        src='/opt/airflow/dags/output/posts.json',
        dst=f'output/posts.json',
        bucket='week-6',
        dag=dag,
    )

    todos_local_to_gcs_task = LocalFilesystemToGCSOperator(
        task_id='todos_transfer_to_gcs',
        src='/opt/airflow/dags/output/todos.json',
        dst=f'output/todos.json',
        bucket='week-6',
        dag=dag,
    )

    load_users_to_bigquery_task = GCSToBigQueryOperator(
    task_id='load_users_to_bigquery_task',
    bucket='week-6',
    source_objects=['output/users.json'],
    destination_project_dataset_table=f"{DATASET_NAME}.{RAW_USER_TABLE_NAME}",
    source_format='NEWLINE_DELIMITED_JSON',
    write_disposition='WRITE_APPEND',
    autodetect=True,
    deferrable=True,
    dag=dag,
    )

    load_carts_to_bigquery_task = GCSToBigQueryOperator(
    task_id='load_carts_to_bigquery_task',
    bucket='week-6',
    source_objects=['output/carts.json'],
    destination_project_dataset_table=f"{DATASET_NAME}.{RAW_CART_TABLE_NAME}",
    source_format='NEWLINE_DELIMITED_JSON',
    write_disposition='WRITE_APPEND',
    autodetect=True,
    deferrable=True,
    dag=dag,
    )

    load_posts_to_bigquery_task = GCSToBigQueryOperator(
    task_id='load_posts_to_bigquery_task',
    bucket='week-6',
    source_objects=['output/posts.json'],
    destination_project_dataset_table=f"{DATASET_NAME}.{RAW_POST_TABLE_NAME}",
    source_format='NEWLINE_DELIMITED_JSON',
    write_disposition='WRITE_APPEND',
    autodetect=True,
    deferrable=True,
    dag=dag,
    )

    load_todos_to_bigquery_task = GCSToBigQueryOperator(
    task_id='load_todos_to_bigquery_task',
    bucket='week-6',
    source_objects=['output/todos.json'],
    destination_project_dataset_table=f"{DATASET_NAME}.{RAW_TODO_TABLE_NAME}",
    source_format='NEWLINE_DELIMITED_JSON',
    write_disposition='WRITE_APPEND',
    autodetect=True,
    deferrable=True,
    dag=dag,
    )

    user_activity_summary_query_job = BigQueryInsertJobOperator(
        task_id="user_activity_summary_query_job",
        configuration={
            "query": {
                "query": (
                    """
                    CREATE OR REPLACE TABLE `dfellowship12.week6.user_activity_summary` AS
                    SELECT 
                        u.id AS user_id, 
                        u.firstName, 
                        u.lastName, 
                        SUM(c.totalProducts) AS total_products, 
                        SUM(c.totalQuantity) AS total_quantity, 
                        SUM(c.total) AS total_amount, 
                        COUNT(p.id) AS post_count, 
                        SUM(p.reactions) AS total_reactions, 
                        COUNT(t.id) AS total_todos, 
                        SUM(CASE WHEN t.completed THEN 1 ELSE 0 END) AS completed_todos, 
                        SUM(CASE WHEN t.completed THEN 0 ELSE 1 END) AS pending_todos
                    FROM 
                        `dfellowship12.week6.raw_users` u
                    LEFT JOIN 
                        `dfellowship12.week6.raw_carts` c 
                    ON 
                        u.id = c.userId
                    LEFT JOIN 
                        `dfellowship12.week6.raw_posts` p 
                    ON 
                        u.id = p.userId
                    LEFT JOIN 
                        `dfellowship12.week6.raw_todos` t 
                    ON 
                        u.id = t.userId
                    GROUP BY 
                        u.id, u.firstName, u.lastName
                    ORDER BY 
                        total_amount DESC, post_count DESC, total_todos DESC
                    """
                ),
                "useLegacySql": False,
                "priority": "BATCH",
            }
        },
        location="US",
        gcp_conn_id="google_cloud_default",
        dag=dag,
    )


    #User Tasks
    create_assignment_dataset >> is_users_api_available_task >>\
    extract_users_task >> check_for_new_users_task >> store_users_task  >> users_local_to_gcs_task >>\
    load_users_to_bigquery_task

    #Cart Tasks
    create_assignment_dataset >> is_carts_api_available_task >>\
    extract_carts_task >> check_for_new_carts_task >> store_carts_task >> carts_local_to_gcs_task >>\
    load_carts_to_bigquery_task
    
    #Post Tasks
    create_assignment_dataset >> is_posts_api_available_task >>\
    extract_posts_task >> check_for_new_posts_task >> store_posts_task >> posts_local_to_gcs_task >>\
    load_posts_to_bigquery_task

    #Todo Tasks
    create_assignment_dataset >> is_todos_api_available_task >>\
    extract_todos_task >> check_for_new_todos_task >> store_todos_task >> todos_local_to_gcs_task >>\
    load_todos_to_bigquery_task

    user_activity_summary_query_job