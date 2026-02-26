import pytest

from arize_toolkit.queries.trace_queries import GetSpanColumnsQuery, GetTraceDetailQuery, ListTracesQuery

DATASET = {
    "startTime": "2025-01-01T00:00:00Z",
    "endTime": "2025-01-02T00:00:00Z",
    "environmentName": "tracing",
}
SORT = {"column": "start_time", "dir": "DESC"}


class TestListTracesQuery:
    def test_success(self, gql_client):
        mock_response = {
            "node": {
                "__typename": "Model",
                "id": "model-123",
                "spans": {
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                    "edges": [
                        {
                            "span": {
                                "name": "LLMChain",
                                "spanKind": "LLM",
                                "statusCode": "OK",
                                "startTime": "2025-01-01T00:00:00Z",
                                "parentId": None,
                                "latencyMs": 150.5,
                                "traceId": "trace-1",
                                "spanId": "span-1",
                                "attributes": '{"openinference.span.kind": "LLM", "input.value": "hello"}',
                                "traceTokenCounts": {
                                    "aggregatePromptTokenCount": 100.0,
                                    "aggregateCompletionTokenCount": 50.0,
                                    "aggregateTotalTokenCount": 150.0,
                                },
                                "columns": [
                                    {
                                        "name": "attributes.input.value",
                                        "value": {
                                            "__typename": "CategoricalDimensionValue",
                                            "stringValue": "hello",
                                        },
                                    },
                                ],
                            }
                        },
                        {
                            "span": {
                                "name": "Retriever",
                                "spanKind": "RETRIEVER",
                                "statusCode": "OK",
                                "startTime": "2025-01-01T00:00:01Z",
                                "parentId": None,
                                "latencyMs": 50.0,
                                "traceId": "trace-2",
                                "spanId": "span-2",
                                "attributes": '{"openinference.span.kind": "RETRIEVER"}',
                                "traceTokenCounts": None,
                                "columns": [],
                            }
                        },
                    ],
                },
            }
        }
        gql_client.execute.return_value = mock_response

        result = ListTracesQuery.iterate_over_pages(
            gql_client,
            id="model-123",
            dataset=DATASET,
            sort=SORT,
            count=20,
            columnNames=[],
        )
        assert len(result) == 2
        assert result[0].traceId == "trace-1"
        assert result[0].spanKind.name == "LLM"
        assert result[0].latencyMs == 150.5
        assert result[0].attributes is not None
        assert '"input.value": "hello"' in result[0].attributes
        assert result[0].traceTokenCounts is not None
        assert result[0].traceTokenCounts.aggregateTotalTokenCount == 150.0
        assert len(result[0].columns) == 1
        assert result[0].columns[0].name == "attributes.input.value"
        assert result[1].traceId == "trace-2"
        assert result[1].spanKind.name == "RETRIEVER"
        assert result[1].attributes is not None
        assert result[1].traceTokenCounts is None

    def test_pagination(self, gql_client):
        page1 = {
            "node": {
                "__typename": "Model",
                "id": "m1",
                "spans": {
                    "pageInfo": {"hasNextPage": True, "endCursor": "cursor1"},
                    "edges": [
                        {
                            "span": {
                                "name": "s1",
                                "traceId": "t1",
                                "spanId": "s1",
                                "spanKind": "LLM",
                                "statusCode": "OK",
                                "startTime": "2025-01-01T00:00:00Z",
                                "parentId": None,
                                "latencyMs": 100.0,
                                "attributes": "{}",
                            }
                        }
                    ],
                },
            }
        }
        page2 = {
            "node": {
                "__typename": "Model",
                "id": "m1",
                "spans": {
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                    "edges": [
                        {
                            "span": {
                                "name": "s2",
                                "traceId": "t2",
                                "spanId": "s2",
                                "spanKind": "CHAIN",
                                "statusCode": "OK",
                                "startTime": "2025-01-01T00:00:01Z",
                                "parentId": None,
                                "latencyMs": 200.0,
                                "attributes": "{}",
                            }
                        }
                    ],
                },
            }
        }
        gql_client.execute.side_effect = [page1, page2]

        result = ListTracesQuery.iterate_over_pages(
            gql_client,
            id="m1",
            dataset=DATASET,
            sort=SORT,
            count=1,
            columnNames=[],
        )
        assert len(result) == 2
        assert result[0].traceId == "t1"
        assert result[1].traceId == "t2"

    def test_empty_edges(self, gql_client):
        gql_client.execute.return_value = {
            "node": {
                "__typename": "Model",
                "id": "m1",
                "spans": {
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                    "edges": [],
                },
            }
        }

        result = ListTracesQuery.iterate_over_pages(
            gql_client,
            id="m1",
            dataset=DATASET,
            sort=SORT,
            count=20,
            columnNames=[],
        )
        assert len(result) == 0

    def test_no_spans_raises(self, gql_client):
        gql_client.execute.return_value = {"node": {"__typename": "Model", "id": "m1"}}

        with pytest.raises(ListTracesQuery.QueryException, match="No spans found"):
            ListTracesQuery._graphql_query(
                gql_client,
                id="m1",
                dataset=DATASET,
                sort=SORT,
                count=20,
                columnNames=[],
            )


