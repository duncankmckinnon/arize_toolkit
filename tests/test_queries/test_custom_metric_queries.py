import pytest

from arize_toolkit.queries.custom_metric_queries import (
    CreateCustomMetricMutation,
    DeleteCustomMetricMutation,
    GetAllCustomMetricsQuery,
    GetCustomMetricByIDQuery,
    GetCustomMetricQuery,
    UpdateCustomMetricMutation,
)


class TestGetAllCustomMetricsQuery:
    def test_get_all_custom_metrics_query_success(self, gql_client):
        # Simulate a successful GraphQL response
        mock_response = [
            {
                "node": {
                    "models": {
                        "edges": [
                            {
                                "node": {
                                    "customMetrics": {
                                        "pageInfo": {
                                            "hasNextPage": True,
                                            "endCursor": "cursor123",
                                        },
                                        "edges": [
                                            {
                                                "node": {
                                                    "id": "1",
                                                    "name": "CustomMetric1",
                                                    "createdAt": "2021-01-01T00:00:00Z",
                                                    "description": "Test metric 1",
                                                    "metric": "sum(x)/count(x)",
                                                    "requiresPositiveClass": False,
                                                }
                                            },
                                        ],
                                    }
                                }
                            }
                        ]
                    }
                }
            },
            {
                "node": {
                    "models": {
                        "edges": [
                            {
                                "node": {
                                    "customMetrics": {
                                        "pageInfo": {
                                            "hasNextPage": False,
                                            "endCursor": None,
                                        },
                                        "edges": [
                                            {
                                                "node": {
                                                    "id": "2",
                                                    "name": "CustomMetric2",
                                                    "createdAt": "2021-01-01T00:00:00Z",
                                                    "description": "Test metric 2",
                                                    "metric": "count(x > 0)/count(x)",
                                                    "requiresPositiveClass": True,
                                                }
                                            },
                                        ],
                                    }
                                }
                            }
                        ]
                    }
                }
            },
        ]
        gql_client.execute.side_effect = mock_response

        # Execute the query
        result = GetAllCustomMetricsQuery.iterate_over_pages(
            gql_client, space_id="123", model_name="test_model"
        )

        # Assertions
        assert len(result) == 2
        assert gql_client.execute.call_count == 2
        assert result[0].id == "1"
        assert result[0].name == "CustomMetric1"
        assert result[0].createdAt.isoformat() == "2021-01-01T00:00:00+00:00"
        assert result[0].description == "Test metric 1"
        assert result[0].metric == "sum(x)/count(x)"
        assert not result[0].requiresPositiveClass

        assert result[1].id == "2"
        assert result[1].name == "CustomMetric2"
        assert result[1].description == "Test metric 2"
        assert result[1].metric == "count(x > 0)/count(x)"
        assert result[1].requiresPositiveClass

    def test_get_all_custom_metrics_query_no_model(self, gql_client):
        # Simulate a GraphQL response with no model
        gql_client.execute.reset_mock()
        mock_response = {"node": {"models": {"edges": []}}}
        gql_client.execute.return_value = mock_response

        # Execute the query and expect an exception
        with pytest.raises(
            GetAllCustomMetricsQuery.QueryException,
            match="No model found with the given name",
        ):
            GetAllCustomMetricsQuery.iterate_over_pages(
                gql_client, space_id="123", model_name="test_model"
            )

    def test_get_all_custom_metrics_query_no_metrics(self, gql_client):
        # Simulate a GraphQL response with no custom metrics
        mock_response = {
            "node": {
                "models": {
                    "edges": [
                        {
                            "node": {
                                "customMetrics": {
                                    "pageInfo": {
                                        "hasNextPage": False,
                                        "endCursor": None,
                                    },
                                    "edges": [],
                                }
                            }
                        }
                    ]
                }
            }
        }
        gql_client.execute.return_value = mock_response

        # Execute the query and expect an exception
        with pytest.raises(
            GetAllCustomMetricsQuery.QueryException,
            match="No custom metric found with the given name",
        ):
            GetAllCustomMetricsQuery.iterate_over_pages(
                gql_client, space_id="123", model_name="test_model"
            )


