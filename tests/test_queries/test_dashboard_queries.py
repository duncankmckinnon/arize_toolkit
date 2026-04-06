import pytest

from arize_toolkit.queries.dashboard_queries import CreateDashboardMutation, CreateLineChartWidgetMutation, GetDashboardPerformanceSlicesQuery, GetDashboardQuery
from arize_toolkit.types import WidgetCreationStatus


class TestGetDashboardQuery:
    def test_get_dashboard_by_name_success(self, gql_client):
        """Test that an exact name match returns the correct dashboard"""
        mock_response = {
            "node": {
                "dashboards": {
                    "edges": [
                        {"node": {"id": "dash1", "name": "My Dashboard"}},
                    ]
                }
            }
        }
        gql_client.execute.return_value = mock_response
        result = GetDashboardQuery.run_graphql_query(gql_client, spaceId="space1", dashboardName="My Dashboard")
        assert result.id == "dash1"
        assert result.name == "My Dashboard"

    def test_get_dashboard_by_name_no_exact_match(self, gql_client):
        """Test that a fuzzy match (no exact match) raises an error"""
        mock_response = {
            "node": {
                "dashboards": {
                    "edges": [
                        {"node": {"id": "dash1", "name": "My Dashboard Production"}},
                    ]
                }
            }
        }
        gql_client.execute.return_value = mock_response
        with pytest.raises(GetDashboardQuery.QueryException, match="No dashboard found with the exact name"):
            GetDashboardQuery.run_graphql_query(gql_client, spaceId="space1", dashboardName="My Dashboard")

    def test_get_dashboard_by_name_multiple_results(self, gql_client):
        """Test that the exact match is found among multiple fuzzy results"""
        mock_response = {
            "node": {
                "dashboards": {
                    "edges": [
                        {"node": {"id": "dash2", "name": "My Dashboard v2"}},
                        {"node": {"id": "dash1", "name": "My Dashboard"}},
                    ]
                }
            }
        }
        gql_client.execute.return_value = mock_response
        result = GetDashboardQuery.run_graphql_query(gql_client, spaceId="space1", dashboardName="My Dashboard")
        assert result.id == "dash1"
        assert result.name == "My Dashboard"

    def test_get_dashboard_by_name_not_found(self, gql_client):
        """Test that empty results raise a 'not found' error"""
        mock_response = {"node": {"dashboards": {"edges": []}}}
        gql_client.execute.return_value = mock_response
        with pytest.raises(GetDashboardQuery.QueryException, match="No dashboard found with the given name"):
            GetDashboardQuery.run_graphql_query(gql_client, spaceId="space1", dashboardName="Missing")

    def test_get_dashboard_by_name_case_sensitive(self, gql_client):
        """Test that name matching is case-sensitive"""
        mock_response = {
            "node": {
                "dashboards": {
                    "edges": [
                        {"node": {"id": "dash1", "name": "my dashboard"}},
                    ]
                }
            }
        }
        gql_client.execute.return_value = mock_response
        with pytest.raises(GetDashboardQuery.QueryException, match="No dashboard found with the exact name"):
            GetDashboardQuery.run_graphql_query(gql_client, spaceId="space1", dashboardName="My Dashboard")


class TestDashboardQueries:
    def test_get_dashboard_performance_slices(self, gql_client):
        dashboard_id = "test_dashboard_id"
        gql_client.execute.return_value = {
            "node": {
                "performanceSlices": {
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                    "edges": [
                        {"node": {"id": "slice1"}},
                        {"node": {"id": "slice2"}},
                    ],
                }
            }
        }
        result = GetDashboardPerformanceSlicesQuery.iterate_over_pages(gql_client, dashboardId=dashboard_id)
        assert len(result) == 2
        assert result[0].id == "slice1"
        assert result[1].id == "slice2"


class TestDashboardMutations:
    def test_create_dashboard_mutation(self, gql_client):
        """Test creating a new dashboard"""
        gql_client.execute.return_value = {
            "createDashboard": {
                "dashboard": {
                    "id": "new_dashboard_id",
                    "name": "Test Dashboard",
                    "status": "active",
                    "createdAt": "2024-01-01T00:00:00Z",
                },
                "clientMutationId": "test_mutation_id",
            }
        }

        result = CreateDashboardMutation.run_graphql_mutation(
            gql_client,
            name="Test Dashboard",
            spaceId="test_space_id",
            clientMutationId="test_mutation_id",
        )

        assert result.id == "new_dashboard_id"
        assert result.name == "Test Dashboard"
        assert result.status == "active"
        assert result.createdAt == "2024-01-01T00:00:00Z"

    def test_create_dashboard_mutation_error(self, gql_client):
        """Test error handling when dashboard creation fails"""
        gql_client.execute.return_value = {"createDashboard": {}}

        with pytest.raises(CreateDashboardMutation.QueryException):
            CreateDashboardMutation.run_graphql_mutation(gql_client, name="Test Dashboard", spaceId="test_space_id")

    def test_create_line_chart_widget_mutation(self, gql_client):
        """Test creating a line chart widget"""
        gql_client.execute.return_value = {
            "createLineChartWidget": {
                "lineChartWidget": {
                    "id": "new_widget_id",
                    "title": "Model Volume",
                    "dashboardId": "test_dashboard_id",
                    "gridPosition": [0, 0, 6, 4],
                    "creationStatus": "created",
                },
            }
        }

        plots = [
            {
                "modelId": "test_model_id",
                "title": "Model A Volume",
                "position": 0,
                "modelEnvironmentName": "production",
                "metric": "count",
                "filters": [],
            }
        ]

        result = CreateLineChartWidgetMutation.run_graphql_mutation(
            gql_client,
            title="Model Volume",
            dashboardId="test_dashboard_id",
            plots=plots,
        )

        assert result.id == "new_widget_id"
        assert result.title == "Model Volume"
        assert result.dashboardId == "test_dashboard_id"
        assert result.gridPosition == [0, 0, 6, 4]
        assert result.creationStatus == WidgetCreationStatus.created

    def test_create_line_chart_widget_mutation_error(self, gql_client):
        """Test error handling when widget creation fails"""
        gql_client.execute.return_value = {"createLineChartWidget": {}}

        plots = [
            {
                "modelId": "test_model_id",
                "title": "Model A Volume",
                "position": 0,
                "modelEnvironmentName": "production",
                "metric": "count",
                "filters": [],
            }
        ]

        with pytest.raises(CreateLineChartWidgetMutation.QueryException):
            CreateLineChartWidgetMutation.run_graphql_mutation(
                gql_client,
                title="Model Volume",
                dashboardId="test_dashboard_id",
                plots=plots,
            )
