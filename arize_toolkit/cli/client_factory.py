import click

from arize_toolkit.cli.config_cmd import resolve_config
from arize_toolkit.cli.output import print_error


def get_client(ctx: click.Context):
    """Build and return an Arize Client from the current Click context."""
    if "client" in ctx.obj:
        return ctx.obj["client"]

    config = resolve_config(
        profile=ctx.obj.get("profile"),
        api_key=ctx.obj.get("api_key"),
        org=ctx.obj.get("org"),
        space=ctx.obj.get("space"),
        app_url=ctx.obj.get("app_url"),
    )

    if not config.get("api_key"):
        print_error("No API key found. Set ARIZE_DEVELOPER_KEY, use --api-key, " "or run 'arize_toolkit config init'.")

    from arize_toolkit import Client

    try:
        client = Client(
            arize_developer_key=config["api_key"],
            organization=config.get("organization"),
            space=config.get("space"),
            arize_app_url=config.get("app_url", "https://app.arize.com"),
        )
    except Exception as e:
        print_error(f"Failed to initialize client: {e}")

    ctx.obj["client"] = client
    return client
