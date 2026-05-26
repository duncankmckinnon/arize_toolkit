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


@spaces_group.command("update")
@click.option("--name", default=None, help="New name for the space.")
@click.option("--space-id", default=None, help="ID of the space to update. Defaults to the active space.")
@click.option("--private/--public", default=None, help="Whether the space is private.")
@click.option("--description", default=None, help="Description for the space.")
@click.option("--gradient-start-color", default=None, help="Hex color code for gradient start.")
@click.option("--gradient-end-color", default=None, help="Hex color code for gradient end.")
@click.option("--ml-models-enabled/--ml-models-disabled", default=None, help="Whether ML models are enabled.")
@click.pass_context
def spaces_update(ctx, name, space_id, private, description, gradient_start_color, gradient_end_color, ml_models_enabled):
    """Update a space's properties."""
    client = get_client(ctx)
    data = client.update_space(
        name=name,
        space_id=space_id,
        private=private,
        description=description,
        gradient_start_color=gradient_start_color,
        gradient_end_color=gradient_end_color,
        ml_models_enabled=ml_models_enabled,
    )
    print_result(data, json_mode=ctx.obj["json_mode"])


@spaces_group.command("users")
@click.option("--search", default=None, help="Filter users by name or email.")
@click.option("--user-type", default=None, type=click.Choice(["human", "bot"]), help="Filter by user type.")
@click.pass_context
def spaces_users(ctx, search, user_type):
    """List all users with access to the current space."""
    client = get_client(ctx)
    data = client.get_space_users(search=search, user_type=user_type)
    # Flatten nested user info for table display
    flat_data = []
    for item in data:
        user = item.get("user", {})
        flat_data.append(
            {
                "id": user.get("id"),
                "name": user.get("name"),
                "email": user.get("email"),
                "role": item.get("role"),
                "membership": item.get("membership"),
            }
        )
    print_result(
        flat_data,
        columns=["id", "name", "email", "role", "membership"],
        title="Space Users",
        json_mode=ctx.obj["json_mode"],
    )


@spaces_group.command("create-key")
@click.argument("name")
@click.pass_context
def spaces_create_key(ctx, name):
    """Create a space admin API key."""
    client = get_client(ctx)
    data = client.create_space_admin_api_key(name=name)
    print_result(data, json_mode=ctx.obj["json_mode"])
