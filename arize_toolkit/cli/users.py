import click

from arize_toolkit.cli.client_factory import get_client
from arize_toolkit.cli.output import print_result


@click.group("users")
def users_group():
    """Manage users and space membership."""
    pass


@users_group.command("get")
@click.argument("search")
@click.pass_context
def users_get(ctx, search):
    """Search for a user by name or email."""
    client = get_client(ctx)
    data = client.get_user(search=search)
    print_result(data, json_mode=ctx.obj["json_mode"])


@users_group.command("assign")
@click.argument("user_names", nargs=-1, required=True)
@click.option("--spaces", multiple=True, help="Space names to assign to.")
@click.option(
    "--role",
    type=click.Choice(["admin", "member", "readOnly", "annotator"]),
    default="member",
    help="Role to assign.",
)
@click.pass_context
def users_assign(ctx, user_names, spaces, role):
    """Assign users to spaces."""
    client = get_client(ctx)
    space_list = list(spaces) if spaces else None
    data = client.assign_space_membership(
        user_names=list(user_names),
        space_names=space_list,
        role=role,
    )
    print_result(data, json_mode=ctx.obj["json_mode"])


@users_group.command("remove")
@click.argument("user_name")
@click.option("--space", default=None, help="Space to remove from (default: current).")
@click.pass_context
def users_remove(ctx, user_name, space):
    """Remove a user from a space."""
    client = get_client(ctx)
    data = client.remove_space_member(user_name=user_name, space_name=space)
    print_result(data, json_mode=ctx.obj["json_mode"])
