from datetime import datetime

import pytest

from arize_toolkit.queries.space_queries import (
    CreateNewOrganizationMutation,
    CreateNewSpaceMutation,
    CreateSpaceAdminApiKeyMutation,
    GetAllOrganizationsQuery,
    GetAllSpacesQuery,
    GetSpaceByIdQuery,
    GetSpaceByNameQuery,
    OrgAndFirstSpaceQuery,
    OrgIDandSpaceIDQuery,
)


class TestOrgIDandSpaceIDQuery:
    """Test the OrgIDandSpaceIDQuery class."""

    def test_query_structure(self):
        """Test that the query structure is correct."""
        query = OrgIDandSpaceIDQuery.graphql_query
        assert "query orgIDandSpaceID" in query
        assert "$organization: String!" in query
        assert "$space: String!" in query
        assert "account" in query
        assert "organizations" in query
        assert "spaces" in query

    def test_successful_query(self, gql_client):
        """Test successful organization and space ID lookup."""
        mock_response = {
            "account": {
                "organizations": {
                    "edges": [
                        {
                            "node": {
                                "id": "org_123",
                                "spaces": {"edges": [{"node": {"id": "space_456"}}]},
                            }
                        }
                    ]
                }
            }
        }
        gql_client.execute.return_value = mock_response

        result = OrgIDandSpaceIDQuery.run_graphql_query(gql_client, organization="test_org", space="test_space")

        assert result.organization_id == "org_123"
        assert result.space_id == "space_456"
        gql_client.execute.assert_called_once()

    def test_organization_not_found(self, gql_client):
        """Test error when organization is not found."""
        mock_response = {"account": {"organizations": {"edges": []}}}
        gql_client.execute.return_value = mock_response

        with pytest.raises(
            OrgIDandSpaceIDQuery.QueryException,
            match="No organization found with the given name",
        ):
            OrgIDandSpaceIDQuery.run_graphql_query(gql_client, organization="nonexistent_org", space="test_space")

        gql_client.execute.assert_called_once()

    def test_space_not_found(self, gql_client):
        """Test error when space is not found."""
        mock_response = {"account": {"organizations": {"edges": [{"node": {"id": "org_123", "spaces": {"edges": []}}}]}}}
        gql_client.execute.return_value = mock_response

        with pytest.raises(
            OrgIDandSpaceIDQuery.QueryException,
            match="No space found with the given name",
        ):
            OrgIDandSpaceIDQuery.run_graphql_query(gql_client, organization="test_org", space="nonexistent_space")

        gql_client.execute.assert_called_once()

    def test_variables_validation(self):
        """Test input validation for required variables."""
        # Test missing organization
        with pytest.raises(Exception) as exc_info:
            OrgIDandSpaceIDQuery.Variables(space="test_space")
        assert "organization" in str(exc_info.value)

        # Test missing space
        with pytest.raises(Exception) as exc_info:
            OrgIDandSpaceIDQuery.Variables(organization="test_org")
        assert "space" in str(exc_info.value)

        # Test valid variables
        variables = OrgIDandSpaceIDQuery.Variables(organization="test_org", space="test_space")
        assert variables.organization == "test_org"
        assert variables.space == "test_space"


class TestOrgAndFirstSpaceQuery:
    """Test the OrgAndFirstSpaceQuery class."""

    def test_query_structure(self):
        """Test that the query structure is correct."""
        query = OrgAndFirstSpaceQuery.graphql_query
        assert "query orgAndFirstSpace" in query
        assert "$organization: String!" in query
        assert "account" in query
        assert "organizations" in query
        assert "spaces(first: 1)" in query

    def test_successful_query(self, gql_client):
        """Test successful organization and first space lookup."""
        mock_response = {
            "account": {
                "organizations": {
                    "edges": [
                        {
                            "node": {
                                "id": "org_789",
                                "spaces": {
                                    "edges": [
                                        {
                                            "node": {
                                                "id": "space_first",
                                                "name": "First Space",
                                            }
                                        }
                                    ]
                                },
                            }
                        }
                    ]
                }
            }
        }
        gql_client.execute.return_value = mock_response

        result = OrgAndFirstSpaceQuery.run_graphql_query(gql_client, organization="test_org")

        assert result.organization_id == "org_789"
        assert result.space_id == "space_first"
        assert result.space_name == "First Space"
        gql_client.execute.assert_called_once()

    def test_no_spaces_in_organization(self, gql_client):
        """Test error when organization has no spaces."""
        mock_response = {"account": {"organizations": {"edges": [{"node": {"id": "org_123", "spaces": {"edges": []}}}]}}}
        gql_client.execute.return_value = mock_response

        with pytest.raises(
            OrgAndFirstSpaceQuery.QueryException,
            match="No spaces found in the organization",
        ):
            OrgAndFirstSpaceQuery.run_graphql_query(gql_client, organization="empty_org")

        gql_client.execute.assert_called_once()

    def test_variables_validation(self):
        """Test input validation for required variables."""
        # Test missing organization
        with pytest.raises(Exception) as exc_info:
            OrgAndFirstSpaceQuery.Variables()
        assert "organization" in str(exc_info.value)

        # Test valid variables
        variables = OrgAndFirstSpaceQuery.Variables(organization="test_org")
        assert variables.organization == "test_org"


