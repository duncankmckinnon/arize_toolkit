from datetime import datetime, timezone

from arize_toolkit.models import Model
from arize_toolkit.models.base_models import User
from arize_toolkit.models.space_models import CustomRole, Organization, Space, SpaceUser
from arize_toolkit.types import ModelType, SpaceMemberRole, SpaceMembership


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


class TestSpaceUserModels:
    def test_space_user_init_with_legacy_role(self):
        """Test SpaceUser model initialization with a legacy role."""
        user = User(id="user123", name="John Doe", email="john@example.com")
        space_user = SpaceUser(
            role=SpaceMemberRole.admin,
            membership=SpaceMembership.EXPLICIT_MEMBERSHIP,
            user=user,
        )

        assert space_user.role == SpaceMemberRole.admin
        assert space_user.membership == SpaceMembership.EXPLICIT_MEMBERSHIP
        assert space_user.customRole is None
        assert space_user.user.id == "user123"
        assert space_user.user.email == "john@example.com"

    def test_space_user_init_with_custom_role(self):
        """Test SpaceUser model initialization with a custom role."""
        user = User(id="user456", name="Jane Doe", email="jane@example.com")
        custom_role = CustomRole(id="role123", name="Data Scientist")
        space_user = SpaceUser(
            membership=SpaceMembership.EXPLICIT_MEMBERSHIP,
            customRole=custom_role,
            user=user,
        )

        assert space_user.role is None
        assert space_user.customRole.id == "role123"
        assert space_user.customRole.name == "Data Scientist"

    def test_space_user_init_inherited_membership(self):
        """Test SpaceUser model initialization with inherited membership."""
        user = User(id="user789", name="Admin User", email="admin@example.com")
        space_user = SpaceUser(
            membership=SpaceMembership.ACCOUNT_ADMIN,
            user=user,
        )

        assert space_user.role is None
        assert space_user.membership == SpaceMembership.ACCOUNT_ADMIN
        assert space_user.customRole is None

    def test_space_user_to_dict(self):
        """Test SpaceUser model serialization to dictionary."""
        user = User(id="user123", name="John Doe", email="john@example.com")
        space_user = SpaceUser(
            role=SpaceMemberRole.member,
            membership=SpaceMembership.EXPLICIT_MEMBERSHIP,
            user=user,
        )

        d = space_user.to_dict()
        assert d["role"] == "member"
        assert d["membership"] == "EXPLICIT_MEMBERSHIP"
        assert d["user"]["id"] == "user123"
        assert d["user"]["email"] == "john@example.com"

    def test_space_user_graphql_fields(self):
        """Test SpaceUser model GraphQL fields generation."""
        fields = SpaceUser.to_graphql_fields()

        assert "role" in fields
        assert "membership" in fields
        assert "customRole" in fields
        assert "user" in fields
        # Nested fields should be included
        assert "id" in fields
        assert "name" in fields
        assert "email" in fields


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
