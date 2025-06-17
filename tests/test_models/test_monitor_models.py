from datetime import datetime, timezone

from arize_toolkit.models import CustomMetric, Dimension, DimensionFilterInput, DynamicAutoThreshold, IntegrationKey, MetricFilterItem, MetricWindow, Monitor, MonitorContact, User
from arize_toolkit.types import ComparisonOperator, DataQualityMetric, DimensionCategory, DriftMetric, FilterRowType, ModelEnvironment, MonitorCategory, PerformanceMetric


class TestMonitorModels:
    def test_monitor_contact_input(self):
        """Test MonitorContactInput model."""
        from arize_toolkit.models import MonitorContactInput

        # Email contact
        email_contact = MonitorContactInput(notificationChannelType="email", emailAddress="user@example.com")

        assert email_contact.notificationChannelType == "email"
        assert email_contact.emailAddress == "user@example.com"
        assert email_contact.integrationKeyId is None

        # Integration contact
        integration_contact = MonitorContactInput(notificationChannelType="integration", integrationKeyId="key123")

        assert integration_contact.notificationChannelType == "integration"
        assert integration_contact.integrationKeyId == "key123"
        assert integration_contact.emailAddress is None

    def test_performance_monitor(self):
        """Test PerformanceMonitor model."""
        from arize_toolkit.models import PerformanceMonitor

        monitor = PerformanceMonitor(
            spaceId="space123",
            modelName="my-model",
            name="Accuracy Monitor",
            performanceMetric=PerformanceMetric.accuracy,
            operator=ComparisonOperator.lessThan,
            threshold=0.9,
            modelEnvironmentName=ModelEnvironment.production,
        )

        assert monitor.spaceId == "space123"
        assert monitor.modelName == "my-model"
        assert monitor.name == "Accuracy Monitor"
        assert monitor.performanceMetric == PerformanceMetric.accuracy
        assert monitor.operator == ComparisonOperator.lessThan
        assert monitor.threshold == 0.9
        assert monitor.modelEnvironmentName == ModelEnvironment.production

        # Check defaults
        assert monitor.evaluationWindowLengthSeconds == 259200
        assert monitor.delaySeconds == 0
        assert monitor.thresholdMode == "single"


