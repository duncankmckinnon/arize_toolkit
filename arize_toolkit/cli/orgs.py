import click

from arize_toolkit.cli.client_factory import get_client
from arize_toolkit.cli.output import print_result, print_url


@click.group("orgs")
def orgs_group():
    """Manage Arize organizations."""
    pass


@orgs_group.command("list")
@click.pass_context
def orgs_list(ctx):
    """List all organizations in the account."""
    client = get_client(ctx)
    data = client.get_all_organizations()
    print_result(
        data,
        columns=["id", "name", "createdAt"],
        title="Organizations",
        json_mode=ctx.obj["json_mode"],
    )


@orgs_group.command("create")
@click.argument("org_name")
@click.argument("space_name")
@click.option("--description", default=None, help="Organization description.")
@click.option(
    "--space-private/--space-public",
    default=False,
    help="Whether the initial space is private.",
)
@click.pass_context
def orgs_create(ctx, org_name, space_name, description, space_private):
    """Create a new organization and space."""
    client = get_client(ctx)
    url = client.create_new_organization_and_space(
        org_name=org_name,
        space_name=space_name,
        org_description=description,
        space_private=space_private,
    )
    print_url(url, label="Created")
