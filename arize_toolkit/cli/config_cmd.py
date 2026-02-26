import os
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib
from typing import Any, Dict, Optional

import click
import tomli_w

CONFIG_DIR = Path.home() / ".arize_toolkit"
CONFIG_FILE = CONFIG_DIR / "config.toml"


def load_config() -> Dict[str, Any]:
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE, "rb") as f:
        return tomllib.load(f)


def save_config(config: Dict[str, Any]) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "wb") as f:
        tomli_w.dump(config, f)


def get_profile(profile_name: str = "default") -> Dict[str, Any]:
    config = load_config()
    return config.get(profile_name, {})


def update_profile(profile_name: str = "default", **updates: str) -> None:
    """Update specific fields in a config profile and save."""
    config = load_config()
    profile = config.get(profile_name, {})
    profile.update(updates)
    config[profile_name] = profile
    save_config(config)


def resolve_config(
    profile: Optional[str] = None,
    api_key: Optional[str] = None,
    org: Optional[str] = None,
    space: Optional[str] = None,
    app_url: Optional[str] = None,
) -> Dict[str, str]:
    profile_data = get_profile(profile or "default")

    resolved = {
        "api_key": (api_key or os.environ.get("ARIZE_DEVELOPER_KEY") or profile_data.get("api_key")),
        "organization": (org or os.environ.get("ARIZE_ORGANIZATION") or profile_data.get("organization")),
        "space": (space or os.environ.get("ARIZE_SPACE") or profile_data.get("space")),
        "app_url": (app_url or os.environ.get("ARIZE_APP_URL") or profile_data.get("app_url", "https://app.arize.com")),
    }
    return {k: v for k, v in resolved.items() if v is not None}


@click.group("config")
def config_group():
    """Manage CLI configuration profiles."""
    pass


@config_group.command("init")
@click.option("--profile-name", default="default", help="Name for this profile.")
def config_init(profile_name):
    """Interactive setup: create a configuration profile."""
    api_key = click.prompt("Arize Developer Key", hide_input=True)
    organization = click.prompt("Organization name")
    space = click.prompt("Space name")
    app_url = click.prompt("Arize app URL", default="https://app.arize.com", show_default=True)

    config = load_config()
    config[profile_name] = {
        "api_key": api_key,
        "organization": organization,
        "space": space,
        "app_url": app_url,
    }
    save_config(config)
    click.echo(f"Profile '{profile_name}' saved to {CONFIG_FILE}")


@config_group.command("list")
def config_list():
    """List all configuration profiles."""
    config = load_config()
    if not config:
        click.echo("No profiles found. Run 'arize_toolkit config init' to create one.")
        return
    for name in config:
        profile = config[name]
        click.echo(f"  {name}: org={profile.get('organization', '?')}, " f"space={profile.get('space', '?')}")


@config_group.command("show")
@click.option("--profile-name", default="default", help="Profile to show.")
def config_show(profile_name):
    """Show details for a configuration profile."""
    profile = get_profile(profile_name)
    if not profile:
        click.echo(f"Profile '{profile_name}' not found.")
        return
    for key, value in profile.items():
        display_value = "***" if key == "api_key" else value
        click.echo(f"  {key}: {display_value}")


@config_group.command("use")
@click.argument("name")
def config_use(name):
    """Set the active default profile."""
    config = load_config()
    if name not in config:
        click.echo(f"Profile '{name}' not found.")
        sys.exit(1)

    profile_data = config.pop(name)
    old_default = config.pop("default", None)

    new_config = {"default": profile_data}
    if old_default:
        new_config[name] = old_default
    new_config.update(config)

    save_config(new_config)
    click.echo(f"Switched default profile to '{name}'.")
