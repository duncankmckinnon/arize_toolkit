import pytest

from arize_toolkit.queries.model_queries import DeleteDataMutation, GetAllModelsQuery, GetModelQuery, GetModelVolumeQuery, GetPerformanceMetricValuesQuery


class TestGetAllModelsQuery:
    def test_get_all_models_query_success(self, gql_client):
        # Simulate a successful GraphQL response
        mock_response = {
            "node": {
                "models": {
                    "pageInfo": {"hasNextPage": True, "endCursor": "cursor123"},
                    "edges": [
                        {
                            "node": {
                                "name": "Model1",
                                "id": "1",
                                "modelType": "numeric",
                                "createdAt": "2021-01-01T00:00:00Z",
                                "isDemoModel": False,
                            }
                        },
                        {
                            "node": {
                                "name": "Model2",
                                "id": "2",
                                "modelType": "score_categorical",
                                "createdAt": "2021-01-01T00:00:00Z",
                                "isDemoModel": False,
                            }
                        },
                    ],
                }
            }
        }
        gql_client.execute.return_value = mock_response

        # Execute the query
        result = GetAllModelsQuery.iterate_over_pages(gql_client, space_id="123")

        # Assertion
        assert result[0].name == "Model1"
        assert result[0].id == "1"
        assert result[0].modelType.name == "numeric"
        assert result[0].createdAt.isoformat() == "2021-01-01T00:00:00+00:00"
        assert not result[0].isDemoModel
        assert result[1].name == "Model2"
        assert result[1].id == "2"
        assert result[1].modelType.name == "score_categorical"
        assert result[1].createdAt.isoformat() == "2021-01-01T00:00:00+00:00"
        assert not result[1].isDemoModel

    def test_get_all_models_query_no_models(self, gql_client):
        # Simulate a GraphQL response with no models

        mock_response = {
            "node": {
                "models": {
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                    "edges": [],
                }
            }
        }
        gql_client.execute.return_value = mock_response

        # Execute the query
        result, has_next_page, end_cursor = GetAllModelsQuery._graphql_query(gql_client, space_id="123")

        # Assertions
        assert has_next_page is False
        assert end_cursor is None
        assert len(result) == 0

    def test_get_all_models_query_error(self, gql_client):
        # Simulate an error in the GraphQL response

        mock_response = {"errors": [{"message": "Some error occurred"}]}
        gql_client.execute.return_value = mock_response

        # Execute the query and expect an exception
        with pytest.raises(GetAllModelsQuery.QueryException):
            GetAllModelsQuery.iterate_over_pages(gql_client, space_id="123")


class TestGetModelQuery:
    def test_get_model_query_success(self, gql_client):
        mock_response = {
            "node": {
                "models": {
                    "edges": [
                        {
                            "node": {
                                "id": "1",
                                "name": "Model1",
                                "modelType": "ranking",
                                "createdAt": "2021-01-01T00:00:00Z",
                                "isDemoModel": False,
                            }
                        }
                    ]
                }
            }
        }
        gql_client.execute.return_value = mock_response

        # Execute the query
        result = GetModelQuery.run_graphql_query(gql_client, model_name="Model1", space_id="123")

        # Assertions
        assert result.id == "1"
        assert result.name == "Model1"
        assert result.modelType.name == "ranking"
        assert result.createdAt.isoformat() == "2021-01-01T00:00:00+00:00"
        assert not result.isDemoModel

    def test_get_model_query_no_model(self, gql_client):
        mock_response = {"node": {"models": {"edges": []}}}
        gql_client.execute.return_value = mock_response

        # Execute the query and expect an exception
        result = None
        with pytest.raises(GetModelQuery.QueryException, match="No model found with the given name"):
            result = GetModelQuery.run_graphql_query(gql_client, model_name="Model1", space_id="123")
        assert result is None


