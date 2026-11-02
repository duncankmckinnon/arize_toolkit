"""Every query has to fit inside the Arize API's GraphQL complexity budget.

The API scores a query before executing it and rejects anything over MAX_QUERY_COST with
`Query is too complex: <n>. Maximum allowed complexity: 1000`. Cost is not the number of
fields: a Relay connection is charged `page size x cost of one node`, so raising `first:`
on a connection that selects a wide type multiplies the whole subtree. That is easy to do
by accident and only fails against a live API, so the cost model is reproduced here and
applied to every query in the package.
"""

import importlib
import inspect
import pkgutil

import pytest
from graphql import parse
from graphql.language import ast

import arize_toolkit.queries as queries_package
from arize_toolkit.queries.basequery import BaseQuery

# arizeweb: MAX_QUERY_COST, applied to every request on the programmatic endpoint.
# For reference, the most expensive query in the package is currently at 731.
MAX_QUERY_COST = 1000


def all_queries():
    """Every BaseQuery subclass in the package that carries a query document."""
    found = {}
    for module_info in pkgutil.iter_modules(queries_package.__path__):
        module = importlib.import_module(f"{queries_package.__name__}.{module_info.name}")
        for name, obj in vars(module).items():
            if inspect.isclass(obj) and issubclass(obj, BaseQuery) and isinstance(getattr(obj, "graphql_query", None), str):
                found[f"{module_info.name}.{name}"] = obj
    return sorted(found.items())


def _field_cost(node: ast.FieldNode) -> int:
    """Cost of one field: a connection multiplies its children, anything else adds one."""
    child_cost = _selection_set_cost(node.selection_set) if node.selection_set else 0

    page_size = None
    for argument in node.arguments:
        if argument.name.value in ("first", "last") and isinstance(argument.value, ast.IntValueNode):
            page_size = int(argument.value.value)

    is_connection = node.selection_set is not None and any(isinstance(selection, ast.FieldNode) and selection.name.value in ("edges", "pageInfo") for selection in node.selection_set.selections)
    if is_connection and page_size:
        return page_size * child_cost
    return 1 + child_cost


def _selection_set_cost(selection_set) -> int:
    cost = 0
    for selection in selection_set.selections:
        if isinstance(selection, ast.FieldNode):
            cost += _field_cost(selection)
        elif isinstance(selection, ast.InlineFragmentNode):
            cost += _selection_set_cost(selection.selection_set)
    return cost


def query_cost(graphql_query: str) -> int:
    """Score a query document the way the Arize API scores it."""
    return sum(_selection_set_cost(definition.selection_set) for definition in parse(graphql_query).definitions if isinstance(definition, ast.OperationDefinitionNode))


@pytest.mark.parametrize("name,query_class", all_queries())
def test_query_is_within_complexity_limit(name, query_class):
    cost = query_cost(query_class.graphql_query)
    assert cost <= MAX_QUERY_COST, f"{name} costs {cost}, over the API limit of {MAX_QUERY_COST}. Select a narrow field set from the connection and hydrate by id in a second query."


class TestCostModel:
    def test_finds_every_query(self):
        names = [name for name, _ in all_queries()]
        assert len(names) > 50
        assert "monitor_queries.GetMonitorIdByNameQuery" in names
        assert "llm_utils_queries.GetAllPromptVersionsQuery" in names

    def test_connection_multiplies_by_page_size(self):
        one = query_cost("query q { node(id: 1) { things(first: 1) { edges { node { a b } } } } }")
        ten = query_cost("query q { node(id: 1) { things(first: 10) { edges { node { a b } } } } }")
        assert one == 1 + 1 * (1 + (1 + 2))
        assert ten == 1 + 10 * (1 + (1 + 2))

    def test_plain_fields_cost_one_each(self):
        assert query_cost("query q { a b c }") == 3

    def test_inline_fragment_adds_nothing_itself(self):
        assert query_cost("query q { node(id: 1) { ... on Thing { a } } }") == 2

    def test_scores_the_v1_0_19_monitor_query_at_its_reported_cost(self):
        """The monitor-by-name query shipped in v1.0.19 cost 1081 and always failed."""
        from arize_toolkit.models import Monitor

        broken = (
            """
            query getMonitorQuery($space_id: ID!, $model_name: String, $monitor_name: String){
                node(id:$space_id){
                    ...on Space{
                        monitors(first: 10, search: $monitor_name, modelName: $model_name){
                            edges{
                                node{ """
            + Monitor.to_graphql_fields()
            + """ }
                            }
                        }
                    }
                }
            }
            """
        )
        assert query_cost(broken) == 1081