class TestMonitorDetailedModels:
    def test_custom_metric(self):
        """Test CustomMetric model."""
        created_time = datetime(2024, 1, 1, tzinfo=timezone.utc)

        metric = CustomMetric(
            id="metric123",
            name="Custom F1",
            createdAt=created_time,
            description="Custom F1 score implementation",
            metric="(2 * precision * recall) / (precision + recall)",
            requiresPositiveClass=True,
        )

        assert metric.id == "metric123"
        assert metric.name == "Custom F1"
        assert metric.createdAt == created_time
        assert metric.description == "Custom F1 score implementation"
        assert metric.requiresPositiveClass is True

    def test_integration_key(self):
        """Test IntegrationKey model."""
        created_time = datetime(2024, 1, 1, tzinfo=timezone.utc)

        key = IntegrationKey(
            id="key123",
            name="Slack Integration",
            providerName="slack",
            createdAt=created_time,
            channelName="#alerts",
            alertSeverity="high",
        )

        assert key.id == "key123"
        assert key.name == "Slack Integration"
        assert key.providerName == "slack"
        assert key.channelName == "#alerts"
        assert key.alertSeverity == "high"

    def test_monitor_contact(self):
        """Test MonitorContact model."""
        # Email contact
        email_contact = MonitorContact(
            id="contact1",
            notificationChannelType="email",
            emailAddress="user@example.com",
        )

        assert email_contact.notificationChannelType == "email"
        assert email_contact.emailAddress == "user@example.com"

        # Integration contact
        integration = IntegrationKey(id="key123", name="PagerDuty", providerName="pagerduty")

        integration_contact = MonitorContact(
            id="contact2",
            notificationChannelType="integration",
            integration=integration,
        )

        assert integration_contact.notificationChannelType == "integration"
        assert integration_contact.integration.providerName == "pagerduty"

    def test_metric_window(self):
        """Test MetricWindow model."""
        dimension = Dimension(name="user_age")

        window = MetricWindow(
            id="window123",
            type="moving",
            windowLengthMs=86400000,  # 24 hours
            dimensionCategory=DimensionCategory.featureLabel,
            dimension=dimension,
        )

        assert window.id == "window123"
        assert window.type == "moving"
        assert window.windowLengthMs == 86400000
        assert window.dimensionCategory == DimensionCategory.featureLabel
        assert window.dimension.name == "user_age"

    def test_dynamic_auto_threshold(self):
        """Test DynamicAutoThreshold model."""
        threshold = DynamicAutoThreshold(stdDevMultiplier=3.0)
        assert threshold.stdDevMultiplier == 3.0

        # Test default
        threshold_default = DynamicAutoThreshold()
        assert threshold_default.stdDevMultiplier == 2.0

    def test_data_quality_monitor(self):
        """Test DataQualityMonitor model."""
        from arize_toolkit.models import DataQualityMonitor

        monitor = DataQualityMonitor(
            spaceId="space123",
            modelName="my-model",
            name="Missing Values Monitor",
            dataQualityMetric=DataQualityMetric.percentEmpty,
            dimensionCategory=DimensionCategory.featureLabel,
            dimensionName="user_age",
            operator=ComparisonOperator.greaterThan,
            threshold=0.1,
            modelEnvironmentName=ModelEnvironment.production,
        )

        assert monitor.spaceId == "space123"
        assert monitor.modelName == "my-model"
        assert monitor.name == "Missing Values Monitor"
        assert monitor.dataQualityMetric == DataQualityMetric.percentEmpty
        assert monitor.dimensionCategory == DimensionCategory.featureLabel
        assert monitor.dimensionName == "user_age"
        assert monitor.operator == ComparisonOperator.greaterThan
        assert monitor.threshold == 0.1

    def test_drift_monitor(self):
        """Test DriftMonitor model."""
        from arize_toolkit.models import DriftMonitor

        monitor = DriftMonitor(
            spaceId="space123",
            modelName="my-model",
            name="PSI Monitor",
            driftMetric=DriftMetric.psi,
            dimensionCategory=DimensionCategory.prediction,
            dimensionName="prediction_score",
            operator=ComparisonOperator.greaterThan,
            threshold=0.2,
        )

        assert monitor.spaceId == "space123"
        assert monitor.name == "PSI Monitor"
        assert monitor.driftMetric == DriftMetric.psi
        assert monitor.dimensionCategory == DimensionCategory.prediction
        assert monitor.dimensionName == "prediction_score"
        assert monitor.operator == ComparisonOperator.greaterThan
        assert monitor.threshold == 0.2

    def test_monitor_comprehensive(self):
        """Test Monitor model with comprehensive fields."""
        created_time = datetime(2024, 1, 1, tzinfo=timezone.utc)
        evaluated_time = datetime(2024, 1, 2, tzinfo=timezone.utc)

        user = User(id="user123", name="Test User")
        contact = MonitorContact(
            id="contact1",
            notificationChannelType="email",
            emailAddress="alert@example.com",
        )
        custom_metric = CustomMetric(
            id="metric123",
            name="Custom Metric",
            metric="custom_formula",
            requiresPositiveClass=False,
        )
        metric_window = MetricWindow(id="window123", type="moving", windowLengthMs=86400000)

        monitor = Monitor(
            id="monitor123",
            name="Performance Monitor",
            monitorCategory=MonitorCategory.performance,
            createdDate=created_time,
            evaluationIntervalSeconds=3600,
            evaluatedAt=evaluated_time,
            creator=user,
            notes="Monitor for tracking model performance",
            contacts=[contact],
            dimensionCategory=DimensionCategory.prediction,
            status="cleared",
            isTriggered=False,
            isManaged=False,
            threshold=0.9,
            thresholdMode="single",
            threshold2=None,
            dynamicAutoThresholdEnabled=True,
            stdDevMultiplier=2.5,
            notificationsEnabled=True,
            updatedAt=evaluated_time,
            scheduledRuntimeEnabled=True,
            scheduledRuntimeCadenceSeconds=86400,
            scheduledRuntimeDaysOfWeek=[1, 2, 3, 4, 5],  # Weekdays
            latestComputedValue=0.92,
            performanceMetric=PerformanceMetric.accuracy,
            customMetric=custom_metric,
            operator=ComparisonOperator.greaterThan,
            positiveClassValue="1",
            primaryMetricWindow=metric_window,
        )

        assert monitor.id == "monitor123"
        assert monitor.name == "Performance Monitor"
        assert monitor.monitorCategory == MonitorCategory.performance
        assert monitor.creator.name == "Test User"
        assert len(monitor.contacts) == 1
        assert monitor.status == "cleared"
        assert monitor.isTriggered is False
        assert monitor.threshold == 0.9
        assert monitor.dynamicAutoThresholdEnabled is True
        assert monitor.stdDevMultiplier == 2.5
        assert monitor.notificationsEnabled is True
        assert monitor.scheduledRuntimeCadenceSeconds == 86400
        assert len(monitor.scheduledRuntimeDaysOfWeek) == 5
        assert monitor.latestComputedValue == 0.92
        assert monitor.performanceMetric == PerformanceMetric.accuracy
        assert monitor.positiveClassValue == "1"


