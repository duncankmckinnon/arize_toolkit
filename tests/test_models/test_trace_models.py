from arize_toolkit.models.trace_models import (
    DimensionInput,
    DimensionValueInput,
    FilterItemInput,
    ModelDatasetInput,
    SpanColumn,
    SpanColumnValue,
    SpanPropertyDimension,
    SpanPropertyEntry,
    SpanRecord,
    SpanSortInput,
    TotalCost,
    TraceTokenCounts,
)


class TestSpanColumnValue:
    def test_categorical_value(self):
        val = SpanColumnValue(**{"__typename": "CategoricalDimensionValue", "stringValue": "hello"})
        assert val.resolved_value == "hello"

    def test_numeric_value(self):
        val = SpanColumnValue(**{"__typename": "NumericDimensionValue", "numericValue": 42.0})
        assert val.resolved_value == 42.0

    def test_none_value(self):
        val = SpanColumnValue()
        assert val.resolved_value is None

    def test_fallback_string(self):
        val = SpanColumnValue(stringValue="fallback")
        assert val.resolved_value == "fallback"

    def test_fallback_numeric(self):
        val = SpanColumnValue(numericValue=3.14)
        assert val.resolved_value == 3.14

    def test_to_dict(self):
        val = SpanColumnValue(**{"__typename": "CategoricalDimensionValue", "stringValue": "test"})
        d = val.to_dict(exclude_none=True)
        assert d["stringValue"] == "test"


class TestSpanColumn:
    def test_basic(self):
        col = SpanColumn(name="attributes.input.value")
        assert col.name == "attributes.input.value"
        assert col.value is None

    def test_with_value(self):
        col = SpanColumn(
            name="attributes.input.value",
            value={
                "__typename": "CategoricalDimensionValue",
                "stringValue": "hello world",
            },
        )
        assert col.value.resolved_value == "hello world"


class TestSpanRecord:
    def test_basic(self):
        span = SpanRecord(
            name="LLMChain",
            spanKind="LLM",
            statusCode="OK",
            startTime="2025-01-01T00:00:00Z",
            latencyMs=150.5,
            traceId="trace-123",
            spanId="span-456",
        )
        assert span.name == "LLMChain"
        assert span.spanKind.name == "LLM"
        assert span.statusCode.name == "OK"
        assert span.latencyMs == 150.5
        assert span.traceId == "trace-123"

    def test_with_columns(self):
        span = SpanRecord(
            name="test",
            traceId="t1",
            spanId="s1",
            columns=[
                {
                    "name": "attributes.input.value",
                    "value": {
                        "__typename": "CategoricalDimensionValue",
                        "stringValue": "hello",
                    },
                },
                {
                    "name": "attributes.output.value",
                    "value": {
                        "__typename": "CategoricalDimensionValue",
                        "stringValue": "world",
                    },
                },
            ],
        )
        assert len(span.columns) == 2
        assert span.columns[0].name == "attributes.input.value"
        assert span.columns[0].value.resolved_value == "hello"

    def test_with_attributes(self):
        attrs_json = '{"input.value": "hello", "llm.model_name": "gpt-4", "llm.token_count.total": 100}'
        span = SpanRecord(
            name="LLM",
            traceId="t1",
            spanId="s1",
            attributes=attrs_json,
        )
        assert span.attributes == attrs_json
        import json

        attrs = json.loads(span.attributes)
        assert attrs["input.value"] == "hello"
        assert attrs["llm.model_name"] == "gpt-4"
        assert attrs["llm.token_count.total"] == 100

    def test_optional_fields(self):
        span = SpanRecord()
        assert span.name is None
        assert span.spanKind is None
        assert span.columns is None
        assert span.attributes is None

    def test_to_dict(self):
        span = SpanRecord(name="test", traceId="t1", spanId="s1", attributes='{"key": "val"}')
        d = span.to_dict()
        assert d["name"] == "test"
        assert d["traceId"] == "t1"
        assert d["attributes"] == '{"key": "val"}'

    def test_with_trace_token_counts(self):
        span = SpanRecord(
            name="LLM",
            traceId="t1",
            spanId="s1",
            traceTokenCounts={
                "aggregatePromptTokenCount": 100.0,
                "aggregateCompletionTokenCount": 50.0,
                "aggregateTotalTokenCount": 150.0,
            },
        )
        assert span.traceTokenCounts is not None
        assert span.traceTokenCounts.aggregatePromptTokenCount == 100.0
        assert span.traceTokenCounts.aggregateCompletionTokenCount == 50.0
        assert span.traceTokenCounts.aggregateTotalTokenCount == 150.0

    def test_with_total_cost(self):
        span = SpanRecord(
            name="LLM",
            traceId="t1",
            spanId="s1",
            totalCost={
                "aggregateTotalCost": 0.05,
                "aggregatePromptCost": 0.03,
                "aggregateCompletionCost": 0.02,
            },
        )
        assert span.totalCost is not None
        assert span.totalCost.aggregateTotalCost == 0.05


