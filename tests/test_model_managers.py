import pytest
from datetime import datetime
from arize_toolkit.models import (
    Monitor,
    MonitorContact,
    Dimension,
    MetricWindow,
    ModelEnvironment,
)
from arize_toolkit.model_managers import MonitorManager
from arize_toolkit.types import (
    MonitorCategory,
    PerformanceMetric,
    DataQualityMetric,
    DriftMetric,
    DimensionCategory,
    ComparisonOperator,
    DimensionDataType,
)


class TestMonitorManager:
    @pytest.fixture
    def monitor_test_data(self):
        """Test data for different types of monitors"""
        base_config = {
            "id": "test_monitor_id",
            "createdDate": datetime.now(),
            "evaluationIntervalSeconds": 3600,
            "notes": "Test monitor",
            "contacts": [
                MonitorContact(
                    id="contact1",
                    notificationChannelType="email",
                    emailAddress="test@example.com",
                )
            ],
            "status": "cleared",
            "isTriggered": False,
            "isManaged": True,
            "notificationsEnabled": True,
            "primaryMetricWindow": MetricWindow(
                type="moving",
                windowLengthMs=86400000,  # 24 hours
                dimensionCategory=DimensionCategory.featureLabel,
                dimension=Dimension(
                    name="test_dimension",
                    dataType=DimensionDataType.STRING,
                    category=DimensionCategory.featureLabel,
                ),
            ),
            # Adding all required fields with None values
            "evaluatedAt": None,
            "creator": None,
            "dimensionCategory": None,
            "threshold2": None,
            "dynamicAutoThresholdEnabled": False,
            "stdDevMultiplier2": None,
            "updatedAt": None,
            "downtimeStart": None,
            "downtimeDurationHrs": None,
            "downtimeFrequencyDays": None,
            "scheduledRuntimeEnabled": False,
            "scheduledRuntimeCadenceSeconds": None,
            "scheduledRuntimeDaysOfWeek": [],
            "latestComputedValue": None,
            "dataQualityMetric": None,
            "driftMetric": None,
            "customMetric": None,
            "operator2": None,
            "performanceMetric": None,
        }

        return {
            "performance": {
                **base_config,
                "name": "accuracy_monitor",
                "monitorCategory": MonitorCategory.performance,
                "performanceMetric": PerformanceMetric.accuracy,
                "modelEnvironmentName": ModelEnvironment.production,
                "threshold": 0.95,
                "thresholdMode": "single",
                "operator": ComparisonOperator.lessThan,
                "stdDevMultiplier": 2.0,
                "positiveClassValue": "positive",
                "metricAtRankingKValue": 10,
                "topKPercentileValue": 0.95,
                "dataQualityMetric": None,
                "driftMetric": None,
                "predictionClassValue": None,
            },
            "data_quality": {
                **base_config,
                "name": "missing_values_monitor",
                "monitorCategory": MonitorCategory.dataQuality,
                "dataQualityMetric": DataQualityMetric.percentEmpty,
                "dimensionCategory": DimensionCategory.featureLabel,
                "modelEnvironmentName": ModelEnvironment.production,
                "threshold": 0.1,
                "thresholdMode": "single",
                "operator": ComparisonOperator.lessThan,
                "stdDevMultiplier": 2.0,
                "performanceMetric": None,
                "driftMetric": None,
                "metricAtRankingKValue": None,
                "positiveClassValue": None,
                "topKPercentileValue": None,
            },
            "drift": {
                **base_config,
                "name": "feature_drift_monitor",
                "monitorCategory": MonitorCategory.drift,
                "driftMetric": DriftMetric.js,
                "dimensionCategory": DimensionCategory.featureLabel,
                "threshold": 0.5,
                "thresholdMode": "single",
                "operator": ComparisonOperator.lessThan,
                "stdDevMultiplier": 2.0,
                "performanceMetric": None,
                "dataQualityMetric": None,
                "metricAtRankingKValue": None,
                "positiveClassValue": None,
                "topKPercentileValue": None,
            },
            "range_threshold": {
                **base_config,
                "name": "range_monitor",
                "monitorCategory": MonitorCategory.performance,
                "performanceMetric": PerformanceMetric.accuracy,
                "modelEnvironmentName": ModelEnvironment.production,
                "threshold": 0.8,
                "threshold2": 0.95,
                "thresholdMode": "range",
                "operator": ComparisonOperator.greaterThan,
                "operator2": ComparisonOperator.lessThan,
                "stdDevMultiplier": 1.5,
                "stdDevMultiplier2": 2.5,
                "dataQualityMetric": None,
                "driftMetric": None,
                "metricAtRankingKValue": None,
                "positiveClassValue": None,
                "topKPercentileValue": None,
            },
        }

    def test_monitor_extraction(self, monitor_test_data):
        """Test extraction of different monitor types"""
        # Test performance monitor
        monitor = Monitor(**monitor_test_data["performance"])
        result = MonitorManager.extract_monitor_type(
            space_id="test_space", model_name="test_model", monitor=monitor
        )
        assert result.name == "accuracy_monitor"
        assert result.performanceMetric == PerformanceMetric.accuracy
        assert result.threshold == 0.95
        assert result.operator == ComparisonOperator.lessThan

        # Test data quality monitor
        monitor = Monitor(**monitor_test_data["data_quality"])
        result = MonitorManager.extract_monitor_type(
            space_id="test_space", model_name="test_model", monitor=monitor
        )
        assert result.name == "missing_values_monitor"
        assert result.dataQualityMetric == DataQualityMetric.percentEmpty
        assert result.threshold == 0.1
        assert result.dimensionCategory == DimensionCategory.featureLabel

        # Test drift monitor
        monitor = Monitor(**monitor_test_data["drift"])
        result = MonitorManager.extract_monitor_type(
            space_id="test_space", model_name="test_model", monitor=monitor
        )
        assert result.name == "feature_drift_monitor"
        assert result.driftMetric == DriftMetric.js
        assert result.threshold == 0.5
        assert result.dimensionCategory == DimensionCategory.featureLabel

        # Test range threshold monitor
        monitor = Monitor(**monitor_test_data["range_threshold"])
        result = MonitorManager.extract_monitor_type(
            space_id="test_space", model_name="test_model", monitor=monitor
        )
        assert result.name == "range_monitor"
        assert result.thresholdMode == "range"
        assert result.threshold == 0.8
        assert result.threshold2 == 0.95
        assert result.operator == ComparisonOperator.greaterThan
        assert result.operator2 == ComparisonOperator.lessThan
        assert result.dynamicAutoThreshold.stdDevMultiplier == 1.5
        assert result.stdDevMultiplier2 == 2.5

    def test_process_multiple_monitors(self, monitor_test_data):
        """Test processing multiple monitors of different types"""
        monitors = [
            Monitor(**monitor_test_data["performance"]),
            Monitor(**monitor_test_data["data_quality"]),
            Monitor(**monitor_test_data["drift"]),
            Monitor(**monitor_test_data["range_threshold"]),
        ]

        results = MonitorManager.process_monitors(
            space_id="test_space", model_name="test_model", monitors=monitors
        )

        assert len(results) == 4
        assert results[0].name == "accuracy_monitor"
        assert results[1].name == "missing_values_monitor"
        assert results[2].name == "feature_drift_monitor"
        assert results[3].name == "range_monitor"

        # Verify specific monitor type attributes
        assert results[0].performanceMetric == PerformanceMetric.accuracy
        assert results[1].dataQualityMetric == DataQualityMetric.percentEmpty
        assert results[2].driftMetric == DriftMetric.js
        assert results[3].thresholdMode == "range"
