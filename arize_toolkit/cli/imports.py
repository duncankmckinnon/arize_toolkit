import json

import click

from arize_toolkit.cli.client_factory import get_client
from arize_toolkit.cli.output import print_error, print_result, print_success

ENVIRONMENT_CHOICES = ["production", "validation", "training", "tracing"]
MODEL_TYPE_CHOICES = [
    "classification",
    "regression",
    "ranking",
    "object_detection",
    "multi-class",
    "generative",
]


@click.group("imports")
def imports_group():
    """Manage data import jobs."""
    pass


# --- File imports ---


@imports_group.group("files")
def files_group():
    """Manage file import jobs (S3, GCS, Azure)."""
    pass


@files_group.command("list")
@click.pass_context
def files_list(ctx):
    """List all file import jobs."""
    client = get_client(ctx)
    data = client.get_all_file_import_jobs()
    print_result(
        data,
        columns=["id", "jobId", "jobStatus", "createdAt"],
        title="File Import Jobs",
        json_mode=ctx.obj["json_mode"],
    )


@files_group.command("get")
@click.argument("job_id")
@click.pass_context
def files_get(ctx, job_id):
    """Get a file import job by ID."""
    client = get_client(ctx)
    data = client.get_file_import_job(job_id=job_id)
    print_result(data, json_mode=ctx.obj["json_mode"])


@files_group.command("create")
@click.option(
    "--blob-store",
    required=True,
    type=click.Choice(["s3", "gcs", "azure"]),
    help="Cloud storage provider.",
)
@click.option("--bucket", required=True, help="Bucket name.")
@click.option("--prefix", required=True, help="Object prefix/path.")
@click.option("--model", required=True, help="Model name.")
@click.option(
    "--model-type",
    required=True,
    type=click.Choice(MODEL_TYPE_CHOICES),
    help="Model type.",
)
@click.option(
    "--schema",
    required=True,
    help="Model schema as JSON string or @filepath.",
)
@click.option("--model-version", default=None, help="Model version.")
@click.option(
    "--environment",
    type=click.Choice(ENVIRONMENT_CHOICES),
    default="production",
    help="Model environment.",
)
@click.option("--dry-run", is_flag=True, help="Run as dry run.")
@click.option("--batch-id", default=None, help="Batch ID.")
@click.option("--azure-tenant-id", default=None, help="Azure tenant ID.")
@click.option("--azure-storage-account", default=None, help="Azure storage account name.")
@click.pass_context
def files_create(
    ctx,
    blob_store,
    bucket,
    prefix,
    model,
    model_type,
    schema,
    model_version,
    environment,
    dry_run,
    batch_id,
    azure_tenant_id,
    azure_storage_account,
):
    """Create a file import job."""
    schema_data = _parse_json_arg(schema)
    client = get_client(ctx)
    result = client.create_file_import_job(
        blob_store=blob_store,
        bucket_name=bucket,
        prefix=prefix,
        model_name=model,
        model_type=model_type,
        model_schema=schema_data,
        model_version=model_version,
        model_environment_name=environment,
        dry_run=dry_run,
        batch_id=batch_id,
        azure_tenant_id=azure_tenant_id,
        azure_storage_account_name=azure_storage_account,
    )
    print_result(result, json_mode=ctx.obj["json_mode"])


@files_group.command("delete")
@click.argument("job_id")
@click.confirmation_option(prompt="Are you sure you want to delete this import job?")
@click.pass_context
def files_delete(ctx, job_id):
    """Delete a file import job."""
    client = get_client(ctx)
    result = client.delete_file_import_job(job_id=job_id)
    if result:
        print_success(f"File import job '{job_id}' deleted.")
    else:
        print_error(f"Failed to delete file import job '{job_id}'.")


# --- Table imports ---


@imports_group.group("tables")
def tables_group():
    """Manage table import jobs (BigQuery, Snowflake, Databricks)."""
    pass


@tables_group.command("list")
@click.pass_context
def tables_list(ctx):
    """List all table import jobs."""
    client = get_client(ctx)
    data = client.get_all_table_import_jobs()
    print_result(
        data,
        columns=["id", "jobId", "jobStatus", "createdAt"],
        title="Table Import Jobs",
        json_mode=ctx.obj["json_mode"],
    )


@tables_group.command("get")
@click.argument("job_id")
@click.pass_context
def tables_get(ctx, job_id):
    """Get a table import job by ID."""
    client = get_client(ctx)
    data = client.get_table_import_job(job_id=job_id)
    print_result(data, json_mode=ctx.obj["json_mode"])


@tables_group.command("create")
@click.option(
    "--table-store",
    required=True,
    type=click.Choice(["BigQuery", "Snowflake", "Databricks"]),
    help="Table store provider.",
)
@click.option("--model", required=True, help="Model name.")
@click.option(
    "--model-type",
    required=True,
    type=click.Choice(MODEL_TYPE_CHOICES),
    help="Model type.",
)
@click.option(
    "--schema",
    required=True,
    help="Model schema as JSON string or @filepath.",
)
@click.option(
    "--table-config",
    required=True,
    help="Table configuration as JSON string or @filepath.",
)
@click.option("--model-version", default=None, help="Model version.")
@click.option(
    "--environment",
    type=click.Choice(ENVIRONMENT_CHOICES),
    default="production",
    help="Model environment.",
)
@click.option("--dry-run", is_flag=True, help="Run as dry run.")
@click.option("--batch-id", default=None, help="Batch ID.")
@click.pass_context
def tables_create(
    ctx,
    table_store,
    model,
    model_type,
    schema,
    table_config,
    model_version,
    environment,
    dry_run,
    batch_id,
):
    """Create a table import job."""
    schema_data = _parse_json_arg(schema)
    config_data = _parse_json_arg(table_config)

    kwargs = {
        "table_store": table_store,
        "model_name": model,
        "model_type": model_type,
        "model_schema": schema_data,
        "model_version": model_version,
        "model_environment_name": environment,
        "dry_run": dry_run,
        "batch_id": batch_id,
    }

    config_key = {
        "BigQuery": "bigquery_table_config",
        "Snowflake": "snowflake_table_config",
        "Databricks": "databricks_table_config",
    }[table_store]
    kwargs[config_key] = config_data

    client = get_client(ctx)
    result = client.create_table_import_job(**kwargs)
    print_result(result, json_mode=ctx.obj["json_mode"])


@tables_group.command("delete")
@click.argument("job_id")
@click.confirmation_option(prompt="Are you sure you want to delete this import job?")
@click.pass_context
def tables_delete(ctx, job_id):
    """Delete a table import job."""
    client = get_client(ctx)
    result = client.delete_table_import_job(job_id=job_id)
    if result:
        print_success(f"Table import job '{job_id}' deleted.")
    else:
        print_error(f"Failed to delete table import job '{job_id}'.")


def _parse_json_arg(value: str):
    """Parse a JSON string or @filepath into a Python object."""
    if value.startswith("@"):
        filepath = value[1:]
        try:
            with open(filepath) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print_error(f"Failed to read JSON from '{filepath}': {e}")
    try:
        return json.loads(value)
    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON: {e}")
