import click

from arize_toolkit.cli.client_factory import get_client
from arize_toolkit.cli.output import print_error, print_result, print_success


@click.group("models")
def models_group():
    """Manage Arize models (also available as 'projects')."""
    pass


@models_group.command("list")
@click.pass_context
def models_list(ctx):
    """List all models in the current space."""
    client = get_client(ctx)
    data = client.get_all_models()
    print_result(
        data,
        columns=["id", "name", "modelType", "createdAt"],
        title="Models",
        json_mode=ctx.obj["json_mode"],
    )


@models_group.command("get")
@click.argument("name")
@click.pass_context
def models_get(ctx, name):
    """Get a model by name."""
    client = get_client(ctx)
    data = client.get_model(model_name=name)
    print_result(data, json_mode=ctx.obj["json_mode"])


@models_group.command("volume")
@click.argument("name")
@click.option("--start-time", default=None, help="Start time (ISO format).")
@click.option("--end-time", default=None, help="End time (ISO format).")
@click.pass_context
def models_volume(ctx, name, start_time, end_time):
    """Get prediction volume for a model."""
    client = get_client(ctx)
    data = client.get_model_volume(model_name=name, start_time=start_time, end_time=end_time)
    print_result(data, json_mode=ctx.obj["json_mode"])


@models_group.command("total-volume")
@click.option("--model-name", default=None, help="Model name.")
@click.option("--model-id", default=None, help="Model ID.")
@click.option("--start-time", default=None, help="Start time (ISO format).")
@click.option("--end-time", default=None, help="End time (ISO format).")
@click.pass_context
def models_total_volume(ctx, model_name, model_id, start_time, end_time):
    """Get total prediction volume."""
    client = get_client(ctx)
    total = client.get_total_volume(
        model_name=model_name,
        model_id=model_id,
        start_time=start_time,
        end_time=end_time,
    )
    if ctx.obj["json_mode"]:
        from arize_toolkit.cli.output import print_json

        print_json({"total_volume": total})
    else:
        click.echo(f"Total volume: {total}")


@models_group.command("performance")
@click.argument("metric")
@click.argument("environment")
@click.option("--model-name", default=None, help="Model name.")
@click.option("--model-id", default=None, help="Model ID.")
@click.option(
    "--granularity",
    type=click.Choice(["hour", "day", "week", "month"]),
    default="month",
    help="Time granularity.",
)
@click.option("--start-time", default=None, help="Start time (ISO format).")
@click.option("--end-time", default=None, help="End time (ISO format).")
@click.pass_context
def models_performance(ctx, metric, environment, model_name, model_id, granularity, start_time, end_time):
    """Get performance metrics over time."""
    client = get_client(ctx)
    from datetime import datetime

    st = datetime.fromisoformat(start_time) if start_time else None
    et = datetime.fromisoformat(end_time) if end_time else None
    data = client.get_performance_metric_over_time(
        metric=metric,
        environment=environment,
        model_name=model_name,
        model_id=model_id,
        granularity=granularity,
        start_time=st,
        end_time=et,
        to_dataframe=False,
    )
    print_result(data, json_mode=ctx.obj["json_mode"])


@models_group.command("delete-data")
@click.argument("name")
@click.option("--start-time", default=None, help="Start time (ISO format).")
@click.option("--end-time", default=None, help="End time (ISO format).")
@click.confirmation_option(prompt="Are you sure you want to delete data?")
@click.pass_context
def models_delete_data(ctx, name, start_time, end_time):
    """Delete data from a model."""
    client = get_client(ctx)
    result = client.delete_data(model_name=name, start_time=start_time, end_time=end_time)
    if result:
        print_success(f"Data deleted from model '{name}'.")
    else:
        print_error(f"Failed to delete data from model '{name}'.")
