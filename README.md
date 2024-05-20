# dummyJSON

## Background
Our business team needs data related to our users (users, their carts, their posts, and their todos). The data can be acquired from [dummyJSON](https://dummyjson.com/). Business team also needs you to generate any insights we can get from those data. You’ll collaborate with a data visualization expert that will create a dashboard for the business team. You need to provide summary tables for data visualization experts. Business team always uses this dashboard for daily check-in meetings at 08.00 WIB.

## Architecture
![architecture](https://github.com/aisyahputami/dummyJSON/blob/main/documentation/Architecture.png)

## Workflows
![workflows](https://github.com/aisyahputami/dummyJSON/blob/main/documentation/Workflows.png)

## Tasks
![tasks](https://github.com/aisyahputami/dummyJSON/blob/main/documentation/Tasks.png)

## Overview
The workflow steps are similar to the diagram in the Task above. However, before that, create connections on the Airflow Webserver consisting of:

1. A connection to link Airflow with the API.
2. A connection to link Airflow with Google Cloud Platform services.

![connection](https://github.com/aisyahputami/dummyJSON/blob/main/documentation/Connection.png)

The description of each step in the task execution process is as follows:

### Create a Dataset in Google BigQuery
The task create_assignment_dataset uses the **BigQueryCreateEmptyDatasetOperator** to create an empty dataset in Google BigQuery. It is identified by the task_id "**create_assignment_dataset**" and is part of the DAG specified by dag. The connection to Google Cloud Platform uses the credentials stored under the connection ID "google_cloud_default".

### Check API Availability
The **HttpSensor** tasks ensure that **the respective API endpoints (/users, /carts, /posts, /todos) are available** before the DAG proceeds with other operations that depend on these endpoints. This prevents downstream tasks from failing due to an unavailable API.

### Extract Data from API
This step, Extract Data from API, includes **tasks to extract users, carts, posts, and todos data from an API using the SimpleHttpOperator**. Each task performs a GET request to the respective endpoint (/users, /carts, /posts, and /todos) to retrieve the data. The response is checked to ensure the status code is 200 for successful extraction, and the response is logged for debugging purposes.

### Check for New Data and Branch
This step, Check for New Data and Branch, includes **tasks to check for new data in users, carts, posts, and todos datasets using the BranchPythonOperator**. Each task calls a Python function **check_if_last_row** to determine if there is new data in the respective dataset. The **op_kwargs** parameter specifies the current extraction task, the dataset object, and the next task to execute if new data is found. This setup ensures that the workflow only proceeds to storing the data if new data is available.

### Store Extracted Data
This step, Store Extracted Data, includes **tasks to store the extracted data for users, carts, posts, and todos into the designated storage or database**. Each task uses the **PythonOperator** to call the **store_object** function, passing in specific parameters to handle the respective dataset. The **op_kwargs** parameter specifies the extraction task, the dataset object name, the key for the last row variable, and the last row value. This setup ensures that the extracted data is properly stored and updated for each dataset.

### Transfer Local Files to Google Cloud Storage
This step involves **transferring the locally stored JSON files for users, carts, posts, and todos to a specified Google Cloud Storage (GCS) bucket**. The **LocalFilesystemToGCSOperator** is used to handle the file transfer for each dataset.

### Load Data from Google Cloud Storage to BigQuery
This step involves **loading JSON data files from Google Cloud Storage (GCS) into BigQuery tables**. The **GCSToBigQueryOperator** is used to load data for each dataset from GCS to BigQuery. Each dataset, including users, carts, posts, and todos, has its own task for loading data into the corresponding BigQuery table.

