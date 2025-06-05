from typing import List, Optional, Tuple

from arize_toolkit.models import Dashboard, DashboardBasis, LineChartWidget, StatisticWidget, WidgetBasis
from arize_toolkit.queries.basequery import ArizeAPIException, BaseQuery, BaseResponse, BaseVariables


class GetDashboardsQuery(BaseQuery):
    graphql_query = (
        """
    query getDashboards($spaceId: ID!, $endCursor: String) {
        node(id: $spaceId) {
            ... on Space {
                dashboards(first: 10, after: $endCursor) {
                    pageInfo {
                        endCursor
                        hasNextPage
                    }
                    edges {
                        node {"""
        + DashboardBasis.to_graphql_fields()
        + """}
                    }
                }
            }
        }
    }
    """
    )
    query_description = "Get all dashboards in a space"

    class Variables(BaseVariables):
        spaceId: str

    class QueryException(ArizeAPIException):
        message: str = "Error getting all dashboards in a space"

    class QueryResponse(DashboardBasis):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if not result["node"]["dashboards"]["edges"]:
            return [], False, None

        dashboard_edges = result["node"]["dashboards"]["edges"]
        has_next_page = result["node"]["dashboards"]["pageInfo"]["hasNextPage"]
        end_cursor = result["node"]["dashboards"]["pageInfo"]["endCursor"]
        dashboards = [cls.QueryResponse(**dashboard["node"]) for dashboard in dashboard_edges]
        return dashboards, has_next_page, end_cursor


class GetDashboardByIdQuery(BaseQuery):
    graphql_query = (
        """
    query getDashboardById($dashboardId: ID!) {
        node(id: $dashboardId) {
            ... on Dashboard {"""
        + Dashboard.to_graphql_fields()
        + """}
        }
    }
    """
    )
    query_description = "Get a detailed dashboard by ID with all widget connections"

    class Variables(BaseVariables):
        dashboardId: str

    class QueryException(ArizeAPIException):
        message: str = "Error getting dashboard by ID"

    class QueryResponse(Dashboard):
        pass


class GetDashboardQuery(BaseQuery):
    graphql_query = (
        """
    query getDashboardByName($spaceId: ID!, $dashboardName: String!) {
        node(id: $spaceId) {
            ... on Space {
                dashboards(search: $dashboardName, first: 1) {
                    edges {
                        node {"""
        + DashboardBasis.to_graphql_fields()
        + """}
                    }
                }
            }
        }
    }
    """
    )
    query_description = "Get a dashboard by name"

    class Variables(BaseVariables):
        spaceId: str
        dashboardName: str

    class QueryException(ArizeAPIException):
        message: str = "Error getting dashboard by name"

    class QueryResponse(DashboardBasis):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if not result["node"]["dashboards"]["edges"]:
            cls.raise_exception("No dashboard found with the given name")

        dashboard_node = result["node"]["dashboards"]["edges"][0]["node"]
        return [cls.QueryResponse(**dashboard_node)], False, None


# Widget-specific queries for paginated retrieval


class GetDashboardStatisticWidgetsQuery(BaseQuery):
    graphql_query = """
    query getDashboardStatisticWidgets($dashboardId: ID!, $endCursor: String) {
        node(id: $dashboardId) {
            ... on Dashboard {
                statisticWidgets(first: 10, after: $endCursor) {
                    pageInfo {
                        endCursor
                        hasNextPage
                    }
                    edges {
                        node {
                            id
                            dashboardId
                            title
                            gridPosition
                            creationStatus
                            timeSeriesMetricType
                            modelId
                            modelVersionIds
                            dimensionCategory
                            performanceMetric
                            aggregation
                            predictionValueClass
                            rankingAtK
                            modelEnvironmentName
                            modelVersionEnvironmentBatches
                        }
                    }
                }
            }
        }
    }
    """
    query_description = "Get paginated statistic widgets for a dashboard"

    class Variables(BaseVariables):
        dashboardId: str

    class QueryException(ArizeAPIException):
        message: str = "Error getting dashboard statistic widgets"

    class QueryResponse(StatisticWidget):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if not result["node"]["statisticWidgets"]["edges"]:
            return [], False, None

        widget_edges = result["node"]["statisticWidgets"]["edges"]
        has_next_page = result["node"]["statisticWidgets"]["pageInfo"]["hasNextPage"]
        end_cursor = result["node"]["statisticWidgets"]["pageInfo"]["endCursor"]
        widgets = [StatisticWidget(**widget["node"]) for widget in widget_edges]
        return widgets, has_next_page, end_cursor


