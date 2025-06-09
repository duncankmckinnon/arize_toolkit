<div align="center">
  <img src="docs_site/docs/images/logos/arize_toolkit_v2.png" alt="Arize Toolkit Logo" width="200"/>
</div>

<div align="center">

[![Tests](https://github.com/duncankmckinnon/arize_toolkit/actions/workflows/test.yml/badge.svg)](https://github.com/duncankmckinnon/arize_toolkit/actions/workflows/test.yml)
[![Documentation](https://github.com/duncankmckinnon/arize_toolkit/actions/workflows/docs.yml/badge.svg)](https://github.com/duncankmckinnon/arize_toolkit/actions/workflows/docs.yml)
[![PyPI Package](https://github.com/duncankmckinnon/arize_toolkit/actions/workflows/publish.yml/badge.svg)](https://github.com/duncankmckinnon/arize_toolkit/actions/workflows/publish.yml)
[![Lint and Format](https://github.com/duncankmckinnon/arize_toolkit/actions/workflows/lint.yml/badge.svg)](https://github.com/duncankmckinnon/arize_toolkit/actions/workflows/lint.yml)
[![Python Version](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org)
[![Poetry](https://img.shields.io/badge/poetry-1.0+-blueviolet)](https://python-poetry.org)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Flake8](https://img.shields.io/badge/flake8-7.2.0-blue)](https://flake8.pycqa.org)
[![isort](https://img.shields.io/badge/isort-5.13.2-blue)](https://pycqa.github.io/isort)
[![mdformat](https://img.shields.io/badge/mdformat-0.7.22-blue)](https://mdformat.readthedocs.io)
[![pytest](https://img.shields.io/badge/pytest-latest-blue)](https://docs.pytest.org)
[![coverage](https://img.shields.io/badge/coverage-latest-blue)](https://coverage.readthedocs.io)

</div>

Check out the [docs](https://duncankmckinnon.github.io/arize_toolkit) for the latest features and information.

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

![Arize UI Path](docs_site/docs/images/api_key_ref.png)

### Organization and Space

You will also need to provide an `organization` name and `space` name. To give some context, models are scoped to a space, and the space is scoped to an organization. These can be found by navigating to the Arize UI and looking at the upper left path in the `Projects & Models` page. They will be in the format `organization/space`.

For the example below, the organization is `Demo Models` and the space is `Demo Model Manager`.

![Arize UI Path](docs_site/docs/images/path_ref.png)

### For On Prem deployments

For SaaS users, the default API endpoint is always going to be `https://api.arize.com`.
If you are using an on prem deployment of Arize, you will need to provide the `api_url` parameter.
This parameters should just be the base url of your Arize instance.
