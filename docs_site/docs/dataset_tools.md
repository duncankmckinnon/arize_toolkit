# Dataset Tools

## Overview

In Arize, datasets are collections of examples used for experimentation and evaluation. Each dataset contains rows of data organized by columns, with support for string, numeric, and list-of-string values.

In `arize_toolkit`, the `Client` exposes helpers for:

1. Listing all datasets in a space
1. Retrieving dataset metadata by name or ID
1. Fetching all example rows from the latest dataset version

| Operation | Helper |
|-----------|--------|
| List all datasets | [`get_all_datasets`](#get_all_datasets) |
| Get dataset by name | [`get_dataset`](#get_dataset) |
| Get dataset by ID | [`get_dataset_by_id`](#get_dataset_by_id) |
| Get dataset examples | [`get_dataset_examples`](#get_dataset_examples) |

## Dataset Operations

______________________________________________________________________

### `get_all_datasets`

```python
datasets: list[dict] = client.get_all_datasets()
```

Retrieves all datasets in the current space. Automatically paginates through all results.

**Returns**

A list of dataset dictionaries, each containing `id`, `name`, `createdAt`, `updatedAt`, `datasetType`, `status`, `columns`, `experimentCount`.

**Example**

```python
datasets = client.get_all_datasets()
for ds in datasets:
    print(f"{ds['name']} ({ds['status']}) - {ds['experimentCount']} experiments")
```

______________________________________________________________________

### `get_dataset`

```python
dataset: dict = client.get_dataset(name="my-dataset")
```

Retrieves a dataset by name within the current space.

**Parameters**

- `name` (str) — Name of the dataset to retrieve.

**Returns**

A dictionary with dataset metadata: `id`, `name`, `createdAt`, `updatedAt`, `datasetType`, `status`, `columns`, `experimentCount`.

**Example**

```python
dataset = client.get_dataset(name="pharmacy-malicious-baseline")
print(dataset["id"])  # "RGF0YXNldDox..."
print(dataset["status"])  # "active"
print(dataset["columns"])  # ["input", "output", "timestamp"]
```

______________________________________________________________________

### `get_dataset_by_id`

```python
dataset: dict = client.get_dataset_by_id(dataset_id="RGF0YXNldDox...")
```

Retrieves a dataset by its ID.

**Parameters**

- `dataset_id` (str) — ID of the dataset (base64-encoded).

**Returns**

A dictionary with dataset metadata: `id`, `name`, `createdAt`, `updatedAt`, `datasetType`, `status`, `columns`, `experimentCount`.

**Example**

```python
dataset = client.get_dataset_by_id(dataset_id="RGF0YXNldDox...")
print(dataset["name"])  # "pharmacy-malicious-baseline"
```

______________________________________________________________________

### `get_dataset_examples`

```python
examples: list[dict] = client.get_dataset_examples(name="my-dataset")
```

Retrieves all examples (rows) from the latest version of a dataset. Automatically paginates through all results. Each example contains a `data` dictionary mapping column names to their values.

**Parameters**

- `name` (Optional[str]) — Name of the dataset. Either `name` or `dataset_id` must be provided.
- `dataset_id` (Optional[str]) — ID of the dataset. Either `name` or `dataset_id` must be provided.

**Returns**

A list of example dictionaries, each containing:

- `id` (str) — Unique identifier for the example
- `createdAt` (datetime) — When the example was created
- `updatedAt` (datetime) — When the example was last updated
- `data` (dict) — Column name to value mapping

**Example**

```python
examples = client.get_dataset_examples(name="pharmacy-malicious-baseline")
for ex in examples:
    print(ex["id"])  # "RGF0YXNldEV4YW1wbGU6..."
    print(ex["data"]["input"])  # "What is the dosage for..."
    print(ex["data"]["output"])  # "The recommended dosage..."

# Or by dataset ID
examples = client.get_dataset_examples(dataset_id="RGF0YXNldDox...")
print(len(examples))  # 50
```
