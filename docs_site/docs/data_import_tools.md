# Data Import Tools

The Arize Toolkit provides comprehensive tools for importing data from various sources into Arize. You can import data from cloud storage (S3, GCS, Azure) or directly from databases (BigQuery, Snowflake, Databricks).

## Table of Contents

- [File Import Jobs](#file-import-jobs)
  - [Creating a File Import Job](#creating-a-file-import-job)
  - [Model Schema Configuration](#model-schema-configuration)
  - [Monitoring File Import Jobs](#monitoring-file-import-jobs)
- [Table Import Jobs](#table-import-jobs)
  - [Creating a Table Import Job](#creating-a-table-import-job)
  - [Table Configuration](#table-configuration)
  - [Monitoring Table Import Jobs](#monitoring-table-import-jobs)
- [Examples by Model Type](#examples-by-model-type)

## File Import Jobs

File import jobs allow you to import data from cloud storage providers like Amazon S3, Google Cloud Storage, and Azure Storage.

### Creating a File Import Job

```python
from arize_toolkit import Client

client = Client(
    organization="your-org", space="your-space", arize_developer_key="your-api-key"
)

# Create a file import job
import_job = client.create_file_import_job(
    blob_store="s3",  # Options: "s3", "gcs", "azure"
    bucket_name="my-bucket",
    prefix="data/predictions/",
    model_name="my-model",
    model_type="classification",  # See model types below
    model_schema={
        "predictionLabel": "prediction_column",
        "actualLabel": "actual_column",
        "predictionId": "id_column",
        "timestamp": "timestamp_column",
    },
    model_environment_name="production",  # Options: "production", "validation", "training", "tracing"
)
```

### Model Schema Configuration

The model schema defines how your data columns map to Arize's data model. The schema varies based on your model type.

#### Common Fields (All Model Types)

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

#### Model Type Specific Fields

##### Classification Models

```python
from arize_toolkit.models import ClassificationSchemaInput

schema = ClassificationSchemaInput(
    predictionLabel="prediction_column",  # Required
    predictionScores="prediction_scores_column",  # Optional
    actualLabel="actual_label_column",  # Optional
    actualScores="actual_scores_column",  # Optional
    predictionId="id_column",
    timestamp="timestamp_column",
)
```

##### Regression Models

```python
from arize_toolkit.models import RegressionSchemaInput

schema = RegressionSchemaInput(
    predictionScore="prediction_value_column",  # Required
    actualScore="actual_value_column",  # Optional
    predictionId="id_column",
    timestamp="timestamp_column",
)
```

##### Ranking Models

```python
from arize_toolkit.models import RankSchemaInput

schema = RankSchemaInput(
    rank="rank_column",  # Required
    predictionGroupId="group_id_column",  # Required
    predictionScores="scores_column",  # Optional
    relevanceScore="relevance_score_column",  # Optional
    relevanceLabel="relevance_label_column",  # Optional
    predictionId="id_column",
    timestamp="timestamp_column",
)
```

##### Multi-Class Models

```python
from arize_toolkit.models import MultiClassSchemaInput

schema = MultiClassSchemaInput(
    predictionScores="prediction_scores_column",  # Required
    actualScores="actual_scores_column",  # Optional
    thresholdScores="threshold_scores_column",  # Optional
    predictionId="id_column",
    timestamp="timestamp_column",
)
```

##### Object Detection Models

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
    predictionId="id_column",
    timestamp="timestamp_column",
)
```

### Monitoring File Import Jobs

#### Get a Specific File Import Job

```python
# Get status of a specific import job
job_status = client.get_file_import_job(job_id="job123")

print(f"Job Status: {job_status['jobStatus']}")
print(f"Files Pending: {job_status['totalFilesPendingCount']}")
print(f"Files Success: {job_status['totalFilesSuccessCount']}")
print(f"Files Failed: {job_status['totalFilesFailedCount']}")
```

#### Get All File Import Jobs

```python
# Get all file import jobs for the space
all_jobs = client.get_all_file_import_jobs()

for job in all_jobs:
    print(f"Job {job['jobId']}: {job['jobStatus']}")
    print(f"  Model: {job['modelName']}")
    print(f"  Created: {job['createdAt']}")
```

## Table Import Jobs

Table import jobs allow you to import data directly from databases like BigQuery, Snowflake, and Databricks.

### Creating a Table Import Job

```python
from arize_toolkit import Client

# Create a BigQuery import job
import_job = client.create_table_import_job(
    table_store="BigQuery",
    model_name="my-model",
    model_type="classification",
    model_schema={
        "predictionLabel": "prediction_column",
        "actualLabel": "actual_column",
        "predictionId": "id_column",
        "timestamp": "timestamp_column",
    },
    bigquery_table_config={
        "projectId": "my-project",
        "dataset": "my-dataset",
        "tableName": "predictions_table",
    },
    model_environment_name="production",
)
```

### Table Configuration

#### BigQuery Configuration

```python
from arize_toolkit.models import BigQueryTableConfig

config = BigQueryTableConfig(
    projectId="your-gcp-project", dataset="your-dataset", tableName="your-table"
)
```

#### Snowflake Configuration

```python
from arize_toolkit.models import SnowflakeTableConfig

config = SnowflakeTableConfig(
    accountID="your-account",
    snowflakeSchema="your-schema",  # Note: Uses 'schema' alias in API
    database="your-database",
    tableName="your-table",
)
```

#### Databricks Configuration

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

### Monitoring Table Import Jobs

#### Get a Specific Table Import Job

```python
# Get status of a specific import job
job_status = client.get_table_import_job(job_id="job123")

print(f"Job Status: {job_status['jobStatus']}")
print(f"Queries Pending: {job_status['totalQueriesPendingCount']}")
print(f"Queries Success: {job_status['totalQueriesSuccessCount']}")
print(f"Queries Failed: {job_status['totalQueriesFailedCount']}")
```

#### Get All Table Import Jobs

```python
# Get all table import jobs for the space
all_jobs = client.get_all_table_import_jobs()

for job in all_jobs:
    print(f"Job {job['jobId']}: {job['jobStatus']}")
    print(f"  Table: {job['table']} ({job['tableStore']})")
    print(f"  Model: {job['modelName']}")
```

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
