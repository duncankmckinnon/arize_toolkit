from datetime import datetime
from typing import List, Optional, Tuple

from pydantic import Field

from arize_toolkit.exceptions import ArizeAPIException
from arize_toolkit.models.trace_models import ModelDatasetInput, SpanPropertyEntry, SpanRecord, SpanSortInput
from arize_toolkit.queries.basequery import BaseQuery, BaseResponse, BaseVariables


class ListTracesQuery(BaseQuery):
    """List root spans (one per trace) in a time window for a model."""

    graphql_query = """
    query ListTraces(
        $id: ID!,
        $dataset: ModelDatasetInput!,
        $sort: SpanSort!,
        $count: Int!,
        $endCursor: String,
        $columnNames: [String!]!,
        $truncateStringLength: Int
    ) {
        node(id: $id) {
            __typename
            ... on Model {
                spans: spanRecordsPublic(
                    first: $count,
                    after: $endCursor,
                    dataset: $dataset,
                    sort: $sort,
                    columnNames: $columnNames,
                    includeRootSpans: true,
                    truncateStringLength: $truncateStringLength
                ) {
                    pageInfo { hasNextPage endCursor }
                    edges {
                        span: node {
                            name spanKind statusCode startTime
                            parentId latencyMs traceId spanId
                            attributes
                            traceTokenCounts {
                                aggregateCompletionTokenCount
                                aggregatePromptTokenCount
                                aggregateTotalTokenCount
                            }
                            columns {
                                name
                                value {
                                    __typename
                                    ... on CategoricalDimensionValue {
                                        stringValue: value
                                    }
                                    ... on NumericDimensionValue {
                                        numericValue: value
                                    }
                                }
                            }
                        }
                    }
                }
            }
            id
        }
    }
    """
    query_description = "List root spans (traces) in a time window"

    class Variables(BaseVariables):
        id: str = Field(description="Model ID (base64-encoded)")
        dataset: ModelDatasetInput = Field(description="Dataset filter with time window and environment")
        sort: SpanSortInput = Field(description="Sort specification")
        count: int = Field(default=20, description="Number of results per page (max ~50)")
        columnNames: List[str] = Field(default_factory=list, description="Column names to include")
        truncateStringLength: Optional[int] = Field(default=5000, description="Max string length for column values")

    class QueryException(ArizeAPIException):
        message: str = "Error listing traces"

    class QueryResponse(SpanRecord):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        node = result.get("node")
        if not node or "spans" not in node:
            cls.raise_exception("No spans found for the given model")
        spans_data = node["spans"]
        page_info = spans_data["pageInfo"]
        has_next_page = page_info["hasNextPage"]
        end_cursor = page_info.get("endCursor")
        edges = spans_data.get("edges", [])
        span_list = [cls.QueryResponse(**edge["span"]) for edge in edges]
        return span_list, has_next_page, end_cursor


class GetTraceDetailQuery(BaseQuery):
    """Get all spans for a specific trace with input/output column data."""

    graphql_query = """
    query GetTrace(
        $id: ID!,
        $dataset: ModelDatasetInput!,
        $sort: SpanSort!,
        $count: Int!,
        $endCursor: String,
        $columnNames: [String!]!,
        $includeRootSpans: Boolean!,
        $truncateStringLength: Int
    ) {
        node(id: $id) {
            __typename
            ... on Model {
                spans: spanRecordsPublic(
                    first: $count,
                    after: $endCursor,
                    dataset: $dataset,
                    sort: $sort,
                    columnNames: $columnNames,
                    includeRootSpans: $includeRootSpans,
                    truncateStringLength: $truncateStringLength
                ) {
                    pageInfo { hasNextPage endCursor }
                    edges {
                        span: node {
                            name spanKind statusCode startTime
                            parentId latencyMs traceId spanId
                            attributes
                            traceTokenCounts {
                                aggregateCompletionTokenCount
                                aggregatePromptTokenCount
                                aggregateTotalTokenCount
                            }
                            columns {
                                name
                                value {
                                    __typename
                                    ... on CategoricalDimensionValue {
                                        stringValue: value
                                    }
                                    ... on NumericDimensionValue {
                                        numericValue: value
                                    }
                                }
                            }
                        }
                    }
                }
            }
            id
        }
    }
    """
    query_description = "Get all spans for a specific trace with column data"

    class Variables(BaseVariables):
        id: str = Field(description="Model ID (base64-encoded)")
        dataset: ModelDatasetInput = Field(description="Dataset filter with time window, environment, and trace filter")
        sort: SpanSortInput = Field(description="Sort specification")
        count: int = Field(default=20, description="Number of results per page")
        columnNames: List[str] = Field(default_factory=list, description="Column names to include")
        includeRootSpans: bool = Field(default=True, description="Whether to include root spans")
        truncateStringLength: Optional[int] = Field(default=5000, description="Max string length for column values")

    class QueryException(ArizeAPIException):
        message: str = "Error getting trace detail"

    class QueryResponse(SpanRecord):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        node = result.get("node")
        if not node or "spans" not in node:
            cls.raise_exception("No spans found for the given trace")
        spans_data = node["spans"]
        page_info = spans_data["pageInfo"]
        has_next_page = page_info["hasNextPage"]
        end_cursor = page_info.get("endCursor")
        edges = spans_data.get("edges", [])
        span_list = [cls.QueryResponse(**edge["span"]) for edge in edges]
        return span_list, has_next_page, end_cursor


class GetSpanColumnsQuery(BaseQuery):
    """Discover available span column names for a model via tracingSchema.spanProperties."""

    graphql_query = """
    query GetSpanColumns(
        $id: ID!,
        $startTime: DateTime!,
        $endTime: DateTime!,
        $count: Int!,
        $endCursor: String
    ) {
        node(id: $id) {
            __typename
            ... on Model {
                tracingSchema(startTime: $startTime, endTime: $endTime) {
                    spanProperties(first: $count, after: $endCursor) {
                        pageInfo { hasNextPage endCursor }
                        edges {
                            node {
                                dimension { name dataType category }
                            }
                        }
                    }
                }
            }
            id
        }
    }
    """
    query_description = "Get available span column names for a model"

    class Variables(BaseVariables):
        id: str = Field(description="Model ID (base64-encoded)")
        startTime: datetime = Field(description="Start of time window")
        endTime: datetime = Field(description="End of time window")
        count: int = Field(default=20, description="Number of results per page")

    class QueryException(ArizeAPIException):
        message: str = "Error getting span columns"

    class QueryResponse(SpanPropertyEntry):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        node = result.get("node")
        if not node:
            cls.raise_exception("Model not found")
        tracing_schema = node.get("tracingSchema")
        if not tracing_schema or "spanProperties" not in tracing_schema:
            return [], False, None
        span_props = tracing_schema["spanProperties"]
        page_info = span_props["pageInfo"]
        has_next_page = page_info["hasNextPage"]
        end_cursor = page_info.get("endCursor")
        edges = span_props.get("edges", [])
        entries = [cls.QueryResponse(**edge["node"]) for edge in edges]
        return entries, has_next_page, end_cursor
