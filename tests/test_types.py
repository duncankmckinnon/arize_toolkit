import pytest

from arize_toolkit.types import (
    ComparisonOperator,
    InputValidationEnum,
    ModelType,
    MonitorCategory,
    PerformanceMetric,
)


class TestInputValidationEnum:
    def test_input_validation_enum(self):
        """Test the base InputValidationEnum class"""

        class TestEnum(InputValidationEnum):
            test = "test", "Test"
            multiple = "multiple", "Multiple", "multi"

        # Test valid inputs
        assert TestEnum.from_input("test") == "test"
        assert TestEnum.from_input("multiple") == "multiple"
        assert TestEnum.from_input("multi") == "multiple"

        # Test invalid input
        with pytest.raises(ValueError) as exc_info:
            TestEnum.from_input("invalid")
        assert "invalid is not a valid TestEnum" in str(exc_info.value)

    def test_performance_metric(self):
        """Test PerformanceMetric enum validation"""
        # Test valid metrics
        assert PerformanceMetric.from_input("accuracy") == "accuracy"
        assert PerformanceMetric.from_input("Accuracy") == "accuracy"
        assert PerformanceMetric.from_input("f_1") == "f_1"
        assert PerformanceMetric.from_input("F1 Score") == "f_1"
        assert PerformanceMetric.from_input("MSE") == "mse"

        # Test invalid metric
        with pytest.raises(ValueError) as exc_info:
            PerformanceMetric.from_input("invalid_metric")
        assert "invalid_metric is not a valid PerformanceMetric" in str(exc_info.value)

    def test_comparison_operator(self):
        """Test ComparisonOperator enum validation"""
        # Test valid operators
        assert ComparisonOperator.from_input("greaterThan") == "greaterThan"
        assert ComparisonOperator.from_input("Greater Than") == "greaterThan"
        assert ComparisonOperator.from_input(">") == "greaterThan"
        assert ComparisonOperator.from_input("=") == "equals"

        # Test invalid operator
        with pytest.raises(ValueError) as exc_info:
            ComparisonOperator.from_input("invalid_operator")
        assert "invalid_operator is not a valid ComparisonOperator" in str(
            exc_info.value
        )

    def test_monitor_category(self):
        """Test MonitorCategory enum validation"""
        # Test valid categories
        assert MonitorCategory.from_input("performance") == "performance"
        assert MonitorCategory.from_input("Performance") == "performance"
        assert MonitorCategory.from_input("drift") == "drift"
        assert MonitorCategory.from_input("Data Quality") == "dataQuality"

        # Test invalid category
        with pytest.raises(ValueError) as exc_info:
            MonitorCategory.from_input("invalid_category")
        assert "invalid_category is not a valid MonitorCategory" in str(exc_info.value)

    def test_model_type(self):
        """Test ModelType enum validation"""
        # Test valid model types
        assert ModelType.from_input("score_categorical") == "score_categorical"
        assert ModelType.from_input("Classification") == "score_categorical"
        assert ModelType.from_input("numeric") == "numeric"
        assert ModelType.from_input("Regression") == "numeric"
        assert ModelType.from_input("LLM") == "generative_llm"
        assert ModelType.from_input("Computer Vision") == "object_detection"

        # Test invalid model type
        with pytest.raises(ValueError) as exc_info:
            ModelType.from_input("invalid_model_type")
        assert "invalid_model_type is not a valid ModelType" in str(exc_info.value)

    def test_enum_values_consistency(self):
        """Test that enum values are consistent and unique"""

        def get_all_values(enum_class):
            all_values = set()
            for member in enum_class:
                all_values.update(member.value)
            return all_values

        # Check for duplicate values in each enum
        performance_metric_values = get_all_values(PerformanceMetric)
        assert len(performance_metric_values) == sum(
            len(member.value) for member in PerformanceMetric
        )

        comparison_operator_values = get_all_values(ComparisonOperator)
        assert len(comparison_operator_values) == sum(
            len(member.value) for member in ComparisonOperator
        )

        monitor_category_values = get_all_values(MonitorCategory)
        assert len(monitor_category_values) == sum(
            len(member.value) for member in MonitorCategory
        )

        model_type_values = get_all_values(ModelType)
        assert len(model_type_values) == sum(len(member.value) for member in ModelType)
