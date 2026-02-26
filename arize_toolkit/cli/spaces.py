import click

from arize_toolkit.cli.client_factory import get_client
from arize_toolkit.cli.output import print_result, print_success, print_url


@click.group("spaces")
def spaces_group():
    """Manage Arize spaces."""
    pass


@spaces_group.command("list")
@click.pass_context
def spaces_list(ctx):
    """List all spaces in the current organization."""
    client = get_client(ctx)
    data = client.get_all_spaces()
    print_result(
        data,
        columns=["id", "name", "createdAt"],
        title="Spaces",
        json_mode=ctx.obj["json_mode"],
    )


@spaces_group.command("get")
@click.argument("name")
@click.pass_context
def spaces_get(ctx, name):
    """Get a space by name."""
    client = get_client(ctx)
    data = client.get_space(name)
    print_result(data, json_mode=ctx.obj["json_mode"])


@spaces_group.command("create")
@click.argument("name")
@click.option("--private/--public", default=True, help="Whether the space is private.")
@click.option(
    "--no-switch",
    is_flag=True,
    help="Don't switch to the new space after creation.",
)
@click.pass_context
def spaces_create(ctx, name, private, no_switch):
    """Create a new space."""
    client = get_client(ctx)
    space_id = client.create_new_space(name=name, private=private, set_as_active=not no_switch)
    print_success(f"Space '{name}' created (id: {space_id}).")


@spaces_group.command("switch")
@click.argument("name")
@click.option("--org", default=None, help="Organization to switch to.")
@click.pass_context
def spaces_switch(ctx, name, org):
    """Switch the active space."""
    client = get_client(ctx)
    url = client.switch_space(space=name, organization=org)
    print_url(url, label="Switched to")


@spaces_group.command("create-key")
@click.argument("name")
@click.pass_context
def spaces_create_key(ctx, name):
    """Create a space admin API key."""
    client = get_client(ctx)
    data = client.create_space_admin_api_key(name=name)
    print_result(data, json_mode=ctx.obj["json_mode"])
