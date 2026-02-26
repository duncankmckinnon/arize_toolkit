import click

from arize_toolkit.cli.client_factory import get_client
from arize_toolkit.cli.output import print_error, print_result, print_success, print_url

OPERATOR_CHOICES = ["greaterThan", "lessThan", "greaterThanOrEqual", "lessThanOrEqual"]
ENVIRONMENT_CHOICES = ["tracing", "production", "validation", "training"]


def _common_monitor_options(f):
    """Shared options for all monitor create commands."""
    f = click.option("--notes", default=None, help="Notes for the monitor.")(f)
    f = click.option("--threshold", type=float, default=None, help="Alert threshold value.")(f)
    f = click.option("--std-dev-multiplier", type=float, default=2.0, help="Std dev multiplier.")(f)
    f = click.option("--operator", type=click.Choice(OPERATOR_CHOICES), default="greaterThan", help="Comparison operator.")(f)
    f = click.option("--evaluation-window", type=int, default=259200, help="Evaluation window in seconds.")(f)
    f = click.option("--delay", type=int, default=0, help="Delay in seconds.")(f)
    f = click.option("--threshold-mode", type=click.Choice(["single", "double"]), default="single", help="Threshold mode.")(f)
    f = click.option("--threshold2", type=float, default=None, help="Second threshold (double mode).")(f)
    f = click.option("--operator2", type=click.Choice(OPERATOR_CHOICES), default=None, help="Second operator (double mode).")(f)
    f = click.option("--email", multiple=True, help="Email addresses for notifications.")(f)
    f = click.option("--integration-key-id", multiple=True, help="Integration key IDs for notifications.")(f)
    return f


@click.group("monitors")
def monitors_group():
    """Manage Arize monitors."""
    pass


@monitors_group.command("list")
@click.option("--model-name", default=None, help="Model name.")
@click.option("--model-id", default=None, help="Model ID.")
@click.option(
    "--category",
    type=click.Choice(["drift", "dataQuality", "performance"]),
    default=None,
    help="Monitor category filter.",
)
@click.pass_context
def monitors_list(ctx, model_name, model_id, category):
    """List monitors for a model."""
    client = get_client(ctx)
    data = client.get_all_monitors(model_name=model_name, model_id=model_id, monitor_category=category)
    print_result(
        data,
        columns=["id", "name", "monitorCategory", "createdAt"],
        title="Monitors",
        json_mode=ctx.obj["json_mode"],
    )


@monitors_group.command("get")
@click.argument("name")
@click.option("--model", required=True, help="Model name.")
@click.pass_context
def monitors_get(ctx, name, model):
    """Get a monitor by name."""
    client = get_client(ctx)
    data = client.get_monitor(model_name=model, monitor_name=name)
    print_result(data, json_mode=ctx.obj["json_mode"])


@monitors_group.command("create-performance")
@click.argument("name")
@click.option("--model", required=True, help="Model name.")
@click.option("--environment", required=True, type=click.Choice(ENVIRONMENT_CHOICES), help="Model environment.")
@click.option("--performance-metric", default=None, help="Performance metric name.")
@click.option("--custom-metric-id", default=None, help="Custom metric ID.")
@_common_monitor_options
@click.pass_context
def monitors_create_performance(
    ctx,
    name,
    model,
    environment,
    performance_metric,
    custom_metric_id,
    notes,
    threshold,
    std_dev_multiplier,
    operator,
    evaluation_window,
    delay,
    threshold_mode,
    threshold2,
    operator2,
    email,
    integration_key_id,
):
    """Create a performance monitor."""
    client = get_client(ctx)
    url = client.create_performance_monitor(
        name=name,
        model_name=model,
        model_environment_name=environment,
        operator=operator,
        performance_metric=performance_metric,
        custom_metric_id=custom_metric_id,
        notes=notes,
        threshold=threshold,
        std_dev_multiplier=std_dev_multiplier,
        evaluation_window_length_seconds=evaluation_window,
        delay_seconds=delay,
        threshold_mode=threshold_mode,
        threshold2=threshold2,
        operator2=operator2,
        email_addresses=list(email) if email else None,
        integration_key_ids=list(integration_key_id) if integration_key_id else None,
    )
    print_url(url, label="Created monitor")


@monitors_group.command("create-drift")
@click.argument("name")
@click.option("--model", required=True, help="Model name.")
@click.option("--drift-metric", type=click.Choice(["psi", "js", "kl", "ks", "euclideanDistance", "cosineSimilarity"]), default="psi", help="Drift metric.")
@click.option("--dimension-category", default="prediction", help="Dimension category.")
@click.option("--dimension-name", default=None, help="Dimension name.")
@_common_monitor_options
@click.pass_context
def monitors_create_drift(
    ctx,
    name,
    model,
    drift_metric,
    dimension_category,
    dimension_name,
    notes,
    threshold,
    std_dev_multiplier,
    operator,
    evaluation_window,
    delay,
    threshold_mode,
    threshold2,
    operator2,
    email,
    integration_key_id,
):
    """Create a drift monitor."""
    client = get_client(ctx)
    url = client.create_drift_monitor(
        name=name,
        model_name=model,
        drift_metric=drift_metric,
        dimension_category=dimension_category,
        dimension_name=dimension_name,
        operator=operator,
        notes=notes,
        threshold=threshold,
        std_dev_multiplier=std_dev_multiplier,
        evaluation_window_length_seconds=evaluation_window,
        delay_seconds=delay,
        threshold_mode=threshold_mode,
        threshold2=threshold2,
        operator2=operator2,
        email_addresses=list(email) if email else None,
        integration_key_ids=list(integration_key_id) if integration_key_id else None,
    )
    print_url(url, label="Created monitor")


