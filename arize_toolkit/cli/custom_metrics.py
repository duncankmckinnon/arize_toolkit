import click

from arize_toolkit.cli.client_factory import get_client
from arize_toolkit.cli.output import print_error, print_result, print_success, print_url

ENVIRONMENT_CHOICES = ["tracing", "production", "staging", "development"]


@click.group("custom-metrics")
def custom_metrics_group():
    """Manage Arize custom metrics."""
    pass


@custom_metrics_group.command("list")
@click.option("--model-name", default=None, help="Model name (omit for all models).")
@click.pass_context
def custom_metrics_list(ctx, model_name):
    """List custom metrics."""
    client = get_client(ctx)
    data = client.get_all_custom_metrics(model_name=model_name)
    if isinstance(data, dict):
        # When no model specified, returns dict of model -> metrics
        if ctx.obj["json_mode"]:
            from arize_toolkit.cli.output import print_json

            print_json(data)
        else:
            for model, metrics in data.items():
                print_result(
                    metrics,
                    columns=["id", "name", "metric", "createdAt"],
                    title=f"Custom Metrics — {model}",
                    json_mode=False,
                )
    else:
        print_result(
            data,
            columns=["id", "name", "metric", "createdAt"],
            title="Custom Metrics",
            json_mode=ctx.obj["json_mode"],
        )


@custom_metrics_group.command("get")
@click.argument("metric_name")
@click.option("--model", required=True, help="Model name.")
@click.pass_context
def custom_metrics_get(ctx, metric_name, model):
    """Get a custom metric by name."""
    client = get_client(ctx)
    data = client.get_custom_metric(model_name=model, metric_name=metric_name)
    print_result(data, json_mode=ctx.obj["json_mode"])


@custom_metrics_group.command("create")
@click.argument("metric_name")
@click.option("--metric", required=True, help="Metric expression/formula.")
@click.option("--model", required=True, help="Model name.")
@click.option(
    "--environment",
    type=click.Choice(ENVIRONMENT_CHOICES),
    default="production",
    help="Metric environment.",
)
@click.option("--description", default=None, help="Metric description.")
@click.pass_context
def custom_metrics_create(ctx, metric_name, metric, model, environment, description):
    """Create a custom metric."""
    client = get_client(ctx)
    url = client.create_custom_metric(
        metric=metric,
        metric_name=metric_name,
        model_name=model,
        metric_environment=environment,
        metric_description=description,
    )
    print_url(url, label="Created custom metric")


@custom_metrics_group.command("update")
@click.argument("metric_name")
@click.option("--model", required=True, help="Model name.")
@click.option("--new-name", default=None, help="Updated metric name.")
@click.option("--metric", default=None, help="Updated metric expression.")
@click.option("--description", default=None, help="Updated description.")
@click.option(
    "--environment",
    type=click.Choice(ENVIRONMENT_CHOICES),
    default=None,
    help="Updated environment.",
)
@click.pass_context
def custom_metrics_update(ctx, metric_name, model, new_name, metric, description, environment):
    """Update a custom metric."""
    client = get_client(ctx)
    url = client.update_custom_metric(
        custom_metric_name=metric_name,
        model_name=model,
        name=new_name,
        metric=metric,
        description=description,
        environment=environment,
    )
    print_url(url, label="Updated custom metric")


@custom_metrics_group.command("delete")
@click.argument("metric_name")
@click.option("--model", required=True, help="Model name.")
@click.confirmation_option(prompt="Are you sure you want to delete this custom metric?")
@click.pass_context
def custom_metrics_delete(ctx, metric_name, model):
    """Delete a custom metric."""
    client = get_client(ctx)
    result = client.delete_custom_metric(model_name=model, metric_name=metric_name)
    if result:
        print_success(f"Custom metric '{metric_name}' deleted.")
    else:
        print_error(f"Failed to delete custom metric '{metric_name}'.")


@custom_metrics_group.command("copy")
@click.argument("metric_name")
@click.option("--model", required=True, help="Source model name.")
@click.option("--new-model", default=None, help="Target model name.")
@click.option("--new-name", default=None, help="Name for the copied metric.")
@click.option("--new-description", default=None, help="Description for the copied metric.")
@click.option(
    "--new-environment",
    type=click.Choice(ENVIRONMENT_CHOICES),
    default="production",
    help="Environment for the copied metric.",
)
@click.pass_context
def custom_metrics_copy(ctx, metric_name, model, new_model, new_name, new_description, new_environment):
    """Copy a custom metric to another model."""
    client = get_client(ctx)
    url = client.copy_custom_metric(
        current_metric_name=metric_name,
        current_model_name=model,
        new_model_name=new_model,
        new_metric_name=new_name,
        new_metric_description=new_description,
        new_model_environment=new_environment,
    )
    print_url(url, label="Copied custom metric")
