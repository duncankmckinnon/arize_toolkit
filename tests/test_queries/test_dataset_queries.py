import pytest

from arize_toolkit.queries.dataset_queries import GetAllDatasetsQuery, GetDatasetByIdQuery, GetDatasetByNameQuery, GetDatasetExamplesQuery


class TestGetAllDatasetsQuery:
    """Test the GetAllDatasetsQuery class."""

    def test_query_structure(self):
        query = GetAllDatasetsQuery.graphql_query
        assert "query getAllDatasets" in query
        assert "$spaceId: ID!" in query
        assert "datasets(first: 50" in query
        assert "pageInfo" in query

    def test_successful_query(self, gql_client):
        mock_response = {
            "node": {
                "datasets": {
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                    "edges": [
                        {
                            "node": {
                                "id": "d1",
                                "name": "dataset-one",
                                "createdAt": "2026-01-01T00:00:00Z",
                                "updatedAt": "2026-01-02T00:00:00Z",
                                "datasetType": "generative",
                                "status": "active",
                                "columns": ["input", "output"],
                                "experimentCount": 3,
                            }
                        },
                        {
                            "node": {
                                "id": "d2",
                                "name": "dataset-two",
                                "createdAt": "2026-01-03T00:00:00Z",
                                "updatedAt": "2026-01-04T00:00:00Z",
                                "datasetType": "generative",
                                "status": "active",
                                "columns": ["text"],
                                "experimentCount": 0,
                            }
                        },
                    ],
                }
            }
        }
        gql_client.execute.return_value = mock_response

        results = GetAllDatasetsQuery.run_graphql_query_to_list(gql_client, spaceId="space_123")

        assert len(results) == 2
        assert results[0].name == "dataset-one"
        assert results[1].name == "dataset-two"

    def test_empty_datasets(self, gql_client):
        mock_response = {
            "node": {
                "datasets": {
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                    "edges": [],
                }
            }
        }
        gql_client.execute.return_value = mock_response

        results = GetAllDatasetsQuery.run_graphql_query_to_list(gql_client, spaceId="space_123")
        assert len(results) == 0

    def test_pagination(self, gql_client):
        page1 = {
            "node": {
                "datasets": {
                    "pageInfo": {"hasNextPage": True, "endCursor": "cursor1"},
                    "edges": [{"node": {"id": "d1", "name": "ds1"}}],
                }
            }
        }
        page2 = {
            "node": {
                "datasets": {
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                    "edges": [{"node": {"id": "d2", "name": "ds2"}}],
                }
            }
        }
        gql_client.execute.side_effect = [page1, page2]

        results = GetAllDatasetsQuery.iterate_over_pages(gql_client, spaceId="space_123")
        assert len(results) == 2
        assert gql_client.execute.call_count == 2


class TestGetDatasetByIdQuery:
    """Test the GetDatasetByIdQuery class."""

    def test_query_structure(self):
        query = GetDatasetByIdQuery.graphql_query
        assert "query getDatasetById" in query
        assert "$datasetId: ID!" in query
        assert "... on Dataset" in query

    def test_successful_query(self, gql_client):
        mock_response = {
            "node": {
                "id": "RGF0YXNldDozMjg0NDA6VE10WA==",
                "name": "pharmacy-malicious-baseline",
                "createdAt": "2026-01-13T23:37:29.000Z",
                "updatedAt": "2026-01-14T00:00:00.000Z",
                "datasetType": "generative",
                "status": "active",
                "columns": ["text", "timestamp"],
                "experimentCount": None,
            }
        }
        gql_client.execute.return_value = mock_response

        result = GetDatasetByIdQuery.run_graphql_query(gql_client, datasetId="RGF0YXNldDozMjg0NDA6VE10WA==")

        assert result.id == "RGF0YXNldDozMjg0NDA6VE10WA=="
        assert result.name == "pharmacy-malicious-baseline"
        assert result.columns == ["text", "timestamp"]
        assert result.experimentCount is None
        gql_client.execute.assert_called_once()

    def test_dataset_not_found(self, gql_client):
        mock_response = {"node": None}
        gql_client.execute.return_value = mock_response

        with pytest.raises(GetDatasetByIdQuery.QueryException, match="Object not found"):
            GetDatasetByIdQuery.run_graphql_query(gql_client, datasetId="nonexistent")

    def test_variables_validation(self):
        with pytest.raises(Exception) as exc_info:
            GetDatasetByIdQuery.Variables()
        assert "datasetId" in str(exc_info.value)

        variables = GetDatasetByIdQuery.Variables(datasetId="dataset_123")
        assert variables.datasetId == "dataset_123"


