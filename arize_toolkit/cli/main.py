import logging

import click

from arize_toolkit import __version__
from arize_toolkit.cli.config_cmd import config_group, get_profile, update_profile
from arize_toolkit.cli.custom_metrics import custom_metrics_group
from arize_toolkit.cli.dashboards import dashboards_group
from arize_toolkit.cli.evaluators import evaluators_group
from arize_toolkit.cli.imports import imports_group
from arize_toolkit.cli.models import models_group
from arize_toolkit.cli.monitors import monitors_group
from arize_toolkit.cli.orgs import orgs_group
from arize_toolkit.cli.prompts import prompts_group
from arize_toolkit.cli.spaces import spaces_group
from arize_toolkit.cli.traces import traces_group
from arize_toolkit.cli.users import users_group


@click.group()
@click.version_option(version=__version__, prog_name="arize_toolkit")
@click.option("--profile", default=None, help="Configuration profile name.")
@click.option("--json", "json_mode", is_flag=True, help="Output as JSON.")
@click.option("--api-key", default=None, help="Arize developer API key.")
@click.option("--org", default=None, help="Arize organization name.")
@click.option("--space", default=None, help="Arize space name.")
@click.option("--app-url", default=None, help="Arize app URL.")
@click.option("-v", "--verbose", is_flag=True, help="Enable debug logging.")
@click.pass_context
def cli(ctx, profile, json_mode, api_key, org, space, app_url, verbose):
    """Arize Toolkit CLI — manage models, monitors, prompts, and more."""
    if verbose:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(name)s %(message)s"))
        arize_logger = logging.getLogger("arize_toolkit")
        arize_logger.setLevel(logging.DEBUG)
        arize_logger.addHandler(handler)
    ctx.ensure_object(dict)
    ctx.obj["profile"] = profile
    ctx.obj["json_mode"] = json_mode
    ctx.obj["api_key"] = api_key
    ctx.obj["org"] = org
    ctx.obj["space"] = space
    ctx.obj["app_url"] = app_url


@cli.result_callback()
@click.pass_context
def persist_client_state(ctx, *args, **kwargs):
    """After each command, persist any client space/org changes to the config profile."""
    client = ctx.obj.get("client")
    if client is None:
        return

    profile_name = ctx.obj.get("profile") or "default"
    profile = get_profile(profile_name)
    if not profile:
        return

    updates = {}
    if client.space and client.space != profile.get("space"):
        updates["space"] = client.space
    if client.organization and client.organization != profile.get("organization"):
        updates["organization"] = client.organization
    org_id = getattr(client, "org_id", None)
    if isinstance(org_id, str) and org_id != profile.get("org_id"):
        updates["org_id"] = org_id
    space_id = getattr(client, "space_id", None)
    if isinstance(space_id, str) and space_id != profile.get("space_id"):
        updates["space_id"] = space_id
    # Persist last-used model from cache
    if client._model_cache:
        last_name, last_id = next(reversed(client._model_cache.items()))
        if last_name != profile.get("model_name") or last_id != profile.get("model_id"):
            updates["model_name"] = last_name
            updates["model_id"] = last_id

    if updates:
        update_profile(profile_name, **updates)


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
cli.add_command(traces_group)


if __name__ == "__main__":
    cli()
