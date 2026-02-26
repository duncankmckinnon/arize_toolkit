import json

import click

from arize_toolkit.cli.client_factory import get_client
from arize_toolkit.cli.output import print_error, print_result, print_success


@click.group("evaluators")
def evaluators_group():
    """Manage Arize evaluators."""
    pass


@evaluators_group.command("list")
@click.option("--search", default=None, help="Search by name.")
@click.option("--name", default=None, help="Filter by exact name.")
@click.option(
    "--task-type",
    type=click.Choice(["template_evaluation", "code_evaluation"]),
    default=None,
    help="Filter by task type.",
)
@click.pass_context
def evaluators_list(ctx, search, name, task_type):
    """List evaluators."""
    client = get_client(ctx)
    data = client.get_evaluators(search=search, name=name, task_type=task_type)
    print_result(
        data,
        columns=["id", "name", "description", "createdAt"],
        title="Evaluators",
        json_mode=ctx.obj["json_mode"],
    )


@evaluators_group.command("get")
@click.argument("name")
@click.pass_context
def evaluators_get(ctx, name):
    """Get an evaluator by name."""
    client = get_client(ctx)
    data = client.get_evaluator(name=name)
    print_result(data, json_mode=ctx.obj["json_mode"])


@evaluators_group.command("create-template")
@click.argument("name")
@click.option("--template", required=True, help="Prompt template string or @filepath.")
@click.option("--metric-name", required=True, help="Metric output name.")
@click.option("--commit-message", default="Initial version", help="Commit message.")
@click.option("--description", default=None, help="Evaluator description.")
@click.option("--tag", multiple=True, help="Tags.")
@click.option("--classification-choices", default=None, help='JSON mapping labels to scores (e.g. \'{"Yes":0,"No":1}\').')
@click.option("--direction", type=click.Choice(["maximize", "minimize"]), default="maximize", help="Score direction.")
@click.option("--data-granularity", type=click.Choice(["span", "trace", "session"]), default="span", help="Data granularity.")
@click.option("--include-explanations/--no-explanations", default=True, help="Include explanations.")
@click.option("--use-function-calling/--no-function-calling", default=False, help="Use function calling.")
@click.option("--llm-integration-name", default=None, help="LLM integration name.")
@click.option("--llm-model-name", default=None, help="LLM model name.")
@click.pass_context
def evaluators_create_template(
    ctx,
    name,
    template,
    metric_name,
    commit_message,
    description,
    tag,
    classification_choices,
    direction,
    data_granularity,
    include_explanations,
    use_function_calling,
    llm_integration_name,
    llm_model_name,
):
    """Create an LLM template evaluator."""
    template_str = _read_string_or_file(template)
    choices = json.loads(classification_choices) if classification_choices else None

    client = get_client(ctx)
    data = client.create_template_evaluator(
        name=name,
        template=template_str,
        metric_name=metric_name,
        commit_message=commit_message,
        description=description,
        tags=list(tag) if tag else None,
        classification_choices=choices,
        direction=direction,
        data_granularity_type=data_granularity,
        include_explanations=include_explanations,
        use_function_calling=use_function_calling,
        llm_integration_name=llm_integration_name,
        llm_model_name=llm_model_name,
    )
    print_result(data, json_mode=ctx.obj["json_mode"])


@evaluators_group.command("create-code")
@click.argument("name")
@click.option("--metric-name", required=True, help="Metric output name.")
@click.option("--code", required=True, help="Python code string or @filepath.")
@click.option("--evaluation-class", required=True, help="Class name in the code block.")
@click.option("--span-attribute", multiple=True, required=True, help="Span attributes to pass as inputs.")
@click.option("--commit-message", default="Initial version", help="Commit message.")
@click.option("--description", default=None, help="Evaluator description.")
@click.option("--tag", multiple=True, help="Tags.")
@click.option("--data-granularity", type=click.Choice(["span", "trace", "session"]), default="span", help="Data granularity.")
@click.option("--package-imports", default=None, help="Package imports string.")
@click.pass_context
def evaluators_create_code(
    ctx,
    name,
    metric_name,
    code,
    evaluation_class,
    span_attribute,
    commit_message,
    description,
    tag,
    data_granularity,
    package_imports,
):
    """Create a Python code evaluator."""
    code_str = _read_string_or_file(code)

    client = get_client(ctx)
    data = client.create_code_evaluator(
        name=name,
        metric_name=metric_name,
        code_block=code_str,
        evaluation_class=evaluation_class,
        span_attributes=list(span_attribute),
        commit_message=commit_message,
        description=description,
        tags=list(tag) if tag else None,
        data_granularity_type=data_granularity,
        package_imports=package_imports,
    )
    print_result(data, json_mode=ctx.obj["json_mode"])


@evaluators_group.command("edit")
@click.argument("evaluator_id")
@click.option("--name", default=None, help="Updated name.")
@click.option("--description", default=None, help="Updated description.")
@click.option("--tag", multiple=True, help="Updated tags.")
@click.pass_context
def evaluators_edit(ctx, evaluator_id, name, description, tag):
    """Edit evaluator metadata."""
    client = get_client(ctx)
    data = client.edit_evaluator(
        evaluator_id=evaluator_id,
        updated_name=name,
        description=description,
        tags=list(tag) if tag else None,
    )
    print_result(data, json_mode=ctx.obj["json_mode"])


@evaluators_group.command("delete")
@click.argument("evaluator_id")
@click.confirmation_option(prompt="Are you sure you want to delete this evaluator?")
@click.pass_context
def evaluators_delete(ctx, evaluator_id):
    """Delete an evaluator."""
    client = get_client(ctx)
    result = client.delete_evaluator(evaluator_id=evaluator_id)
    if result:
        print_success(f"Evaluator '{evaluator_id}' deleted.")
    else:
        print_error(f"Failed to delete evaluator '{evaluator_id}'.")


def _read_string_or_file(value: str) -> str:
    """Read from @filepath or return string as-is."""
    if value.startswith("@"):
        filepath = value[1:]
        try:
            with open(filepath) as f:
                return f.read()
        except FileNotFoundError:
            print_error(f"File not found: '{filepath}'")
    return value
