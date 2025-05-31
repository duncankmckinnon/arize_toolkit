# Data Import Tools

## Overview

The Arize Toolkit provides comprehensive tools for importing data from various sources into Arize. You can import data from cloud storage (S3, GCS, Azure) or directly from databases (BigQuery, Snowflake, Databricks). For more information about data ingestion in Arize, check out the **[Arize data ingestion documentation](https://docs.arize.com/arize/data-ingestion)**.

In `arize_toolkit`, the `Client` exposes helpers for:

1. Creating file import jobs from cloud storage providers
1. Creating table import jobs from databases
1. Monitoring the status of import jobs
1. Updating existing import jobs with new configurations
1. Deleting import jobs to stop data ingestion
1. Managing the complete lifecycle of data import operations

For completeness, the full set of data import helpers is repeated below.
Click on the function name to jump to the detailed section.

| Operation | Helper |
|-----------|--------|
| Create a file import job | [`create_file_import_job`](#create_file_import_job) |
| Get file import job status | [`get_file_import_job`](#get_file_import_job) |
| List all file import jobs | [`get_all_file_import_jobs`](#get_all_file_import_jobs) |
| Update a file import job | [`update_file_import_job`](#update_file_import_job) |
| Delete a file import job | [`delete_file_import_job`](#delete_file_import_job) |
| Create a table import job | [`create_table_import_job`](#create_table_import_job) |
| Get table import job status | [`get_table_import_job`](#get_table_import_job) |
| List all table import jobs | [`get_all_table_import_jobs`](#get_all_table_import_jobs) |
| Update a table import job | [`update_table_import_job`](#update_table_import_job) |
| Delete a table import job | [`delete_table_import_job`](#delete_table_import_job) |

## File Import Operations

File import jobs allow you to import data from cloud storage providers like Amazon S3, Google Cloud Storage, and Azure Storage.

______________________________________________________________________

### `create_file_import_job`

```python
import_job: dict = client.create_file_import_job(
    blob_store: Literal["s3", "gcs", "azure"],
    bucket_name: str,
    prefix: str,
    model_name: str,
    model_type: str,
    model_schema: dict,
    model_environment_name: Literal["production", "validation", "training", "tracing"] = "production",
    model_version: str | None = None,     # optional
    batch_id: str | None = None,          # optional
    dry_run: bool = False,                # optional
    azure_storage_identifier: dict | None = None,  # optional - required for azure
)
```

Creates a new file import job to ingest data from cloud storage into Arize.

**Parameters**

- `blob_store` – The cloud storage provider (`"s3"`, `"gcs"`, or `"azure"`)
- `bucket_name` – Name of the storage bucket
- `prefix` – Path prefix within the bucket (e.g., `"data/predictions/"`)
- `model_name` – *Human-readable* name for the model in Arize
- `model_type` – Type of model (`"classification"`, `"regression"`, `"ranking"`, `"multi_class"`, `"object_detection"`)
- `model_schema` – Schema mapping your data columns to Arize's data model (see [Model Schema Configuration](#model-schema-configuration))
- `model_environment_name` (optional) – Environment for the data. Defaults to `"production"`
- `model_version` (optional) – Version identifier for the model
- `batch_id` (optional) – Batch identifier for validation data
- `dry_run` (optional) – If `True`, validates configuration without creating the job
- `azure_storage_identifier` (optional) – Required for Azure storage. Dict with `tenantId` and `storageAccountName`

**Returns**

A dictionary containing:

- `id` – Unique identifier for the import job
- `jobId` – Job identifier (same as `id`)
- `jobStatus` – Current status (`"active"`, `"inactive"`, `"deleted"`)
- `totalFilesPendingCount` – Number of files waiting to be processed
- `totalFilesSuccessCount` – Number of successfully imported files
- `totalFilesFailedCount` – Number of failed files

**Example**

```python
import_job = client.create_file_import_job(
    blob_store="s3",
    bucket_name="my-ml-data",
    prefix="predictions/daily/",
    model_name="fraud-detector",
    model_type="classification",
    model_schema={
        "predictionLabel": "predicted_fraud",
        "actualLabel": "actual_fraud",
        "predictionId": "transaction_id",
        "timestamp": "prediction_timestamp",
    },
    model_environment_name="production",
)
print(f"Created job: {import_job['jobId']}")
```

______________________________________________________________________

### `get_file_import_job`

```python
job_status: dict = client.get_file_import_job(job_id: str)
```

Retrieves the current status of a file import job.

**Parameters**

- `job_id` – The unique identifier of the import job

**Returns**

A dictionary containing:

- `id` – Unique identifier for the import job
- `jobId` – Job identifier (same as `id`)
- `jobStatus` – Current status (`"active"`, `"inactive"`, `"deleted"`)
- `totalFilesPendingCount` – Number of files waiting to be processed
- `totalFilesSuccessCount` – Number of successfully imported files
- `totalFilesFailedCount` – Number of failed files
- `createdAt` – Timestamp when the job was created
- `modelName` – Name of the associated model
- `modelId` – ID of the associated model

**Example**

```python
status = client.get_file_import_job("job123")
print(f"Status: {status['jobStatus']}")
print(
    f"Progress: {status['totalFilesSuccessCount']} / "
    f"{status['totalFilesSuccessCount'] + status['totalFilesPendingCount']}"
)
```

______________________________________________________________________

### `get_all_file_import_jobs`

```python
all_jobs: list[dict] = client.get_all_file_import_jobs()
```

Retrieves all file import jobs for the current space.

**Returns**

A list of dictionaries, each containing:

- `id` – Unique identifier for the import job
- `jobId` – Job identifier (same as `id`)
- `jobStatus` – Current status
- `totalFilesPendingCount` – Number of pending files
- `totalFilesSuccessCount` – Number of successful files
- `totalFilesFailedCount` – Number of failed files
- `createdAt` – Creation timestamp
- `modelName` – Associated model name

**Example**

```python
all_jobs = client.get_all_file_import_jobs()
active_jobs = [job for job in all_jobs if job["jobStatus"] == "active"]
print(f"Active import jobs: {len(active_jobs)}")
```

______________________________________________________________________

### `update_file_import_job`

```python
updated_job: dict = client.update_file_import_job(
    job_id: str,
    job_status: Literal["active", "inactive"] | None = None,  # optional
    model_schema: dict,  # required
)
```

Updates an existing file import job. Can be used to pause/resume jobs or update the schema configuration.

**Parameters**

- `job_id` – The unique identifier of the import job
- `job_status` (optional) – New status for the job (`"active"` or `"inactive"`)
- `model_schema` – Updated schema configuration. **Note:** Must always be provided, even if only updating status

**Returns**

A dictionary containing the updated job information with the same fields as `get_file_import_job`.

**Example**

```python
# Pause an active job
updated_job = client.update_file_import_job(
    job_id="job123",
    job_status="inactive",
    model_schema={
        "predictionLabel": "predicted_fraud",
        "actualLabel": "actual_fraud",
        "predictionId": "transaction_id",
        "timestamp": "prediction_timestamp",
    },
)
print(f"Job paused: {updated_job['jobStatus'] == 'inactive'}")
```

______________________________________________________________________

### `delete_file_import_job`

```python
deleted_job: dict = client.delete_file_import_job(job_id: str)
```

Permanently deletes a file import job. This action cannot be undone.

**Parameters**

- `job_id` – The unique identifier of the import job to delete

**Returns**

A dictionary containing:

- `jobStatus` – Final status (usually `"deleted"`)

**Example**

```python
deleted_job = client.delete_file_import_job("job123")
if deleted_job["jobStatus"] == "deleted":
    print("Job successfully deleted")
```

______________________________________________________________________

## Table Import Operations

Table import jobs allow you to import data directly from databases like BigQuery, Snowflake, and Databricks.

______________________________________________________________________

### `create_table_import_job`

```python
import_job: dict = client.create_table_import_job(
    table_store: Literal["BigQuery", "Snowflake", "Databricks"],
    model_name: str,
    model_type: str,
    model_schema: dict,
    bigquery_table_config: dict | None = None,      # required for BigQuery
    snowflake_table_config: dict | None = None,     # required for Snowflake
    databricks_table_config: dict | None = None,    # required for Databricks
    model_environment_name: Literal["production", "validation", "training", "tracing"] = "production",
    model_version: str | None = None,                # optional
    batch_id: str | None = None,                     # optional
    dry_run: bool = False,                           # optional
)
```

Creates a new table import job to ingest data from a database into Arize.

**Parameters**

- `table_store` – The database type (`"BigQuery"`, `"Snowflake"`, or `"Databricks"`)
- `model_name` – *Human-readable* name for the model in Arize
- `model_type` – Type of model (`"classification"`, `"regression"`, `"ranking"`, `"multi_class"`, `"object_detection"`)
- `model_schema` – Schema mapping your data columns to Arize's data model
- `bigquery_table_config` (conditional) – Required for BigQuery. See [BigQuery Configuration](#bigquery-configuration)
- `snowflake_table_config` (conditional) – Required for Snowflake. See [Snowflake Configuration](#snowflake-configuration)
- `databricks_table_config` (conditional) – Required for Databricks. See [Databricks Configuration](#databricks-configuration)
- `model_environment_name` (optional) – Environment for the data. Defaults to `"production"`
- `model_version` (optional) – Version identifier for the model
- `batch_id` (optional) – Batch identifier for validation data
- `dry_run` (optional) – If `True`, validates configuration without creating the job

**Returns**

A dictionary containing:

- `id` – Unique identifier for the import job
- `jobId` – Job identifier (same as `id`)
- `jobStatus` – Current status (`"active"`, `"inactive"`, `"deleted"`)
- `totalQueriesPendingCount` – Number of queries waiting to execute
- `totalQueriesSuccessCount` – Number of successful queries
- `totalQueriesFailedCount` – Number of failed queries

**Example**

```python
import_job = client.create_table_import_job(
    table_store="BigQuery",
    model_name="revenue-predictor",
    model_type="regression",
    model_schema={
        "predictionScore": "predicted_revenue",
        "actualScore": "actual_revenue",
        "predictionId": "prediction_id",
        "timestamp": "prediction_date",
    },
    bigquery_table_config={
        "projectId": "my-gcp-project",
        "dataset": "ml_predictions",
        "tableName": "revenue_predictions",
    },
)
print(f"Created table import job: {import_job['jobId']}")
```

______________________________________________________________________

### `get_table_import_job`

```python
job_status: dict = client.get_table_import_job(job_id: str)
```

Retrieves the current status of a table import job.

**Parameters**

- `job_id` – The unique identifier of the import job

**Returns**

A dictionary containing:

- `id` – Unique identifier for the import job
- `jobId` – Job identifier (same as `id`)
- `jobStatus` – Current status
- `totalQueriesPendingCount` – Number of pending queries
- `totalQueriesSuccessCount` – Number of successful queries
- `totalQueriesFailedCount` – Number of failed queries
- Additional fields including table configuration and model information

**Example**

```python
status = client.get_table_import_job("job456")
print(f"Queries executed: {status['totalQueriesSuccessCount']}")
```

______________________________________________________________________

### `get_all_table_import_jobs`

```python
all_jobs: list[dict] = client.get_all_table_import_jobs()
```

Retrieves all table import jobs for the current space.

**Returns**

A list of dictionaries with the same structure as `get_table_import_job`.

**Example**

```python
all_jobs = client.get_all_table_import_jobs()
for job in all_jobs:
    print(f"{job['modelName']}: {job['table']} ({job['tableStore']})")
```

______________________________________________________________________

### `update_table_import_job`

```python
updated_job: dict = client.update_table_import_job(
    job_id: str,
    model_schema: dict,                               # required
    job_status: Literal["active", "inactive"] | None = None,      # optional
    model_version: str | None = None,                 # optional
    refresh_interval: int | None = None,              # optional
    query_window_size: int | None = None,             # optional
)
```

Updates an existing table import job with new configuration or ingestion parameters.

**Parameters**

- `job_id` – The unique identifier of the import job
- `model_schema` – Updated schema configuration. **Note:** Must always be provided
- `job_status` (optional) – New status for the job (`"active"` or `"inactive"`)
- `model_version` (optional) – Updated model version
- `refresh_interval` (optional) – How often to refresh data, in minutes
- `query_window_size` (optional) – Size of the query window, in hours

**Returns**

A dictionary containing the updated job information.

**Example**

```python
# Update ingestion parameters
updated_job = client.update_table_import_job(
    job_id="job456",
    model_schema={
        "predictionScore": "predicted_revenue",
        "actualScore": "actual_revenue",
        "predictionId": "prediction_id",
        "timestamp": "prediction_date",
    },
    refresh_interval=30,  # Every 30 minutes
    query_window_size=24,  # Last 24 hours
)
```

______________________________________________________________________

### `delete_table_import_job`

```python
deleted_job: dict = client.delete_table_import_job(job_id: str)
```

Permanently deletes a table import job. This action cannot be undone.

**Parameters**

- `job_id` – The unique identifier of the import job to delete

**Returns**

A dictionary containing:

- `jobStatus` – Final status (usually `"deleted"`)

**Example**

```python
deleted_job = client.delete_table_import_job("job456")
print(f"Deletion status: {deleted_job['jobStatus']}")
```

______________________________________________________________________

## Model Schema Configuration

The model schema defines how your data columns map to Arize's data model. The schema varies based on your model type.

### Common Fields (All Model Types)

All model types **require** these fields:

- `predictionId` (str): Column containing unique prediction identifiers
- `timestamp` (str): Column containing timestamps for predictions

All model types can **optionally** include:

- `features` (str): Prefix for feature column names (e.g., "feature\_")
- `featuresList` (List[str]): List of specific feature column names
- `tags` (str): Prefix for tag column names (e.g., "tag\_")
- `tagsList` (List[str]): List of specific tag column names
- `batchId` (str): Column containing batch identifiers
- `shapValues` (str): Prefix for SHAP value columns
- `version` (str): Column containing model version information
- `exclude` (List[str]): List of columns to exclude from import
- `embeddingFeatures` (List[dict]): Configuration for embedding features:
  ```python
  {
      "featureName": "text_embedding",
      "vectorCol": "embedding_vector_column",
      "rawDataCol": "raw_text_column",
      "linkToDataCol": "image_url_column",  # Optional, for images/videos
  }
  ```

### Model Type Specific Fields

#### Classification Models

```python
from arize_toolkit.models import ClassificationSchemaInput, EmbeddingFeatureInput

schema = ClassificationSchemaInput(
    predictionLabel="prediction_column",  # Required
    predictionScores="prediction_scores_column",  # Optional
    actualLabel="actual_label_column",  # Optional
    actualScores="actual_scores_column",  # Optional
    predictionId="id_column",  # Required
    timestamp="timestamp_column",  # Required
    features="feature_",  # Optional
    tags="tag_",  # Optional
    embeddingFeatures=[
        EmbeddingFeatureInput(
            featureName="text_embedding",
            vectorCol="embedding_vector_column",
            rawDataCol="raw_text_column",
        )
    ],
)

# as dictionary
schema_dict = {
    "predictionLabel": "prediction_column",
    "predictionScores": "prediction_scores_column",
    "actualLabel": "actual_label_column",
    "actualScores": "actual_scores_column",
    "predictionId": "id_column",
    "timestamp": "timestamp_column",
    "features": "feature_",
    "tags": "tag_",
    "embeddingFeatures": [
        {
            "featureName": "text_embedding",
            "vectorCol": "embedding_vector_column",
            "rawDataCol": "raw_text_column",
        }
    ],
}
```

#### Regression Models

```python
from arize_toolkit.models import RegressionSchemaInput

schema = RegressionSchemaInput(
    predictionScore="prediction_value_column",  # Required
    actualScore="actual_value_column",  # Optional
    predictionId="id_column",
    timestamp="timestamp_column",
)
```

#### Ranking Models

```python
from arize_toolkit.models import RankSchemaInput

schema = RankSchemaInput(
    rank="rank_column",  # Required
    predictionGroupId="group_id_column",  # Required
    predictionScores="scores_column",  # Optional
    relevanceScore="relevance_score_column",  # Optional
    relevanceLabel="relevance_label_column",  # Optional
    predictionId="id_column",  # Required
    timestamp="timestamp_column",  # Required
    features_list=["feature_1", "feature_2"],  # Optional
    tags_list=["tag_1", "tag_2"],  # Optional
)

# as dictionary
schema_dict = {
    "rank": "rank_column",
    "predictionGroupId": "group_id_column",
    "predictionScores": "scores_column",
    "relevanceScore": "relevance_score_column",
    "relevanceLabel": "relevance_label_column",
    "predictionId": "id_column",
    "timestamp": "timestamp_column",
    "features_list": ["feature_1", "feature_2"],
    "tags_list": ["tag_1", "tag_2"],
}
```

#### Multi-Class Models

```python
from arize_toolkit.models import MultiClassSchemaInput

schema = MultiClassSchemaInput(
    predictionScores="prediction_scores_column",  # Required
    actualScores="actual_scores_column",  # Optional
    thresholdScores="threshold_scores_column",  # Optional
    predictionId="id_column",  # Required
    timestamp="timestamp_column",  # Required
    features_list=["feature_1", "feature_2"],  # Optional
    tags_list=["tag_1", "tag_2"],  # Optional
)

# as dictionary
schema_dict = {
    "predictionScores": "prediction_scores_column",
    "actualScores": "actual_scores_column",
    "thresholdScores": "threshold_scores_column",
    "predictionId": "id_column",
    "timestamp": "timestamp_column",
    "features_list": ["feature_1", "feature_2"],
    "tags_list": ["tag_1", "tag_2"],
}
```

#### Object Detection Models

```python
from arize_toolkit.models import ObjectDetectionSchemaInput, ObjectDetectionInput

schema = ObjectDetectionSchemaInput(
    predictionObjectDetection=ObjectDetectionInput(
        boundingBoxesCoordinatesColumnName="pred_coordinates_column",  # Required
        boundingBoxesCategoriesColumnName="pred_categories_column",  # Required
        boundingBoxesScoresColumnName="pred_scores_column",  # Optional
    ),
    actualObjectDetection=ObjectDetectionInput(  # Optional
        boundingBoxesCoordinatesColumnName="actual_coordinates_column",
        boundingBoxesCategoriesColumnName="actual_categories_column",
        boundingBoxesScoresColumnName="actual_scores_column",
    ),
    predictionId="id_column",  # Required
    timestamp="timestamp_column",  # Required
    features_list=["feature_1", "feature_2"],  # Optional
    tags_list=["tag_1", "tag_2"],  # Optional
)

# as dictionary
schema_dict = {
    "predictionObjectDetection": {
        "boundingBoxesCoordinatesColumnName": "pred_coordinates_column",
        "boundingBoxesCategoriesColumnName": "pred_categories_column",
        "boundingBoxesScoresColumnName": "pred_scores_column",
    },
    "actualObjectDetection": {
        "boundingBoxesCoordinatesColumnName": "actual_coordinates_column",
        "boundingBoxesCategoriesColumnName": "actual_categories_column",
        "boundingBoxesScoresColumnName": "actual_scores_column",
    },
    "predictionId": "id_column",
    "timestamp": "timestamp_column",
    "features_list": ["feature_1", "feature_2"],
    "tags_list": ["tag_1", "tag_2"],
}
```

______________________________________________________________________

## Table Configuration

### BigQuery Configuration

```python
from arize_toolkit.models import BigQueryTableConfig

config = BigQueryTableConfig(
    projectId="your-gcp-project", dataset="your-dataset", tableName="your-table"
)
```

### Snowflake Configuration

```python
from arize_toolkit.models import SnowflakeTableConfig

config = SnowflakeTableConfig(
    accountID="your-account",
    snowflakeSchema="your-schema",  # Note: Uses 'schema' alias in API
    database="your-database",
    tableName="your-table",
)
```

### Databricks Configuration

```python
from arize_toolkit.models import DatabricksTableConfig

config = DatabricksTableConfig(
    hostName="your-databricks-host.cloud.databricks.com",
    endpoint="/sql/1.0/endpoints/your-endpoint-id",
    port="443",
    catalog="your-catalog",
    databricksSchema="your-schema",
    tableName="your-table",
    token="your-access-token",  # Optional
    azureResourceId="resource-id",  # Optional, for Azure Databricks
    azureTenantId="tenant-id",  # Optional, for Azure Databricks
)
```

______________________________________________________________________

## Examples by Model Type

### Classification Model Example

```python
# File import for classification model
import_job = client.create_file_import_job(
    blob_store="s3",
    bucket_name="ml-data-bucket",
    prefix="fraud-detection/predictions/",
    model_name="fraud-detector",
    model_type="classification",
    model_schema={
        "predictionLabel": "predicted_fraud",
        "predictionScores": "fraud_probability",
        "actualLabel": "actual_fraud",
        "predictionId": "transaction_id",
        "timestamp": "prediction_timestamp",
        "features": "feature_",  # Will import feature_amount, feature_merchant, etc.
        "tags": "tag_",  # Will import tag_region, tag_device_type, etc.
        "embeddingFeatures": [
            {
                "featureName": "transaction_description_embedding",
                "vectorCol": "description_vector",
                "rawDataCol": "transaction_description",
            }
        ],
    },
    model_version="v2.1",
    model_environment_name="production",
)
```

### Regression Model Example

```python
# Table import for regression model
import_job = client.create_table_import_job(
    table_store="Snowflake",
    model_name="price-predictor",
    model_type="regression",
    model_schema={
        "predictionScore": "predicted_price",
        "actualScore": "actual_price",
        "predictionId": "prediction_id",
        "timestamp": "prediction_date",
        "featuresList": ["product_category", "brand", "condition", "market_segment"],
        "shapValues": "shap_",  # Will import shap_product_category, shap_brand, etc.
    },
    snowflake_table_config={
        "accountID": "myaccount",
        "schema": "ML_PREDICTIONS",  # Note: You can use "schema" here - it will be converted to "snowflakeSchema" automatically
        "database": "SALES_DATA",
        "tableName": "PRICE_PREDICTIONS",
    },
    model_environment_name="production",
)
```

### Multi-Class Model Example

```python
# File import for multi-class model
import_job = client.create_file_import_job(
    blob_store="gcs",
    bucket_name="ml-predictions",
    prefix="sentiment-analysis/daily/",
    model_name="sentiment-classifier",
    model_type="multi-class",
    model_schema={
        "predictionScores": "class_probabilities",  # JSON column with class probabilities
        "actualScores": "actual_class_one_hot",  # One-hot encoded actual class
        "thresholdScores": "class_thresholds",  # Per-class decision thresholds
        "predictionId": "review_id",
        "timestamp": "analysis_timestamp",
        "tagsList": ["product_category", "source_platform", "language"],
        "embeddingFeatures": [
            {
                "featureName": "review_text_embedding",
                "vectorCol": "text_embedding_vector",
                "rawDataCol": "review_text",
            }
        ],
    },
    model_environment_name="validation",
)
```

### Handling Import Errors

```python
try:
    import_job = client.create_file_import_job(...)
    job_id = import_job["jobId"]

    # Monitor job status
    import time

    while True:
        status = client.get_file_import_job(job_id)

        if status["jobStatus"] == "inactive":
            print("Import completed successfully!")
            break
        elif status["jobStatus"] == "deleted":
            print("Import job was deleted")
            break
        elif status["totalFilesFailedCount"] > 0:
            print(f"Warning: {status['totalFilesFailedCount']} files failed to import")

        print(f"Progress: {status['totalFilesSuccessCount']} files completed")
        time.sleep(30)  # Check every 30 seconds

except Exception as e:
    print(f"Error creating import job: {e}")
```

### Managing Import Jobs

Here's a complete example of managing the lifecycle of an import job:

```python
import time
from arize_toolkit import Client

client = Client(
    organization="your-org", space="your-space", arize_developer_key="your-api-key"
)

# 1. Create an import job
job = client.create_file_import_job(
    blob_store="s3",
    bucket_name="ml-data",
    prefix="predictions/",
    model_name="my-model",
    model_type="classification",
    model_schema={
        "predictionLabel": "prediction",
        "actualLabel": "actual",
        "predictionId": "id",
        "timestamp": "ts",
    },
    model_environment_name="production",
)

job_id = job["jobId"]
print(f"Created job: {job_id}")

# 2. Monitor the job
max_retries = 10
retry_count = 0

while retry_count < max_retries:
    status = client.get_file_import_job(job_id)

    if status["totalFilesFailedCount"] > 5:
        print("Too many failures, pausing job...")
        # 3. Update job to inactive if too many failures
        client.update_file_import_job(
            job_id=job_id,
            job_status="inactive",
            model_schema={
                "predictionLabel": "prediction",
                "actualLabel": "actual",
                "predictionId": "id",
                "timestamp": "ts",
            },
        )
        break

    if status["totalFilesPendingCount"] == 0:
        print("All files processed!")
        break

    print(
        f"Progress: {status['totalFilesSuccessCount']} completed, "
        f"{status['totalFilesPendingCount']} pending"
    )

    time.sleep(60)  # Check every minute
    retry_count += 1

# 4. Clean up old jobs
all_jobs = client.get_all_file_import_jobs()
for job in all_jobs:
    if job["jobStatus"] == "inactive" and job["totalFilesPendingCount"] == 0:
        # Delete completed inactive jobs
        client.delete_file_import_job(job_id=job["jobId"])
        print(f"Deleted completed job: {job['jobId']}")
```

______________________________________________________________________

## Best Practices

1. **Validate Schema First**: Use `dry_run=True` to validate your schema configuration before importing data:

   ```python
   import_job = client.create_file_import_job(..., dry_run=True)
   ```

1. **Use Batch IDs**: For validation data, use batch IDs to group related predictions:

   ```python
   model_schema = {..., "batchId": "experiment_batch_id"}
   ```

1. **Monitor Large Imports**: For large imports, implement monitoring logic to track progress and handle failures.

1. **Schema Consistency**: Ensure your data schema remains consistent across imports to avoid issues with model monitoring and analysis.

1. **Environment Selection**: Use appropriate environments:

   - `production`: For live production predictions
   - `validation`: For model validation and testing
   - `training`: For training data imports
   - `tracing`: For LLM tracing data

1. **Manage Job Lifecycle**:

   - Monitor active jobs regularly to detect issues early
   - Pause jobs (set to inactive) if you detect problems
   - Clean up old or failed jobs to keep your workspace organized
   - Always provide the complete schema when updating jobs

1. **Table Import Best Practices**:

   - Set appropriate `refresh_interval` based on your data update frequency
   - Use `query_window_size` to control data volume and query performance
   - Monitor query success/failure rates to detect table access issues
