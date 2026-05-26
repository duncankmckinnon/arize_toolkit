import click

from arize_toolkit.cli.client_factory import get_client
from arize_toolkit.cli.output import print_result, print_url


@click.group("dashboards")
def dashboards_group():
    """Manage Arize dashboards."""
    pass


@dashboards_group.command("list")
@click.pass_context
def dashboards_list(ctx):
    """List all dashboards in the current space."""
    client = get_client(ctx)
    data = client.get_all_dashboards()
    print_result(
        data,
        columns=["id", "name", "createdAt"],
        title="Dashboards",
        json_mode=ctx.obj["json_mode"],
    )


@dashboards_group.command("get")
@click.argument("name")
@click.pass_context
def dashboards_get(ctx, name):
    """Get a dashboard by name."""
    client = get_client(ctx)
    data = client.get_dashboard(dashboard_name=name)
    print_result(data, json_mode=ctx.obj["json_mode"])


@dashboards_group.command("create")
@click.argument("name")
@click.pass_context
def dashboards_create(ctx, name):
    """Create an empty dashboard."""
    client = get_client(ctx)
    url = client.create_dashboard(name=name)
    print_url(url, label="Created dashboard")


@dashboards_group.command("create-volume")
@click.argument("name")
@click.option(
    "--model",
    multiple=True,
    help="Model names to include (omit for all models).",
)
@click.pass_context
def dashboards_create_volume(ctx, name, model):
    """Create a model volume dashboard."""
    client = get_client(ctx)
    model_names = list(model) if model else None
    url = client.create_model_volume_dashboard(dashboard_name=name, model_names=model_names)
    print_url(url, label="Created volume dashboard")