class TestMetricFilterItem:
    """Test MetricFilterItem model"""

    def test_init(self):
        """Test MetricFilterItem initialization with all fields"""
        from arize_toolkit.models import DimensionValue

        dimension = Dimension(id="dim123", name="test_dim")
        dim_values = [
            DimensionValue(id="val1", value="value1"),
            DimensionValue(id="val2", value="value2"),
        ]

        filter_item = MetricFilterItem(
            id="filter123",
            filterType=FilterRowType.featureLabel,
            operator=ComparisonOperator.equals,
            dimension=dimension,
            dimensionValues=dim_values,
            binaryValues=["true", "false"],
            numericValues=["1.0", "2.0", "3.0"],
            categoricalValues=["cat1", "cat2", "cat3"],
        )

        assert filter_item.id == "filter123"
        assert filter_item.filterType == FilterRowType.featureLabel
        assert filter_item.operator == ComparisonOperator.equals
        assert filter_item.dimension.name == "test_dim"
        assert len(filter_item.dimensionValues) == 2
        assert filter_item.binaryValues == ["true", "false"]
        assert filter_item.numericValues == ["1.0", "2.0", "3.0"]
        assert filter_item.categoricalValues == ["cat1", "cat2", "cat3"]

    def test_all_optional_fields(self):
        """Test MetricFilterItem with all fields as None"""
        filter_item = MetricFilterItem()

        assert filter_item.id is None
        assert filter_item.filterType is None
        assert filter_item.operator is None
        assert filter_item.dimension is None
        assert filter_item.dimensionValues is None
        assert filter_item.binaryValues is None
        assert filter_item.numericValues is None
        assert filter_item.categoricalValues is None

    def test_partial_fields(self):
        """Test MetricFilterItem with partial fields"""
        filter_item = MetricFilterItem(
            filterType=FilterRowType.predictionValue,
            operator=ComparisonOperator.greaterThan,
            numericValues=["100", "200"],
        )

        assert filter_item.filterType == FilterRowType.predictionValue
        assert filter_item.operator == ComparisonOperator.greaterThan
        assert filter_item.numericValues == ["100", "200"]
        assert filter_item.id is None
        assert filter_item.dimension is None


