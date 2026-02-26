import click

from arize_toolkit.cli.client_factory import get_client
from arize_toolkit.cli.output import print_result


@click.group("traces")
def traces_group():
    """Query and inspect traces and spans."""
    pass


@traces_group.command("list")
@click.option("--model-name", default=None, help="Model name.")
@click.option("--model-id", default=None, help="Model ID (base64-encoded).")
@click.option("--start-time", default=None, help="Start time (ISO format or Unix timestamp).")
@click.option("--end-time", default=None, help="End time (ISO format or Unix timestamp).")
@click.option("--count", type=int, default=20, help="Number of traces per page (default 20).")
@click.option(
    "--sort",
    type=click.Choice(["desc", "asc"]),
    default="desc",
    help="Sort direction (default desc).",
)
@click.option("--csv", "csv_path", default=None, help="Export results to a CSV file.")
@click.pass_context
def traces_list(ctx, model_name, model_id, start_time, end_time, count, sort, csv_path):
    """List recent traces (root spans) for a model."""
    client = get_client(ctx)
    if csv_path:
        df = client.list_traces(
            model_name=model_name,
            model_id=model_id,
            start_time=start_time,
            end_time=end_time,
            count=count,
            sort_direction=sort,
            to_dataframe=True,
        )
        df.to_csv(csv_path, index=False)
        click.echo(f"Exported {len(df)} traces to {csv_path}")
        return
    data = client.list_traces(
        model_name=model_name,
        model_id=model_id,
        start_time=start_time,
        end_time=end_time,
        count=count,
        sort_direction=sort,
    )
    flat = client._flatten_span_dicts(data)
    base_cols = ["traceId", "name", "spanKind", "statusCode", "startTime", "latencyMs"]
    attr_cols = sorted({k for row in flat for k in row if k.startswith("attributes.")})
    print_result(
        flat,
        columns=base_cols + attr_cols,
        title="Traces",
        json_mode=ctx.obj["json_mode"],
    )


@traces_group.command("get")
@click.argument("trace_id")
@click.option("--model-name", default=None, help="Model name.")
@click.option("--model-id", default=None, help="Model ID (base64-encoded).")
@click.option("--start-time", default=None, help="Start time (ISO format).")
@click.option("--end-time", default=None, help="End time (ISO format).")
@click.option(
    "--columns",
    default=None,
    help="Comma-separated attribute names to include (default: all attributes).",
)
@click.option("--count", type=int, default=20, help="Number of spans per page.")
@click.option("--csv", "csv_path", default=None, help="Export results to a CSV file.")
@click.pass_context
def traces_get(ctx, trace_id, model_name, model_id, start_time, end_time, columns, count, csv_path):
    """Get all spans for a specific trace."""
    client = get_client(ctx)
    column_names = [c.strip() for c in columns.split(",")] if columns else None
    if csv_path:
        df = client.get_trace(
            trace_id=trace_id,
            model_name=model_name,
            model_id=model_id,
            start_time=start_time,
            end_time=end_time,
            column_names=column_names,
            count=count,
            to_dataframe=True,
        )
        df.to_csv(csv_path, index=False)
        click.echo(f"Exported {len(df)} spans to {csv_path}")
        return
    data = client.get_trace(
        trace_id=trace_id,
        model_name=model_name,
        model_id=model_id,
        start_time=start_time,
        end_time=end_time,
        column_names=column_names,
        count=count,
    )
    flat = client._flatten_span_dicts(data, column_names=column_names)
    print_result(
        flat,
        title=f"Trace: {trace_id}",
        json_mode=ctx.obj["json_mode"],
    )
