from arize_toolkit.models import CustomMetricInput


class TestCustomMetricModels:
    def test_custom_metric_input(self):
        """Test CustomMetricInput model."""
        from arize_toolkit.types import ModelEnvironment

        metric = CustomMetricInput(
            modelId="model123",
            name="Custom F1 Score",
            description="Custom implementation of F1 score",
            metric="(2 * precision * recall) / (precision + recall)",
        )

        assert metric.modelId == "model123"
        assert metric.name == "Custom F1 Score"
        assert metric.description == "Custom implementation of F1 score"
        assert metric.metric == "(2 * precision * recall) / (precision + recall)"
        assert metric.modelEnvironmentName == ModelEnvironment.production  # Default

    def test_custom_metric_input_defaults(self):
        """Test CustomMetricInput default values."""
        metric = CustomMetricInput(modelId="model123", name="Metric", metric="value")

        assert metric.description == "a custom metric"  # Default description
