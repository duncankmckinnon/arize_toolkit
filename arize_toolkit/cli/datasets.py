import click

from arize_toolkit.cli.client_factory import get_client
from arize_toolkit.cli.output import print_result


@click.group("datasets")
def datasets_group():
    """Manage Arize datasets."""
    pass


@datasets_group.command("list")
@click.pass_context
def datasets_list(ctx):
    """List all datasets in the current space."""
    client = get_client(ctx)
    data = client.get_all_datasets()
    columns = ["id", "name", "datasetType", "status", "experimentCount"]
    print_result(data, columns=columns, title="Datasets", json_mode=ctx.obj["json_mode"])


@datasets_group.command("info")
@click.argument("name")
@click.pass_context
def datasets_info(ctx, name):
    """Get dataset metadata by name."""
    client = get_client(ctx)
    data = client.get_dataset(name)
    print_result(data, json_mode=ctx.obj["json_mode"])


@datasets_group.command("get")
@click.argument("name")
@click.option("--dataset-id", default=None, help="Use dataset ID instead of name.")
@click.pass_context
def datasets_get(ctx, name, dataset_id):
    """Get examples from the latest version of a dataset."""
    client = get_client(ctx)
    data = client.get_dataset_examples(name=name if not dataset_id else None, dataset_id=dataset_id)
    columns = ["id", "data"]
    print_result(data, columns=columns, title="Dataset Examples", json_mode=ctx.obj["json_mode"])