class TestGetTraceDetailQuery:
    def test_success_with_columns(self, gql_client):
        mock_response = {
            "node": {
                "__typename": "Model",
                "id": "m1",
                "spans": {
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                    "edges": [
                        {
                            "span": {
                                "name": "LLMChain",
                                "spanKind": "LLM",
                                "statusCode": "OK",
                                "startTime": "2025-01-01T00:00:00Z",
                                "parentId": None,
                                "latencyMs": 150.5,
                                "traceId": "trace-1",
                                "spanId": "span-1",
                                "attributes": '{"input.value": "hello world", "output.value": "response text", "llm.model_name": "gpt-4"}',
                                "columns": [
                                    {
                                        "name": "attributes.input.value",
                                        "value": {
                                            "__typename": "CategoricalDimensionValue",
                                            "stringValue": "hello world",
                                        },
                                    },
                                    {
                                        "name": "attributes.output.value",
                                        "value": {
                                            "__typename": "CategoricalDimensionValue",
                                            "stringValue": "response text",
                                        },
                                    },
                                ],
                            }
                        }
                    ],
                },
            }
        }
        gql_client.execute.return_value = mock_response

        dataset_with_filter = {
            **DATASET,
            "filters": [
                {
                    "filterType": "spanProperty",
                    "operator": "equals",
                    "dimension": {
                        "id": "context.trace_id",
                        "name": "context.trace_id",
                        "dataType": "STRING",
                        "category": "spanProperty",
                    },
                    "dimensionValues": [{"id": "trace-1", "value": "trace-1"}],
                }
            ],
        }

        result = GetTraceDetailQuery.iterate_over_pages(
            gql_client,
            id="m1",
            dataset=dataset_with_filter,
            sort={"column": "start_time", "dir": "ASC"},
            count=20,
            columnNames=["attributes.input.value", "attributes.output.value"],
            includeRootSpans=True,
        )
        assert len(result) == 1
        assert result[0].traceId == "trace-1"
        assert result[0].attributes is not None
        import json

        attrs = json.loads(result[0].attributes)
        assert attrs["input.value"] == "hello world"
        assert attrs["llm.model_name"] == "gpt-4"
        assert len(result[0].columns) == 2
        assert result[0].columns[0].name == "attributes.input.value"
        assert result[0].columns[0].value.resolved_value == "hello world"

    def test_no_spans_raises(self, gql_client):
        gql_client.execute.return_value = {"node": {"__typename": "Model", "id": "m1"}}

        with pytest.raises(GetTraceDetailQuery.QueryException, match="No spans found"):
            GetTraceDetailQuery._graphql_query(
                gql_client,
                id="m1",
                dataset=DATASET,
                sort=SORT,
                count=20,
                columnNames=[],
                includeRootSpans=True,
            )

    def test_numeric_column_value(self, gql_client):
        mock_response = {
            "node": {
                "__typename": "Model",
                "id": "m1",
                "spans": {
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                    "edges": [
                        {
                            "span": {
                                "name": "LLM",
                                "spanKind": "LLM",
                                "statusCode": "OK",
                                "startTime": "2025-01-01T00:00:00Z",
                                "parentId": None,
                                "latencyMs": 100.0,
                                "traceId": "t1",
                                "spanId": "s1",
                                "attributes": '{"llm.token_count.total": 1500}',
                                "columns": [
                                    {
                                        "name": "attributes.llm.token_count.total",
                                        "value": {
                                            "__typename": "NumericDimensionValue",
                                            "numericValue": 1500.0,
                                        },
                                    }
                                ],
                            }
                        }
                    ],
                },
            }
        }
        gql_client.execute.return_value = mock_response

        result = GetTraceDetailQuery.iterate_over_pages(
            gql_client,
            id="m1",
            dataset=DATASET,
            sort=SORT,
            count=20,
            columnNames=["attributes.llm.token_count.total"],
            includeRootSpans=True,
        )
        assert result[0].columns[0].value.resolved_value == 1500.0