class TestGetCustomMetricQuery:
    def test_get_custom_metric_query_success(self, gql_client):
        gql_client.execute.reset_mock()
        mock_response = {
            "node": {
                "models": {
                    "edges": [
                        {
                            "node": {
                                "customMetrics": {
                                    "pageInfo": {
                                        "hasNextPage": False,
                                        "endCursor": None,
                                    },
                                    "edges": [
                                        {
                                            "node": {
                                                "id": "1",
                                                "name": "CustomMetric1",
                                                "createdAt": "2021-01-01T00:00:00Z",
                                                "description": "Test metric",
                                                "metric": "sum(x)/count(x)",
                                                "requiresPositiveClass": False,
                                            }
                                        }
                                    ],
                                }
                            }
                        }
                    ]
                }
            }
        }
        gql_client.execute.return_value = mock_response

        # Execute the query
        result = GetCustomMetricQuery.run_graphql_query(
            gql_client,
            space_id="123",
            model_name="test_model",
            metric_name="CustomMetric1",
        )

        # Assertions
        assert result.id == "1"
        assert result.name == "CustomMetric1"
        assert result.createdAt.isoformat() == "2021-01-01T00:00:00+00:00"
        assert result.description == "Test metric"
        assert result.metric == "sum(x)/count(x)"
        assert not result.requiresPositiveClass

    def test_get_custom_metric_query_no_model(self, gql_client):
        mock_response = {"node": {"models": {"edges": []}}}
        gql_client.execute.return_value = mock_response

        # Execute the query and expect an exception
        with pytest.raises(
            GetCustomMetricQuery.QueryException,
            match="No model found with the given name",
        ):
            GetCustomMetricQuery.run_graphql_query(
                gql_client,
                space_id="123",
                model_name="test_model",
                metric_name="CustomMetric1",
            )

    def test_get_custom_metric_by_id_query_success(self, gql_client):
        mock_response = {
            "node": {
                "id": "1",
                "name": "CustomMetric1",
                "description": "Test metric",
                "metric": "select avg(prediction) from model",
                "createdAt": "2021-01-01T00:00:00Z",
                "requiresPositiveClass": False,
            }
        }

        gql_client.execute.return_value = mock_response

        # Execute the query
        result = GetCustomMetricByIDQuery.run_graphql_query(
            gql_client,
            custom_metric_id="1",
        )

        # Assertions
        assert result.id == "1"
        assert result.name == "CustomMetric1"
        assert result.description == "Test metric"
        assert result.metric == "select avg(prediction) from model"
        assert not result.requiresPositiveClass

    def test_get_custom_metric_query_no_metric(self, gql_client):
        mock_response = {
            "node": {"models": {"edges": [{"node": {"customMetrics": {"edges": []}}}]}}
        }
        gql_client.execute.return_value = mock_response

        # Execute the query and expect an exception
        with pytest.raises(
            GetCustomMetricQuery.QueryException,
            match="No custom metric found with the given name",
        ):
            GetCustomMetricQuery.run_graphql_query(
                gql_client,
                space_id="123",
                model_name="test_model",
                metric_name="CustomMetric1",
            )