@monitors_group.command("create-data-quality")
@click.argument("name")
@click.option("--model", required=True, help="Model name.")
@click.option("--data-quality-metric", required=True, help="Data quality metric (e.g. percentEmpty, cardinality, avg).")
@click.option("--environment", required=True, type=click.Choice(ENVIRONMENT_CHOICES), help="Model environment.")
@click.option("--dimension-category", default="prediction", help="Dimension category.")
@click.option("--dimension-name", default=None, help="Dimension name.")
@_common_monitor_options
@click.pass_context
def monitors_create_data_quality(
    ctx,
    name,
    model,
    data_quality_metric,
    environment,
    dimension_category,
    dimension_name,
    notes,
    threshold,
    std_dev_multiplier,
    operator,
    evaluation_window,
    delay,
    threshold_mode,
    threshold2,
    operator2,
    email,
    integration_key_id,
):
    """Create a data quality monitor."""
    client = get_client(ctx)
    url = client.create_data_quality_monitor(
        name=name,
        model_name=model,
        data_quality_metric=data_quality_metric,
        model_environment_name=environment,
        dimension_category=dimension_category,
        dimension_name=dimension_name,
        operator=operator,
        notes=notes,
        threshold=threshold,
        std_dev_multiplier=std_dev_multiplier,
        evaluation_window_length_seconds=evaluation_window,
        delay_seconds=delay,
        threshold_mode=threshold_mode,
        threshold2=threshold2,
        operator2=operator2,
        email_addresses=list(email) if email else None,
        integration_key_ids=list(integration_key_id) if integration_key_id else None,
    )
    print_url(url, label="Created monitor")


@monitors_group.command("delete")
@click.argument("name")
@click.option("--model", required=True, help="Model name.")
@click.confirmation_option(prompt="Are you sure you want to delete this monitor?")
@click.pass_context
def monitors_delete(ctx, name, model):
    """Delete a monitor."""
    client = get_client(ctx)
    result = client.delete_monitor(monitor_name=name, model_name=model)
    if result:
        print_success(f"Monitor '{name}' deleted.")
    else:
        print_error(f"Failed to delete monitor '{name}'.")


@monitors_group.command("copy")
@click.argument("monitor_name")
@click.option("--model", required=True, help="Source model name.")
@click.option("--new-name", default=None, help="Name for the new monitor.")
@click.option("--new-model", default=None, help="Target model name.")
@click.option("--new-space-id", default=None, help="Target space ID.")
@click.pass_context
def monitors_copy(ctx, monitor_name, model, new_name, new_model, new_space_id):
    """Copy a monitor to another model."""
    client = get_client(ctx)
    url = client.copy_monitor(
        current_monitor_name=monitor_name,
        current_model_name=model,
        new_monitor_name=new_name,
        new_model_name=new_model,
        new_space_id=new_space_id,
    )
    print_url(url, label="Copied monitor")


@monitors_group.command("values")
@click.argument("monitor_name")
@click.option("--model", required=True, help="Model name.")
@click.option(
    "--granularity",
    type=click.Choice(["hour", "day", "week", "month"]),
    default="hour",
    help="Time series granularity.",
)
@click.option("--start-time", default=None, help="Start time (ISO format).")
@click.option("--end-time", default=None, help="End time (ISO format).")
@click.pass_context
def monitors_values(ctx, monitor_name, model, granularity, start_time, end_time):
    """Get monitor metric values over time."""
    client = get_client(ctx)
    data = client.get_monitor_metric_values(
        monitor_name=monitor_name,
        model_name=model,
        time_series_data_granularity=granularity,
        start_date=start_time,
        end_date=end_time,
        to_dataframe=False,
    )
    print_result(data, json_mode=ctx.obj["json_mode"])


@monitors_group.command("latest-value")
@click.argument("monitor_name")
@click.option("--model", required=True, help="Model name.")
@click.option(
    "--granularity",
    type=click.Choice(["hour", "day", "week", "month"]),
    default="hour",
    help="Time series granularity.",
)
@click.pass_context
def monitors_latest_value(ctx, monitor_name, model, granularity):
    """Get the latest monitor value."""
    client = get_client(ctx)
    data = client.get_latest_monitor_value(
        monitor_name=monitor_name,
        model_name=model,
        time_series_data_granularity=granularity,
    )
    print_result(data, json_mode=ctx.obj["json_mode"])
