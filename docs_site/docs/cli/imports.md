# Data Imports

## Overview

The `imports` command group manages data import jobs that bring data from external sources into Arize. There are two sub-groups:

- **`imports files`** — Import from cloud object storage (S3, GCS, Azure Blob Storage)
- **`imports tables`** — Import from data warehouses (BigQuery, Snowflake, Databricks)

### File Import Commands

| Command | Description | Client Method |
|---------|-------------|---------------|
| [`imports files list`](#imports-files-list) | List file import jobs | `get_all_file_import_jobs` |
| [`imports files get`](#imports-files-get) | Get a file import job by ID | `get_file_import_job` |
| [`imports files create`](#imports-files-create) | Create a file import job | `create_file_import_job` |
| [`imports files delete`](#imports-files-delete) | Delete a file import job | `delete_file_import_job` |

### Table Import Commands

| Command | Description | Client Method |
|---------|-------------|---------------|
| [`imports tables list`](#imports-tables-list) | List table import jobs | `get_all_table_import_jobs` |
| [`imports tables get`](#imports-tables-get) | Get a table import job by ID | `get_table_import_job` |
| [`imports tables create`](#imports-tables-create) | Create a table import job | `create_table_import_job` |
| [`imports tables delete`](#imports-tables-delete) | Delete a table import job | `delete_table_import_job` |

______________________________________________________________________

## File Imports

### `imports files list`

```bash
arize_toolkit imports files list
```

Lists all file import jobs in the current space.

**Example**

```bash
$ arize_toolkit imports files list
                    File Import Jobs
┌──────────┬──────────┬────────────┬────────────┐
│ id       │ jobId    │ jobStatus  │ createdAt  │
├──────────┼──────────┼────────────┼────────────┤
│ f1       │ j-abc    │ completed  │ 2025-01-10 │
│ f2       │ j-def    │ running    │ 2025-02-01 │
└──────────┴──────────┴────────────┴────────────┘
```

______________________________________________________________________

### `imports files get`

```bash
arize_toolkit imports files get JOB_ID
```

Retrieves details for a file import job, including file counts and schema.

**Arguments**

- `JOB_ID` — The import job ID.

**Example**

```bash
arize_toolkit --json imports files get "j-abc123"
```

______________________________________________________________________

### `imports files create`

```bash
arize_toolkit imports files create --blob-store STORE --bucket BUCKET --prefix PREFIX --model MODEL --model-type TYPE --schema JSON [OPTIONS]
```

Creates a new file import job from cloud object storage.

**Required Options**

- `--blob-store` — Cloud provider: `s3`, `gcs`, or `azure`.
- `--bucket` — Bucket or container name.
- `--prefix` — Object prefix/path within the bucket.
- `--model` — Target model name.
- `--model-type` — Model type: `classification`, `regression`, `ranking`, `object_detection`, `multi-class`, or `generative`.
- `--schema` — Model schema as a JSON string or `@filepath`.

**Optional Options**

- `--model-version` — Model version string.
- `--environment` — Environment: `production`, `validation`, `training`, `tracing`. Defaults to `production`.
- `--dry-run` — Validate without importing.
- `--batch-id` — Batch ID for validation data.
- `--azure-tenant-id` — Azure tenant ID (Azure only).
- `--azure-storage-account` — Azure storage account name (Azure only).

**Schema Format**

The schema defines column mappings. Pass as inline JSON or from a file:

```json
{
  "predictionId": "id_column",
  "timestamp": "ts_column",
  "predictionLabel": "pred_column",
  "actualLabel": "actual_column",
  "features": "feature_"
}
```

**Example**

```bash
arize_toolkit imports files create \
    --blob-store s3 \
    --bucket "my-data-bucket" \
    --prefix "models/fraud/2025-01/" \
    --model "fraud-detection-v3" \
    --model-type classification \
    --schema @schema.json \
    --environment production
```

______________________________________________________________________

### `imports files delete`

```bash
arize_toolkit imports files delete JOB_ID [--yes]
```

Deletes a file import job. Prompts for confirmation unless `--yes` is passed.

**Arguments**

- `JOB_ID` — The import job ID.

**Options**

- `--yes` — Skip confirmation.

**Example**

```bash
arize_toolkit imports files delete "j-abc123" --yes
```

______________________________________________________________________

## Table Imports

### `imports tables list`

```bash
arize_toolkit imports tables list
```

Lists all table import jobs in the current space.

**Example**

```bash
arize_toolkit imports tables list
```

______________________________________________________________________

### `imports tables get`

```bash
arize_toolkit imports tables get JOB_ID
```

Retrieves details for a table import job.

**Arguments**

- `JOB_ID` — The import job ID.

**Example**

```bash
arize_toolkit --json imports tables get "j-xyz789"
```

______________________________________________________________________

### `imports tables create`

```bash
arize_toolkit imports tables create --table-store STORE --model MODEL --model-type TYPE --schema JSON --table-config JSON [OPTIONS]
```

Creates a new table import job from a data warehouse.

**Required Options**

- `--table-store` — Provider: `BigQuery`, `Snowflake`, or `Databricks`.
- `--model` — Target model name.
- `--model-type` — Model type: `classification`, `regression`, `ranking`, `object_detection`, `multi-class`, or `generative`.
- `--schema` — Model schema as a JSON string or `@filepath`.
- `--table-config` — Table configuration as a JSON string or `@filepath`.

**Optional Options**

- `--model-version` — Model version string.
- `--environment` — Environment: `production`, `validation`, `training`, `tracing`. Defaults to `production`.
- `--dry-run` — Validate without importing.
- `--batch-id` — Batch ID for validation data.

**Table Configuration Formats**

=== "BigQuery"

```json
{
  "projectId": "my-gcp-project",
  "dataset": "ml_data",
  "tableName": "predictions"
}
```

=== "Snowflake"

```json
{
  "accountID": "abc123",
  "schema": "PUBLIC",
  "database": "ML_DB",
  "tableName": "PREDICTIONS"
}
```

=== "Databricks"

```json
{
  "hostName": "my-workspace.databricks.com",
  "endpoint": "/sql/1.0/warehouses/abc",
  "port": "443",
  "catalog": "main",
  "databricksSchema": "default",
  "tableName": "predictions"
}
```

**Example**

```bash
arize_toolkit imports tables create \
    --table-store BigQuery \
    --model "fraud-detection-v3" \
    --model-type classification \
    --schema @schema.json \
    --table-config '{"projectId":"my-project","dataset":"ml","tableName":"preds"}'
```

______________________________________________________________________

### `imports tables delete`

```bash
arize_toolkit imports tables delete JOB_ID [--yes]
```

Deletes a table import job. Prompts for confirmation unless `--yes` is passed.

**Arguments**

- `JOB_ID` — The import job ID.

**Options**

- `--yes` — Skip confirmation.

**Example**

```bash
arize_toolkit imports tables delete "j-xyz789" --yes
```