class TestGetSpaceByNameQuery:
    """Test the GetSpaceByNameQuery class."""

    def test_query_structure(self):
        """Test that the query structure is correct."""
        query = GetSpaceByNameQuery.graphql_query
        assert "query getSpaceByName" in query
        assert "$organization_id: ID!" in query
        assert "$spaceName: String!" in query
        assert "node(id: $organization_id)" in query
        assert "spaces(search: $spaceName, first: 1)" in query

    def test_successful_query(self, gql_client):
        """Test successful space retrieval by name."""
        mock_response = {
            "node": {
                "spaces": {
                    "edges": [
                        {
                            "node": {
                                "id": "space_123",
                                "name": "Production Space",
                                "createdAt": "2024-01-01T00:00:00Z",
                                "description": "Main production space",
                                "private": False,
                            }
                        }
                    ]
                }
            }
        }
        gql_client.execute.return_value = mock_response

        result = GetSpaceByNameQuery.run_graphql_query(gql_client, organization_id="org_123", spaceName="Production Space")

        assert result.id == "space_123"
        assert result.name == "Production Space"
        assert result.description == "Main production space"
        assert result.private is False
        gql_client.execute.assert_called_once()

    def test_space_not_found(self, gql_client):
        """Test error when no space matches the name."""
        mock_response = {"node": {"spaces": {"edges": []}}}
        gql_client.execute.return_value = mock_response

        with pytest.raises(
            GetSpaceByNameQuery.QueryException,
            match="No space found matching the given name",
        ):
            GetSpaceByNameQuery.run_graphql_query(gql_client, organization_id="org_123", spaceName="nonexistent")

        gql_client.execute.assert_called_once()

    def test_missing_spaces_structure(self, gql_client):
        """Test error when spaces structure is missing."""
        mock_response = {"node": {}}
        gql_client.execute.return_value = mock_response

        with pytest.raises(
            GetSpaceByNameQuery.QueryException,
            match="No spaces found",
        ):
            GetSpaceByNameQuery.run_graphql_query(gql_client, organization_id="org_123", spaceName="test")

        gql_client.execute.assert_called_once()

    def test_variables_validation(self):
        """Test input validation for required variables."""
        # Test missing organization_id
        with pytest.raises(Exception) as exc_info:
            GetSpaceByNameQuery.Variables(spaceName="test")
        assert "organization_id" in str(exc_info.value)

        # Test missing spaceName
        with pytest.raises(Exception) as exc_info:
            GetSpaceByNameQuery.Variables(organization_id="org_123")
        assert "spaceName" in str(exc_info.value)

        # Test valid variables
        variables = GetSpaceByNameQuery.Variables(organization_id="org_123", spaceName="test")
        assert variables.organization_id == "org_123"
        assert variables.spaceName == "test"