class TestCreateCustomMetricMutation:
    def test_create_custom_metric_mutation_success(self, gql_client):
        mock_response = {
            "createCustomMetric": {"customMetric": {"id": "new_metric_id"}}
        }
        gql_client.execute.return_value = mock_response

        # Execute the mutation
        result = CreateCustomMetricMutation.run_graphql_mutation(
            gql_client,
            modelId="test_model_id",
            name="NewCustomMetric",
            description="Test metric",
            metric="sum(x)/count(x)",
        )

        # Assertions
        assert result.metric_id == "new_metric_id"
        gql_client.execute.assert_called_once()

    def test_create_custom_metric_mutation_error(self, gql_client):
        mock_response = {"errors": ["Invalid metric expression"]}
        gql_client.execute.return_value = mock_response

        # Execute the mutation and expect an exception
        with pytest.raises(
            CreateCustomMetricMutation.QueryException,
            match="Invalid metric expression",
        ):
            CreateCustomMetricMutation.run_graphql_mutation(
                gql_client,
                modelId="test_model_id",
                name="NewCustomMetric",
                description="Test metric",
                metric="invalid_expression",
            )

    def test_create_custom_metric_mutation_no_id(self, gql_client):
        mock_response = {"createCustomMetric": {}}
        gql_client.execute.return_value = mock_response

        # Execute the mutation and expect an exception
        with pytest.raises(
            CreateCustomMetricMutation.QueryException,
            match="no custom metric id returned",
        ):
            CreateCustomMetricMutation.run_graphql_mutation(
                gql_client,
                modelId="test_model_id",
                name="NewCustomMetric",
                description="Test metric",
                metric="sum(x)/count(x)",
            )


class TestDeleteCustomMetricMutation:
    def test_delete_custom_metric_mutation_success(self, gql_client):
        mock_response = {"deleteCustomMetric": {"model": {"id": "deleted_model_id"}}}
        gql_client.execute.return_value = mock_response

        # Execute the mutation
        result = DeleteCustomMetricMutation.run_graphql_mutation(
            gql_client,
            customMetricId="test_metric_id",
            modelId="test_model_id",
        )

        # Assertions
        assert result.model_id == "deleted_model_id"
        gql_client.execute.assert_called_once()

    def test_delete_custom_metric_mutation_no_id(self, gql_client):
        mock_response = {"deleteCustomMetric": {}}
        gql_client.execute.return_value = mock_response

        # Execute the mutation and expect an exception
        with pytest.raises(
            DeleteCustomMetricMutation.QueryException,
            match="no model id returned",
        ):
            DeleteCustomMetricMutation.run_graphql_mutation(
                gql_client,
                customMetricId="test_metric_id",
                modelId="test_model_id",
            )

    def test_delete_custom_metric_mutation_error(self, gql_client):
        mock_response = {"errors": ["Invalid metric expression"]}
        gql_client.execute.return_value = mock_response

        # Execute the mutation and expect an exception
        with pytest.raises(
            DeleteCustomMetricMutation.QueryException,
            match="Invalid metric expression",
        ):
            DeleteCustomMetricMutation.run_graphql_mutation(
                gql_client,
                customMetricId="test_metric_id",
                modelId="test_model_id",
            )


class TestUpdateCustomMetricMutation:
    def test_update_custom_metric_mutation_success(self, gql_client):
        mock_response = {
            "updateCustomMetric": {
                "customMetric": {
                    "id": "updated_metric_id",
                    "name": "UpdatedMetric",
                    "description": "Updated description",
                    "metric": "sum(x)/count(x)",
                    "requiresPositiveClass": False,
                }
            }
        }
        gql_client.execute.return_value = mock_response

        # Execute the mutation
        result = UpdateCustomMetricMutation.run_graphql_mutation(
            gql_client,
            customMetricId="test_metric_id",
            modelId="test_model_id",
            name="UpdatedMetric",
            description="Updated description",
            metric="sum(x)/count(x)",
        )

        assert result.id == "updated_metric_id"
        assert result.name == "UpdatedMetric"
        assert result.description == "Updated description"
        assert result.metric == "sum(x)/count(x)"
        assert not result.requiresPositiveClass

        assert gql_client.execute.call_count == 1

    def test_update_custom_metric_mutation_no_id(self, gql_client):
        mock_response = {"updateCustomMetric": {}}
        gql_client.execute.return_value = mock_response

        with pytest.raises(
            UpdateCustomMetricMutation.QueryException,
            match="no custom metric id returned",
        ):
            UpdateCustomMetricMutation.run_graphql_mutation(
                gql_client,
                customMetricId="test_metric_id",
                modelId="test_model_id",
                name="UpdatedMetric",
                description="Updated description",
                metric="sum(x)/count(x)",
            )
