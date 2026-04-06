from datetime import datetime
from typing import List, Optional, Tuple

from arize_toolkit.models.space_models import AccountUser, Organization, Space, SpaceMember, SpaceMemberInput, SpaceUser
from arize_toolkit.queries.basequery import ArizeAPIException, BaseQuery, BaseResponse, BaseVariables


class OrgIDandSpaceIDQuery(BaseQuery):
    graphql_query = """
    query orgIDandSpaceID($organization: String!, $space: String!) {
        account {
            organizations(search: $organization, first: 10) {
                edges {
                    node {
                        id
                        name
                        spaces(search: $space, first: 10) {
                            edges {
                                node {
                                    id
                                    name
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    """
    query_description = "Get the organization ID and space ID from the names of the organization and space"

    class Variables(BaseVariables):
        organization: str
        space: str

    class QueryException(ArizeAPIException):
        message: str = "Error running query to retrieve Organization ID and Space ID"

    class QueryResponse(BaseResponse):
        organization_id: str
        space_id: str

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        variables = result.pop("__query_variables__", {})
        org_name = variables.get("organization", "")
        space_name = variables.get("space", "")
        if "account" not in result or "organizations" not in result["account"] or "edges" not in result["account"]["organizations"] or len(result["account"]["organizations"]["edges"]) == 0:
            cls.raise_exception("No organization found with the given name")
        org_edges = result["account"]["organizations"]["edges"]
        org_node = cls._find_exact_name_match(org_edges, org_name)
        if org_node is None:
            cls.raise_exception(f"No organization found with the exact name '{org_name}'")
        organization_id = org_node["id"]
        if "spaces" not in org_node or "edges" not in org_node["spaces"] or len(org_node["spaces"]["edges"]) == 0:
            cls.raise_exception("No space found with the given name")
        space_edges = org_node["spaces"]["edges"]
        space_node = cls._find_exact_name_match(space_edges, space_name)
        if space_node is None:
            cls.raise_exception(f"No space found with the exact name '{space_name}'")
        space_id = space_node["id"]
        return (
            [cls.QueryResponse(organization_id=organization_id, space_id=space_id)],
            False,
            None,
        )


class OrgAndFirstSpaceQuery(OrgIDandSpaceIDQuery):
    graphql_query = """
    query orgAndFirstSpace($organization: String!) {
        account {
            organizations(search: $organization, first: 10) {
                edges {
                    node {
                        id
                        name
                        spaces(first: 1) {
                            edges {
                                node {
                                    name
                                    id
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    """
    query_description = "Get the organization ID and first space ID from the name of the organization"

    class Variables(BaseVariables):
        organization: str

    class QueryException(ArizeAPIException):
        message: str = "Error running query to retrieve Organization ID and first Space ID"

    class QueryResponse(BaseResponse):
        organization_id: str
        space_id: str
        space_name: str

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        variables = result.pop("__query_variables__", {})
        org_name = variables.get("organization", "")
        if "account" not in result or "organizations" not in result["account"] or "edges" not in result["account"]["organizations"] or len(result["account"]["organizations"]["edges"]) == 0:
            cls.raise_exception("No organization found with the given name")
        org_edges = result["account"]["organizations"]["edges"]
        org_node = cls._find_exact_name_match(org_edges, org_name)
        if org_node is None:
            cls.raise_exception(f"No organization found with the exact name '{org_name}'")
        organization_id = org_node["id"]
        if "spaces" not in org_node or "edges" not in org_node["spaces"] or len(org_node["spaces"]["edges"]) == 0:
            cls.raise_exception("No spaces found in the organization")
        space_id = org_node["spaces"]["edges"][0]["node"]["id"]
        space_name = org_node["spaces"]["edges"][0]["node"]["name"]
        return (
            [
                cls.QueryResponse(
                    organization_id=organization_id,
                    space_id=space_id,
                    space_name=space_name,
                )
            ],
            False,
            None,
        )


