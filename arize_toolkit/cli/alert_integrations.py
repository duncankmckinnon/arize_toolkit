import click

from arize_toolkit.cli.client_factory import get_client
from arize_toolkit.cli.output import print_result

PROVIDER_CHOICES = ["slack", "pagerduty", "opsgenie"]


@click.group("alert-integrations")
def alert_integrations_group():
    """Manage alert integrations (Slack, PagerDuty, OpsGenie)."""
    pass


@alert_integrations_group.command("list")
@click.option(
    "--provider",
    type=click.Choice(PROVIDER_CHOICES),
    default=None,
    help="Filter by provider.",
)
@click.option("--search", default=None, help="Search by integration name.")
@click.pass_context
def integrations_list(ctx, provider, search):
    """List alert integrations for the organization."""
    client = get_client(ctx)
    data = client.list_integrations(provider_name=provider, search=search)
    print_result(
        data,
        columns=["id", "name", "providerName", "channelName", "alertSeverity"],
        title="Alert Integrations",
        json_mode=ctx.obj["json_mode"],
    )
