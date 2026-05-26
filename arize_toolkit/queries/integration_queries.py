from typing import List, Optional, Tuple

from arize_toolkit.models.monitor_models import IntegrationKey
from arize_toolkit.queries.basequery import ArizeAPIException, BaseQuery, BaseResponse, BaseVariables


class GetIntegrationKeysQuery(BaseQuery):
    graphql_query = (
        """
        query getIntegrationKeys($organization_id: ID!, $providerName: IntegrationProvider, $search: String) {
            node(id: $organization_id) {
                ... on AccountOrganization {
                    integrations(providerName: $providerName, search: $search) { """
        + IntegrationKey.to_graphql_fields()
        + """
                    }
                }
            }
        }
    """
    )
    query_description = "Get all alert integration keys for an organization"

    class Variables(BaseVariables):
        organization_id: str
        providerName: Optional[str] = None
        search: Optional[str] = None

    class QueryException(ArizeAPIException):
        message: str = "Error getting integration keys"

    class QueryResponse(IntegrationKey):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        integrations = result.get("node", {}).get("integrations", [])
        return (
            [cls.QueryResponse(**integration) for integration in integrations],
            False,
            None,
        )
