import json

import click

from arize_toolkit.cli.client_factory import get_client
from arize_toolkit.cli.output import print_error, print_result, print_success


@click.group("prompts")
def prompts_group():
    """Manage Arize prompts."""
    pass


@prompts_group.command("list")
@click.pass_context
def prompts_list(ctx):
    """List all prompts in the current space."""
    client = get_client(ctx)
    data = client.get_all_prompts()
    print_result(
        data,
        columns=["id", "name", "description", "createdAt"],
        title="Prompts",
        json_mode=ctx.obj["json_mode"],
    )


@prompts_group.command("get")
@click.argument("name")
@click.pass_context
def prompts_get(ctx, name):
    """Get a prompt by name."""
    client = get_client(ctx)
    data = client.get_prompt(prompt_name=name)
    print_result(data, json_mode=ctx.obj["json_mode"])


@prompts_group.command("versions")
@click.argument("name")
@click.pass_context
def prompts_versions(ctx, name):
    """List all versions of a prompt."""
    client = get_client(ctx)
    data = client.get_all_prompt_versions(prompt_name=name)
    print_result(data, title=f"Versions of '{name}'", json_mode=ctx.obj["json_mode"])


@prompts_group.command("create")
@click.argument("name")
@click.option(
    "--messages",
    required=True,
    help="JSON string or @filepath with message list.",
)
@click.option("--commit-message", default="created prompt", help="Commit message.")
@click.option("--description", default=None, help="Prompt description.")
@click.option("--tag", multiple=True, help="Tags for the prompt.")
@click.option("--provider", default=None, help="LLM provider (e.g. openAI).")
@click.option("--model-name", default=None, help="LLM model name (e.g. gpt-4o).")
@click.option(
    "--input-variable-format",
    type=click.Choice(["f_string", "mustache", "none"]),
    default=None,
    help="Variable format.",
)
@click.pass_context
def prompts_create(
    ctx,
    name,
    messages,
    commit_message,
    description,
    tag,
    provider,
    model_name,
    input_variable_format,
):
    """Create a new prompt or prompt version."""
    msgs = _parse_json_arg(messages)
    client = get_client(ctx)
    result = client.create_prompt(
        name=name,
        messages=msgs,
        commit_message=commit_message,
        description=description,
        tags=list(tag) if tag else None,
        provider=provider,
        model_name=model_name,
        input_variable_format=input_variable_format,
    )
    if result:
        print_success(f"Prompt '{name}' created.")
    else:
        print_error(f"Failed to create prompt '{name}'.")


@prompts_group.command("update")
@click.argument("name")
@click.option("--new-name", default=None, help="Updated prompt name.")
@click.option("--description", default=None, help="Updated description.")
@click.option("--tag", multiple=True, help="Updated tags.")
@click.pass_context
def prompts_update(ctx, name, new_name, description, tag):
    """Update a prompt's metadata."""
    client = get_client(ctx)
    result = client.update_prompt(
        prompt_name=name,
        updated_name=new_name,
        description=description,
        tags=list(tag) if tag else None,
    )
    if result:
        print_success(f"Prompt '{name}' updated.")
    else:
        print_error(f"Failed to update prompt '{name}'.")


@prompts_group.command("delete")
@click.argument("name")
@click.confirmation_option(prompt="Are you sure you want to delete this prompt?")
@click.pass_context
def prompts_delete(ctx, name):
    """Delete a prompt."""
    client = get_client(ctx)
    result = client.delete_prompt(prompt_name=name)
    if result:
        print_success(f"Prompt '{name}' deleted.")
    else:
        print_error(f"Failed to delete prompt '{name}'.")


def _parse_json_arg(value: str):
    """Parse a JSON string or @filepath into a Python object."""
    if value.startswith("@"):
        filepath = value[1:]
        try:
            with open(filepath) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print_error(f"Failed to read JSON from '{filepath}': {e}")
    try:
        return json.loads(value)
    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON: {e}")
