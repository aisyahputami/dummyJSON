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

Deskripsi dari masing-masing tahapan adalah sebagai berikut.
