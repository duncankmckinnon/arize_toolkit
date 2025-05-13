from arize_api.queries.monitor_queries import (
    CreateDriftMonitorMutation,
    CreateDataQualityMonitorMutation,
    CreatePerformanceMonitorMutation,
    GetMonitorQuery,
    GetAllModelMonitorsQuery,
    DeleteMonitorMutation,
    GetMonitorByIDQuery,
)
from arize_api.types import (
    MonitorCategory,
    DimensionCategory,
    ComparisonOperator,
    DriftMetric,
    DataQualityMetric,
    PerformanceMetric,
)

from arize_api.models import DataQualityMonitor, PerformanceMonitor, DriftMonitor


class TestGetMonitorQuery:
    def test_get_monitor_query(self, gql_client):
        """Test getting a monitor"""
        gql_client.execute.return_value = {
            "node": {
                "monitors": {
                    "edges": [
                        {
                            "node": {
                                "id": "test_monitor_id",
                                "name": "test_monitor",
                                "monitorCategory": "drift",
                                "dimensionCategory": "featureLabel",
                                "driftMetric": "psi",
                            }
                        }
                    ]
                }
            }
        }

        result = GetMonitorQuery.run_graphql_query(
            gql_client,
            model_name="test_model",
            monitor_name="test_monitor",
            space_id="test_space",
        )

        assert result.id == "test_monitor_id"
        assert result.monitorCategory == MonitorCategory.drift
        gql_client.execute.assert_called_once()

    def test_get_monitor_query_by_id(self, gql_client):
        """Test getting a monitor by ID"""
        gql_client.execute.return_value = {
            "node": {
                "id": "test_monitor_id",
                "name": "test_monitor",
                "monitorCategory": "drift",
                "dimensionCategory": "featureLabel",
                "operator": "greaterThan",
                "driftMetric": "psi",
            }
        }

        result = GetMonitorByIDQuery.run_graphql_query(
            gql_client, monitor_id="test_monitor_id"
        )

        assert result.id == "test_monitor_id"
        assert result.monitorCategory == MonitorCategory.drift
        gql_client.execute.assert_called_once()

    def test_get_all_monitors_query(self, gql_client):
        """Test getting all monitors"""
        gql_client.execute.return_value = {
            "node": {
                "monitors": {
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                    "edges": [
                        {
                            "node": {
                                "id": "monitor1",
                                "name": "drift_monitor",
                                "monitorCategory": "drift",
                                "dimensionCategory": "featureLabel",
                                "driftMetric": "psi",
                            }
                        },
                        {
                            "node": {
                                "id": "monitor2",
                                "name": "quality_monitor",
                                "monitorCategory": "dataQuality",
                                "dimensionCategory": "featureLabel",
                                "dataQualityMetric": "percentEmpty",
                            }
                        },
                    ],
                }
            }
        }

        results = GetAllModelMonitorsQuery.iterate_over_pages(
            gql_client, model_id="test_model_id"
        )

        assert len(results) == 2
        assert results[0].id == "monitor1"
        assert results[1].id == "monitor2"
        gql_client.execute.assert_called_once()

    def test_get_all_monitors_pagination(self, gql_client):
        """Test monitor pagination"""
        gql_client.execute.side_effect = [
            {
                "node": {
                    "monitors": {
                        "pageInfo": {"hasNextPage": True, "endCursor": "cursor1"},
                        "edges": [
                            {
                                "node": {
                                    "id": "monitor1",
                                    "name": "drift_monitor",
                                    "monitorCategory": "drift",
                                    "dimensionCategory": "featureLabel",
                                    "driftMetric": "psi",
                                }
                            }
                        ],
                    }
                }
            },
            {
                "node": {
                    "monitors": {
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                        "edges": [
                            {
                                "node": {
                                    "id": "monitor2",
                                    "name": "quality_monitor",
                                    "monitorCategory": "dataQuality",
                                    "dimensionCategory": "featureLabel",
                                    "dataQualityMetric": "percentEmpty",
                                }
                            }
                        ],
                    }
                }
            },
        ]

        results = GetAllModelMonitorsQuery.iterate_over_pages(
            gql_client, model_id="test_model_id"
        )

        assert len(results) == 2
        assert gql_client.execute.call_count == 2


class TestCreateMonitorMutation:
    def test_create_drift_monitor_mutation(self, gql_client):
        """Test creating a drift monitor"""
        gql_client.execute.return_value = {
            "createDriftMonitor": {"monitor": {"id": "new_monitor_id"}}
        }

        variables = DriftMonitor(
            spaceId="test_space",
            modelName="test_model",
            name="test_drift_monitor",
            driftMetric=DriftMetric.psi,
            dimensionCategory=DimensionCategory.featureLabel,
            operator=ComparisonOperator.greaterThan,
        )

        result = CreateDriftMonitorMutation.run_graphql_mutation(
            gql_client, **variables.to_dict()
        )

        assert result.monitor_id == "new_monitor_id"
        gql_client.execute.assert_called_once()

    def test_create_data_quality_monitor_mutation(self, gql_client):
        """Test creating a data quality monitor"""
        gql_client.execute.return_value = {
            "createDataQualityMonitor": {"monitor": {"id": "new_monitor_id"}}
        }

        variables = DataQualityMonitor(
            spaceId="test_space",
            modelName="test_model",
            name="test_quality_monitor",
            dataQualityMetric=DataQualityMetric.percentEmpty,
            dimensionCategory=DimensionCategory.featureLabel,
            operator=ComparisonOperator.lessThan,
        )

        result = CreateDataQualityMonitorMutation.run_graphql_mutation(
            gql_client, **variables.to_dict()
        )

        assert result.monitor_id == "new_monitor_id"
        gql_client.execute.assert_called_once()

    def test_create_performance_monitor_mutation(self, gql_client):
        """Test creating a performance monitor"""
        gql_client.execute.return_value = {
            "createPerformanceMonitor": {"monitor": {"id": "new_monitor_id"}}
        }

        variables = PerformanceMonitor(
            spaceId="test_space",
            modelName="test_model",
            name="test_performance_monitor",
            performanceMetric=PerformanceMetric.accuracy,
            operator=ComparisonOperator.greaterThan,
        )

        result = CreatePerformanceMonitorMutation.run_graphql_mutation(
            gql_client, **variables.to_dict()
        )

        assert result.monitor_id == "new_monitor_id"
        gql_client.execute.assert_called_once()


class TestDeleteMonitorMutation:
    def test_delete_monitor_mutation(self, gql_client):
        """Test deleting a monitor"""
        gql_client.execute.return_value = {
            "deleteMonitor": {"monitor": {"id": "deleted_monitor_id"}}
        }

        result = DeleteMonitorMutation.run_graphql_mutation(
            gql_client, monitorId="test_monitor_id"
        )

        assert result.monitor_id == "deleted_monitor_id"
        gql_client.execute.assert_called_once()