class GetSpaceByNameQuery(BaseQuery):
    graphql_query = (
        """
    query getSpaceByName($organization_id: ID!, $spaceName: String!) {
        node(id: $organization_id) {
            ... on AccountOrganization {
                spaces(search: $spaceName, first: 10) {
                    edges {
                        node { """
        + Space.to_graphql_fields()
        + """
                        }
                    }
                }
            }
        }
    }
    """
    )
    query_description = "Get a space by name within an organization"

    class Variables(BaseVariables):
        organization_id: str
        spaceName: str

    class QueryException(ArizeAPIException):
        message: str = "Error running query to retrieve space by name"

    class QueryResponse(Space):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        variables = result.pop("__query_variables__", {})
        space_name = variables.get("spaceName", "")
        if "node" not in result or "spaces" not in result["node"] or "edges" not in result["node"]["spaces"]:
            cls.raise_exception("No spaces found")
        edges = result["node"]["spaces"]["edges"]
        if len(edges) == 0:
            cls.raise_exception("No space found matching the given name")
        space = cls._find_exact_name_match(edges, space_name)
        if space is None:
            cls.raise_exception(f"No space found with the exact name '{space_name}'")
        return ([cls.QueryResponse(**space)], False, None)


class GetSpaceByIdQuery(BaseQuery):
    graphql_query = (
        """
    query getSpaceById($spaceId: ID!) {
        node(id: $spaceId) {
            ... on Space { """
        + Space.to_graphql_fields()
        + """
            }
        }
    }
    """
    )
    query_description = "Get a space by its ID"

    class Variables(BaseVariables):
        spaceId: str

    class QueryException(ArizeAPIException):
        message: str = "Error running query to retrieve space by ID"

    class QueryResponse(Space):
        pass


class GetAllSpacesQuery(BaseQuery):
    graphql_query = (
        """
    query getAllSpaces($organization_id: ID!, $endCursor: String) {
        node(id: $organization_id) {
            ... on AccountOrganization {
                spaces(first: 10, after: $endCursor) {
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                    edges {
                        node { """
        + Space.to_graphql_fields()
        + """
                        }
                    }
                }
            }
        }
    }
    """
    )

    class Variables(BaseVariables):
        organization_id: str

    class QueryException(ArizeAPIException):
        message: str = "Error running query to retrieve all spaces"

    class QueryResponse(Space):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if "node" not in result or "spaces" not in result["node"] or "edges" not in result["node"]["spaces"]:
            cls.raise_exception("No spaces found")
        spaces = result["node"]["spaces"]
        page_info = spaces["pageInfo"]
        space_nodes = [cls.QueryResponse(**space["node"]) for space in spaces["edges"]]
        has_next_page = page_info["hasNextPage"]
        end_cursor = page_info["endCursor"]
        return (space_nodes, has_next_page, end_cursor)


class GetAllOrganizationsQuery(BaseQuery):
    graphql_query = (
        """
    query getAllOrganizations($endCursor: String) {
        account {
            organizations(first: 10, after: $endCursor) {
                pageInfo {
                    hasNextPage
                    endCursor
                }
                edges {
                    node { """
        + Organization.to_graphql_fields()
        + """
                    }
                }
            }
        }
    }
    """
    )

    class Variables(BaseVariables):
        pass

    class QueryException(ArizeAPIException):
        message: str = "Error running query to retrieve all organizations"

    class QueryResponse(Organization):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if "account" not in result or "organizations" not in result["account"] or "edges" not in result["account"]["organizations"]:
            cls.raise_exception("No organizations found")
        orgs = result["account"]["organizations"]
        page_info = orgs["pageInfo"]
        org_nodes = [cls.QueryResponse(**org["node"]) for org in orgs["edges"]]
        has_next_page = page_info["hasNextPage"]
        end_cursor = page_info["endCursor"]
        return (org_nodes, has_next_page, end_cursor)