class TestGetSpanColumnsQuery:
    def test_success(self, gql_client):
        mock_response = {
            "node": {
                "__typename": "Model",
                "id": "model-123",
                "tracingSchema": {
                    "spanProperties": {
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                        "edges": [
                            {
                                "node": {
                                    "dimension": {
                                        "name": "attributes.input.value",
                                        "dataType": "STRING",
                                        "category": "spanProperty",
                                    }
                                }
                            },
                            {
                                "node": {
                                    "dimension": {
                                        "name": "attributes.output.value",
                                        "dataType": "STRING",
                                        "category": "spanProperty",
                                    }
                                }
                            },
                        ],
                    }
                },
            }
        }
        gql_client.execute.return_value = mock_response

        result = GetSpanColumnsQuery.iterate_over_pages(
            gql_client,
            id="model-123",
            startTime="2025-01-01T00:00:00.000000Z",
            endTime="2025-01-08T00:00:00.000000Z",
            count=20,
        )
        assert len(result) == 2
        assert result[0].dimension.name == "attributes.input.value"
        assert result[0].dimension.dataType == "STRING"
        assert result[1].dimension.name == "attributes.output.value"

    def test_pagination(self, gql_client):
        page1 = {
            "node": {
                "__typename": "Model",
                "id": "m1",
                "tracingSchema": {
                    "spanProperties": {
                        "pageInfo": {"hasNextPage": True, "endCursor": "cursor1"},
                        "edges": [
                            {
                                "node": {
                                    "dimension": {
                                        "name": "attributes.input.value",
                                        "dataType": "STRING",
                                        "category": "spanProperty",
                                    }
                                }
                            },
                        ],
                    }
                },
            }
        }
        page2 = {
            "node": {
                "__typename": "Model",
                "id": "m1",
                "tracingSchema": {
                    "spanProperties": {
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                        "edges": [
                            {
                                "node": {
                                    "dimension": {
                                        "name": "attributes.output.value",
                                        "dataType": "STRING",
                                        "category": "spanProperty",
                                    }
                                }
                            },
                        ],
                    }
                },
            }
        }
        gql_client.execute.side_effect = [page1, page2]

        result = GetSpanColumnsQuery.iterate_over_pages(
            gql_client,
            id="m1",
            startTime="2025-01-01T00:00:00.000000Z",
            endTime="2025-01-08T00:00:00.000000Z",
            count=1,
        )
        assert len(result) == 2
        assert result[0].dimension.name == "attributes.input.value"
        assert result[1].dimension.name == "attributes.output.value"

    def test_empty(self, gql_client):
        mock_response = {
            "node": {
                "__typename": "Model",
                "id": "m1",
                "tracingSchema": {
                    "spanProperties": {
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                        "edges": [],
                    }
                },
            }
        }
        gql_client.execute.return_value = mock_response

        result = GetSpanColumnsQuery.iterate_over_pages(
            gql_client,
            id="m1",
            startTime="2025-01-01T00:00:00.000000Z",
            endTime="2025-01-08T00:00:00.000000Z",
            count=20,
        )
        assert len(result) == 0

    def test_no_tracing_schema(self, gql_client):
        mock_response = {
            "node": {
                "__typename": "Model",
                "id": "m1",
            }
        }
        gql_client.execute.return_value = mock_response

        result = GetSpanColumnsQuery.iterate_over_pages(
            gql_client,
            id="m1",
            startTime="2025-01-01T00:00:00.000000Z",
            endTime="2025-01-08T00:00:00.000000Z",
            count=20,
        )
        assert len(result) == 0
