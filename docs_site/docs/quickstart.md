# Quickstart Guide

Welcome to the Arize Toolkit! This guide will walk you through getting started with the Python SDK for the Arize AI platform. You'll learn how to set up the client and perform common tasks across all major functionality areas.

## 📦 Installation

Install the Arize Toolkit using pip:

```bash
pip install arize-toolkit
```

## 🔐 Authentication & Setup

### Step 1: Get Your API Key

1. Log into your Arize account at [app.arize.com](https://app.arize.com)
1. Navigate to your space settings
1. Copy your **Developer API Key** (this will only be shown once, so make sure to save it somewhere safe)

For detailed instructions on how to get your API key, see [this guide](https://arize.com/docs/ax/reference/authentication-and-security/api-keys).

### Step 2: Set Up Your Environment

You can authenticate using an environment variable (recommended) or pass the key directly:

```bash
# Option 1: Set environment variable (recommended)
export ARIZE_DEVELOPER_KEY="your-api-key-here"
```

Alternatively, you can use a `.env` file to store your API key and other configuration.

```bash
# Option 2: Use .env file
ARIZE_DEVELOPER_KEY=your-api-key-here
ARIZE_APP_URL=https://your-arize-instance.com
ARIZE_ORGANIZATION=your-org-name
ARIZE_SPACE=your-space-name
```

The developer key will automatically be picked up from the environment variables, but the other parameters will need to be passed in manually. You can use the `dotenv` package and `load_dotenv` function to load the environment variables from the `.env` file.

```python
import os

from arize_toolkit import Client
from dotenv import load_dotenv

load_dotenv()

ORGANIZATION = os.getenv("ARIZE_ORGANIZATION")
SPACE = os.getenv("ARIZE_SPACE")
ARIZE_APP_URL = os.getenv("ARIZE_APP_URL")

client = Client(organization=ORGANIZATION, space=SPACE, arize_app_url=ARIZE_APP_URL)
```

### Step 3: Initialize the Client

All of the tools are available through the client, which stores the connection information for making requests to the Arize APIs. The client is initialized with the organization and space names. If you are using the Arize SaaS platform, you can find the organization and space names in the Arize UI.

For teams working across the account, you can use a single client and the `switch_space` method to transition between organizations and spaces.

If you are working with an on-premise deployment, you will need to provide the `arize_app_url` parameter. This should be the base url of your Arize instance.

```python
from arize_toolkit import Client

# Option 1: Using environment variable
client = Client(organization="your-org-name", space="your-space-name")

# Option 2: Pass API key directly
client = Client(
    organization="your-org-name",
    space="your-space-name",
    arize_developer_key="your-api-key-here",
)

# Option 3: For on-premise deployments
client = Client(
    organization="your-org-name",
    space="your-space-name",
    arize_app_url="https://your-arize-instance.com",
)
```

______________________________________________________________________

## 🏢 Managing Spaces & Organizations

### Get All Organizations

```python
# List all organizations in your account
organizations = client.get_all_organizations()

for org in organizations:
    print(f"Organization: {org['name']} (ID: {org['id']})")
    print(f"  Created: {org['createdAt']}")
    print(f"  Description: {org['description']}")
```

### Get All Spaces

```python
# List all spaces in current organization
spaces = client.get_all_spaces()

for space in spaces:
    print(f"Space: {space['name']} (ID: {space['id']})")
    print(f"  Private: {space['private']}")
    print(f"  Description: {space['description']}")
```

### Switch Spaces

The `switch_space` method can be used to transition between spaces. There are three ways to call the method:

1. `switch_space(space="space-name")` - Switch to a space in the current organization
1. `switch_space(space="space-name", organization="organization-name")` - Switch to a space in a different organization
1. `switch_space(organization="organization-name")` - Switch to the any existing space in a different organization

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

## 🤖 Working with Models

### List All Models

```python
# Get all models in the current space
models = client.get_all_models()

for model in models:
    print(f"Model: {model['name']} (Type: {model['modelType']})")
    print(f"  ID: {model['id']}")
    print(f"  Created: {model['createdAt']}")
    print(f"  Demo Model: {model['isDemoModel']}")
```

### Get a Specific Model

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

## 📊 Custom Metrics

Arize supports many metrics out of the box, but often you will want to create your own metrics to track specific performance or KPI's. Custom metrics are created by writing a SQL query that returns a single value. The query is run on the features, tags, inference data, and actuals for a model and the result is made available in Arize for monitoring and tracking.

The format of custom metrics query is:

```sql
SELECT <metric_definition> FROM model
```

For example, the following query calculates the precision at a threshold of 0.7:

```sql
SELECT COUNT(numericPredictionLabel) 
FILTER(WHERE numericPredictionLabel < 0.7 AND numericActualLabel = 1) / COUNT(numericPredictionLabel)
FROM model
```

### List Custom Metrics

```python
# Get all custom metrics for a specific model
metrics = client.get_all_custom_metrics(model_name="fraud-detection-v2")

for metric in metrics:
    print(f"Metric: {metric['name']}")
    print(f"  Description: {metric['description']}")
    print(f"  SQL: {metric['metric']}")
    print(f"  Requires Positive Class: {metric['requiresPositiveClass']}")
```

### Create a Custom Metric

```python
# Create a new custom metric
metric_url = client.create_custom_metric(
    model_name="fraud-detection-v2",
    metric_name="precision_at_threshold",
    metric="SELECT AVG(CASE WHEN prediction_score > 0.7 AND actual_label = 1 THEN 1 ELSE 0 END) FROM model",
    metric_description="Precision when prediction score > 0.7",
    metric_environment="production",
)

print(f"Created metric: {metric_url}")
```

### Update a Custom Metric

```python
# Update an existing custom metric
updated_metric = client.update_custom_metric(
    custom_metric_name="precision_at_threshold",
    model_name="fraud-detection-v2",
    name="precision_at_75_threshold",
    metric="SELECT AVG(CASE WHEN prediction_score > 0.75 AND actual_label = 1 THEN 1 ELSE 0 END) FROM model",
    description="Updated precision threshold to 0.75",
)

print(f"Updated metric: {updated_metric['name']}")
```

### Copy a Custom Metric

```python
# Copy a metric from one model to another
new_metric_url = client.copy_custom_metric(
    current_metric_name="precision_at_75_threshold",
    current_model_name="fraud-detection-v2",
    new_model_name="fraud-detection-v3",
    new_metric_name="precision_v3",
    new_metric_description="Precision metric for v3 model",
)

print(f"Copied metric: {new_metric_url}")
```

______________________________________________________________________

## 🚨 Monitors

### List All Monitors

```python
# Get all monitors for a model
monitors = client.get_all_monitors(model_name="fraud-detection-v2")

for monitor in monitors:
    print(f"Monitor: {monitor['name']} (Category: {monitor['monitorCategory']})")
    print(f"  Status: {monitor['status']}")
    print(f"  Triggered: {monitor['isTriggered']}")
    print(f"  Threshold: {monitor['threshold']}")
```

### Create Performance Monitors

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

### Create Drift Monitors

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

### Create Data Quality Monitors

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

______________________________________________________________________

## 🧠 Language Models & Prompts

### List All Prompts

```python
# Get all prompts in the space
prompts = client.get_all_prompts()

for prompt in prompts:
    print(f"Prompt: {prompt['name']}")
    print(f"  Description: {prompt['description']}")
    print(f"  Provider: {prompt['provider']}")
    print(f"  Model: {prompt['modelName']}")
    print(f"  Tags: {prompt['tags']}")
```

### Get a Specific Prompt

```python
# Get prompt by name
prompt = client.get_prompt("customer-support-classifier")
print(f"Prompt ID: {prompt['id']}")
print(f"Messages: {prompt['messages']}")
print(f"Parameters: {prompt['llmParameters']}")

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

### Update and Version Prompts

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

______________________________________________________________________

## 📥 Data Import Jobs

### File Import Jobs

```python
# Create a file import job for S3
file_job = client.create_file_import_job(
    blob_store="s3",
    bucket_name="ml-data-bucket",
    prefix="fraud-model/predictions/",
    model_name="fraud-detection-v2",
    model_type="score_categorical",
    model_schema={
        "predictionLabel": "prediction_label",
        "predictionScore": "prediction_score",
        "actualLabel": "actual_label",
        "predictionId": "transaction_id",
        "timestamp": "event_timestamp",
    },
    model_environment_name="production",
)

print(f"Created file import job: {file_job['jobId']}")

# Get all file import jobs
file_jobs = client.get_all_file_import_jobs()
for job in file_jobs:
    print(f"Job: {job['jobId']} - Status: {job['jobStatus']}")
    print(f"  Success: {job['totalFilesSuccessCount']}")
    print(f"  Failed: {job['totalFilesFailedCount']}")
    print(f"  Pending: {job['totalFilesPendingCount']}")
```

### Table Import Jobs

```python
# Create a BigQuery table import job
table_job = client.create_table_import_job(
    table_store="BigQuery",
    model_name="fraud-detection-v2",
    model_type="score_categorical",
    model_schema={
        "predictionLabel": "pred_label",
        "predictionScore": "pred_score",
        "actualLabel": "true_label",
        "predictionId": "id",
        "timestamp": "ts",
    },
    bigquery_table_config={
        "projectId": "my-gcp-project",
        "dataset": "ml_predictions",
        "tableName": "fraud_predictions",
    },
)

print(f"Created table import job: {table_job['jobId']}")

# Monitor job status
job_status = client.get_table_import_job(table_job["jobId"])
print(f"Job Status: {job_status['jobStatus']}")
print(f"Queries Success: {job_status['totalQueriesSuccessCount']}")
print(f"Queries Failed: {job_status['totalQueriesFailedCount']}")
```

______________________________________________________________________

## 📊 Dashboards

### List All Dashboards

```python
# Get all dashboards in the space
dashboards = client.get_all_dashboards()

for dashboard in dashboards:
    print(f"Dashboard: {dashboard['name']}")
    print(f"  Created by: {dashboard['creator']['name']}")
    print(f"  Created: {dashboard['createdAt']}")
    print(f"  Status: {dashboard['status']}")
```

### Get Dashboard Details

```python
# Get complete dashboard with all widgets
dashboard = client.get_dashboard("Model Performance Overview")

print(f"Dashboard: {dashboard['name']}")
print(f"Created by: {dashboard['creator']['name']}")

# Print widget summary
print(f"Widgets:")
print(f"  Statistic widgets: {len(dashboard['statisticWidgets'])}")
print(f"  Line chart widgets: {len(dashboard['lineChartWidgets'])}")
print(f"  Bar chart widgets: {len(dashboard['barChartWidgets'])}")
print(f"  Text widgets: {len(dashboard['textWidgets'])}")

# Get dashboard URL
dashboard_url = client.get_dashboard_url("Model Performance Overview")
print(f"Dashboard URL: {dashboard_url}")
```

______________________________________________________________________

## 🔗 Working with Annotations

### Create Annotations

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

## 🛠️ Utility Functions

### Configure Rate Limiting

```python
# Set sleep time between API requests (helpful for rate limiting)
client.set_sleep_time(1)  # 1 second between requests

# Reset to no delay
client.set_sleep_time(0)
```

### Get URLs for Different Resources

```python
# Get various resource URLs
model_url = client.model_url("model_123")
monitor_url = client.monitor_url("monitor_456")
prompt_url = client.prompt_url("prompt_789")
dashboard_url = client.dashboard_url("dashboard_abc")

print(f"Model: {model_url}")
print(f"Monitor: {monitor_url}")
print(f"Prompt: {prompt_url}")
print(f"Dashboard: {dashboard_url}")
```

______________________________________________________________________

## 🎯 Common Workflows

### Model Health Check Workflow

```python
def model_health_check(model_name):
    """Complete health check for a model"""

    # Get model info
    model = client.get_model(model_name)
    print(f"Checking model: {model['name']} (Type: {model['modelType']})")

    # Check recent volume
    volume = client.get_model_volume(model_name)
    print(f"Recent volume: {volume} predictions")

    # Check monitors
    monitors = client.get_all_monitors(model_name=model_name)
    triggered_monitors = [m for m in monitors if m["isTriggered"]]

    print(f"Total monitors: {len(monitors)}")
    print(f"Triggered monitors: {len(triggered_monitors)}")

    for monitor in triggered_monitors:
        print(f"  🚨 {monitor['name']} - {monitor['monitorCategory']}")

    # Check custom metrics
    custom_metrics = client.get_all_custom_metrics_for_model(model_name=model_name)
    print(f"Custom metrics: {len(custom_metrics)}")

    return {
        "model": model,
        "volume": volume,
        "monitors": monitors,
        "triggered_monitors": triggered_monitors,
        "custom_metrics": custom_metrics,
    }


# Run health check
health_report = model_health_check("fraud-detection-v2")
```

### Data Pipeline Setup Workflow

```python
def setup_data_pipeline(model_name, data_source_config):
    """Set up a complete data import pipeline"""

    # Create import job based on source type
    if data_source_config["type"] == "bigquery":
        job = client.create_table_import_job(
            table_store="BigQuery",
            model_name=model_name,
            model_type=data_source_config["model_type"],
            model_schema=data_source_config["schema"],
            bigquery_table_config=data_source_config["bigquery_config"],
        )
    elif data_source_config["type"] == "s3":
        job = client.create_file_import_job(
            blob_store="s3",
            bucket_name=data_source_config["bucket"],
            prefix=data_source_config["prefix"],
            model_name=model_name,
            model_type=data_source_config["model_type"],
            model_schema=data_source_config["schema"],
        )

    # Create basic monitors
    perf_monitor = client.create_performance_monitor(
        name=f"{model_name} Accuracy Monitor",
        model_name=model_name,
        model_environment_name="production",
        performance_metric="accuracy",
        operator="lessThan",
        threshold=0.8,
    )

    drift_monitor = client.create_drift_monitor(
        name=f"{model_name} Drift Monitor",
        model_name=model_name,
        drift_metric="psi",
        dimension_category="prediction",
        threshold=0.2,
    )

    return {
        "import_job": job,
        "performance_monitor": perf_monitor,
        "drift_monitor": drift_monitor,
    }


# Example usage
pipeline_config = {
    "type": "bigquery",
    "model_type": "score_categorical",
    "schema": {
        "predictionLabel": "pred_label",
        "predictionScore": "pred_score",
        "actualLabel": "true_label",
        "predictionId": "id",
        "timestamp": "timestamp",
    },
    "bigquery_config": {
        "projectId": "my-project",
        "dataset": "predictions",
        "tableName": "model_outputs",
    },
}

pipeline = setup_data_pipeline("new-model-v1", pipeline_config)
```

______________________________________________________________________

## 🚨 Error Handling

```python
from arize_toolkit.exceptions import ArizeAPIException

try:
    model = client.get_model("non-existent-model")
except ArizeAPIException as e:
    print(f"Model not found: {e}")

try:
    # Handle API rate limits
    client.set_sleep_time(2)  # Add delay between requests
    models = client.get_all_models()
except Exception as e:
    print(f"API error: {e}")
```

______________________________________________________________________

## 📚 Next Steps

Now that you've learned the basics, explore more advanced features:

- **[Model Tools](model_tools.md)** - Advanced model management
- **[Monitor Tools](monitor_tools.md)** - Comprehensive monitoring setup
- **[Custom Metrics Tools](custom_metrics_tools.md)** - Advanced custom metrics
- **[Language Model Tools](language_model_tools.md)** - LLM and prompt management
- **[Data Import Tools](data_import_tools.md)** - Advanced data pipeline setup
- **[Dashboard Tools](dashboard_tools.md)** - Dashboard creation and management
- **[Space & Organization Tools](space_and_organization_tools.md)** - Multi-tenant management

## 💡 Tips & Best Practices

1. **Use environment variables** for API keys to keep them secure
1. **Set appropriate sleep times** if you encounter rate limiting
1. **Monitor your imports** regularly using the job status methods
1. **Use descriptive names** for monitors, metrics, and prompts
1. **Tag your resources** for better organization
1. **Check monitor statuses** regularly as part of your ML operations workflow
1. **Version your prompts** when making significant changes

Happy building with Arize Toolkit! 🚀