class TestGetModelVolumeQuery:
    def test_get_model_volume_query_success(self, gql_client):
        mock_response = {"node": {"modelPredictionVolume": {"totalVolume": 100}}}
        gql_client.execute.return_value = mock_response

        # Execute the query
        result = GetModelVolumeQuery.run_graphql_query(
            gql_client,
            model_id="123",
            start_time="2021-01-01T00:00:00Z",
            end_time="2021-01-01T00:00:00Z",
        )

        # Assertions
        assert result.totalVolume == 100

    def test_get_model_volume_query_no_model(self, gql_client):
        mock_response = {"node": {"errors": [{"message": "No model prediction volume found with the given id"}]}}
        gql_client.execute.return_value = mock_response

        # Execute the query and expect an exception
        result = None
        with pytest.raises(
            GetModelVolumeQuery.QueryException,
            match="No model prediction volume found with the given id",
        ):
            result = GetModelVolumeQuery.run_graphql_query(
                gql_client,
                model_id="123",
                start_time="2021-01-01T00:00:00Z",
                end_time="2021-01-01T00:00:00Z",
            )
        assert result is None


class TestDeleteDataMutation:
    def test_delete_data_mutation_success(self, gql_client):
        mock_response = {"deleteData": {"clientMutationId": None}}
        gql_client.execute.return_value = mock_response

        # Execute the query
        result = DeleteDataMutation.run_graphql_mutation(
            gql_client,
            modelId="123",
            startTime="2024-01-01T00:00:00Z",
        )

        # Assertions
        assert result.success is True

    def test_delete_data_mutation_no_model(self, gql_client):
        mock_response = {"errors": [{"message": "No model found with the given id"}]}
        gql_client.execute.return_value = mock_response

        # Execute the query and expect an exception
        result = None
        with pytest.raises(DeleteDataMutation.QueryException, match="No model found with the given id"):
            result = DeleteDataMutation.run_graphql_mutation(
                gql_client,
                modelId="123",
                startTime="2024-01-01T00:00:00Z",
                endTime="2025-01-01T00:00:00Z",
                environment="PREPRODUCTION",
            )
        assert result is None


class TestGetPerformanceMetricValuesQuery:
    def test_get_performance_metric_values_query_success(self, gql_client):
        mock_response = {
            "node": {
                "performanceMetricOverTime": {
                    "dataWindows": [
                        {
                            "metricDisplayDate": "2021-01-01T00:00:00Z",
                            "metricValue": 100,
                        },
                        {
                            "metricDisplayDate": "2021-01-02T00:00:00Z",
                            "metricValue": 200,
                        },
                        {
                            "metricDisplayDate": "2021-01-03T00:00:00Z",
                            "metricValue": 300,
                        },
                        {
                            "metricDisplayDate": "2021-01-04T00:00:00Z",
                            "metricValue": 400,
                        },
                        {
                            "metricDisplayDate": "2021-01-05T00:00:00Z",
                            "metricValue": None,
                        },
                    ]
                }
            }
        }
        gql_client.execute.return_value = mock_response

        # Execute the query
        result = GetPerformanceMetricValuesQuery.run_graphql_query_to_list(
            gql_client,
            modelId="123",
            metric="predictionAverage",
            environment="production",
            granularity="day",
            startDate="2021-01-01T00:00:00Z",
            endDate="2021-01-06T00:00:00Z",
        )
        final_result = [r.to_dict() for r in result]

        # Assertions
        assert final_result[0]["metricDisplayDate"] == "2021-01-01T00:00:00.000000Z"
        assert final_result[0]["metricValue"] == 100
        assert final_result[1]["metricDisplayDate"] == "2021-01-02T00:00:00.000000Z"
        assert final_result[1]["metricValue"] == 200
        assert final_result[2]["metricDisplayDate"] == "2021-01-03T00:00:00.000000Z"
        assert final_result[2]["metricValue"] == 300
        assert final_result[3]["metricDisplayDate"] == "2021-01-04T00:00:00.000000Z"
        assert final_result[3]["metricValue"] == 400
        assert final_result[4]["metricDisplayDate"] == "2021-01-05T00:00:00.000000Z"
        assert final_result[4]["metricValue"] is None
