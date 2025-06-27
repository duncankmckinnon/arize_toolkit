import pytest

from arize_toolkit.queries.dashboard_queries import CreateDashboardMutation, CreateLineChartWidgetMutation, GetDashboardPerformanceSlicesQuery


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

        assert result.dashboard_id == "new_dashboard_id"
        assert result.name == "Test Dashboard"
        assert result.status == "active"
        assert result.created_at == "2024-01-01T00:00:00Z"

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
                    "timeSeriesMetricType": "modelDataMetric",
                    "gridPosition": [0, 0, 6, 4],
                },
                "clientMutationId": "test_mutation_id",
            }
        }

        plots = [{"modelId": "test_model_id", "title": "Model A Volume", "position": 0}]

        result = CreateLineChartWidgetMutation.run_graphql_mutation(
            gql_client,
            title="Model Volume",
            dashboardId="test_dashboard_id",
            plots=plots,
            gridPosition=[0, 0, 6, 4],
            clientMutationId="test_mutation_id",
        )

        assert result.widget_id == "new_widget_id"
        assert result.title == "Model Volume"
        assert result.dashboard_id == "test_dashboard_id"
        assert result.time_series_metric_type == "modelDataMetric"
        assert result.grid_position == [0, 0, 6, 4]

    def test_create_line_chart_widget_mutation_error(self, gql_client):
        """Test error handling when widget creation fails"""
        gql_client.execute.return_value = {"createLineChartWidget": {}}

        plots = [{"modelId": "test_model_id"}]

        with pytest.raises(CreateLineChartWidgetMutation.QueryException):
            CreateLineChartWidgetMutation.run_graphql_mutation(
                gql_client,
                title="Model Volume",
                dashboardId="test_dashboard_id",
                plots=plots,
            )
