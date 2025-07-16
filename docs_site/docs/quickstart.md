# Quickstart Guide

Welcome to the Arize Toolkit! This guide will walk you through getting started with the Python SDK for the Arize AI platform. You'll learn how to set up the client and perform common tasks across all major functionality areas.

## 📦 Installation

Install the Arize Toolkit using pip:

```bash
pip install arize_toolkit
```

## 🔐 Authentication & Setup

### Step 1: Get Your API Key

1. Log in or create an Arize account at [app.arize.com](https://app.arize.com)
1. Navigate in the sidebar to the **Settings->Account Settings** page
1. Go to the **API Keys** tab and click **Create API Key**
1. Name and copy your **Developer API Key**. This will only be shown once, so make sure to save it somewhere safe, or use the `.env` file method below

For detailed instructions on how to get your API key, see [this guide](https://arize.com/docs/ax/reference/authentication-and-security/api-keys).

### Step 2: Set Up Your Environment

You can authenticate using an environment variable (recommended in most cases) or pass the key to the client.
To use the environment variable method, you can set the `ARIZE_DEVELOPER_KEY` environment variable to your API key.

```bash
# Option 1: Set environment variable (recommended)
export ARIZE_DEVELOPER_KEY="your-api-key-here"
```

#### Using a `.env` File

Alternatively, you can use a `.env` file to store your API key (and other configurations) as shown below. Using a `.env` file with a `.gitignore` for development is generally safer because you won't accidentally commit your API key or other sensitive information to a public repository.

```bash
# Option 2: Use .env file
ARIZE_DEVELOPER_KEY=your-api-key-here
ARIZE_ORGANIZATION=your-org-name
ARIZE_SPACE=your-space-name
```

You can use the `dotenv` package and `load_dotenv` function to load the environment variables from the `.env` file. With this approach, `ARIZE_DEVELOPER_KEY` will automatically be picked up from the environment variables, but the other parameters need to be passed in manually.

```python
import os

from arize_toolkit import Client
from dotenv import load_dotenv

load_dotenv()

ORGANIZATION = os.getenv("ARIZE_ORGANIZATION")
SPACE = os.getenv("ARIZE_SPACE")

client = Client(organization=ORGANIZATION, space=SPACE)
```

### Step 3: Initialize the Client

All of the tools are available through the client, which stores the connection information for making requests to the Arize APIs. The client is initialized with the organization and space names. If you are using the Arize SaaS platform, you can find the organization and space names in the Arize UI.

For teams working across the account, you can use a single client and the `switch_space` method to transition between organizations and spaces.

If you are working with an on-premise deployment, you will need to provide the `arize_app_url` parameter. This should be the base url of your Arize instance.

```python
from arize_toolkit import Client
from dotenv import load_dotenv

load_dotenv()

# Option 1: Using environment variable or .env file (recommended)
client = Client(organization="your-org-name", space="your-space-name")
```

```python
# Option 2: Pass API key directly
client = Client(
    organization="your-org-name",
    space="your-space-name",
    arize_developer_key="your-api-key-here",
)
```

```python
# Option 3: For on-premise deployments
client = Client(
    organization="your-org-name",
    space="your-space-name",
    arize_developer_key="your-api-key-here",
    arize_app_url="https://your-arize-instance.com",
)
```

______________________________________________________________________

## 🏢 [Managing Spaces & Organizations](space_and_organization_tools.md)

In some cases, you may need to work across multiple organizations or spaces. The toolkit provides tools to manage these resources while working with a single client. If you need to be able to run operations across multiple organizations or spaces you have permissions for, you can use the `get_all_organizations` and `get_all_spaces` methods to get list the available organizations and spaces.

### Get All Organizations

Get all organizations in the account for which you have permissions.

```python
# List all organizations in your account
organizations = client.get_all_organizations()

for org in organizations:
    print(f"Organization: {org['name']} (ID: {org['id']})")
    print(f"  Created: {org['createdAt']}")
    print(f"  Description: {org['description']}")
```

### Get All Spaces

Get all spaces in the current organization for which you have permissions.

```python
# List all spaces in current organization
spaces = client.get_all_spaces()

for space in spaces:
    print(f"Space: {space['name']} (ID: {space['id']})")
    print(f"  Private: {space['private']}")
    print(f"  Description: {space['description']}")
```

### Switch Spaces

The `switch_space` method can be used to transition between spaces and organizations. There are three ways to call the method:

1. `switch_space(space="space-name")` - Switch to a space in the current organization
1. `switch_space(space="space-name", organization="organization-name")` - Switch to a space in a different organization
1. `switch_space(organization="organization-name")` - Switch to a different organization (the first available space in the organization will be selected)

```python
# Switch to a different space in the same organization
client.switch_space(space="production-space")

# Switch to a space in a different organization
client.switch_space(space="ml-models", organization="data-science-org")

# Switch to first space in a different organization
client.switch_space(organization="staging-org")

# Get the current space URL
print(f"Current space: {client.space_url}")
```

______________________________________________________________________

## 🤖 [Working with Projects or Models](model_tools.md)

### List All Models (Projects)

```python
# Get all models in the current space
models = client.get_all_models()

for model in models:
    print(f"Model: {model['name']} (Type: {model['modelType']})")
    print(f"  ID: {model['id']}")
    print(f"  Created: {model['createdAt']}")
    print(f"  Demo Model: {model['isDemoModel']}")
```

### Get a Specific Model (Project)

When retrieving a model, you can either get the model by name or by ID. The model ID is the unique identifier for the model in Arize. The model name is the name of the model as it appears in the Arize UI. The model retrieved is a simplified version of the model object that can then be used to get more detailed information about the model with other tools.

```python
# Get model by name
model = client.get_model("fraud-detection-v2")
print(f"Model ID: {model['id']}")
print(f"Model Type: {model['modelType']}")

# Get model by ID
model = client.get_model_by_id("model_123")
print(f"Model Name: {model['name']}")

# Get model URL
model_url = client.get_model_url("fraud-detection-v2")
print(f"Model URL: {model_url}")
```

### Get Model Inference Volume

The `get_model_volume` method can be used to get the inference volume for a model. The method takes the model name or ID and a start and end time. The start and end time are optional and if not provided, the default is the last 30 days.

```python
from datetime import datetime, timedelta

# Get volume for the last 30 days (default)
volume = client.get_model_volume("fraud-detection-v2")
print(f"Total predictions: {volume}")

# Get volume for a specific time range
end_time = datetime.now()
start_time = end_time - timedelta(days=7)

volume = client.get_model_volume(
    "fraud-detection-v2", start_time=start_time, end_time=end_time
)
print(f"Predictions in last 7 days: {volume}")
```

### Get Total Inference Volume Across All Models

The `get_total_volume` method can be used to get the total prediction volume across all models in the space.

`get_total_volume` goes through all models in the space and gets the volume for each model. It returns the total volume and a dictionary of model name to volume, or a dataframe with columns for model name and volume (if `return_df` is True).

```python
# Get total volume across all models
total_volume, model_volumes = client.get_total_volume()
print(f"Total space volume: {total_volume}")
for model_name, vol in model_volumes.items():
    print(f"  {model_name}: {vol}")
```

______________________________________________________________________

## 📊 [Custom Metrics](custom_metrics_tools.md)

Arize supports many metrics out of the box, but often you will want to create your own metrics to track specific performance or KPI's. Custom metrics are created by writing a SQL query that returns a single value. The query is run on the features, tags, inference data, and actuals for a model and the result is made available in Arize for monitoring and tracking.

The format of custom metrics query is:

```sql
SELECT <metric_definition> FROM model
```

For example, the following query calculates the precision at a threshold of 0.7:

```sql
SELECT COUNT(numericPredictionLabel) 
FILTER(WHERE numericPredictionLabel > 0.7 AND numericActualLabel = 1) / COUNT(numericPredictionLabel)
FROM model
```

The `arize_toolkit` supports the following functions for custom metrics:

### List Custom Metrics

get all the custom metrics that have been defined for a model (by model name).

```python
# Get all custom metrics for a specific model
metrics = client.get_all_custom_metrics(model_name="fraud-detection-v2")

for metric in metrics:
    print(f"Metric: {metric['name']}")
    print(f"  Description: {metric['description']}")
    print(f"  SQL: {metric['metric']}")
    print(f"  Requires Positive Class: {metric['requiresPositiveClass']}")
```

### Get a Custom Metric

get a custom metric by model name and metric name. For convenience, you can also get a custom metric by its id in the Arize platform.

```python
# Get a custom metric by name
metric = client.get_custom_metric(
    model_name="fraud-detection-v2", metric_name="precision_at_threshold"
)

print(f"Metric: {metric['name']}")
print(f"  Description: {metric['description']}")
print(f"  SQL: {metric['metric']}")

metric_by_id = client.get_custom_metric_by_id(custom_metric_id="metric_123")
print(f"Metric: {metric_by_id['name']}")
print(f"  Description: {metric_by_id['description']}")
print(f"  SQL: {metric_by_id['metric']}")
```

### Create a Custom Metric

You can create a custom metric by providing the model name, metric name, and the SQL query. The metric name must be unique within the model and use the format shown above. There are also optional parameters for the metric description and environment (production, training, or validation). When creating a custom metric, the URL of the new metric is returned, so you can check the metric in the Arize UI directly or get the custom metric id from the URL.

```python
# Create a new custom metric
new_metric_url = client.create_custom_metric(
    model_name="fraud-detection-v2",
    metric_name="precision_at_threshold",
    metric="SELECT COUNT(numericPredictionLabel) \
        FILTER(WHERE numericPredictionLabel > 0.7 AND numericActualLabel = 1) / COUNT(numericPredictionLabel) \
        FROM model",
    metric_description="Precision when prediction score > 0.7",
    metric_environment="production",
)

print(f"Created metric: {new_metric_url}")
```

### Update a Custom Metric

You can update a custom metric by providing the current name and model name and then specificying any fields you want to update.
The name and metric can be updated, as well as the description and environment.

```python
# Update an existing custom metric
updated_metric = client.update_custom_metric(
    custom_metric_name="precision_at_threshold",
    model_name="fraud-detection-v2",
    name="precision_at_75_threshold",
    metric="SELECT COUNT(numericPredictionLabel) \
        FILTER(WHERE numericPredictionLabel > 0.75 AND numericActualLabel = 1) / COUNT(numericPredictionLabel) \
        FROM model",
    description="Updated precision threshold to 0.75",
)

print(f"Updated metric: {updated_metric['name']}")
```

### Copy a Custom Metric

If you want to copy a custom metric from one model to another, you can use the `copy_custom_metric` method.
This metric only requires the current metric name, current model name, and the new model name. The new metric name is optional and will default to the current metric name as long as it is unique in the new model. The other fields are optional and will default to the current metric values. The copy method returns the URL of the new metric, so you can check the metric in the Arize UI directly or get the custom metric id from the URL.

```python
# Copy a metric from one model to another
new_metric_url = client.copy_custom_metric(
    current_metric_name="precision_at_75_threshold",
    current_model_name="fraud-detection-v2",
    new_model_name="fraud-detection-v3",
    new_model_id="model_123",  # only have to provide one of new_model_name or new_model_id
    new_metric_name="precision_v3",
    new_metric_description="Precision metric for v3 model",
    new_metric_environment="production",
)

print(f"Copied metric: {new_metric_url}")
```

### Delete a Custom Metric

You can delete a custom metric by providing the model name and metric name. There is also an option to delete a metric by its id.

```python
# Delete a metric by name - returns True if deleted, False if not found
is_deleted = client.delete_custom_metric(
    model_name="fraud-detection-v2", metric_name="precision_at_threshold"
)

# Delete a metric by id - returns True if deleted, False if not found
is_deleted = client.delete_custom_metric_by_id(custom_metric_id="metric_123")
```

______________________________________________________________________

## 🚨 [Monitors](monitor_tools.md)

Monitors are used to track the performance of a model over time. There are three categories of monitors in Arize:

- Performance Monitors: Track the performance of model metrics (including custom metrics) over time.
- Drift Monitors: Track the drift of predictions, actuals, features, or tags over time.
- Data Quality Monitors: Track various indicators of data quality over time.

When retrieving monitors the category is included in the response, but when creating monitors, there are separate methods for each category.

The `arize_toolkit` supports the following functions for monitors:

### List All Monitors

list all monitors for a model. You can also filter by monitor category.
The response is a list of monitors, each with the category included in the response.
The response for the list method only includes basic information about the monitor, but you can get full details about the monitor by using the `get_monitor` methods for specific monitors instead.
When listing monitors, you can pass either the model name or model id and you can also filter by monitor category.

```python
# Get all monitors for a model
monitors = client.get_all_monitors(model_name="fraud-detection-v2")

drift_monitors = client.get_all_monitors(model_id="model_123", monitor_category="drift")

for monitor in monitors:
    print(f"Monitor: {monitor['name']} (Category: {monitor['monitorCategory']})")
```

### Get a Specific Monitor

get a specific monitor by name or id. This will return the full monitor object with all the available fields. The full monitor object contains a lot of information - the details are listed in the [monitor_tools](monitor_tools.md) section of the documentation.

```python
monitor = client.get_monitor(monitor_name="accuracy_alert")
print(f"Monitor: {monitor['name']}")
print(f"  Category: {monitor['monitorCategory']}")
print(f"  Status: {monitor['status']}")
print(f"  Triggered: {monitor['isTriggered']}")
print(f"  Threshold: {monitor['threshold']}")

monitor_by_id = client.get_monitor_by_id(monitor_id="monitor_123")
print(f"Monitor: {monitor_by_id['name']}")
print(f"  Category: {monitor_by_id['monitorCategory']}")
print(f"  Status: {monitor_by_id['status']}")
print(f"  Triggered: {monitor_by_id['isTriggered']}")
print(f"  Threshold: {monitor_by_id['threshold']}")
```

### Create a Monitor

There are separate methods for creating each type of monitor. The different monitor types vary in the specific fields they require, primarily the metric and dimensions that they operate on. All of these methods return the URL of the new monitor, so you can check the monitor in the Arize UI directly or get the monitor id from the URL.

#### Create Performance Monitors

create a performance monitor.

```python
# Create a performance monitor
performance_monitor_url = client.create_performance_monitor(
    name="Accuracy Alert",
    model_name="fraud-detection-v2",
    model_environment_name="production",
    performance_metric="accuracy",
    operator="lessThan",
    threshold=0.85,
    notes="Alert when accuracy drops below 85%",
    email_addresses=["ml-team@company.com"],
)

print(f"Created performance monitor: {performance_monitor_url}")
```

#### Create Drift Monitors

```python
# Create a drift monitor
drift_monitor_url = client.create_drift_monitor(
    name="Feature Drift Alert",
    model_name="fraud-detection-v2",
    drift_metric="psi",
    dimension_category="feature",
    dimension_name="transaction_amount",
    operator="greaterThan",
    threshold=0.2,
    notes="Alert when transaction_amount feature drifts significantly",
)

print(f"Created drift monitor: {drift_monitor_url}")
```

#### Create Data Quality Monitors

```python
# Create a data quality monitor
dq_monitor_url = client.create_data_quality_monitor(
    name="Missing Values Alert",
    model_name="fraud-detection-v2",
    model_environment_name="production",
    data_quality_metric="missing_percentage",
    dimension_category="feature",
    dimension_name="customer_age",
    operator="greaterThan",
    threshold=0.05,
    notes="Alert when customer_age has >5% missing values",
)

print(f"Created data quality monitor: {dq_monitor_url}")
```

### Copy a Monitor

You can copy an existing monitor to the same or a different model. The new monitor name is optional and will default to the current monitor name as long as it is unique in the new model. The other fields are optional and will default to the current monitor values. The copy method returns the URL of the new monitor, so you can check the monitor in the Arize UI directly or get the monitor id from the URL.

```python
# Copy a monitor
new_monitor_url = client.copy_monitor(
    current_monitor_name="accuracy_alert_v1",
    current_model_name="fraud-detection-v1",
    new_monitor_name="accuracy_alert_v2",
    new_model_name="fraud-detection-v2",
    ...,  # any fields you want to override in the new monitor
)

print(f"Copied monitor: {new_monitor_url}")
```

### Delete a Monitor

You can delete a monitor by providing the monitor name and the model name. There is also an option to delete a monitor by its id.

```python
# Delete a monitor
is_deleted = client.delete_monitor(
    monitor_name="accuracy_alert_v1",
    model_name="fraud-detection-v1",
)

is_deleted = client.delete_monitor_by_id(monitor_id="monitor_123")
```

______________________________________________________________________

## 🧠 [Prompts](language_model_tools.md)

Arize has robust support for AI engineering workflows, including prompts, annotations, experiments, datasets and more. There is a lot of support already for these features in other packages in the Arize ecosystem, but the `arize_toolkit` provides a few additional tools for interacting with the prompt and annotations api.

The `arize_toolkit` supports the following functions for language models:

### List All Prompts

Prompts are stored in the Arize prompt hub. These are robust definitions of the prompt object that can be used directly in workflows and agentic applications. You can list all prompts in the space and get back the detailed definition of each prompt.

```python
# Get all prompts in the space
prompts = client.get_all_prompts()

for prompt in prompts:
    print(f"Prompt: {prompt['name']}")
    print(f"  Description: {prompt['description']}")
    print(f"  Provider: {prompt['provider']}")
    print(f"  Model: {prompt['modelName']}")
    print(f"  Tags: {prompt['tags']}")
    ...
```

### Get a Specific Prompt

get a specific prompt by name or id.

```python
# Get prompt by name
prompt = client.get_prompt("customer-support-classifier")
print(f"Prompt ID: {prompt['id']}")
print(f"Messages: {prompt['messages']}")
print(f"Parameters: {prompt['llmParameters']}")
```

### Get a Formatted Prompt

In situations where you want to use a prompt in a workflow, you can get a formatted prompt by providing the prompt name and any variables you want to fill in. This convenience method returns the object required by the LLM provider with the variables filled in.

```python
# Get formatted prompt with variables
formatted_prompt = client.get_formatted_prompt(
    "customer-support-classifier",
    customer_message="My order hasn't arrived yet",
    context="Order placed 3 days ago",
)

print("Formatted messages:")
for message in formatted_prompt.messages:
    print(f"  {message['role']}: {message['content']}")
```

### Create a New Prompt

You can create a new prompt by providing the prompt name, description, messages, tags, provider, model name, and any additional parameters you want to include. This can be useful if you have an agentic application that may create new prompt versions on the fly. If the prompt already exists, a new version is created and set as the current version.

```python
# Create a new prompt
prompt_url = client.create_prompt(
    name="sentiment-analyzer",
    description="Analyzes sentiment of customer feedback",
    messages=[
        {
            "role": "system",
            "content": "You are a sentiment analysis expert. Classify the sentiment as positive, negative, or neutral.",
        },
        {"role": "user", "content": "Analyze this feedback: {feedback_text}"},
    ],
    tags=["sentiment", "analysis", "customer-feedback"],
    provider="openai",
    model_name="gpt-4",
    invocation_params={"temperature": 0.1, "max_tokens": 50},
)

print(f"Created prompt: {prompt_url}")
```

### Update Prompt Metadata

You can update the metadata of a prompt by providing the prompt name and any fields you want to update. This only updates the metadata of the prompt, not the actual prompt object.

```python
# Update prompt metadata
updated_prompt = client.update_prompt(
    prompt_name="sentiment-analyzer",
    description="Enhanced sentiment analysis with confidence scoring",
    tags=["sentiment", "analysis", "customer-feedback", "confidence"],
)

print(f"Updated prompt: {updated_prompt['name']}")

# Get all versions of a prompt
versions = client.get_all_prompt_versions("sentiment-analyzer")
for version in versions:
    print(f"Version: {version['id']} - {version['commitMessage']}")
```

### Delete a Prompt

You can delete a prompt by providing the prompt name. There is also an option to delete a prompt by its id.

```python
# Delete a prompt by name
is_deleted = client.delete_prompt(prompt_name="sentiment-analyzer")

# Delete a prompt by id
is_deleted = client.delete_prompt_by_id(prompt_id="prompt_123")
```

______________________________________________________________________

## 📝 [Annotations](language_model_tools.md)

Annotations are used to provide human feedback on LLM responses. The annotations provided can be used to monitor or improve model performance and align expectations with the business needs.

The `arize_toolkit` provides a convenience method for creating new annotations on individual responses. This capability will likely be expanded in the future to support more complex workflows.

### Create Annotation

create a new annotation on a specific record. This method requires a lot of detailed information about the model, record, and environment, but makes it possible to create annotiations in Arize from in-house infrastructure tools.
This probably isn't a function you want to expose to your end users, but it's useful when abstracted inside an internal tool.

There are two types of annotations that can be created:

- Label annotations: These are used to provide a label for a specific record.
- Score annotations: These are used to provide a score for a specific record.

```python
# Create a label annotation
annotation_success = client.create_annotation(
    name="manual_review_label",
    label="fraud",
    updated_by="ml-engineer@company.com",
    annotation_type="label",
    model_name="fraud-detection-v2",
    record_id="transaction_12345",
    model_environment="production",
    note="Confirmed fraud case through manual investigation",
)

print(f"Annotation created: {annotation_success}")

# Create a score annotation
score_annotation_success = client.create_annotation(
    name="confidence_score",
    score=0.95,
    updated_by="data-scientist@company.com",
    annotation_type="score",
    model_name="fraud-detection-v2",
    record_id="transaction_12346",
    model_environment="production",
    note="High confidence prediction",
)

print(f"Score annotation created: {score_annotation_success}")
```

______________________________________________________________________

## 📥 [Data Import Jobs](data_import_tools.md)

Data import jobs are the backbone of continuous model monitoring in Arize. They automate the process of ingesting prediction data, actual outcomes, and feature values from your production systems into Arize for monitoring and analysis. This is essential for maintaining visibility into model performance over time without manual data uploads.

There are two main types of import jobs:

**File Import Jobs** are ideal when your data is stored in cloud storage (S3, GCS, Azure) as files. These jobs continuously monitor specified storage locations and automatically import new files as they arrive. This pattern works well for batch prediction workflows where results are written to files on a schedule.

**Table Import Jobs** connect directly to databases (BigQuery, Snowflake, Databricks) and can query tables on a schedule. This is perfect for real-time or near-real-time prediction systems where data is continuously written to database tables.

Both types of jobs require a **model schema** that maps your data columns to Arize's expected fields (prediction IDs, timestamps, predictions, actuals, features, and tags). Once configured, import jobs run automatically and provide detailed status reporting so you can monitor data ingestion health.

### File Import Jobs

File import jobs are ideal for importing data from cloud storage providers. They continuously monitor specified prefixes in your storage buckets and automatically process new files as they appear. This is particularly useful for batch ML workflows where predictions are written to files on a regular schedule.

#### Create a File Import Job

When creating a file import job, you need to specify the storage location, model configuration, and most importantly, the schema that maps your file columns to Arize's data model. The schema tells Arize which columns contain predictions, actuals, features, and other important fields.

```python
# Define the schema mapping your data columns to Arize's expected fields
model_schema = {
    "predictionId": "transaction_id",
    "timestamp": "event_timestamp",
    "predictionLabel": "predicted_class",
    "predictionScore": "prediction_confidence",
    "actualLabel": "actual_class",
    # Feature mappings
    "featureList": ["feature_1", "feature_2", "feature_3"],
    "tagList": ["tag_1", "tag_2", "tag_3"],
}

# Create the import job for S3
file_job = client.create_file_import_job(
    blob_store="s3",
    bucket_name="my-company-predictions",
    prefix="fraud-model/daily-predictions/",
    model_name="daily-fraud-model",
    model_type="classification",  # or "regression", "ranking", etc.
    model_schema=model_schema,
    model_environment_name="production",
    model_version="v2.1",  # optional
)

print(f"✅ Successfully created import job with ID: {file_job['jobId']}")
print(f"Job Status: {file_job['jobStatus']}")
```

#### Monitor File Import Job Progress

Once a job is running, it's important to monitor its progress to ensure data is being ingested successfully. Failed file imports can indicate schema mismatches, permission issues, or data quality problems that need attention.

```python
# Check job status and progress
job_id = file_job["jobId"]
status = client.get_file_import_job(job_id)

print(f"📊 Job Status Report:")
print(f"  Status: {status['jobStatus']}")
print(f"  Files Succeeded: {status['totalFilesSuccessCount']}")
print(f"  Files Failed: {status['totalFilesFailedCount']}")
print(f"  Files Pending: {status['totalFilesPendingCount']}")
print(f"  Model: {status['modelName']} (ID: {status['modelId']})")
print(f"  Created: {status['createdAt']}")

# Calculate progress percentage
total_files = (
    status["totalFilesSuccessCount"]
    + status["totalFilesFailedCount"]
    + status["totalFilesPendingCount"]
)
if total_files > 0:
    progress = (status["totalFilesSuccessCount"] / total_files) * 100
    print(f"  Progress: {progress:.1f}% complete")
```

#### Manage File Import Jobs

Import jobs can be paused, resumed, or updated as your data pipeline evolves. This is useful for maintenance windows, schema changes, or troubleshooting data quality issues.

```python
# List all file import jobs in the space
all_file_jobs = client.get_all_file_import_jobs()
print(f"📁 Found {len(all_file_jobs)} file import jobs:")

for job in all_file_jobs:
    print(f"  - {job['jobId']}: {job['modelName']} ({job['jobStatus']})")
    if job["jobStatus"] == "active":
        print(f"    ✅ Success: {job['totalFilesSuccessCount']}")
        print(f"    ❌ Failed: {job['totalFilesFailedCount']}")
        print(f"    ⏳ Pending: {job['totalFilesPendingCount']}")

# Pause a job (set to inactive)
updated_job = client.update_file_import_job(
    job_id=job_id,
    job_status="inactive",
    model_schema=model_schema,  # Required even when just updating status
)
print(f"Job paused: {updated_job['jobStatus'] == 'inactive'}")

# Resume a job (set back to active)
resumed_job = client.update_file_import_job(
    job_id=job_id,
    job_status="active",
    model_schema=model_schema,
)
print(f"Job resumed: {resumed_job['jobStatus'] == 'active'}")
```

### Table Import Jobs

Table import jobs connect directly to your databases and can query tables on a schedule. This approach is ideal for real-time or streaming ML systems where prediction data is continuously written to database tables. The jobs can handle incremental data loading and are more efficient for high-volume, continuous data flows.

#### Create a BigQuery Table Import Job

BigQuery table imports are common for Google Cloud-based ML systems. The job will periodically query your specified table and import new records based on timestamp or other incremental loading strategies.

```python
# Create a BigQuery table import job
table_job = client.create_table_import_job(
    table_store="BigQuery",
    model_name="fraud-detection-v2",
    model_type="classification",
    model_schema={
        "predictionLabel": "pred_label",
        "predictionScore": "pred_score",
        "actualLabel": "true_label",
        "predictionId": "transaction_id",
        "timestamp": "prediction_timestamp",
        "feature_amount": "transaction_amount",
        "feature_location": "merchant_location",
    },
    bigquery_table_config={
        "projectId": "my-gcp-project",
        "dataset": "ml_predictions",
        "tableName": "fraud_predictions",
    },
    model_environment_name="production",
)

print(f"✅ Created BigQuery import job: {table_job['jobId']}")
```

#### Create a Snowflake Table Import Job

Snowflake imports work similarly but are configured for Snowflake's architecture. This is useful for organizations using Snowflake as their data warehouse for ML feature stores and prediction logging.

```python
# Create a Snowflake table import job
snowflake_job = client.create_table_import_job(
    table_store="Snowflake",
    model_name="recommendation-engine",
    model_type="ranking",
    model_schema={
        "predictionId": "user_session_id",
        "timestamp": "event_time",
        "predictionLabel": "recommended_item",
        "predictionScore": "relevance_score",
        "actualLabel": "clicked_item",
        "feature_user_age": "user_age_group",
        "feature_category": "item_category",
    },
    snowflake_table_config={
        "account": "my-account.snowflakecomputing.com",
        "database": "ANALYTICS",
        "schema": "ML_PREDICTIONS",
        "tableName": "RECOMMENDATION_RESULTS",
        "warehouse": "COMPUTE_WH",
    },
)

print(f"✅ Created Snowflake import job: {snowflake_job['jobId']}")
```

#### Monitor Table Import Jobs

Table import jobs track queries rather than files, so the monitoring metrics are slightly different. Failed queries often indicate database connectivity issues, permission problems, or SQL execution errors.

```python
# Monitor table job status
table_job_status = client.get_table_import_job(table_job["jobId"])

print(f"📊 Table Import Job Status:")
print(f"  Job ID: {table_job_status['jobId']}")
print(f"  Status: {table_job_status['jobStatus']}")
print(f"  Model: {table_job_status['modelName']}")
print(f"  Queries Success: {table_job_status['totalQueriesSuccessCount']}")
print(f"  Queries Failed: {table_job_status['totalQueriesFailedCount']}")
print(f"  Queries Pending: {table_job_status['totalQueriesPendingCount']}")

# List all table import jobs
all_table_jobs = client.get_all_table_import_jobs()
print(f"\n📋 All Table Import Jobs ({len(all_table_jobs)}):")
for job in all_table_jobs:
    print(f"  - {job['modelName']}: {job['jobStatus']}")
    print(
        f"    Success: {job['totalQueriesSuccessCount']}, "
        f"Failed: {job['totalQueriesFailedCount']}, "
        f"Pending: {job['totalQueriesPendingCount']}"
    )
```

### Import Job Management Workflow

Managing import jobs is a critical part of ML operations. This workflow helps you monitor all your data ingestion pipelines and quickly identify issues that could impact model monitoring. Regular monitoring of import job health ensures that your model performance tracking remains accurate and up-to-date.

```python
def monitor_import_jobs():
    """Monitor all import jobs and report status"""

    print("🔍 Monitoring Import Jobs...")

    # Check file import jobs
    file_jobs = client.get_all_file_import_jobs()
    active_file_jobs = [job for job in file_jobs if job["jobStatus"] == "active"]

    print(
        f"\n📁 File Import Jobs: {len(active_file_jobs)} active out of {len(file_jobs)} total"
    )
    for job in active_file_jobs:
        total_files = (
            job["totalFilesSuccessCount"]
            + job["totalFilesFailedCount"]
            + job["totalFilesPendingCount"]
        )
        if total_files > 0:
            success_rate = (job["totalFilesSuccessCount"] / total_files) * 100
            print(f"  📊 {job['modelName']}: {success_rate:.1f}% success rate")

            # Alert on high failure rate
            if job["totalFilesFailedCount"] > 0:
                failure_rate = (job["totalFilesFailedCount"] / total_files) * 100
                if failure_rate > 10:  # Alert if >10% failure rate
                    print(f"    ⚠️  High failure rate: {failure_rate:.1f}%")

    # Check table import jobs
    table_jobs = client.get_all_table_import_jobs()
    active_table_jobs = [job for job in table_jobs if job["jobStatus"] == "active"]

    print(
        f"\n📋 Table Import Jobs: {len(active_table_jobs)} active out of {len(table_jobs)} total"
    )
    for job in active_table_jobs:
        total_queries = (
            job["totalQueriesSuccessCount"]
            + job["totalQueriesFailedCount"]
            + job["totalQueriesPendingCount"]
        )
        if total_queries > 0:
            success_rate = (job["totalQueriesSuccessCount"] / total_queries) * 100
            print(f"  📊 {job['modelName']}: {success_rate:.1f}% query success rate")


# Run the monitoring workflow
monitor_import_jobs()
```

______________________________________________________________________

## 📊 [Dashboards](dashboard_tools.md)

Dashboards in Arize provide a powerful way to visualize and monitor your machine learning models through customizable widgets and charts. They serve as centralized monitoring hubs where you can track model performance, data drift, data quality, and custom business metrics all in one place. Dashboards are particularly useful for stakeholders who need high-level overviews of model health without diving into detailed technical metrics.

The current implementation of dashboards tools can only be used to retrieve information about dashboards. You cannot create, update, or delete dashboards - this will be added in the next release.

Each dashboard can contain multiple types of widgets:

- **Statistic widgets** display single-value metrics like accuracy, precision, or custom KPIs
- **Line chart widgets** show trends over time for performance metrics, drift scores, or data quality indicators
- **Bar chart widgets** visualize categorical breakdowns like performance by segment or feature distributions
- **Text widgets** provide context, explanations, or important notes about the models being monitored
- **Experiment chart widgets** show the performance of different model versions over time
- **Drift line chart widgets** show the drift of different features over time with respect to a reference distribution
- **Monitor line chart widgets** show the performance of different monitors over time

The toolkit allows you to easily access your existing dashboards and explore their components programmatically, which is useful for automated reporting, alerting systems, or integrating dashboard data into other tools.

### List All Dashboards

You can retrieve a list of all dashboards available in your current space. This is useful for discovery and understanding what dashboard views are already set up. Listing dashboards returns the basic information about the dashboard, but you can get the full dashboard object by using the `get_dashboard` method.

```python
# Get all dashboards in the space
dashboards = client.get_all_dashboards()

print(f"Found {len(dashboards)} dashboards in the current space:")
for dashboard in dashboards:
    print(f"- {dashboard['name']} (ID: {dashboard['id']})")
    print(f"  Created by: {dashboard['creator']['name']}")
    print(f"  Created: {dashboard['createdAt']}")
    print(f"  Status: {dashboard['status']}")
```

### Get Dashboard Details and Explore Widgets

To inspect the contents of a dashboard, you can fetch it by name. This returns the complete dashboard configuration including all widgets, which is helpful for understanding what metrics are being tracked and how they're configured.

```python
# Get complete dashboard with all widgets
dashboard = client.get_dashboard("Model Performance Overview")

print(f"Dashboard: {dashboard['name']}")
print(f"Created by: {dashboard['creator']['name']}")
print(f"Models referenced: {len(dashboard['models'])}")

# Print detailed widget summary
print(f"\nWidget breakdown:")
print(f"  📊 Statistic widgets: {len(dashboard['statisticWidgets'])}")
print(f"  📈 Line chart widgets: {len(dashboard['lineChartWidgets'])}")
print(f"  📊 Bar chart widgets: {len(dashboard['barChartWidgets'])}")
print(f"  📝 Text widgets: {len(dashboard['textWidgets'])}")
print(f"  📊 Experiment chart widgets: {len(dashboard['experimentChartWidgets'])}")
print(f"  📊 Drift line chart widgets: {len(dashboard['driftLineChartWidgets'])}")
print(f"  📊 Monitor line chart widgets: {len(dashboard['monitorLineChartWidgets'])}")

# Explore statistic widgets in detail
print(f"\nStatistic Widgets:")
for widget in dashboard["statisticWidgets"]:
    print(f"  - {widget['title']}")
    print(f"    Metric: {widget['performanceMetric']}")
    print(f"    Environment: {widget['modelEnvironmentName']}")
    if "customMetric" in widget and widget["customMetric"]:
        print(f"    Custom Metric: {widget['customMetric']['name']}")

# Explore line chart widgets
print(f"\nLine Chart Widgets:")
for widget in dashboard["lineChartWidgets"]:
    print(f"  - {widget['title']}")
    print(f"    Y-axis: {widget.get('yAxisLabel', 'Not specified')}")
    print(f"    Plots: {len(widget.get('plots', []))}")
```

### Get Dashboard URL

You can get the URL for a dashboard by name. This is useful for sharing monitoring views with stakeholders, embedding in reports, or automating browser-based workflows.

```python
# Get dashboard URL for sharing
dashboard_url = client.get_dashboard_url("Model Performance Overview")
print(f"\n🔗 Dashboard URL: {dashboard_url}")

# Open dashboard in browser (useful for automation)
import webbrowser

webbrowser.open(dashboard_url)
```

______________________________________________________________________

## 🛠️ [Utility Functions](utility_tools.md)

Utility functions are available to help you configure rate limiting, get URLs for different resources, and handle errors.

### Configure Rate Limiting

You can configure the sleep time between API requests to avoid rate limiting. The default sleep time is 0 seconds, but you can set it to a higher value to avoid rate limiting. You can either set the sleep time in the client object, or you can use the `set_sleep_time` method to change the sleep time in a chainable way while making requests. This is just a convenience method to avoid having to set the sleep time in the client object and then call the method again, especially when making a series of requests that may or may not include pagination.

```python
from arize_toolkit.client import ArizeClient

# Set sleep time in the client object
client = ArizeClient(space="your_space", organization="your_organization", sleep_time=0)

# Set higher sleep time between API requests (helpful for rate limiting)
all_models = client.set_sleep_time(10).get_all_models()  # 10 second between requests

# Reset to no delay
client.set_sleep_time(0)
```

### Get URLs for Different Resources

For most resources, you can get the URL for the resource in Arize by passing the id of the resource to its `{x}_url` method.
Some resources, like models, monitors, custom metrics, and dashboards, also have a `get_{x}_url` method that only need the name of the resource to get the URL.

```python
# Get various resource URLs by id
model_url = client.model_url("model_123")
monitor_url = client.monitor_url("monitor_456")
custom_metric_url = client.custom_metric_url("model_123", "custom_metric_789")
prompt_url = client.prompt_url("prompt_789")
prompt_version_url = client.prompt_version_url("prompt_789", "version_123")
dashboard_url = client.dashboard_url("dashboard_abc")

# Get various resource URLs by name
model_url = client.get_model_url("model-name")
monitor_url = client.get_monitor_url("monitor-name")
custom_metric_url = client.get_custom_metric_url("model-name", "custom-metric-name")
dashboard_url = client.get_dashboard_url("dashboard-name")
```

______________________________________________________________________

## 🚨 Error Handling

The toolkit provides a comprehensive error handling system that helps you identify and resolve issues with your API calls.
Any API call that fails will raise an `ArizeAPIException` with a helpful error message for the specific request type that failed, including details about why the request failed.

For common errors, like rate limiting issues or non-existent resources, the message will include explanations and suggestions for addressing the issue.

```python
from arize_toolkit.exceptions import ArizeAPIException

try:
    model = client.get_model("non-existent-model")
except ArizeAPIException as e:
    if e.message == "Model not found":
        print(f"Model not found: {e}")
    else:
        print(f"API error: {e}")

try:
    # Handle API rate limits
    client.set_sleep_time(2)  # Add delay between requests
    models = client.get_all_models()
except ArizeAPIException as e:
    print(f"API error: {e}")
```

______________________________________________________________________

## 📚 Next Steps

Now that you've learned the basics, return to the [main page](index.md) to see the full list of tools and features.

Happy building with Arize Toolkit! 🚀
