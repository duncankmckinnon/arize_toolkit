from typing import List, Optional, Tuple

from arize_toolkit.models import BasicMonitor, DataQualityMonitor, DriftMonitor, Monitor, PerformanceMonitor
from arize_toolkit.queries.basequery import ArizeAPIException, BaseQuery, BaseResponse, BaseVariables


class GetAllModelMonitorsQuery(BaseQuery):
    graphql_query = (
        """
        query getAllMonitors($model_id:ID!, $monitor_category: MonitorCategory, $endCursor: String){
            node(id:$model_id){
                ...on Model{
                    monitors(first: 10, after: $endCursor, monitorCategory: $monitor_category){
                        pageInfo{
                            hasNextPage
                            endCursor
                        }
                        edges{
                            node{ """
        + BasicMonitor.to_graphql_fields()
        + """     }
                        }
                    }
                }
            }
        }
    """
    )
    query_description = "Get all monitors for a given model"

    class Variables(BaseVariables):
        model_id: str
        monitor_category: Optional[str] = None

    class QueryException(ArizeAPIException):
        message: str = "Error getting all monitors for a given model"

    class QueryResponse(BasicMonitor):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        pageInfo = result["node"]["monitors"]["pageInfo"]
        edges = result["node"]["monitors"]["edges"]
        monitors = []
        if len(edges) > 0:
            monitors = [cls.QueryResponse(**edge["node"]) for edge in edges]
        return monitors, pageInfo["hasNextPage"], pageInfo["endCursor"]


class GetMonitorQuery(BaseQuery):
    graphql_query = (
        """
        query getMonitorQuery($space_id: ID!, $model_name: String, $monitor_name: String){
            node(id:$space_id){
                ...on Space{
                    monitors(first: 1, search: $monitor_name, modelName: $model_name){
                        edges{
                            node{ """
        + Monitor.to_graphql_fields()
        + """     }
                        }
                    }
                }
            }
        }
    """
    )
    query_description = "Get a monitor by name"

    class Variables(BaseVariables):
        space_id: str
        model_name: str
        monitor_name: str

    class QueryException(ArizeAPIException):
        message: str = "Error getting a monitor by name"

    class QueryResponse(Monitor):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        edges = result["node"]["monitors"]["edges"]
        if len(edges) == 0:
            cls.raise_exception("No monitor found with the given name")
        node = edges[0]["node"]
        return (
            [cls.QueryResponse(**node)],
            False,
            None,
        )


class GetMonitorByIDQuery(BaseQuery):
    graphql_query = (
        """
        query getMonitorByIDQuery($monitor_id: ID!){
            node(id: $monitor_id){
                ...on Monitor{
                    """
        + Monitor.to_graphql_fields()
        + """     }
            }
        }
    """
    )
    query_description = "Get a monitor by ID"

    class Variables(BaseVariables):
        monitor_id: str

    class QueryException(ArizeAPIException):
        message: str = "Error getting a monitor by ID"

    class QueryResponse(Monitor):
        pass


class CreatePerformanceMonitorMutation(BaseQuery):
    graphql_query = """
        mutation createPerformanceMonitor($input: CreatePerformanceMonitorMutationInput!) {
            createPerformanceMonitor(input: $input) {
                monitor{
                    id
                }
            }
        }
        """

    query_description = "Create a monitor for model performance for a given model and metric"

    class Variables(PerformanceMonitor):
        pass

    class QueryException(ArizeAPIException):
        message: str = "Error creating a monitor for model performance"

    class QueryResponse(BaseResponse):
        monitor_id: str

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        create_result = result["createPerformanceMonitor"]
        if "monitor" not in create_result:
            cls.raise_exception("no monitor id returned")
        return (
            [cls.QueryResponse(monitor_id=create_result["monitor"]["id"])],
            False,
            None,
        )


class CreateDriftMonitorMutation(BaseQuery):
    graphql_query = """
    mutation createDriftMonitor($input: CreateDriftMonitorMutationInput!) {
        createDriftMonitor(input: $input) {
            monitor{
                id
            }
        }
    }
    """
    query_description = "Create a monitor for drift using a drift metric on a given model dimension"

    class Variables(DriftMonitor):
        pass

    class QueryException(ArizeAPIException):
        message: str = "Error creating a monitor for model drift"

    class QueryResponse(BaseResponse):
        monitor_id: str

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        create_result = result["createDriftMonitor"]
        if "monitor" not in create_result:
            cls.raise_exception("no monitor id returned")
        return (
            [cls.QueryResponse(monitor_id=create_result["monitor"]["id"])],
            False,
            None,
        )


class CreateDataQualityMonitorMutation(BaseQuery):
    graphql_query = """
        mutation createDataQualityMonitor($input: CreateDataQualityMonitorMutationInput!) {
            createDataQualityMonitor(input: $input) {
                monitor{
                    id
                }
            }
        }
    """
    query_description = "Create a monitor for data quality using a data quality metric on a given model dimension"

    class Variables(DataQualityMonitor):
        pass

    class QueryException(ArizeAPIException):
        message: str = "Error creating a monitor for data quality"

    class QueryResponse(BaseResponse):
        monitor_id: str

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        create_result = result["createDataQualityMonitor"]
        if "monitor" not in create_result:
            cls.raise_exception("no monitor id returned")
        return (
            [cls.QueryResponse(monitor_id=create_result["monitor"]["id"])],
            False,
            None,
        )


class DeleteMonitorMutation(BaseQuery):
    graphql_query = """
        mutation deleteMonitor($input: DeleteMonitorMutationInput!) {
            deleteMonitor(input: $input) {
                monitor {
                    id
                }
            }
        }
    """
    query_description = "Delete a monitor"

    class Variables(BaseVariables):
        monitorId: str

    class QueryException(ArizeAPIException):
        message: str = "Error deleting a monitor"

    class QueryResponse(BaseResponse):
        monitor_id: str

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        delete_result = result["deleteMonitor"]
        if "monitor" not in delete_result:
            cls.raise_exception("no monitor id returned")
        return (
            [cls.QueryResponse(monitor_id=delete_result["monitor"]["id"])],
            False,
            None,
        )