class TestGetDatasetByNameQuery:
    """Test the GetDatasetByNameQuery class."""

    def test_query_structure(self):
        query = GetDatasetByNameQuery.graphql_query
        assert "query getDatasetByName" in query
        assert "$spaceId: ID!" in query
        assert "$datasetName: String!" in query
        assert "datasets(search: $datasetName" in query

    def test_successful_query(self, gql_client):
        mock_response = {
            "node": {
                "datasets": {
                    "edges": [
                        {
                            "node": {
                                "id": "RGF0YXNldDozMjg0NDA6VE10WA==",
                                "name": "pharmacy-malicious-baseline",
                                "createdAt": "2026-01-13T23:37:29.000Z",
                                "updatedAt": "2026-01-14T00:00:00.000Z",
                                "datasetType": "generative",
                                "status": "active",
                                "columns": ["text", "timestamp"],
                                "experimentCount": None,
                            }
                        }
                    ]
                }
            }
        }
        gql_client.execute.return_value = mock_response

        result = GetDatasetByNameQuery.run_graphql_query(gql_client, spaceId="space_123", datasetName="pharmacy-malicious-baseline")

        assert result.id == "RGF0YXNldDozMjg0NDA6VE10WA=="
        assert result.name == "pharmacy-malicious-baseline"
        assert result.columns == ["text", "timestamp"]
        gql_client.execute.assert_called_once()

    def test_dataset_not_found_empty(self, gql_client):
        mock_response = {"node": {"datasets": {"edges": []}}}
        gql_client.execute.return_value = mock_response

        with pytest.raises(
            GetDatasetByNameQuery.QueryException,
            match="No dataset found matching the given name",
        ):
            GetDatasetByNameQuery.run_graphql_query(gql_client, spaceId="space_123", datasetName="Nonexistent")

    def test_missing_datasets_structure(self, gql_client):
        mock_response = {"node": {}}
        gql_client.execute.return_value = mock_response

        with pytest.raises(GetDatasetByNameQuery.QueryException, match="No datasets found"):
            GetDatasetByNameQuery.run_graphql_query(gql_client, spaceId="space_123", datasetName="Test")

    def test_variables_validation(self):
        with pytest.raises(Exception) as exc_info:
            GetDatasetByNameQuery.Variables(datasetName="Test")
        assert "spaceId" in str(exc_info.value)

        with pytest.raises(Exception) as exc_info:
            GetDatasetByNameQuery.Variables(spaceId="space_123")
        assert "datasetName" in str(exc_info.value)

        variables = GetDatasetByNameQuery.Variables(spaceId="space_123", datasetName="Test")
        assert variables.spaceId == "space_123"
        assert variables.datasetName == "Test"