class TestMetricWindow:
    """Test MetricWindow model"""

    def test_init(self):
        """Test MetricWindow initialization with all fields"""
        dimension = Dimension(id="dim456", name="window_dim")
        filter_items = [
            MetricFilterItem(
                id="f1",
                filterType=FilterRowType.predictionScore,
                numericValues=["10", "20"],
            ),
            MetricFilterItem(
                id="f2",
                filterType=FilterRowType.featureLabel,
                categoricalValues=["cat1", "cat2"],
            ),
        ]

        window = MetricWindow(
            id="window123",
            type="fixed",
            windowLengthMs=172800000,  # 2 days in ms
            dimensionCategory=DimensionCategory.featureLabel,
            dimension=dimension,
            filters=filter_items,
        )

        assert window.id == "window123"
        assert window.type == "fixed"
        assert window.windowLengthMs == 172800000
        assert window.dimensionCategory == DimensionCategory.featureLabel
        assert window.dimension.name == "window_dim"
        assert len(window.filters) == 2
        assert window.filters[0].id == "f1"

    def test_default_values(self):
        """Test MetricWindow default values"""
        window = MetricWindow()

        assert window.id is None
        assert window.type == "moving"  # Default value
        assert window.windowLengthMs == 86400000  # Default value (1 day in ms)
        assert window.dimensionCategory is None
        assert window.dimension is None
        assert window.filters == []  # Default empty list

    def test_partial_initialization(self):
        """Test MetricWindow with partial fields"""
        window = MetricWindow(
            id="window456",
            type="fixed",
            dimensionCategory=DimensionCategory.prediction,
        )

        assert window.id == "window456"
        assert window.type == "fixed"
        assert window.windowLengthMs == 86400000  # Default value
        assert window.dimensionCategory == DimensionCategory.prediction
        assert window.dimension is None
        assert window.filters == []

    def test_filters_list_operations(self):
        """Test that filters list can be modified"""
        window = MetricWindow()
        assert window.filters == []

        # Add a filter
        new_filter = MetricFilterItem(id="filter1")
        window.filters.append(new_filter)
        assert len(window.filters) == 1
        assert window.filters[0].id == "filter1"


class TestDimensionFilterInput:
    """Test DimensionFilterInput model"""

    def test_init(self):
        """Test DimensionFilterInput initialization"""
        filter_input = DimensionFilterInput(
            dimensionType=FilterRowType.predictionValue,
            operator=ComparisonOperator.lessThan,
            name="test_dimension",
            values=["value1", "value2", "value3"],
        )

        assert filter_input.dimensionType == FilterRowType.predictionValue
        assert filter_input.operator == ComparisonOperator.lessThan
        assert filter_input.name == "test_dimension"
        assert filter_input.values == ["value1", "value2", "value3"]

    def test_default_values(self):
        """Test DimensionFilterInput default values"""
        filter_input = DimensionFilterInput(dimensionType=FilterRowType.predictionValue)

        assert filter_input.dimensionType == FilterRowType.predictionValue
        assert filter_input.operator == ComparisonOperator.equals  # Default
        assert filter_input.name is None
        assert filter_input.values == []  # Default empty list

    def test_validation_feature_label_requires_name(self):
        """Test validation that featureLabel filter type requires name"""
        from pytest import raises

        # Should raise error without name
        with raises(
            ValueError,
            match="Name is required for feature label or tag label filter type",
        ):
            DimensionFilterInput(
                dimensionType=FilterRowType.featureLabel,
                values=["value1"],
            )

    def test_validation_tag_label_requires_name(self):
        """Test validation that tagLabel filter type requires name"""
        from pytest import raises

        # Should raise error without name
        with raises(
            ValueError,
            match="Name is required for feature label or tag label filter type",
        ):
            DimensionFilterInput(
                dimensionType=FilterRowType.tagLabel,
                values=["tag1", "tag2"],
            )

    def test_valid_feature_label_with_name(self):
        """Test valid featureLabel filter with name"""
        filter_input = DimensionFilterInput(
            dimensionType=FilterRowType.featureLabel,
            name="feature_name",
            values=["value1", "value2"],
        )

        assert filter_input.dimensionType == FilterRowType.featureLabel
        assert filter_input.name == "feature_name"
        assert filter_input.values == ["value1", "value2"]

    def test_valid_tag_label_with_name(self):
        """Test valid tagLabel filter with name"""
        filter_input = DimensionFilterInput(
            dimensionType=FilterRowType.tagLabel,
            name="tag_name",
            operator=ComparisonOperator.notEquals,
            values=["tag1"],
        )

        assert filter_input.dimensionType == FilterRowType.tagLabel
        assert filter_input.name == "tag_name"
        assert filter_input.operator == ComparisonOperator.notEquals
        assert filter_input.values == ["tag1"]

    def test_other_filter_types_without_name(self):
        """Test that other filter types don't require name"""
        filter_types = [
            FilterRowType.predictionValue,
            FilterRowType.actuals,
            FilterRowType.actualScore,
            FilterRowType.predictionScore,
            FilterRowType.modelVersion,
            FilterRowType.batchId,
        ]

        for filter_type in filter_types:
            filter_input = DimensionFilterInput(
                dimensionType=filter_type,
                values=["test_value"],
            )
            assert filter_input.dimensionType == filter_type
            assert filter_input.name is None
            assert filter_input.values == ["test_value"]


