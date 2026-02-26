import click

from arize_toolkit import __version__
from arize_toolkit.cli.config_cmd import config_group
from arize_toolkit.cli.custom_metrics import custom_metrics_group
from arize_toolkit.cli.dashboards import dashboards_group
from arize_toolkit.cli.evaluators import evaluators_group
from arize_toolkit.cli.imports import imports_group
from arize_toolkit.cli.models import models_group
from arize_toolkit.cli.monitors import monitors_group
from arize_toolkit.cli.orgs import orgs_group
from arize_toolkit.cli.prompts import prompts_group
from arize_toolkit.cli.spaces import spaces_group
from arize_toolkit.cli.users import users_group


@click.group()
@click.version_option(version=__version__, prog_name="arize_toolkit")
@click.option("--profile", default=None, help="Configuration profile name.")
@click.option("--json", "json_mode", is_flag=True, help="Output as JSON.")
@click.option("--api-key", default=None, help="Arize developer API key.")
@click.option("--org", default=None, help="Arize organization name.")
@click.option("--space", default=None, help="Arize space name.")
@click.option("--app-url", default=None, help="Arize app URL.")
@click.pass_context
def cli(ctx, profile, json_mode, api_key, org, space, app_url):
    """Arize Toolkit CLI — manage models, monitors, prompts, and more."""
    ctx.ensure_object(dict)
    ctx.obj["profile"] = profile
    ctx.obj["json_mode"] = json_mode
    ctx.obj["api_key"] = api_key
    ctx.obj["org"] = org
    ctx.obj["space"] = space
    ctx.obj["app_url"] = app_url


cli.add_command(config_group)
cli.add_command(spaces_group)
cli.add_command(orgs_group)
cli.add_command(users_group)
cli.add_command(models_group)
cli.add_command(models_group, name="projects")
cli.add_command(monitors_group)
cli.add_command(prompts_group)
cli.add_command(custom_metrics_group)
cli.add_command(evaluators_group)
cli.add_command(dashboards_group)
cli.add_command(imports_group)


if __name__ == "__main__":
    cli()
