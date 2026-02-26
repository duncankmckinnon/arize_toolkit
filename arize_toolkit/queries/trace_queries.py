from typing import List, Optional, Tuple

from pydantic import Field

from arize_toolkit.exceptions import ArizeAPIException
from arize_toolkit.models.trace_models import ModelDatasetInput, SpanRecord, SpanSortInput
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
        $columnNames: [String!]!
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
                    includeRootSpans: true
                ) {
                    pageInfo { hasNextPage endCursor }
                    edges {
                        span: node {
                            name spanKind statusCode startTime
                            parentId latencyMs traceId spanId
                            attributes
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
        $includeRootSpans: Boolean!
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
                    includeRootSpans: $includeRootSpans
                ) {
                    pageInfo { hasNextPage endCursor }
                    edges {
                        span: node {
                            name spanKind statusCode startTime
                            parentId latencyMs traceId spanId
                            attributes
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
