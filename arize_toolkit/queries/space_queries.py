from typing import List, Optional, Tuple
from arize_toolkit.queries.basequery import (
    ArizeAPIException,
    BaseQuery,
    BaseResponse,
    BaseVariables,
)


class OrgIDandSpaceIDQuery(BaseQuery):
    graphql_query = """
    query orgIDandSpaceID($organization: String!, $space: String!) {
        account {
            organizations(search: $organization, first: 1) {
                edges {
                    node {
                        id
                        spaces(search: $space, first: 1) {
                            edges {
                                node {
                                    id
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    """
    query_description = "Get the organization ID and space ID from the names of the organization and space"

    class Variables(BaseVariables):
        organization: str
        space: str

    class QueryException(ArizeAPIException):
        message: str = "Error running query to retrieve Organization ID and Space ID"

    class QueryResponse(BaseResponse):
        organization_id: str
        space_id: str

    @classmethod
    def _parse_graphql_result(
        cls, result: dict
    ) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if (
            "account" not in result
            or "organizations" not in result["account"]
            or "edges" not in result["account"]["organizations"]
            or len(result["account"]["organizations"]["edges"]) == 0
        ):
            cls.raise_exception("No organization found with the given name")
        node = result["account"]["organizations"]["edges"][0]["node"]
        organization_id = node["id"]
        if (
            "spaces" not in node
            or "edges" not in node["spaces"]
            or len(node["spaces"]["edges"]) == 0
        ):
            cls.raise_exception("No space found with the given name")
        space_id = node["spaces"]["edges"][0]["node"]["id"]
        return (
            [cls.QueryResponse(organization_id=organization_id, space_id=space_id)],
            False,
            None,
        )