class CreateNewSpaceMutation(BaseQuery):
    graphql_query = """
    mutation createNewSpace($input: CreateSpaceMutationInput!) {
        createSpace(
            input: $input
        ) {
            space {
                name
                id
            }
        }
    }
    """
    query_description = "Create a new space in the specified organization"

    class Variables(BaseVariables):
        accountOrganizationId: str
        name: str
        private: bool

    class QueryException(ArizeAPIException):
        message: str = "Error running mutation to create new space"

    class QueryResponse(BaseResponse):
        name: str
        id: str

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if "createSpace" not in result or "space" not in result["createSpace"]:
            cls.raise_exception("Failed to create space")
        space = result["createSpace"]["space"]
        return (
            [cls.QueryResponse(name=space["name"], id=space["id"])],
            False,
            None,
        )


class CreateNewOrganizationMutation(BaseQuery):
    graphql_query = """
    mutation createNewOrganization($input: CreateOrganizationMutationInput!) {
        createOrganization(input: $input) {
            organization {
                id
            }
        }
    }
    """
    query_description = "Create a new organization"

    class Variables(BaseVariables):
        name: str
        description: Optional[str] = None

    class QueryException(ArizeAPIException):
        message: str = "Error running mutation to create new organization"

    class QueryResponse(BaseResponse):
        id: str

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if "createOrganization" not in result or "organization" not in result["createOrganization"]:
            cls.raise_exception("Failed to create organization")
        organization = result["createOrganization"]["organization"]
        return (
            [cls.QueryResponse(id=organization["id"])],
            False,
            None,
        )


class CreateSpaceAdminApiKeyMutation(BaseQuery):
    graphql_query = """
    mutation createSpaceAdminApiKey($input: CreateServiceApiKeyInput!) {
        createServiceApiKey(
            input: $input
        ) {
            apiKey
            keyInfo {
                expiresAt
                id
            }
        }
    }
    """
    query_description = "Create a space admin API key for the specified space"

    class Variables(BaseVariables):
        name: str
        spaceId: str
        spaceRole: str = "admin"
        accountOrganizationRole: str = "member"
        accountRole: str = "member"

    class QueryException(ArizeAPIException):
        message: str = "Error running mutation to create space admin API key"

    class QueryResponse(BaseResponse):
        apiKey: str
        expiresAt: Optional[datetime]
        id: str

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if "createServiceApiKey" not in result or "apiKey" not in result["createServiceApiKey"] or "keyInfo" not in result["createServiceApiKey"]:
            cls.raise_exception("Failed to create space admin API key")
        api_key_data = result["createServiceApiKey"]
        key_info = api_key_data["keyInfo"]
        return (
            [
                cls.QueryResponse(
                    apiKey=api_key_data["apiKey"],
                    expiresAt=key_info.get("expiresAt"),
                    id=key_info["id"],
                )
            ],
            False,
            None,
        )


class AssignSpaceMembershipMutation(BaseQuery):
    graphql_query = (
        """
    mutation assignSpaceMembership($input: AssignSpaceMembershipMutationInput!) {
        assignSpaceMembership(input: $input) {
            spaceMemberships { """
        + SpaceMember.to_graphql_fields()
        + """
            }
        }
    }
    """
    )
    query_description = "Assign multiple users to multiple spaces with appropriate roles"

    class Variables(BaseVariables):
        spaceMemberships: List[SpaceMemberInput]

    class QueryException(ArizeAPIException):
        message: str = "Error running mutation to assign space membership"

    class QueryResponse(BaseResponse):
        spaceMemberships: List[SpaceMember]

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if "assignSpaceMembership" not in result or "spaceMemberships" not in result["assignSpaceMembership"]:
            cls.raise_exception("Failed to assign space membership")
        memberships = [SpaceMember(**m) for m in result["assignSpaceMembership"]["spaceMemberships"]]
        return ([cls.QueryResponse(spaceMemberships=memberships)], False, None)


