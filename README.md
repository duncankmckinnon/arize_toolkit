[![Tests](https://github.com/duncankmckinnon/arize_toolkit/actions/workflows/test.yml/badge.svg)](https://github.com/duncankmckinnon/arize_toolkit/actions/workflows/test.yml)
[![Documentation](https://github.com/duncankmckinnon/arize_toolkit/actions/workflows/docs.yml/badge.svg)](https://github.com/duncankmckinnon/arize_toolkit/actions/workflows/docs.yml)
[![PyPI Package](https://github.com/duncankmckinnon/arize_toolkit/actions/workflows/publish.yml/badge.svg)](https://github.com/duncankmckinnon/arize_toolkit/actions/workflows/publish.yml)

# Arize Toolkit

Check out the [docs](https://duncankmckinnon.github.io/arize_toolkit) for the latest features and information.

## Disclaimer

Although this package is used for development work with and within the Arize platform, it is not an Arize product.
It is a open source project developed and maintained by an Arize Engineer.

## Disclaimer

Although this package is used for development work with and within the Arize platform, it is not an Arize supported product.
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

### Sleep Time

The `Client` class can be configured to wait a certain amount of time between requests. This is useful to avoid rate limiting.
The default sleep time is 0 seconds. When instantiating the client, you can set the `sleep_time` parameter to the number of seconds to wait between requests. This can save time if you are making a large number or requests or getting a large amount of data. If you start seeing rate limit errors, you can increase this value. There is a helper function in the client to update the sleep time in line:

#### `set_sleep_time`

```python
from arize_toolkit import Client

client: Client = client.set_sleep_time(sleep_time: int)
```

This will update the sleep time for the existing client in line.

- **Parameters**

  - `sleep_time` – The number of seconds to wait between requests

- **Returns**

  - `Client` – The updated client

- **Example**

```python
from arize_toolkit import Client

client = Client(..., sleep_time=0)

# Update the sleep time in line
lots_of_models = client.set_sleep_time(10).get_all_models()
```

### Switching Spaces and Organizations

The `Client` class can be configured to switch to a different space or a space in a different organization. This is useful if you are working with multiple spaces or if you need to switch to a different space on the fly without having to create a new client.

#### `set_space`

```python
space_url: str = client.set_space(space: str, organization: Optional[str] = None)
```

This will update the space and organization for the existing client. It will also return the full url of the new space, which is comprised of the organization and space ids.

- **Parameters**

  - `space` – The name of the space to switch to
  - `organization` – *Optional* The name of the organization to switch to if different from the current organization

- **Returns**

  - `str` – The full url of the new space

- **Example**

```python
client = Client(..., space="my_space")

# get the current space url
current_space_url = client.space_url

# Get all models in the current space
current_space_models = client.get_all_models()

# Switch to a different space
other_space_url = client.set_space(
    space="my_other_space", organization="my_other_organization"
)

# Get all models in the new space
other_space_models = client.get_all_models()
```