class GetDashboardLineChartWidgetsQuery(BaseQuery):
    graphql_query = """
    query getDashboardLineChartWidgets($dashboardId: ID!, $endCursor: String) {
        node(id: $dashboardId) {
            ... on Dashboard {
                lineChartWidgets(first: 10, after: $endCursor) {
                    pageInfo {
                        endCursor
                        hasNextPage
                    }
                    edges {
                        node {
                            id
                            dashboardId
                            title
                            gridPosition
                            creationStatus
                            timeSeriesMetricType
                            yMin
                            yMax
                            yAxisLabel
                        }
                    }
                }
            }
        }
    }
    """
    query_description = "Get paginated line chart widgets for a dashboard"

    class Variables(BaseVariables):
        dashboardId: str

    class QueryException(ArizeAPIException):
        message: str = "Error getting dashboard line chart widgets"

    class QueryResponse(LineChartWidget):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if not result["node"]["lineChartWidgets"]["edges"]:
            return [], False, None

        widget_edges = result["node"]["lineChartWidgets"]["edges"]
        has_next_page = result["node"]["lineChartWidgets"]["pageInfo"]["hasNextPage"]
        end_cursor = result["node"]["lineChartWidgets"]["pageInfo"]["endCursor"]
        widgets = [LineChartWidget(**widget["node"]) for widget in widget_edges]
        return widgets, has_next_page, end_cursor


class GetDashboardBarChartWidgetsQuery(BaseQuery):
    graphql_query = """
    query getDashboardBarChartWidgets($dashboardId: ID!, $endCursor: String) {
        node(id: $dashboardId) {
            ... on Dashboard {
                barChartWidgets(first: 10, after: $endCursor) {
                    pageInfo {
                        endCursor
                        hasNextPage
                    }
                    edges {
                        node {
                            id
                            dashboardId
                            title
                            gridPosition
                            creationStatus
                            timeSeriesMetricType
                        }
                    }
                }
            }
        }
    }
    """
    query_description = "Get paginated bar chart widgets for a dashboard"

    class Variables(BaseVariables):
        dashboardId: str

    class QueryException(ArizeAPIException):
        message: str = "Error getting dashboard bar chart widgets"

    class QueryResponse(WidgetBasis):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if not result["node"]["barChartWidgets"]["edges"]:
            return [], False, None

        widget_edges = result["node"]["barChartWidgets"]["edges"]
        has_next_page = result["node"]["barChartWidgets"]["pageInfo"]["hasNextPage"]
        end_cursor = result["node"]["barChartWidgets"]["pageInfo"]["endCursor"]
        widgets = [WidgetBasis(**widget["node"]) for widget in widget_edges]
        return widgets, has_next_page, end_cursor


class GetDashboardTextWidgetsQuery(BaseQuery):
    graphql_query = """
    query getDashboardTextWidgets($dashboardId: ID!, $endCursor: String) {
        node(id: $dashboardId) {
            ... on Dashboard {
                textWidgets(first: 10, after: $endCursor) {
                    pageInfo {
                        endCursor
                        hasNextPage
                    }
                    edges {
                        node {
                            id
                            dashboardId
                            title
                            gridPosition
                            creationStatus
                            timeSeriesMetricType
                        }
                    }
                }
            }
        }
    }
    """
    query_description = "Get paginated text widgets for a dashboard"

    class Variables(BaseVariables):
        dashboardId: str

    class QueryException(ArizeAPIException):
        message: str = "Error getting dashboard text widgets"

    class QueryResponse(WidgetBasis):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if not result["node"]["textWidgets"]["edges"]:
            return [], False, None

        widget_edges = result["node"]["textWidgets"]["edges"]
        has_next_page = result["node"]["textWidgets"]["pageInfo"]["hasNextPage"]
        end_cursor = result["node"]["textWidgets"]["pageInfo"]["endCursor"]
        widgets = [WidgetBasis(**widget["node"]) for widget in widget_edges]
        return widgets, has_next_page, end_cursor


