from datetime import datetime, timezone

from arize_toolkit.models import Model
from arize_toolkit.models.space_models import Organization, Space
from arize_toolkit.types import ModelType


class TestSpaceModels:
    def test_space_init_minimal(self):
        """Test Space model initialization with minimal fields."""
        space = Space(id="space123", name="Production Space")

        assert space.id == "space123"
        assert space.name == "Production Space"
        assert space.createdAt is None
        assert space.description is None
        assert space.private is None

    def test_space_init_full(self):
        """Test Space model initialization with all fields."""
        created_time = datetime(2024, 1, 1, tzinfo=timezone.utc)
        space = Space(
            id="space456",
            name="Development Space",
            createdAt=created_time,
            description="Space for development work",
            private=True,
        )

        assert space.id == "space456"
        assert space.name == "Development Space"
        assert space.createdAt == created_time
        assert space.description == "Space for development work"
        assert space.private is True

    def test_space_to_dict(self):
        """Test Space model serialization to dictionary."""
        created_time = datetime(2024, 1, 1, tzinfo=timezone.utc)
        space = Space(
            id="space789",
            name="Test Space",
            createdAt=created_time,
            description="Test description",
            private=False,
        )

        space_dict = space.to_dict()
        assert space_dict["id"] == "space789"
        assert space_dict["name"] == "Test Space"
        assert space_dict["createdAt"] == "2024-01-01T00:00:00.000000Z"
        assert space_dict["description"] == "Test description"
        assert space_dict["private"] is False

    def test_space_graphql_fields(self):
        """Test Space model GraphQL fields generation."""
        fields = Space.to_graphql_fields()

        # Should include all Space-specific fields plus BaseNode fields
        assert "id" in fields
        assert "name" in fields
        assert "createdAt" in fields
        assert "description" in fields
        assert "private" in fields


class TestOrganizationModels:
    def test_organization_init_minimal(self):
        """Test Organization model initialization with minimal fields."""
        org = Organization(id="org123", name="Demo Organization")

        assert org.id == "org123"
        assert org.name == "Demo Organization"
        assert org.createdAt is None
        assert org.description is None

    def test_organization_init_full(self):
        """Test Organization model initialization with all fields."""
        created_time = datetime(2024, 2, 1, tzinfo=timezone.utc)
        org = Organization(
            id="org456",
            name="Production Organization",
            createdAt=created_time,
            description="Main production organization",
        )

        assert org.id == "org456"
        assert org.name == "Production Organization"
        assert org.createdAt == created_time
        assert org.description == "Main production organization"

    def test_organization_to_dict(self):
        """Test Organization model serialization to dictionary."""
        created_time = datetime(2024, 3, 1, tzinfo=timezone.utc)
        org = Organization(
            id="org789",
            name="Test Organization",
            createdAt=created_time,
            description="Organization for testing",
        )

        org_dict = org.to_dict()
        assert org_dict["id"] == "org789"
        assert org_dict["name"] == "Test Organization"
        assert org_dict["createdAt"] == "2024-03-01T00:00:00.000000Z"
        assert org_dict["description"] == "Organization for testing"

    def test_organization_graphql_fields(self):
        """Test Organization model GraphQL fields generation."""
        fields = Organization.to_graphql_fields()

        # Should include all Organization-specific fields plus BaseNode fields
        assert "id" in fields
        assert "name" in fields
        assert "createdAt" in fields
        assert "description" in fields


class TestSpaceAndModel:
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
