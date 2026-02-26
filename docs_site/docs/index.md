# Arize Toolkit

<meta property="og:title" content="Arize Toolkit">
<meta property="og:description" content="Arize Toolkit is a Python client for interacting with the Arize AI API.">
<meta property="og:image" content="https://arize.com/images/arize_toolkit_v2.png">
<meta property="og:url" content="https://arize.com/toolkit">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Arize Toolkit">
<meta property="og:locale" content="en_US">
<meta property="og:image:width" content="200">
<meta property="og:image:height" content="200">
<div align="center">
  <img src="images/logos/arize_toolkit_v2.png" alt="Arize Toolkit Logo" width="200"/>
</div>

Welcome to the documentation for Arize Toolkit, a Python client for interacting with the Arize AI API.
To get started with the toolkit, check out the [Quickstart Guide 🚀 ](quickstart.md).

## Quick Links

- [Model Tools](model_tools.md) - Documentation for model tools
- [Monitor Tools](monitor_tools.md) - Documentation for monitor tools
- [Custom Metrics Tools](custom_metrics_tools.md) - Documentation for custom metrics tools
- [Language Model Tools](language_model_tools.md) - Documentation for language model tools
- [Space & Organization Tools](space_and_organization_tools.md) - Documentation for space, organization, & navigation tools
- [Data Import Tools](data_import_tools.md) - Documentation for importing data from files and databases
- [Dashboard Tools](dashboard_tools.md) - Documentation for dashboard tools
- [Utility Tools](utility_tools.md) - Documentation for client configuration and utility functions

## Extensions

- [Prompt Optimization](extensions/prompt_optimization.md) - Automated prompt improvement based on historical performance

## Claude Code Plugins

- [Plugin Marketplace](plugins/index.md) - Install AI-assisted skills for querying, managing, and developing with the Arize platform

## Disclaimer

Although this package is used for development work with and within the Arize platform, it is not an Arize product.
It is a open source project developed and maintained by an Arize Engineer. Feel free to add issues or reach out for help in the Arize community Slack channel.

## Overview

Arize Toolkit is a set of tools packaged as a Python client that lets you easily interact with Arize AI APIs.
Here's a quick overview of the main features in the current release:

- Access and manage models
- Retrieve performance metrics over a time period
- Retrieve inference volume over a time period
- Create, copy, and manage custom metrics
- Create, copy, and manage monitors and alerting
- Work with LLM features like prompts and annotations
- Import data from cloud storage (S3, GCS, Azure) and databases (BigQuery, Snowflake, Databricks)
- Create, update, and delete data import jobs with full lifecycle management

## Installation

```bash
pip install arize_toolkit
```

## Client Setup

The `Client` class is the entrypoint for interacting with the toolkit. It provides maintains the connection information for making requests to the Arize APIs, and offers a wide range of operations for interacting with models, monitors, dashboards, and more.

### API Key

To create a client, you need to provide your Arize API key. Use this reference to [get your API key](https://docs.arize.com/arize/reference/authentication-and-security/api-keys) from the Arize UI.

![Arize UI Path](images/api_key_ref.png)

### Organization and Space

You will also need to provide an `organization` name and `space` name. To give some context, models are scoped to a space, and the space is scoped to an organization. These can be found by navigating to the Arize UI and looking at the upper left path in the `Projects & Models` page. They will be in the format `organization/space`.

For the example below, the organization is `Demo Models` and the space is `Demo Model Manager`.

![Arize UI Path](images/path_ref.png)

### For On Prem deployments

For SaaS users, the default API endpoint is always going to be `https://api.arize.com`.
If you are using an on prem deployment of Arize, you will need to provide the `api_url` parameter.
This parameters should just be the base url of your Arize instance.

## For Developers

- [Development Guide](developers/development.md) - Information about extending the toolkit
- [Integration Tests](developers/integration_test.md) - Running integration tests
