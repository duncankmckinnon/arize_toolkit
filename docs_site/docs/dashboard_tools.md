# Dashboard Tools

## Overview

In Arize, dashboards provide a powerful way to visualize and monitor your machine learning models through customizable widgets and charts. Dashboards can contain multiple types of widgets including statistics, line charts, bar charts, text widgets, and performance slices. For more information about dashboards in Arize check out the **[documentation on Arize dashboards](https://arize.com/docs/ax/observe/dashboards)**.

In `arize_toolkit`, the `Client` exposes helpers for:

1. Discovering and retrieving existing dashboards
1. Getting complete dashboard details including all widgets
1. Getting direct links to dashboards in the Arize UI
1. Accessing detailed widget information and performance slices

For completeness, the full set of dashboard helpers is repeated below.
Click on the function name to jump to the detailed section.

| Operation | Helper |
|-----------|--------|
| List every dashboard | [`get_all_dashboards`](#get_all_dashboards) |
| Fetch a complete dashboard by *name* | [`get_dashboard`](#get_dashboard) |
| Fetch a complete dashboard by *id* | [`get_dashboard_by_id`](#get_dashboard_by_id) |
| Quick-link to a dashboard in the UI | [`get_dashboard_url`](#get_dashboard_url) |
| Build dashboard URL by *id* | [`dashboard_url`](#dashboard_url) |

## Dashboard Operations

The dashboard operations are a collection of tools that help you retrieve information about dashboards and their components.

______________________________________________________________________

### `get_all_dashboards`

```python
dashboards: list[dict] = client.get_all_dashboards()
```

Retrieves basic information about all dashboards in the current space. This is useful for discovery and getting a list of available dashboards.

**Returns**

A list of dictionaries – one per dashboard – containing basic metadata such as:

- `id` – the canonical identifier for the dashboard
- `name` – the human-readable name shown in the Arize UI
- `creator` – the user who created the dashboard with `id`, `name`, and `email`
- `createdAt` – the date and time the dashboard was created
- `status` – the current status of the dashboard (e.g. "active", "inactive", "deleted")

**Example**

```python
for dashboard in client.get_all_dashboards():
    print(f"{dashboard['name']}: {dashboard['id']}")
    print(f"Created by: {dashboard['creator']['name']}")
```

______________________________________________________________________

### `get_dashboard`

```python
dashboard: dict = client.get_dashboard(dashboard_name: str)
```

Retrieves complete information about a dashboard by its name, including all models, widgets, and performance slices. This is the most comprehensive way to get dashboard data.

**Parameters**

- `dashboard_name` – The *human-readable* name shown in the Arize UI.

**Returns**

A complete dashboard dictionary containing:

- `id` – the canonical identifier for the dashboard
- `name` – the human-readable name shown in the Arize UI
- `creator` – the user who created the dashboard
- `createdAt` – the date and time the dashboard was created
- `status` – the current status of the dashboard
- `models` – list of all models referenced in the dashboard
- `statisticWidgets` – list of statistic widgets
- `lineChartWidgets` – list of line chart widgets
- `experimentChartWidgets` – list of experiment chart widgets
- `driftLineChartWidgets` – list of drift line chart widgets
- `monitorLineChartWidgets` – list of monitor line chart widgets
- `textWidgets` – list of text widgets
- `barChartWidgets` – list of bar chart widgets
- `performanceSlices` – list of dashboard performance slices

(see [Widget Types](#widget-types) below for more information on the widget types)

**Example**

```python
dashboard = client.get_dashboard("Production Monitoring Dashboard")
print(f"Dashboard has {len(dashboard['models'])} models")
print(
    f"Total widgets: {len(dashboard['statisticWidgets']) + len(dashboard['lineChartWidgets'])}"
)

# Access specific widget types
for widget in dashboard["statisticWidgets"]:
    print(f"Statistic Widget: {widget['title']}")
```

______________________________________________________________________

### `get_dashboard_by_id`

```python
dashboard: dict = client.get_dashboard_by_id(dashboard_id: str)
```

Identical to `get_dashboard` but retrieves the dashboard by its canonical ID instead of name. This is useful when you have stored the dashboard ID in a database or CI pipeline.

**Parameters**

- `dashboard_id` – the canonical identifier for the dashboard

**Returns**

A complete dashboard dictionary with the same structure as `get_dashboard`.

- `id` – the canonical identifier for the dashboard
- `name` – the human-readable name shown in the Arize UI
- `creator` – the user who created the dashboard
- `createdAt` – the date and time the dashboard was created
- `status` – the current status of the dashboard
- `models` – list of all models referenced in the dashboard
- `statisticWidgets` – list of statistic widgets
- `lineChartWidgets` – list of line chart widgets
- `experimentChartWidgets` – list of experiment chart widgets
- `driftLineChartWidgets` – list of drift line chart widgets
- `monitorLineChartWidgets` – list of monitor line chart widgets
- `textWidgets` – list of text widgets
- `barChartWidgets` – list of bar chart widgets
- `performanceSlices` – list of dashboard performance slices

(see [Widget Types](#widget-types) below for more information on the widget types)

**Example**

```python
dashboard = client.get_dashboard_by_id("******")
print(f"Dashboard name: {dashboard['name']}")
for model in dashboard["models"]:
    print(f"Model: {model['name']}")
```

______________________________________________________________________

### `get_dashboard_url`

```python
url: str = client.get_dashboard_url(dashboard_name: str)
```

Builds a deep-link that opens the dashboard inside the Arize UI – handy for dashboards, Slack links, or emails.

**Parameters**

- `dashboard_name` – The *human-readable* name shown in the Arize UI.

**Returns**

A URL to the dashboard inside the Arize UI.

**Example**

```python
import webbrowser
from arize_toolkit import Client

client = Client(
    organization=os.getenv("ORG"),
    space=os.getenv("SPACE"),
    arize_developer_key=os.getenv("ARIZE_DEVELOPER_KEY"),
)

# Open the dashboard in the Arize UI
webbrowser.open(client.get_dashboard_url("Production Monitoring Dashboard"))
```

______________________________________________________________________

### `dashboard_url`

```python
url: str = client.dashboard_url(dashboard_id: str)
```

Builds a URL to a dashboard using its canonical ID. This is a utility method for when you already have the dashboard ID.

**Parameters**

- `dashboard_id` – the canonical identifier for the dashboard

**Returns**

A URL to the dashboard inside the Arize UI.

**Example**

```python
dashboard_id = "******"
url = client.dashboard_url(dashboard_id)
print(f"Dashboard URL: {url}")
```

______________________________________________________________________

## Widget Types

Dashboards can contain several different types of widgets, each designed for specific visualization and monitoring needs. Below are detailed breakdowns of each widget type and their key properties.

### Statistic Widgets

Statistic widgets display single-value metrics such as accuracy, count, or average values. These are ideal for showing key performance indicators at a glance.

**Key Properties:**

- `title` – Display name of the widget
- `modelId` – ID of the model being monitored
- `performanceMetric` – The metric being displayed (e.g., "accuracy", "f_1")
- `dimensionCategory` – What aspect is being measured (e.g., "prediction", "actuals")
- `aggregation` – How the data is aggregated (e.g., "avg", "count")
- `modelEnvironmentName` – Which environment (e.g., "production", "validation")
- `timeSeriesMetricType` – Type of metric ("modelDataMetric" or "evaluationMetric")
- `filters` – Applied filters to narrow down the data
- `customMetric` – Custom metric definition if used

**Example Usage:**

```python
dashboard = client.get_dashboard("My Dashboard")
for widget in dashboard["statisticWidgets"]:
    print(f"Widget: {widget['title']}")
    print(f"Metric: {widget['performanceMetric']}")
    print(f"Environment: {widget['modelEnvironmentName']}")
```

### Line Chart Widgets

Line chart widgets show trends over time for various metrics. They're perfect for tracking performance, drift, or data quality metrics across time periods.

**Key Properties:**

- `title` – Display name of the widget
- `yMin`/`yMax` – Y-axis range constraints
- `yAxisLabel` – Label for the Y-axis
- `timeSeriesMetricType` – Type of time series data
- `plots` – List of individual plot configurations within the chart
- `config` – Chart configuration including axis settings and curve type

**Plot Properties:**

- `modelId` – Model being plotted
- `dimensionCategory` – What dimension is being tracked
- `splitByEnabled` – Whether data is split by a dimension
- `cohorts` – Data cohorts for comparison
- `colors` – Color scheme for the plots

### Bar Chart Widgets

Bar chart widgets display categorical data comparisons, such as prediction distributions or feature importance rankings.

**Key Properties:**

- `title` – Display name of the widget
- `sortOrder` – How bars are ordered ("ascending", "descending")
- `yMin`/`yMax` – Y-axis range constraints
- `yAxisLabel` – Label for the Y-axis
- `topN` – Limit to top N values
- `isNormalized` – Whether values are normalized
- `performanceMetric` – Associated performance metric
- `plots` – List of plot configurations
- `config` – Chart configuration

**Plot Properties:**

- `modelId` – Model being plotted
- `dimensionCategory` – Category of data being visualized
- `aggregation` – How data is aggregated
- `predictionValueClass` – For classification models, which class

### Text Widgets

Text widgets provide custom text content, descriptions, or explanations within dashboards.

**Key Properties:**

- `title` – Display name of the widget
- `content` – The text content to display (supports markdown)

### Experiment Chart Widgets

Experiment chart widgets display evaluation results from experiments and A/B tests.

**Key Properties:**

- `title` – Display name of the widget
- `plots` – List of experiment plots

**Plot Properties:**

- `datasetId` – Dataset used for the experiment
- `evaluationMetric` – Metric being evaluated

### Performance Slices

Performance slices provide detailed breakdowns of model performance across different data segments or conditions.

**Key Properties:**

- `id` – Unique identifier for the slice
- `performanceMetric` – The performance metric measured
- `metricValue` – The calculated metric value
- `metricValueType` – Type of the value ("number", "string", "range", "total")
- `metricValueKey` – The segment or condition this applies to
- `evalMetricMin`/`evalMetricMax` – Range for heatmap visualization
- `widget` – Associated bar chart widget
- `barChartBarNode` – Corresponding bar chart data

______________________________________________________________________

## End-to-End Example

Below is a comprehensive script that showcases how dashboard operations can be used to analyze and monitor your models:

```python
from arize_toolkit import Client

client = Client(
    organization="my-org",
    space="my-space",
)

# 1. Discover available dashboards
dashboards = client.get_all_dashboards()
print(f"Found {len(dashboards)} dashboards")

# 2. Get complete dashboard details
dashboard_name = "Production Monitoring Dashboard"
dashboard = client.get_dashboard(dashboard_name)
print(f"Dashboard: {dashboard['name']}")
print(f"Models monitored: {len(dashboard['models'])}")

# 3. Analyze statistic widgets
print("\n=== Statistic Widgets ===")
for widget in dashboard["statisticWidgets"]:
    print(f"Widget: {widget['title']}")
    if widget["performanceMetric"]:
        print(f"  Metric: {widget['performanceMetric']}")
    if widget["modelEnvironmentName"]:
        print(f"  Environment: {widget['modelEnvironmentName']}")

# 4. Review line chart trends
print(f"\n=== Line Chart Widgets ===")
for widget in dashboard["lineChartWidgets"]:
    print(f"Chart: {widget['title']}")
    print(f"  Plots: {len(widget['plots']) if widget['plots'] else 0}")

# 5. Check performance slices for detailed insights
print(f"\n=== Performance Slices ===")
for slice in dashboard["performanceSlices"]:
    if slice["performanceMetric"] and slice["metricValue"]:
        print(f"Metric: {slice['performanceMetric']} = {slice['metricValue']}")
        if slice["metricValueKey"]:
            print(f"  Segment: {slice['metricValueKey']}")

# 6. Get dashboard URL for sharing
url = client.get_dashboard_url(dashboard_name)
print(f"\nDashboard URL: {url}")
```