class GetDashboardExperimentChartWidgetsQuery(BaseQuery):
    graphql_query = """
    query getDashboardExperimentChartWidgets($dashboardId: ID!, $endCursor: String) {
        node(id: $dashboardId) {
            ... on Dashboard {
                experimentChartWidgets(first: 10, after: $endCursor) {
                    pageInfo {
                        endCursor
                        hasNextPage
                    }
                    edges {
                        node {
                            id
                            dashboardId
                            title
                            gridPosition
                            creationStatus
                            timeSeriesMetricType
                        }
                    }
                }
            }
        }
    }
    """
    query_description = "Get paginated experiment chart widgets for a dashboard"

    class Variables(BaseVariables):
        dashboardId: str

    class QueryException(ArizeAPIException):
        message: str = "Error getting dashboard experiment chart widgets"

    class QueryResponse(WidgetBasis):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        from arize_toolkit.models import WidgetBasis

        if not result["node"]["experimentChartWidgets"]["edges"]:
            return [], False, None

        widget_edges = result["node"]["experimentChartWidgets"]["edges"]
        has_next_page = result["node"]["experimentChartWidgets"]["pageInfo"]["hasNextPage"]
        end_cursor = result["node"]["experimentChartWidgets"]["pageInfo"]["endCursor"]
        widgets = [WidgetBasis(**widget["node"]) for widget in widget_edges]
        return widgets, has_next_page, end_cursor


class GetDashboardDriftLineChartWidgetsQuery(BaseQuery):
    graphql_query = """
    query getDashboardDriftLineChartWidgets($dashboardId: ID!, $endCursor: String) {
        node(id: $dashboardId) {
            ... on Dashboard {
                driftLineChartWidgets(first: 10, after: $endCursor) {
                    pageInfo {
                        endCursor
                        hasNextPage
                    }
                    edges {
                        node {
                            id
                            dashboardId
                            title
                            gridPosition
                            creationStatus
                            timeSeriesMetricType
                            yMin
                            yMax
                            yAxisLabel
                        }
                    }
                }
            }
        }
    }
    """
    query_description = "Get paginated drift line chart widgets for a dashboard"

    class Variables(BaseVariables):
        dashboardId: str

    class QueryException(ArizeAPIException):
        message: str = "Error getting dashboard drift line chart widgets"

    class QueryResponse(LineChartWidget):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        from arize_toolkit.models import LineChartWidget

        if not result["node"]["driftLineChartWidgets"]["edges"]:
            return [], False, None

        widget_edges = result["node"]["driftLineChartWidgets"]["edges"]
        has_next_page = result["node"]["driftLineChartWidgets"]["pageInfo"]["hasNextPage"]
        end_cursor = result["node"]["driftLineChartWidgets"]["pageInfo"]["endCursor"]
        widgets = [LineChartWidget(**widget["node"]) for widget in widget_edges]
        return widgets, has_next_page, end_cursor


class GetDashboardMonitorLineChartWidgetsQuery(BaseQuery):
    graphql_query = """
    query getDashboardMonitorLineChartWidgets($dashboardId: ID!, $endCursor: String) {
        node(id: $dashboardId) {
            ... on Dashboard {
                monitorLineChartWidgets(first: 10, after: $endCursor) {
                    pageInfo {
                        endCursor
                        hasNextPage
                    }
                    edges {
                        node {
                            id
                            dashboardId
                            title
                            gridPosition
                            creationStatus
                            timeSeriesMetricType
                            yMin
                            yMax
                            yAxisLabel
                        }
                    }
                }
            }
        }
    }
    """
    query_description = "Get paginated monitor line chart widgets for a dashboard"

    class Variables(BaseVariables):
        dashboardId: str

    class QueryException(ArizeAPIException):
        message: str = "Error getting dashboard monitor line chart widgets"

    class QueryResponse(LineChartWidget):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        from arize_toolkit.models import LineChartWidget

        if not result["node"]["monitorLineChartWidgets"]["edges"]:
            return [], False, None

        widget_edges = result["node"]["monitorLineChartWidgets"]["edges"]
        has_next_page = result["node"]["monitorLineChartWidgets"]["pageInfo"]["hasNextPage"]
        end_cursor = result["node"]["monitorLineChartWidgets"]["pageInfo"]["endCursor"]
        widgets = [LineChartWidget(**widget["node"]) for widget in widget_edges]
        return widgets, has_next_page, end_cursor
