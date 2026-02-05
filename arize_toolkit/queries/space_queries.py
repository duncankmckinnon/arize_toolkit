from datetime import datetime
from typing import List, Optional, Tuple

from arize_toolkit.models.space_models import AccountUser, Organization, Space, SpaceMember, SpaceMemberInput
from arize_toolkit.queries.basequery import ArizeAPIException, BaseQuery, BaseResponse, BaseVariables


class OrgIDandSpaceIDQuery(BaseQuery):
    graphql_query = """
    query orgIDandSpaceID($organization: String!, $space: String!) {
        account {
            organizations(search: $organization, first: 1) {
                edges {
                    node {
                        id
                        spaces(search: $space, first: 1) {
                            edges {
                                node {
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
        if "account" not in result or "organizations" not in result["account"] or "edges" not in result["account"]["organizations"] or len(result["account"]["organizations"]["edges"]) == 0:
            cls.raise_exception("No organization found with the given name")
        node = result["account"]["organizations"]["edges"][0]["node"]
        organization_id = node["id"]
        if "spaces" not in node or "edges" not in node["spaces"] or len(node["spaces"]["edges"]) == 0:
            cls.raise_exception("No space found with the given name")
        space_id = node["spaces"]["edges"][0]["node"]["id"]
        return (
            [cls.QueryResponse(organization_id=organization_id, space_id=space_id)],
            False,
            None,
        )


class OrgAndFirstSpaceQuery(OrgIDandSpaceIDQuery):
    graphql_query = """
    query orgAndFirstSpace($organization: String!) {
        account {
            organizations(search: $organization, first: 1) {
                edges {
                    node {
                        id
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
        if "account" not in result or "organizations" not in result["account"] or "edges" not in result["account"]["organizations"] or len(result["account"]["organizations"]["edges"]) == 0:
            cls.raise_exception("No organization found with the given name")
        node = result["account"]["organizations"]["edges"][0]["node"]
        organization_id = node["id"]
        if "spaces" not in node or "edges" not in node["spaces"] or len(node["spaces"]["edges"]) == 0:
            cls.raise_exception("No spaces found in the organization")
        space_id = node["spaces"]["edges"][0]["node"]["id"]
        space_name = node["spaces"]["edges"][0]["node"]["name"]
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


class GetUserQuery(BaseQuery):
    graphql_query = (
        """
    query getUser($search: String!) {
        account {
            users(search: $search, first: 1) {
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
        if "account" not in result or "users" not in result["account"] or "edges" not in result["account"]["users"]:
            cls.raise_exception("Failed to retrieve user")
        edges = result["account"]["users"]["edges"]
        if len(edges) == 0:
            cls.raise_exception("No user found matching the search criteria")
        user = edges[0]["node"]
        return ([cls.QueryResponse(**user)], False, None)