class TestGetDatasetExamplesQuery:
    """Test the GetDatasetExamplesQuery class."""

    def test_query_structure(self):
        query = GetDatasetExamplesQuery.graphql_query
        assert "query getDatasetExamples" in query
        assert "$datasetId: ID!" in query
        assert "latestDatasetVersion" in query
        assert "CategoricalDimensionValue" in query
        assert "NumericDimensionValue" in query
        assert "sv: value" in query
        assert "nv: value" in query

    def test_successful_query(self, gql_client):
        """Test with realistic data matching actual API response format."""
        mock_response = {
            "node": {
                "latestDatasetVersion": {
                    "examples": {
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                        "edges": [
                            {
                                "node": {
                                    "id": "010896ae-fd1d-403a-89d8-49d0f5d97d28",
                                    "createdAt": "2026-01-13T23:37:29.369Z",
                                    "updatedAt": "2026-01-13T23:37:29.369Z",
                                    "columns": [
                                        {
                                            "dimension": {"name": "text"},
                                            "dimensionValue": {"sv": "What is AI?"},
                                        },
                                        {
                                            "dimension": {"name": "timestamp"},
                                            "dimensionValue": {"sv": "2025-07-09T13:37:54"},
                                        },
                                    ],
                                }
                            },
                            {
                                "node": {
                                    "id": "01a41108-0291-4595-974e-ee147fdaa534",
                                    "createdAt": "2026-01-13T23:37:29.369Z",
                                    "updatedAt": "2026-01-13T23:37:29.369Z",
                                    "columns": [
                                        {
                                            "dimension": {"name": "text"},
                                            "dimensionValue": {"sv": "Hello world"},
                                        },
                                        {
                                            "dimension": {"name": "timestamp"},
                                            "dimensionValue": {"sv": "2025-07-02T16:33:41"},
                                        },
                                    ],
                                }
                            },
                        ],
                    }
                }
            }
        }
        gql_client.execute.return_value = mock_response

        results = GetDatasetExamplesQuery.run_graphql_query_to_list(gql_client, datasetId="dataset_123")

        assert len(results) == 2
        assert results[0].id == "010896ae-fd1d-403a-89d8-49d0f5d97d28"
        assert results[0].data == {"text": "What is AI?", "timestamp": "2025-07-09T13:37:54"}
        assert results[1].id == "01a41108-0291-4595-974e-ee147fdaa534"
        assert results[1].data == {"text": "Hello world", "timestamp": "2025-07-02T16:33:41"}

    def test_mixed_value_types(self, gql_client):
        """Test parsing different dimension value types (string, numeric, list)."""
        mock_response = {
            "node": {
                "latestDatasetVersion": {
                    "examples": {
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                        "edges": [
                            {
                                "node": {
                                    "id": "ex_mixed",
                                    "createdAt": "2026-01-01T00:00:00Z",
                                    "updatedAt": "2026-01-01T00:00:00Z",
                                    "columns": [
                                        {
                                            "dimension": {"name": "text"},
                                            "dimensionValue": {"sv": "sample text"},
                                        },
                                        {
                                            "dimension": {"name": "score"},
                                            "dimensionValue": {"nv": 0.95},
                                        },
                                        {
                                            "dimension": {"name": "tags"},
                                            "dimensionValue": {"lv": ["tag1", "tag2"]},
                                        },
                                        {
                                            "dimension": {"name": "empty_col"},
                                            "dimensionValue": None,
                                        },
                                    ],
                                }
                            }
                        ],
                    }
                }
            }
        }
        gql_client.execute.return_value = mock_response

        results = GetDatasetExamplesQuery.run_graphql_query_to_list(gql_client, datasetId="dataset_123")

        assert len(results) == 1
        assert results[0].data == {
            "text": "sample text",
            "score": 0.95,
            "tags": ["tag1", "tag2"],
            "empty_col": None,
        }

    def test_pagination(self, gql_client):
        page1 = {
            "node": {
                "latestDatasetVersion": {
                    "examples": {
                        "pageInfo": {"hasNextPage": True, "endCursor": "cursor1"},
                        "edges": [
                            {
                                "node": {
                                    "id": "row-001",
                                    "createdAt": "2026-01-01T00:00:00Z",
                                    "updatedAt": "2026-01-01T00:00:00Z",
                                    "columns": [
                                        {"dimension": {"name": "text"}, "dimensionValue": {"sv": "first row"}},
                                    ],
                                }
                            }
                        ],
                    }
                }
            }
        }
        page2 = {
            "node": {
                "latestDatasetVersion": {
                    "examples": {
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                        "edges": [
                            {
                                "node": {
                                    "id": "row-002",
                                    "createdAt": "2026-01-02T00:00:00Z",
                                    "updatedAt": "2026-01-02T00:00:00Z",
                                    "columns": [
                                        {"dimension": {"name": "text"}, "dimensionValue": {"sv": "second row"}},
                                    ],
                                }
                            }
                        ],
                    }
                }
            }
        }
        gql_client.execute.side_effect = [page1, page2]

        results = GetDatasetExamplesQuery.iterate_over_pages(gql_client, datasetId="dataset_123")

        assert len(results) == 2
        assert results[0].id == "row-001"
        assert results[0].data == {"text": "first row"}
        assert results[1].id == "row-002"
        assert results[1].data == {"text": "second row"}
        assert gql_client.execute.call_count == 2

    def test_no_version_found(self, gql_client):
        mock_response = {"node": {"latestDatasetVersion": None}}
        gql_client.execute.return_value = mock_response

        with pytest.raises(GetDatasetExamplesQuery.QueryException, match="No dataset version found"):
            GetDatasetExamplesQuery.run_graphql_query_to_list(gql_client, datasetId="dataset_123")

    def test_dataset_not_found(self, gql_client):
        mock_response = {"node": None}
        gql_client.execute.return_value = mock_response

        with pytest.raises(GetDatasetExamplesQuery.QueryException, match="Dataset not found"):
            GetDatasetExamplesQuery.run_graphql_query_to_list(gql_client, datasetId="nonexistent")

    def test_variables_validation(self):
        variables = GetDatasetExamplesQuery.Variables(datasetId="dataset_123")
        assert variables.datasetId == "dataset_123"
        assert variables.first == 50

        variables = GetDatasetExamplesQuery.Variables(datasetId="dataset_123", first=100)
        assert variables.first == 100