class TestGetSpaceByIdQuery:
    """Test the GetSpaceByIdQuery class."""

    def test_query_structure(self):
        """Test that the query structure is correct."""
        query = GetSpaceByIdQuery.graphql_query
        assert "query getSpaceById" in query
        assert "$spaceId: ID!" in query
        assert "node(id: $spaceId)" in query
        assert "... on Space" in query

    def test_successful_query(self, gql_client):
        """Test successful space retrieval by ID."""
        mock_response = {
            "node": {
                "id": "space_456",
                "name": "Dev Space",
                "createdAt": "2024-02-01T00:00:00Z",
                "description": "Development space",
                "private": True,
            }
        }
        gql_client.execute.return_value = mock_response

        result = GetSpaceByIdQuery.run_graphql_query(gql_client, spaceId="space_456")

        assert result.id == "space_456"
        assert result.name == "Dev Space"
        assert result.description == "Development space"
        assert result.private is True
        gql_client.execute.assert_called_once()

    def test_space_not_found(self, gql_client):
        """Test error when space ID does not exist."""
        mock_response = {"node": None}
        gql_client.execute.return_value = mock_response

        with pytest.raises(
            GetSpaceByIdQuery.QueryException,
            match="Object not found",
        ):
            GetSpaceByIdQuery.run_graphql_query(gql_client, spaceId="nonexistent_id")

        gql_client.execute.assert_called_once()

    def test_variables_validation(self):
        """Test input validation for required variables."""
        # Test missing spaceId
        with pytest.raises(Exception) as exc_info:
            GetSpaceByIdQuery.Variables()
        assert "spaceId" in str(exc_info.value)

        # Test valid variables
        variables = GetSpaceByIdQuery.Variables(spaceId="space_456")
        assert variables.spaceId == "space_456"


class TestGetAllSpacesQuery:
    """Test the GetAllSpacesQuery class."""

    def test_query_structure(self):
        """Test that the query structure is correct."""
        query = GetAllSpacesQuery.graphql_query
        assert "query getAllSpaces" in query
        assert "$organization_id: ID!" in query
        assert "$endCursor: String" in query
        assert "node(id: $organization_id)" in query
        assert "spaces(first: 10, after: $endCursor)" in query
        assert "pageInfo" in query

    def test_successful_query_single_page(self, gql_client):
        """Test successful spaces retrieval with single page."""
        mock_response = {
            "node": {
                "spaces": {
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                    "edges": [
                        {
                            "node": {
                                "id": "space_1",
                                "name": "Production Space",
                                "createdAt": "2024-01-01T00:00:00Z",
                                "description": "Main production space",
                                "private": False,
                            }
                        },
                        {
                            "node": {
                                "id": "space_2",
                                "name": "Dev Space",
                                "createdAt": "2024-01-02T00:00:00Z",
                                "description": "Development space",
                                "private": True,
                            }
                        },
                    ],
                }
            }
        }
        gql_client.execute.return_value = mock_response

        results = list(GetAllSpacesQuery.iterate_over_pages(gql_client, organization_id="org_123"))

        assert len(results) == 2
        assert results[0].id == "space_1"
        assert results[0].name == "Production Space"
        assert results[0].description == "Main production space"
        assert results[0].private is False
        assert results[1].id == "space_2"
        assert results[1].name == "Dev Space"
        assert results[1].description == "Development space"
        assert results[1].private is True
        gql_client.execute.assert_called_once()

    def test_successful_query_with_pagination(self, gql_client):
        """Test successful spaces retrieval with pagination."""
        mock_responses = [
            {
                "node": {
                    "spaces": {
                        "pageInfo": {"hasNextPage": True, "endCursor": "cursor_123"},
                        "edges": [
                            {
                                "node": {
                                    "id": "space_1",
                                    "name": "Space 1",
                                    "createdAt": "2024-01-01T00:00:00Z",
                                    "description": "First space",
                                    "private": False,
                                }
                            }
                        ],
                    }
                }
            },
            {
                "node": {
                    "spaces": {
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                        "edges": [
                            {
                                "node": {
                                    "id": "space_2",
                                    "name": "Space 2",
                                    "createdAt": "2024-01-02T00:00:00Z",
                                    "description": "Second space",
                                    "private": True,
                                }
                            }
                        ],
                    }
                }
            },
        ]
        gql_client.execute.side_effect = mock_responses

        results = list(GetAllSpacesQuery.iterate_over_pages(gql_client, organization_id="org_123"))

        assert len(results) == 2
        assert results[0].id == "space_1"
        assert results[1].id == "space_2"
        assert gql_client.execute.call_count == 2

    def test_no_spaces_found(self, gql_client):
        """Test error when no spaces are found."""
        mock_response = {"node": {}}
        gql_client.execute.return_value = mock_response

        with pytest.raises(GetAllSpacesQuery.QueryException, match="No spaces found"):
            list(GetAllSpacesQuery.iterate_over_pages(gql_client, organization_id="org_123"))

        gql_client.execute.assert_called_once()

    def test_variables_validation(self):
        """Test input validation for required variables."""
        # Test missing organization_id
        with pytest.raises(Exception) as exc_info:
            GetAllSpacesQuery.Variables()
        assert "organization_id" in str(exc_info.value)

        # Test valid variables
        variables = GetAllSpacesQuery.Variables(organization_id="org_123")
        assert variables.organization_id == "org_123"


