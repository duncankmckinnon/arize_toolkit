# Datasets

## Overview

The `datasets` command group retrieves dataset metadata and example data from Arize.

| Command | Description | Client Method |
|---------|-------------|---------------|
| [`datasets list`](#datasets-list) | List all datasets in the current space | `get_all_datasets` |
| [`datasets get`](#datasets-get) | Get a dataset by name | `get_dataset` |
| [`datasets examples`](#datasets-examples) | Get examples from the latest dataset version | `get_dataset_examples` |

______________________________________________________________________

### `datasets list`

```bash
arize_toolkit datasets list
```

Lists all datasets in the current space.

**Example**

```bash
$ arize_toolkit datasets list
                               Datasets
┌──────────────────┬──────────────────────────────┬─────────────┬────────┬─────────────────┐
│ id               │ name                         │ datasetType │ status │ experimentCount │
├──────────────────┼──────────────────────────────┼─────────────┼────────┼─────────────────┤
│ RGF0YXNldDox...  │ pharmacy-malicious-baseline   │ generative  │ active │ 3               │
│ RGF0YXNldDoy...  │ eval-golden-set              │ generative  │ active │ 12              │
└──────────────────┴──────────────────────────────┴─────────────┴────────┴─────────────────┘

$ arize_toolkit --json datasets list
```

______________________________________________________________________

### `datasets get`

```bash
arize_toolkit datasets get NAME
```

Retrieves dataset metadata by name within the current space.

**Arguments**

- `NAME` — Name of the dataset.

**Example**

```bash
$ arize_toolkit datasets get pharmacy-malicious-baseline
┌──────────────────┬──────────────────────────────┬─────────────┬────────┐
│ id               │ name                         │ datasetType │ status │
├──────────────────┼──────────────────────────────┼─────────────┼────────┤
│ RGF0YXNldDox...  │ pharmacy-malicious-baseline   │ generative  │ active │
└──────────────────┴──────────────────────────────┴─────────────┴────────┘

$ arize_toolkit --json datasets get pharmacy-malicious-baseline
```

______________________________________________________________________

### `datasets examples`

```bash
arize_toolkit datasets examples NAME [OPTIONS]
```

Retrieves all example rows from the latest version of a dataset. Each row includes an `id` and a `data` dictionary mapping column names to values.

**Arguments**

- `NAME` — Name of the dataset.

**Options**

- `--dataset-id` — Use a dataset ID instead of the name argument.

**Example**

```bash
$ arize_toolkit datasets examples pharmacy-malicious-baseline
                        Dataset Examples
┌──────────────────────────┬──────────────────────────────────────────────┐
│ id                       │ data                                         │
├──────────────────────────┼──────────────────────────────────────────────┤
│ RGF0YXNldEV4YW1wbGU6... │ {'input': 'What is...', 'output': 'The...'} │
│ RGF0YXNldEV4YW1wbGU6... │ {'input': 'Show me...', 'output': 'Here..'} │
└──────────────────────────┴──────────────────────────────────────────────┘

# By dataset ID
$ arize_toolkit datasets examples ignored --dataset-id "RGF0YXNldDox..."

# JSON output
$ arize_toolkit --json datasets examples pharmacy-malicious-baseline
```
