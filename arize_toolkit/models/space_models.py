from datetime import datetime
from typing import Optional

from pydantic import Field

from arize_toolkit.models.base_models import BaseNode, User
from arize_toolkit.types import AccountRole, SpaceMemberRole, SpaceMembership, UserStatus, UserType
from arize_toolkit.utils import GraphQLModel


class Organization(BaseNode):
    createdAt: Optional[datetime] = Field(default=None, description="The datetime the organization was created")
    description: Optional[str] = Field(default=None, description="The description of the organization")


class Space(BaseNode):
    createdAt: Optional[datetime] = Field(default=None, description="The datetime the space was created")
    description: Optional[str] = Field(default=None, description="The description of the space")
    private: Optional[bool] = Field(default=None, description="Whether the space is private")


class SpaceMember(GraphQLModel):
    """A member of a space with their role"""

    id: str = Field(description="The ID of the space member")
    role: SpaceMemberRole = Field(description="The role of the member in the space")
    user: Optional[User] = Field(default=None, description="The user information")


class SpaceMemberInput(GraphQLModel):
    """Input for assigning a user to a space with a role"""

    userId: str = Field(description="The ID of the user to assign")
    spaceId: str = Field(description="The ID of the space to assign the user to")
    role: Optional[SpaceMemberRole] = Field(
        default=None,
        description="The role to assign (admin, member, readOnly, annotator). Either role or customRoleId must be provided.",
    )
    customRoleId: Optional[str] = Field(
        default=None,
        description="Custom role ID. Either role or customRoleId must be provided, but not both.",
    )


class CustomRole(GraphQLModel):
    """A custom role with permissions"""

    id: str = Field(description="The unique ID of the custom role")
    name: str = Field(description="The name of the custom role")


class SpaceUser(GraphQLModel):
    """A user that has access to the space through explicit or inherited membership"""

    role: Optional[SpaceMemberRole] = Field(
        default=None,
        description="The legacy role for the space (admin, member, readOnly, annotator). Null for custom roles or inherited membership.",
    )
    membership: SpaceMembership = Field(description="The way in which the user has access to the space")
    customRole: Optional[CustomRole] = Field(
        default=None,
        description="The custom role assigned to this space member. Null for legacy roles and inherited memberships.",
    )
    user: User = Field(description="The space member user information")


class AccountUser(GraphQLModel):
    """A user in the account with detailed information"""

    id: str = Field(description="The unique ID of the user")
    name: Optional[str] = Field(default=None, description="The name of the user")
    email: str = Field(description="The email of the user")
    status: Optional[UserStatus] = Field(default=None, description="The status of the user (active/inactive)")
    accountRole: Optional[AccountRole] = Field(default=None, description="The role of the user in the account")
    userType: Optional[UserType] = Field(default=None, description="The type of user (human/bot)")
    createdAt: Optional[datetime] = Field(default=None, description="When the user was created")