class TestTraceTokenCounts:
    def test_basic(self):
        counts = TraceTokenCounts(
            aggregatePromptTokenCount=100.0,
            aggregateCompletionTokenCount=50.0,
            aggregateTotalTokenCount=150.0,
        )
        assert counts.aggregatePromptTokenCount == 100.0
        assert counts.aggregateTotalTokenCount == 150.0

    def test_optional_fields(self):
        counts = TraceTokenCounts()
        assert counts.aggregatePromptTokenCount is None
        assert counts.aggregateCompletionTokenCount is None
        assert counts.aggregateTotalTokenCount is None


class TestTotalCost:
    def test_basic(self):
        cost = TotalCost(
            aggregateTotalCost=0.05,
            aggregatePromptCost=0.03,
            aggregateCompletionCost=0.02,
        )
        assert cost.aggregateTotalCost == 0.05

    def test_optional_fields(self):
        cost = TotalCost()
        assert cost.aggregateTotalCost is None


class TestSpanPropertyEntry:
    def test_basic(self):
        entry = SpanPropertyEntry(
            dimension={
                "name": "attributes.input.value",
                "dataType": "STRING",
                "category": "spanProperty",
            }
        )
        assert entry.dimension.name == "attributes.input.value"
        assert entry.dimension.dataType == "STRING"
        assert entry.dimension.category == "spanProperty"

    def test_dimension_without_category(self):
        dim = SpanPropertyDimension(name="attributes.output.value", dataType="STRING")
        assert dim.category is None


class TestDimensionInput:
    def test_basic(self):
        dim = DimensionInput(
            id="context.trace_id",
            name="context.trace_id",
            dataType="STRING",
            category="spanProperty",
        )
        assert dim.id == "context.trace_id"
        assert dim.dataType.name == "STRING"
        assert dim.category.name == "spanProperty"

    def test_without_category(self):
        dim = DimensionInput(
            id="context.trace_id",
            name="context.trace_id",
            dataType="STRING",
        )
        assert dim.category is None


class TestDimensionValueInput:
    def test_basic(self):
        val = DimensionValueInput(id="trace-123", value="trace-123")
        assert val.id == "trace-123"
        assert val.value == "trace-123"


class TestFilterItemInput:
    def test_basic(self):
        f = FilterItemInput(
            filterType="spanProperty",
            operator="equals",
            dimension={
                "id": "context.trace_id",
                "name": "context.trace_id",
                "dataType": "STRING",
                "category": "spanProperty",
            },
            dimensionValues=[{"id": "t1", "value": "t1"}],
        )
        assert f.filterType.name == "spanProperty"
        assert f.operator.name == "equals"
        assert f.dimension.id == "context.trace_id"
        assert len(f.dimensionValues) == 1

    def test_to_dict(self):
        f = FilterItemInput(
            filterType="spanProperty",
            operator="equals",
        )
        d = f.to_dict()
        assert d["filterType"] == "spanProperty"
        assert d["operator"] == "equals"


class TestSpanSortInput:
    def test_basic(self):
        sort = SpanSortInput(column="start_time", dir="DESC")
        assert sort.column.name == "start_time"
        assert sort.dir.name == "DESC"

    def test_to_dict(self):
        sort = SpanSortInput(column="start_time", dir="ASC")
        d = sort.to_dict()
        assert d["column"] == "start_time"
        assert d["dir"] == "ASC"


class TestModelDatasetInput:
    def test_basic(self):
        ds = ModelDatasetInput(
            startTime="2025-01-01T00:00:00Z",
            endTime="2025-01-02T00:00:00Z",
            environmentName="tracing",
        )
        assert ds.environmentName.name == "tracing"
        assert ds.externalModelVersionIds == []
        assert ds.externalBatchIds == []
        assert ds.filters is None

    def test_with_filters(self):
        ds = ModelDatasetInput(
            startTime="2025-01-01T00:00:00Z",
            endTime="2025-01-02T00:00:00Z",
            environmentName="tracing",
            filters=[
                {
                    "filterType": "spanProperty",
                    "operator": "equals",
                    "dimension": {
                        "id": "context.trace_id",
                        "name": "context.trace_id",
                        "dataType": "STRING",
                        "category": "spanProperty",
                    },
                    "dimensionValues": [{"id": "t1", "value": "t1"}],
                }
            ],
        )
        assert len(ds.filters) == 1
        assert ds.filters[0].filterType.name == "spanProperty"

    def test_to_dict(self):
        ds = ModelDatasetInput(
            startTime="2025-01-01T00:00:00Z",
            endTime="2025-01-02T00:00:00Z",
            environmentName="tracing",
        )
        d = ds.to_dict()
        assert d["environmentName"] == "tracing"
        assert d["externalModelVersionIds"] == []
        assert d["externalBatchIds"] == []
        assert "startTime" in d
        assert "endTime" in d
