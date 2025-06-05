import pytest

from arize_toolkit.models import AnnotationInput, Dimension, DimensionValue, User


class TestUser:
    def test_init(self):
        """Test that User can be initialized with valid parameters."""
        user = User(id="user123", name="Test User", email="test@example.com")

        assert user.id == "user123"
        assert user.name == "Test User"
        assert user.email == "test@example.com"

    def test_optional_fields(self):
        """Test that optional fields have correct defaults."""
        user = User(id="user123")

        assert user.id == "user123"
        assert user.name is None
        assert user.email is None


class TestDimension:
    def test_init(self):
        """Test that Dimension can be initialized with valid parameters."""
        from arize_toolkit.types import DimensionCategory, DimensionDataType

        dimension = Dimension(
            id="dim123",
            name="user_age",
            dataType=DimensionDataType.LONG,
            category=DimensionCategory.prediction,
        )

        assert dimension.id == "dim123"
        assert dimension.name == "user_age"
        assert dimension.dataType == DimensionDataType.LONG
        assert dimension.category == DimensionCategory.prediction

    def test_required_fields(self):
        """Test that required fields must be provided."""
        dimension = Dimension(name="test_dimension")

        assert dimension.name == "test_dimension"
        assert dimension.id is None
        assert dimension.dataType is None
        assert dimension.category is None


class TestDimensionValue:
    """Test DimensionValue model"""

    def test_init(self):
        """Test DimensionValue initialization"""
        # Test with all fields
        dim_value = DimensionValue(id="dim_val_123", value="category_1")
        assert dim_value.id == "dim_val_123"
        assert dim_value.value == "category_1"

    def test_required_fields(self):
        """Test DimensionValue with only required fields"""
        dim_value = DimensionValue(value="test_value")
        assert dim_value.value == "test_value"
        assert dim_value.id is None

    def test_missing_required_field(self):
        """Test DimensionValue without required value field"""
        with pytest.raises(ValueError):
            DimensionValue()


class TestAnnotationInput:
    def test_label_annotation(self):
        """Test label annotation type validation."""
        # Valid label annotation
        annotation = AnnotationInput(
            name="sentiment",
            updatedBy="user123",
            label="positive",
            annotationType="label",
        )

        assert annotation.name == "sentiment"
        assert annotation.label == "positive"
        assert annotation.annotationType == "label"

    def test_score_annotation(self):
        """Test score annotation type validation."""
        # Valid score annotation
        annotation = AnnotationInput(name="quality", updatedBy="user123", score=0.95, annotationType="score")

        assert annotation.name == "quality"
        assert annotation.score == 0.95
        assert annotation.annotationType == "score"

    def test_validation_label_missing(self):
        """Test that label is required for label annotation type."""
        with pytest.raises(ValueError, match="Label is required for label annotation type"):
            AnnotationInput(
                name="sentiment",
                updatedBy="user123",
                annotationType="label",
                # Missing label
            )

    def test_validation_score_missing(self):
        """Test that score is required for score annotation type."""
        with pytest.raises(ValueError, match="Score is required for score annotation type"):
            AnnotationInput(
                name="quality",
                updatedBy="user123",
                annotationType="score",
                # Missing score
            )