class TestGetAllOrganizationsQuery:
    """Test the GetAllOrganizationsQuery class."""

    def test_query_structure(self):
        """Test that the query structure is correct."""
        query = GetAllOrganizationsQuery.graphql_query
        assert "query getAllOrganizations" in query
        assert "$endCursor: String" in query
        assert "account" in query
        assert "organizations(first: 10, after: $endCursor)" in query
        assert "pageInfo" in query

    def test_successful_query_single_page(self, gql_client):
        """Test successful organizations retrieval with single page."""
        mock_response = {
            "account": {
                "organizations": {
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                    "edges": [
                        {
                            "node": {
                                "id": "org_1",
                                "name": "Production Org",
                                "createdAt": "2024-01-01T00:00:00Z",
                                "description": "Main production organization",
                            }
                        },
                        {
                            "node": {
                                "id": "org_2",
                                "name": "Dev Org",
                                "createdAt": "2024-01-02T00:00:00Z",
                                "description": "Development organization",
                            }
                        },
                    ],
                }
            }
        }
        gql_client.execute.return_value = mock_response

        results = list(GetAllOrganizationsQuery.iterate_over_pages(gql_client))

        assert len(results) == 2
        assert results[0].id == "org_1"
        assert results[0].name == "Production Org"
        assert results[0].description == "Main production organization"
        assert results[1].id == "org_2"
        assert results[1].name == "Dev Org"
        assert results[1].description == "Development organization"
        gql_client.execute.assert_called_once()

    def test_successful_query_with_pagination(self, gql_client):
        """Test successful organizations retrieval with pagination."""
        mock_responses = [
            {
                "account": {
                    "organizations": {
                        "pageInfo": {"hasNextPage": True, "endCursor": "cursor_456"},
                        "edges": [
                            {
                                "node": {
                                    "id": "org_1",
                                    "name": "Organization 1",
                                    "createdAt": "2024-01-01T00:00:00Z",
                                    "description": "First organization",
                                }
                            }
                        ],
                    }
                }
            },
            {
                "account": {
                    "organizations": {
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                        "edges": [
                            {
                                "node": {
                                    "id": "org_2",
                                    "name": "Organization 2",
                                    "createdAt": "2024-01-02T00:00:00Z",
                                    "description": "Second organization",
                                }
                            }
                        ],
                    }
                }
            },
        ]
        gql_client.execute.side_effect = mock_responses

        results = list(GetAllOrganizationsQuery.iterate_over_pages(gql_client))

        assert len(results) == 2
        assert results[0].id == "org_1"
        assert results[1].id == "org_2"
        assert gql_client.execute.call_count == 2

    def test_no_organizations_found(self, gql_client):
        """Test behavior when no organizations are found."""
        mock_response = {
            "account": {
                "organizations": {
                    "pageInfo": {
                        "hasNextPage": False,
                        "endCursor": None,
                    },
                    "edges": [],
                }
            }
        }
        gql_client.execute.return_value = mock_response

        results = list(GetAllOrganizationsQuery.iterate_over_pages(gql_client))

        # Should return empty list, not raise exception
        assert len(results) == 0
        gql_client.execute.assert_called_once()

    def test_missing_account_structure(self, gql_client):
        """Test error when account structure is missing."""
        mock_response = {}
        gql_client.execute.return_value = mock_response

        with pytest.raises(GetAllOrganizationsQuery.QueryException, match="No organizations found"):
            list(GetAllOrganizationsQuery.iterate_over_pages(gql_client))

        gql_client.execute.assert_called_once()

    def test_variables_validation(self):
        """Test input validation for variables."""
        # GetAllOrganizationsQuery has no required variables
        variables = GetAllOrganizationsQuery.Variables()
        assert hasattr(variables, "__dict__")


