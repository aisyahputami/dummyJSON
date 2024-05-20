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

![airflow](https://github.com/aisyahputami/dummyJSON/blob/main/documentation/airflow.png)

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

![local](https://github.com/aisyahputami/dummyJSON/blob/main/documentation/Local%20Disk.png)

### Transfer Local Files to Google Cloud Storage
This step involves **transferring the locally stored JSON files for users, carts, posts, and todos to a specified Google Cloud Storage (GCS) bucket**. The **LocalFilesystemToGCSOperator** is used to handle the file transfer for each dataset.

![gcs](https://github.com/aisyahputami/dummyJSON/blob/main/documentation/GCS.png)

### Load Data from Google Cloud Storage to BigQuery
This step involves **loading JSON data files from Google Cloud Storage (GCS) into BigQuery tables**. The **GCSToBigQueryOperator** is used to load data for each dataset from GCS to BigQuery. Each dataset, including users, carts, posts, and todos, has its own task for loading data into the corresponding BigQuery table.

![bq](https://github.com/aisyahputami/dummyJSON/blob/main/documentation/bq_raw.png)

### Generate User Activity Summary Table
This step involves **generating a summary table named user_activity_summary in BigQuery**. The summary table aggregates data from multiple raw tables including raw_users, raw_carts, raw_posts, and raw_todos. The aggregation includes calculations such as total products, total quantity, total amount spent, post count, total reactions, total todos, completed todos, and pending todos for each user. The **BigQueryInsertJobOperator** is utilized to execute the SQL query for creating the summary table.

![summary](https://github.com/aisyahputami/dummyJSON/blob/main/documentation/bq_summary.png)

Based on the information available in the **user_activity_summary** table from the **week6** dataset in the **dfellowship12** project, we can draw several analytical conclusions that are useful for understanding user behavior and activities. Here are some analytical points based on the structure and data of the table:

**Analytical Conclusions**
1. **User Profile**
   **Columns**: user_id, firstName, lastName
   **Analysis**: These columns provide basic information about user identities. By combining data from these columns, we can build individual profiles for each user, which can be useful for personalizing services or marketing campaigns.

2. **Purchase Activity**
   **Columns**: total_products, total_quantity, total_amount
   **Analysis**:
    - total_products indicates the total number of products purchased by users.
    - total_quantity describes the total quantity of items purchased, providing insights into purchasing volume.
    - total_amount shows the total expenditure of users, which is important for identifying high-value customers.
  **Usage**: This data can be used for customer segmentation based on shopping habits and transaction value.
Social Interaction.

3. **Social Interaction**
  **Columns**: post_count, total_reactions
  **Analysis**:
    - post_count indicates how active users are in creating posts.
    - total_reactions indicates the level of interaction received by users in the form of reactions to their posts.
  **Usage**: This data is useful for identifying socially active users and those with high influence or engagement in the community.

4. **Task Management**
  **Columns**: total_todos, completed_todos, pending_todos
  **Analysis**:
    - total_todos indicates the total number of tasks created by users.
    - completed_todos shows the number of tasks that have been completed.
    - pending_todos indicates the number of tasks that are still pending.
  **Usage**: This information is useful for understanding the efficiency and productivity of users in completing tasks. It can also be used to provide reminders or incentives for users with many pending tasks.

**Additional Conclusion**
1. **User Segmentation**
    Using aggregated data from various activities, users can be grouped based on shopping profiles, social activities, and task management. For example, users who frequently shop and have many social interactions can be offered special deals or invited to loyalty programs.
Personalization and Targeting

2. **Personalization and Targeting**
    By understanding shopping habits and social activities, marketing campaigns can be customized to target users based on their preferences and habits. High-spending users could be offered special discounts, while socially active users could be utilized as influencers to promote products.
   
3. **Efficiency and Productivity**
    Data on completed and pending tasks provide insights into user efficiency. Training programs or automated reminders can be implemented to help users complete tasks on time.

**Recommendations**
1. **Analytical Dashboard**
    Create a dashboard displaying key metrics from this table to monitor user activity in real-time. This will aid in data-driven decision-making.
   
2. **Customized Marketing Campaigns**
    Use this data to run more targeted and relevant marketing campaigns for each user segment.
   
3. **Loyalty and Rewards Programs**
    Implement loyalty programs for high-spending users and those who are socially active to enhance retention and engagement.

By analyzing data from the **user_activity_summary** table, organizations can gain valuable insights into user behavior and develop more effective strategies to improve user experience and business value.