class TestTimeSeriesModels:
    """Test time series related models"""

    def test_data_point(self):
        """Test DataPoint model initialization"""
        from arize_toolkit.models import DataPoint

        # Test with both x and y values
        timestamp = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        point = DataPoint(x=timestamp, y=0.95)

        assert point.x == timestamp
        assert point.y == 0.95

        # Test with None y value
        point_none = DataPoint(x=timestamp, y=None)
        assert point_none.x == timestamp
        assert point_none.y is None

    def test_time_series_with_threshold_data_type(self):
        """Test TimeSeriesWithThresholdDataType model"""
        from arize_toolkit.models import DataPoint, TimeSeriesWithThresholdDataType

        # Create data points
        data_points = [DataPoint(x=datetime(2024, 1, 1, i, 0, 0, tzinfo=timezone.utc), y=0.9 + i * 0.01) for i in range(5)]

        # Create threshold data points
        threshold_points = [DataPoint(x=datetime(2024, 1, 1, i, 0, 0, tzinfo=timezone.utc), y=0.85) for i in range(5)]

        # Test with all fields
        time_series = TimeSeriesWithThresholdDataType(
            key="accuracy_metric",
            dataPoints=data_points,
            thresholdDataPoints=threshold_points,
        )

        assert time_series.key == "accuracy_metric"
        assert len(time_series.dataPoints) == 5
        assert len(time_series.thresholdDataPoints) == 5
        assert time_series.dataPoints[0].y == 0.9
        assert time_series.thresholdDataPoints[0].y == 0.85

    def test_time_series_without_threshold(self):
        """Test TimeSeriesWithThresholdDataType without threshold data"""
        from arize_toolkit.models import DataPoint, TimeSeriesWithThresholdDataType

        # Create only data points (no threshold)
        data_points = [DataPoint(x=datetime(2024, 1, 1, i, 0, 0, tzinfo=timezone.utc), y=100 + i * 10) for i in range(3)]

        time_series = TimeSeriesWithThresholdDataType(key="volume_metric", dataPoints=data_points, thresholdDataPoints=None)

        assert time_series.key == "volume_metric"
        assert len(time_series.dataPoints) == 3
        assert time_series.thresholdDataPoints is None

    def test_time_series_empty_data_points(self):
        """Test TimeSeriesWithThresholdDataType with empty data points"""
        from arize_toolkit.models import TimeSeriesWithThresholdDataType

        # Test with empty lists (default)
        time_series = TimeSeriesWithThresholdDataType(key="empty_metric")

        assert time_series.key == "empty_metric"
        assert time_series.dataPoints == []
        assert time_series.thresholdDataPoints is None

    def test_time_series_mixed_y_values(self):
        """Test TimeSeriesWithThresholdDataType with mixed None and float y values"""
        from arize_toolkit.models import DataPoint, TimeSeriesWithThresholdDataType

        # Create data points with some None values
        data_points = [
            DataPoint(x=datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc), y=0.9),
            DataPoint(x=datetime(2024, 1, 1, 1, 0, 0, tzinfo=timezone.utc), y=None),
            DataPoint(x=datetime(2024, 1, 1, 2, 0, 0, tzinfo=timezone.utc), y=0.85),
            DataPoint(x=datetime(2024, 1, 1, 3, 0, 0, tzinfo=timezone.utc), y=None),
        ]

        time_series = TimeSeriesWithThresholdDataType(key="sparse_metric", dataPoints=data_points)

        assert len(time_series.dataPoints) == 4
        assert time_series.dataPoints[0].y == 0.9
        assert time_series.dataPoints[1].y is None
        assert time_series.dataPoints[2].y == 0.85
        assert time_series.dataPoints[3].y is None
