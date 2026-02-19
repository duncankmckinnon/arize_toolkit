from datetime import datetime, timezone

import pytest

from arize_toolkit.models import DataQualityMonitor, DriftMonitor, PerformanceMonitor
from arize_toolkit.queries.monitor_queries import (
    CreateDataQualityMonitorMutation,
    CreateDriftMonitorMutation,
    CreatePerformanceMonitorMutation,
    DeleteMonitorMutation,
    GetAllModelMonitorsQuery,
    GetModelMetricValueQuery,
    GetMonitorByIDQuery,
    GetMonitorQuery,
)
from arize_toolkit.types import (
    ComparisonOperator,
    DataQualityMetric,
    DimensionCategory,
    DriftMetric,
    MonitorCategory,
    PerformanceMetric,
)


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


class TestGetModelMetricValueQuery:
    def test_query_structure(self):
        """Test that the query structure is correct and includes all necessary fields."""
        query = GetModelMetricValueQuery.graphql_query
        assert "query GetModelMetricValue" in query
        assert "$space_id: ID!" in query
        assert "$model_name: String" in query
        assert "$monitor_name: String" in query
        assert "$start_date: DateTime!" in query
        assert "$end_date: DateTime!" in query
        assert "$time_series_data_granularity: DataGranularity!" in query
        assert "metricHistory" in query
        assert "TimeSeriesWithThresholdDataType" in query
        assert "key" in query
        assert "dataPoints" in query
        assert "thresholdDataPoints" in query

    def test_get_model_metric_value_success(self, gql_client):
        """Test successful metric value retrieval."""
        # Mock response with metric history data
        mock_response = {
            "node": {
                "models": {
                    "edges": [
                        {
                            "node": {
                                "monitors": {
                                    "edges": [
                                        {
                                            "node": {
                                                "metricHistory": {
                                                    "key": "accuracy_metric",
                                                    "dataPoints": [
                                                        {
                                                            "x": "2024-01-01T00:00:00Z",
                                                            "y": 0.95,
                                                        },
                                                        {
                                                            "x": "2024-01-01T01:00:00Z",
                                                            "y": 0.94,
                                                        },
                                                        {
                                                            "x": "2024-01-01T02:00:00Z",
                                                            "y": 0.96,
                                                        },
                                                    ],
                                                    "thresholdDataPoints": [
                                                        {
                                                            "x": "2024-01-01T00:00:00Z",
                                                            "y": 0.90,
                                                        },
                                                        {
                                                            "x": "2024-01-01T01:00:00Z",
                                                            "y": 0.90,
                                                        },
                                                        {
                                                            "x": "2024-01-01T02:00:00Z",
                                                            "y": 0.90,
                                                        },
                                                    ],
                                                }
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    ]
                }
            }
        }
        gql_client.execute.return_value = mock_response

        # Execute query
        start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2024, 1, 2, tzinfo=timezone.utc)

        result = GetModelMetricValueQuery.run_graphql_query(
            gql_client,
            space_id="test_space_id",
            model_name="test_model",
            monitor_name="test_monitor",
            start_date=start_date,
            end_date=end_date,
            time_series_data_granularity="hour",
        )

        # Assertions
        assert result.key == "accuracy_metric"
        assert len(result.dataPoints) == 3
        assert result.dataPoints[0].y == 0.95
        assert result.dataPoints[1].y == 0.94
        assert result.dataPoints[2].y == 0.96
        assert len(result.thresholdDataPoints) == 3
        assert all(point.y == 0.90 for point in result.thresholdDataPoints)
        gql_client.execute.assert_called_once()

    def test_get_model_metric_value_without_threshold(self, gql_client):
        """Test metric value retrieval without threshold data."""
        mock_response = {
            "node": {
                "models": {
                    "edges": [
                        {
                            "node": {
                                "monitors": {
                                    "edges": [
                                        {
                                            "node": {
                                                "metricHistory": {
                                                    "key": "volume_metric",
                                                    "dataPoints": [
                                                        {
                                                            "x": "2024-01-01T00:00:00Z",
                                                            "y": 1000,
                                                        },
                                                        {
                                                            "x": "2024-01-01T01:00:00Z",
                                                            "y": 1200,
                                                        },
                                                    ],
                                                    "thresholdDataPoints": None,
                                                }
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    ]
                }
            }
        }
        gql_client.execute.return_value = mock_response

        result = GetModelMetricValueQuery.run_graphql_query(
            gql_client,
            space_id="test_space_id",
            model_name="test_model",
            monitor_name="volume_monitor",
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 2, tzinfo=timezone.utc),
            time_series_data_granularity="hour",
        )

        assert result.key == "volume_metric"
        assert len(result.dataPoints) == 2
        assert result.dataPoints[0].y == 1000
        assert result.dataPoints[1].y == 1200
        assert result.thresholdDataPoints is None

    def test_get_model_metric_value_no_model(self, gql_client):
        """Test error handling when model is not found."""
        mock_response = {"node": {"models": {"edges": []}}}
        gql_client.execute.return_value = mock_response

        with pytest.raises(
            GetModelMetricValueQuery.QueryException,
            match="No model found with the given name",
        ):
            GetModelMetricValueQuery.run_graphql_query(
                gql_client,
                space_id="test_space_id",
                model_name="non_existent_model",
                monitor_name="test_monitor",
                start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
                end_date=datetime(2024, 1, 2, tzinfo=timezone.utc),
                time_series_data_granularity="day",
            )

    def test_get_model_metric_value_no_monitor(self, gql_client):
        """Test error handling when monitor is not found."""
        mock_response = {
            "node": {"models": {"edges": [{"node": {"monitors": {"edges": []}}}]}}
        }
        gql_client.execute.return_value = mock_response

        with pytest.raises(
            GetModelMetricValueQuery.QueryException,
            match="No monitor found with the given name",
        ):
            GetModelMetricValueQuery.run_graphql_query(
                gql_client,
                space_id="test_space_id",
                model_name="test_model",
                monitor_name="non_existent_monitor",
                start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
                end_date=datetime(2024, 1, 2, tzinfo=timezone.utc),
                time_series_data_granularity="week",
            )

    def test_get_model_metric_value_no_history(self, gql_client):
        """Test error handling when no metric history is available."""
        mock_response = {
            "node": {
                "models": {
                    "edges": [
                        {
                            "node": {
                                "monitors": {
                                    "edges": [{"node": {"metricHistory": None}}]
                                }
                            }
                        }
                    ]
                }
            }
        }
        gql_client.execute.return_value = mock_response

        with pytest.raises(
            GetModelMetricValueQuery.QueryException,
            match="No metric history data available for the specified time range",
        ):
            GetModelMetricValueQuery.run_graphql_query(
                gql_client,
                space_id="test_space_id",
                model_name="test_model",
                monitor_name="test_monitor",
                start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
                end_date=datetime(2024, 1, 2, tzinfo=timezone.utc),
                time_series_data_granularity="month",
            )

    def test_get_model_metric_value_with_null_values(self, gql_client):
        """Test handling of data points with null y values."""
        mock_response = {
            "node": {
                "models": {
                    "edges": [
                        {
                            "node": {
                                "monitors": {
                                    "edges": [
                                        {
                                            "node": {
                                                "metricHistory": {
                                                    "key": "sparse_metric",
                                                    "dataPoints": [
                                                        {
                                                            "x": "2024-01-01T00:00:00Z",
                                                            "y": 0.95,
                                                        },
                                                        {
                                                            "x": "2024-01-01T01:00:00Z",
                                                            "y": None,
                                                        },
                                                        {
                                                            "x": "2024-01-01T02:00:00Z",
                                                            "y": 0.93,
                                                        },
                                                    ],
                                                    "thresholdDataPoints": [],
                                                }
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    ]
                }
            }
        }
        gql_client.execute.return_value = mock_response

        result = GetModelMetricValueQuery.run_graphql_query(
            gql_client,
            space_id="test_space_id",
            model_name="test_model",
            monitor_name="test_monitor",
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 2, tzinfo=timezone.utc),
            time_series_data_granularity="hour",
        )

        assert result.key == "sparse_metric"
        assert len(result.dataPoints) == 3
        assert result.dataPoints[0].y == 0.95
        assert result.dataPoints[1].y is None
        assert result.dataPoints[2].y == 0.93
        assert result.thresholdDataPoints == []

    def test_get_model_metric_value_different_granularities(self, gql_client):
        """Test query with different time series data granularities."""
        mock_response = {
            "node": {
                "models": {
                    "edges": [
                        {
                            "node": {
                                "monitors": {
                                    "edges": [
                                        {
                                            "node": {
                                                "metricHistory": {
                                                    "key": "daily_metric",
                                                    "dataPoints": [
                                                        {
                                                            "x": "2024-01-01T00:00:00Z",
                                                            "y": 100,
                                                        },
                                                        {
                                                            "x": "2024-01-02T00:00:00Z",
                                                            "y": 110,
                                                        },
                                                        {
                                                            "x": "2024-01-03T00:00:00Z",
                                                            "y": 105,
                                                        },
                                                    ],
                                                    "thresholdDataPoints": None,
                                                }
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    ]
                }
            }
        }
        gql_client.execute.return_value = mock_response

        # Test with day granularity
        result = GetModelMetricValueQuery.run_graphql_query(
            gql_client,
            space_id="test_space_id",
            model_name="test_model",
            monitor_name="test_monitor",
            start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2024, 1, 7, tzinfo=timezone.utc),
            time_series_data_granularity="day",
        )

        assert result.key == "daily_metric"
        assert len(result.dataPoints) == 3
        assert result.dataPoints[0].y == 100
        assert result.dataPoints[1].y == 110
        assert result.dataPoints[2].y == 105