class TestQueryIntegration:
    """Test integration scenarios between different space queries."""

    def test_organization_to_space_workflow(self, gql_client):
        """Test workflow: get organization ID, then get its spaces."""
        # Mock responses for the workflow
        mock_responses = [
            # First: get org ID and first space
            {
                "account": {
                    "organizations": {
                        "edges": [
                            {
                                "node": {
                                    "id": "org_workflow_123",
                                    "spaces": {
                                        "edges": [
                                            {
                                                "node": {
                                                    "id": "space_workflow_456",
                                                    "name": "Main Space",
                                                }
                                            },
                                            {
                                                "node": {
                                                    "id": "space_workflow_789",
                                                    "name": "Secondary Space",
                                                }
                                            },
                                        ]
                                    },
                                }
                            }
                        ]
                    }
                }
            },
            # Then: get all spaces in that org
            {
                "node": {
                    "spaces": {
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                        "edges": [
                            {
                                "node": {
                                    "id": "space_workflow_456",
                                    "name": "Main Space",
                                    "createdAt": "2024-01-01T00:00:00Z",
                                    "description": "Main space",
                                    "private": False,
                                }
                            },
                            {
                                "node": {
                                    "id": "space_workflow_789",
                                    "name": "Secondary Space",
                                    "createdAt": "2024-01-02T00:00:00Z",
                                    "description": "Secondary space",
                                    "private": True,
                                }
                            },
                        ],
                    }
                }
            },
        ]
        gql_client.execute.side_effect = mock_responses

        # Step 1: Get organization and first space
        org_result = OrgAndFirstSpaceQuery.run_graphql_query(gql_client, organization="workflow_org")
        assert org_result.organization_id == "org_workflow_123"
        assert org_result.space_id == "space_workflow_456"
        assert org_result.space_name == "Main Space"

        # Step 2: Get all spaces in that organization
        spaces = list(GetAllSpacesQuery.iterate_over_pages(gql_client, organization_id=org_result.organization_id))
        assert len(spaces) == 2
        assert spaces[0].id == "space_workflow_456"
        assert spaces[0].name == "Main Space"
        assert spaces[1].id == "space_workflow_789"
        assert spaces[1].name == "Secondary Space"

        # Verify both calls were made
        assert gql_client.execute.call_count == 2


class TestCreateNewOrganizationMutation:
    """Test the CreateNewOrganizationMutation class."""

    def test_mutation_structure(self):
        """Test that the mutation structure is correct."""
        mutation = CreateNewOrganizationMutation.graphql_query
        assert "mutation createNewOrganization" in mutation
        assert "$input: CreateOrganizationMutationInput!" in mutation
        assert "createOrganization" in mutation
        assert "input: $input" in mutation
        assert "organization" in mutation
        assert "id" in mutation

    def test_successful_mutation(self, gql_client):
        """Test successful organization creation."""
        mock_response = {"createOrganization": {"organization": {"id": "org_new_123"}}}
        gql_client.execute.return_value = mock_response

        result = CreateNewOrganizationMutation.run_graphql_mutation(gql_client, name="Test Organization", description="A test organization")

        assert result.id == "org_new_123"
        gql_client.execute.assert_called_once()

    def test_successful_mutation_without_description(self, gql_client):
        """Test successful organization creation without description."""
        mock_response = {"createOrganization": {"organization": {"id": "org_new_456"}}}
        gql_client.execute.return_value = mock_response

        result = CreateNewOrganizationMutation.run_graphql_mutation(gql_client, name="Test Organization")

        assert result.id == "org_new_456"
        gql_client.execute.assert_called_once()

    def test_failed_mutation_no_create_organization(self, gql_client):
        """Test error when createOrganization is not in response."""
        mock_response = {}
        gql_client.execute.return_value = mock_response

        with pytest.raises(
            CreateNewOrganizationMutation.QueryException,
            match="Failed to create organization",
        ):
            CreateNewOrganizationMutation.run_graphql_mutation(gql_client, name="Test Organization")

        gql_client.execute.assert_called_once()

    def test_failed_mutation_no_organization_in_response(self, gql_client):
        """Test error when organization is not in createOrganization response."""
        mock_response = {"createOrganization": {}}
        gql_client.execute.return_value = mock_response

        with pytest.raises(
            CreateNewOrganizationMutation.QueryException,
            match="Failed to create organization",
        ):
            CreateNewOrganizationMutation.run_graphql_mutation(gql_client, name="Test Organization")

        gql_client.execute.assert_called_once()

    def test_variables_validation(self):
        """Test input validation for required variables."""
        # Test missing name
        with pytest.raises(Exception) as exc_info:
            CreateNewOrganizationMutation.Variables(description="A description")
        assert "name" in str(exc_info.value)

        # Test valid variables with description
        variables = CreateNewOrganizationMutation.Variables(name="Test Organization", description="A test organization")
        assert variables.name == "Test Organization"
        assert variables.description == "A test organization"

        # Test valid variables without description
        variables_no_desc = CreateNewOrganizationMutation.Variables(name="Test Organization")
        assert variables_no_desc.name == "Test Organization"
        assert variables_no_desc.description is None