class RemoveSpaceMemberMutation(BaseQuery):
    graphql_query = """
    mutation removeSpaceMember($input: RemoveSpaceMemberMutationInput!) {
        removeSpaceMember(input: $input) {
            space {
                id
                name
            }
        }
    }
    """
    query_description = "Remove a user from a space"

    class Variables(BaseVariables):
        spaceId: str
        userId: str

    class QueryException(ArizeAPIException):
        message: str = "Error running mutation to remove space member"

    class QueryResponse(BaseResponse):
        space_id: str
        space_name: Optional[str] = None

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if "removeSpaceMember" not in result or "space" not in result["removeSpaceMember"]:
            cls.raise_exception("Failed to remove space member")
        space = result["removeSpaceMember"]["space"]
        return (
            [cls.QueryResponse(space_id=space["id"], space_name=space.get("name"))],
            False,
            None,
        )


class UpdateSpaceMutation(BaseQuery):
    graphql_query = (
        """
    mutation updateSpace($input: UpdateSpaceMutationInput!) {
        updateSpace(input: $input) {
            space { """
        + Space.to_graphql_fields()
        + """
            }
        }
    }
    """
    )
    query_description = "Update a space within an organization"

    class Variables(BaseVariables):
        spaceId: str
        name: Optional[str] = None
        private: Optional[bool] = None
        description: Optional[str] = None
        gradientStartColor: Optional[str] = None
        gradientEndColor: Optional[str] = None
        mlModelsEnabled: Optional[bool] = None

    class QueryException(ArizeAPIException):
        message: str = "Error running mutation to update space"

    class QueryResponse(Space):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if "updateSpace" not in result or "space" not in result["updateSpace"]:
            cls.raise_exception("Failed to update space")
        space = result["updateSpace"]["space"]
        return ([cls.QueryResponse(**space)], False, None)


class GetSpaceUsersQuery(BaseQuery):
    graphql_query = (
        """
    query getSpaceUsers($spaceId: ID!, $first: Int, $endCursor: String, $search: String, $userType: UserType) {
        node(id: $spaceId) {
            ... on Space {
                spaceUsers(first: $first, after: $endCursor, search: $search, userType: $userType) {
                    totalCount
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                    edges {
                        node { """
        + SpaceUser.to_graphql_fields()
        + """
                        }
                    }
                }
            }
        }
    }
    """
    )
    query_description = "Get all users with access to a space"

    class Variables(BaseVariables):
        spaceId: str
        first: int = 50
        search: Optional[str] = None
        userType: Optional[str] = None

    class QueryException(ArizeAPIException):
        message: str = "Error running query to retrieve space users"

    class QueryResponse(SpaceUser):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if "node" not in result or "spaceUsers" not in result["node"] or "edges" not in result["node"]["spaceUsers"]:
            cls.raise_exception("No space users found")
        space_users = result["node"]["spaceUsers"]
        page_info = space_users["pageInfo"]
        user_nodes = [cls.QueryResponse(**edge["node"]) for edge in space_users["edges"]]
        has_next_page = page_info["hasNextPage"]
        end_cursor = page_info["endCursor"]
        return (user_nodes, has_next_page, end_cursor)


class GetUserQuery(BaseQuery):
    graphql_query = (
        """
    query getUser($search: String!) {
        account {
            users(search: $search, first: 10) {
                edges {
                    node { """
        + AccountUser.to_graphql_fields()
        + """
                    }
                }
            }
        }
    }
    """
    )
    query_description = "Search for a user by name or email"

    class Variables(BaseVariables):
        search: str

    class QueryException(ArizeAPIException):
        message: str = "Error running query to retrieve user"

    class QueryResponse(AccountUser):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        variables = result.pop("__query_variables__", {})
        search_term = variables.get("search", "")
        if "account" not in result or "users" not in result["account"] or "edges" not in result["account"]["users"]:
            cls.raise_exception("Failed to retrieve user")
        edges = result["account"]["users"]["edges"]
        if len(edges) == 0:
            cls.raise_exception("No user found matching the search criteria")
        # Check for exact match on email first, then name
        user = cls._find_exact_name_match(edges, search_term, name_field="email")
        if user is None:
            user = cls._find_exact_name_match(edges, search_term, name_field="name")
        if user is None:
            cls.raise_exception(f"No user found with the exact name or email '{search_term}'")
        return ([cls.QueryResponse(**user)], False, None)
