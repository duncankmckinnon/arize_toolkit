# Utility Tools

## Overview

The Utility Tools provide helpful methods for configuring and managing the `Client` behavior during runtime. These utilities help optimize performance and handle rate limiting when making multiple API requests.

The utility tools currently include:

1. Managing request rate limiting through sleep time configuration

| Operation | Helper |
|-----------|--------|
| Update request sleep time | [`set_sleep_time`](#set_sleep_time) |

______________________________________________________________________

## Client Configuration

______________________________________________________________________

### `set_sleep_time`

```python
updated_client: Client = client.set_sleep_time(sleep_time: int)
```

Updates the sleep time for the existing client instance. This method configures how long the client will wait between API requests, which is useful for avoiding rate limiting when making multiple requests or processing large amounts of data.

**Parameters**

- `sleep_time` – The number of seconds to wait between requests. A value of 0 means no delay between requests.

**Returns**

- `Client` – The updated client instance (returns the same client object for method chaining)

**Example**

```python
from arize_toolkit import Client

# Initialize client with default sleep time (0 seconds)
client = Client(
    organization="my-org", space="my-space", arize_developer_key="your-api-key"
)

# Update sleep time for rate limiting
client = client.set_sleep_time(2)

# Method chaining example - get all models with rate limiting
models = client.set_sleep_time(5).get_all_models()

# Temporarily increase sleep time for bulk operations
original_client = client.set_sleep_time(10)
all_models = []
for space_name in ["space1", "space2", "space3"]:
    client.switch_space(space=space_name)
    all_models.extend(client.get_all_models())

# Reset to no delay for quick operations
client.set_sleep_time(0)
single_model = client.get_model("my-model")
```