class TestCreateNewSpaceMutation:
    """Test the CreateNewSpaceMutation class."""

    def test_mutation_structure(self):
        """Test that the mutation structure is correct."""
        mutation = CreateNewSpaceMutation.graphql_query
        assert "mutation createNewSpace" in mutation
        assert "$input: CreateSpaceMutationInput!" in mutation
        assert "createSpace" in mutation
        assert "input: $input" in mutation

    def test_successful_mutation(self, gql_client):
        """Test successful space creation."""
        mock_response = {"createSpace": {"space": {"name": "Test Space", "id": "space_new_123"}}}
        gql_client.execute.return_value = mock_response

        result = CreateNewSpaceMutation.run_graphql_mutation(gql_client, accountOrganizationId="org_123", name="Test Space", private=True)

        assert result.name == "Test Space"
        assert result.id == "space_new_123"
        gql_client.execute.assert_called_once()

    def test_failed_mutation_no_create_space(self, gql_client):
        """Test error when createSpace is not in response."""
        mock_response = {}
        gql_client.execute.return_value = mock_response

        with pytest.raises(
            CreateNewSpaceMutation.QueryException,
            match="Failed to create space",
        ):
            CreateNewSpaceMutation.run_graphql_mutation(
                gql_client,
                accountOrganizationId="org_123",
                name="Test Space",
                private=True,
            )

        gql_client.execute.assert_called_once()

    def test_failed_mutation_no_space_in_response(self, gql_client):
        """Test error when space is not in createSpace response."""
        mock_response = {"createSpace": {}}
        gql_client.execute.return_value = mock_response

        with pytest.raises(
            CreateNewSpaceMutation.QueryException,
            match="Failed to create space",
        ):
            CreateNewSpaceMutation.run_graphql_mutation(
                gql_client,
                accountOrganizationId="org_123",
                name="Test Space",
                private=True,
            )

        gql_client.execute.assert_called_once()

    def test_variables_validation(self):
        """Test input validation for required variables."""
        # Test missing accountOrganizationId
        with pytest.raises(Exception) as exc_info:
            CreateNewSpaceMutation.Variables(name="Test Space", private=True)
        assert "accountOrganizationId" in str(exc_info.value)

        # Test missing name
        with pytest.raises(Exception) as exc_info:
            CreateNewSpaceMutation.Variables(accountOrganizationId="org_123", private=True)
        assert "name" in str(exc_info.value)

        # Test missing private
        with pytest.raises(Exception) as exc_info:
            CreateNewSpaceMutation.Variables(accountOrganizationId="org_123", name="Test Space")
        assert "private" in str(exc_info.value)

        # Test valid variables
        variables = CreateNewSpaceMutation.Variables(accountOrganizationId="org_123", name="Test Space", private=True)
        assert variables.accountOrganizationId == "org_123"
        assert variables.name == "Test Space"
        assert variables.private is True

        # Test with private=False
        variables_public = CreateNewSpaceMutation.Variables(accountOrganizationId="org_456", name="Public Space", private=False)
        assert variables_public.accountOrganizationId == "org_456"
        assert variables_public.name == "Public Space"
        assert variables_public.private is False


