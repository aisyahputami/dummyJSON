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
The **HttpSensor** tasks ensure that the respective API endpoints (/users, /carts, /posts, /todos) are available before the DAG proceeds with other operations that depend on these endpoints. This prevents downstream tasks from failing due to an unavailable API.
