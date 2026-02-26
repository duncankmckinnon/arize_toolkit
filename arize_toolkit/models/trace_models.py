from datetime import datetime
from typing import List, Optional, Union

from pydantic import Field

from arize_toolkit.types import ComparisonOperator, DimensionCategory, DimensionDataType, FilterRowType, ModelEnvironment, SortDirection, SpanKind, SpanSortColumn, SpanStatusCode
from arize_toolkit.utils import GraphQLModel

# ── GraphQL Input Models ─────────────────────────────────────────────


class DimensionInput(GraphQLModel):
    """A dimension used in filter definitions.

    Matches GraphQL ``DimensionInput`` input type.
    """

    id: str = Field(description="Dimension identifier (e.g. 'context.trace_id')")
    name: str = Field(description="Dimension label (e.g. 'context.trace_id')")
    dataType: DimensionDataType = Field(description="Data type of dimension values")
    category: Optional[DimensionCategory] = Field(default=None, description="Dimension category (e.g. spanProperty)")


class DimensionValueInput(GraphQLModel):
    """A value used in filter definitions.

    Matches GraphQL ``DimensionValueInput`` input type.
    """

    id: str = Field(description="Value identifier")
    value: str = Field(description="The dimension value string")


class FilterItemInput(GraphQLModel):
    """A single filter item applied to a dataset query.

    Matches GraphQL ``FilterItemInputType`` input type.
    """

    filterType: FilterRowType = Field(description="Type of filter (e.g. spanProperty)")
    operator: ComparisonOperator = Field(description="Comparison operator (e.g. equals)")
    dimension: Optional[DimensionInput] = Field(default=None, description="Dimension to filter on")
    dimensionValues: Optional[List[DimensionValueInput]] = Field(default=None, description="Values to match against")


class SpanSortInput(GraphQLModel):
    """Sort specification for span queries.

    Matches GraphQL ``SpanSort`` input type.
    """

    column: SpanSortColumn = Field(description="Column to sort by")
    dir: SortDirection = Field(description="Sort direction (ASC or DESC)")


class ModelDatasetInput(GraphQLModel):
    """Dataset filter specifying time window, environment, and optional filters.

    Matches GraphQL ``ModelDatasetInput`` input type.
    """

    startTime: datetime = Field(description="Start of time window")
    endTime: datetime = Field(description="End of time window")
    environmentName: ModelEnvironment = Field(description="Environment name (e.g. tracing)")
    externalModelVersionIds: List[str] = Field(
        default_factory=list,
        description="Model version IDs to filter by (empty = all)",
    )
    externalBatchIds: List[str] = Field(
        default_factory=list,
        description="Batch IDs to filter by (empty = all)",
    )
    filters: Optional[List[FilterItemInput]] = Field(default=None, description="Filters to narrow the dataset")


# ── Response Models ──────────────────────────────────────────────────


class SpanColumnValue(GraphQLModel):
    """Union type for span column values — either categorical (string) or numeric.

    Matches GraphQL union of ``CategoricalDimensionValue`` and ``NumericDimensionValue``.
    """

    typename: Optional[str] = Field(default=None, alias="__typename")
    stringValue: Optional[str] = Field(default=None)
    numericValue: Optional[float] = Field(default=None)

    @property
    def resolved_value(self) -> Optional[Union[str, float]]:
        """Return the actual value based on the GraphQL union type."""
        if self.typename == "CategoricalDimensionValue":
            return self.stringValue
        elif self.typename == "NumericDimensionValue":
            return self.numericValue
        return self.stringValue if self.stringValue is not None else self.numericValue


class SpanColumn(GraphQLModel):
    """A named column attached to a span record."""

    name: str = Field(description="Column name (e.g. 'attributes.input.value')")
    value: Optional[SpanColumnValue] = Field(default=None, description="Column value")


class SpanRecord(GraphQLModel):
    """A single span record from the ``spanRecordsPublic`` API."""

    name: Optional[str] = Field(default=None, description="Span name")
    spanKind: Optional[SpanKind] = Field(default=None, description="Span kind")
    statusCode: Optional[SpanStatusCode] = Field(default=None, description="Status code")
    startTime: Optional[datetime] = Field(default=None, description="Span start time")
    parentId: Optional[str] = Field(default=None, description="Parent span ID")
    latencyMs: Optional[float] = Field(default=None, description="Latency in milliseconds")
    traceId: Optional[str] = Field(default=None, description="Trace ID")
    spanId: Optional[str] = Field(default=None, description="Span ID")
    attributes: Optional[str] = Field(default=None, description="All span attributes as a JSON string")
    columns: Optional[List[SpanColumn]] = Field(default=None, description="Requested column values")