class TestCreateSpaceAdminApiKeyMutation:
    """Test the CreateSpaceAdminApiKeyMutation class."""

    def test_mutation_structure(self):
        """Test that the mutation structure is correct."""
        mutation = CreateSpaceAdminApiKeyMutation.graphql_query
        assert "mutation createSpaceAdminApiKey" in mutation
        assert "$input: CreateServiceApiKeyInput!" in mutation
        assert "createServiceApiKey" in mutation
        assert "input: $input" in mutation
        assert "apiKey" in mutation
        assert "keyInfo" in mutation

    def test_successful_mutation(self, gql_client):
        """Test successful API key creation."""
        mock_response = {
            "createServiceApiKey": {
                "apiKey": "sk_test_1234567890abcdef",
                "keyInfo": {"expiresAt": "2024-12-31T23:59:59Z", "id": "key_id_123"},
            }
        }
        gql_client.execute.return_value = mock_response

        result = CreateSpaceAdminApiKeyMutation.run_graphql_mutation(gql_client, name="Test Admin Key", spaceId="space_123")

        assert result.apiKey == "sk_test_1234567890abcdef"
        assert result.expiresAt == datetime.strptime("2024-12-31T23:59:59Z", "%Y-%m-%dT%H:%M:%S%z")
        assert result.id == "key_id_123"
        gql_client.execute.assert_called_once()

    def test_successful_mutation_no_expiration(self, gql_client):
        """Test successful API key creation without expiration date."""
        mock_response = {
            "createServiceApiKey": {
                "apiKey": "sk_test_abcdef1234567890",
                "keyInfo": {"expiresAt": None, "id": "key_id_456"},
            }
        }
        gql_client.execute.return_value = mock_response

        result = CreateSpaceAdminApiKeyMutation.run_graphql_mutation(gql_client, name="Permanent Admin Key", spaceId="space_456")

        assert result.apiKey == "sk_test_abcdef1234567890"
        assert result.expiresAt is None
        assert result.id == "key_id_456"
        gql_client.execute.assert_called_once()

    def test_failed_mutation_no_create_service_api_key(self, gql_client):
        """Test error when createServiceApiKey is not in response."""
        mock_response = {}
        gql_client.execute.return_value = mock_response

        with pytest.raises(
            CreateSpaceAdminApiKeyMutation.QueryException,
            match="Failed to create space admin API key",
        ):
            CreateSpaceAdminApiKeyMutation.run_graphql_mutation(gql_client, name="Test Admin Key", spaceId="space_123")

        gql_client.execute.assert_called_once()

    def test_failed_mutation_missing_api_key(self, gql_client):
        """Test error when apiKey is missing from response."""
        mock_response = {"createServiceApiKey": {"keyInfo": {"expiresAt": "2024-12-31T23:59:59Z", "id": "key_id_123"}}}
        gql_client.execute.return_value = mock_response

        with pytest.raises(
            CreateSpaceAdminApiKeyMutation.QueryException,
            match="Failed to create space admin API key",
        ):
            CreateSpaceAdminApiKeyMutation.run_graphql_mutation(gql_client, name="Test Admin Key", spaceId="space_123")

        gql_client.execute.assert_called_once()

    def test_failed_mutation_missing_key_info(self, gql_client):
        """Test error when keyInfo is missing from response."""
        mock_response = {"createServiceApiKey": {"apiKey": "sk_test_1234567890abcdef"}}
        gql_client.execute.return_value = mock_response

        with pytest.raises(
            CreateSpaceAdminApiKeyMutation.QueryException,
            match="Failed to create space admin API key",
        ):
            CreateSpaceAdminApiKeyMutation.run_graphql_mutation(gql_client, name="Test Admin Key", spaceId="space_123")

        gql_client.execute.assert_called_once()

    def test_variables_validation(self):
        """Test input validation for required variables."""
        # Test missing name
        with pytest.raises(Exception) as exc_info:
            CreateSpaceAdminApiKeyMutation.Variables(spaceId="space_123")
        assert "name" in str(exc_info.value)

        # Test missing spaceId
        with pytest.raises(Exception) as exc_info:
            CreateSpaceAdminApiKeyMutation.Variables(name="Test Admin Key")
        assert "spaceId" in str(exc_info.value)

        # Test valid variables
        variables = CreateSpaceAdminApiKeyMutation.Variables(name="Test Admin Key", spaceId="space_123")
        assert variables.name == "Test Admin Key"
        assert variables.spaceId == "space_123"
