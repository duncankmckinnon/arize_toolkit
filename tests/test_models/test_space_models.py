from datetime import datetime, timezone

from arize_toolkit.models import Model, Space
from arize_toolkit.types import ModelType


class TestSpaceAndModel:
    def test_space_init(self):
        """Test Space model initialization."""
        space = Space(id="space123", name="Production Space")

        assert space.id == "space123"
        assert space.name == "Production Space"

    def test_model_init(self):
        """Test Model initialization."""
        created_time = datetime(2024, 1, 1, tzinfo=timezone.utc)
        model = Model(
            id="model123",
            name="Customer Churn Model",
            modelType=ModelType.score_categorical,
            createdAt=created_time,
            isDemoModel=False,
        )

        assert model.id == "model123"
        assert model.name == "Customer Churn Model"
        assert model.modelType == ModelType.score_categorical
        assert model.createdAt == created_time
        assert model.isDemoModel is False
