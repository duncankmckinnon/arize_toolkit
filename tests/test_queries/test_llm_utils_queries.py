from datetime import datetime, timezone

import pytest

from arize_toolkit.exceptions import ArizeAPIException
from arize_toolkit.queries.llm_utils_queries import (
    CreateAnnotationMutation,
    CreatePromptMutation,
    CreatePromptVersionMutation,
    DeletePromptMutation,
    GetAllPromptVersionsQuery,
    GetPromptByIDQuery,
    GetPromptQuery,
    GetPromptVersionByIDQuery,
    UpdatePromptMutation,
)
from arize_toolkit.types import ExternalLLMProviderModel, LLMIntegrationProvider, PromptVersionInputVariableFormatEnum


@pytest.fixture
def mock_prompt():
    return {
        "id": "123",
        "name": "test",
        "description": "test",
        "tags": ["test"],
        "commitMessage": "test",
        "createdBy": {
            "id": "123",
            "name": "test",
            "email": "test@test.com",
        },
        "messages": [
            {
                "role": "user",
                "content": "test",
            }
        ],
        "inputVariableFormat": "f_string",
        "toolCalls": [
            {
                "id": "123",
                "name": "test",
                "description": "test",
                "parameters": "test",
                "function": {
                    "name": "test",
                    "description": "test",
                },
            }
        ],
        "llmParameters": {"test": "test"},
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-01T00:00:00Z",
        "provider": "openai",
        "modelName": "gpt-3.5-turbo",
    }


@pytest.fixture
def mock_prompt_version():
    return {
        "id": "123",
        "name": "test",
        "description": "test",
        "tags": ["test"],
        "messages": [{"role": "user", "content": "test"}],
        "inputVariableFormat": "f_string",
        "llmParameters": {"test": "test"},
        "createdAt": "2024-01-01T00:00:00Z",
        "provider": "openai",
        "modelName": "gpt-3.5-turbo",
        "commitMessage": "test",
    }


class TestCreateAnnotationMutation:
    @pytest.mark.parametrize(
        "annotations,model_environment,note",
        [
            (
                [
                    {
                        "annotationType": "label",
                        "label": "test",
                        "updatedBy": "test",
                        "name": "test",
                    },
                    {
                        "annotationType": "score",
                        "score": 0.5,
                        "updatedBy": "test",
                        "name": "test",
                    },
                ],
                "tracing",
                {"text": "test"},
            ),
            (
                {
                    "annotationType": "label",
                    "label": "test",
                    "updatedBy": "test",
                    "name": "test",
                },
                "production",
                None,
            ),
        ],
    )
    def test_create_annotation_mutation_success(self, gql_client, annotations, model_environment, note):
        mock_response = {"updateAnnotations": {"clientMutationId": None}}
        gql_client.execute.return_value = mock_response
        # Execute the query
        result = CreateAnnotationMutation.run_graphql_mutation(
            gql_client,
            modelId="123",
            annotations=annotations,
            recordId="123",
            startTime="2024-01-01T00:00:00Z",
            modelEnvironment=model_environment,
            note=note,
        )

        # Assertions
        assert result.success is True


class TestCreatePromptMutation:
    def test_create_prompt_mutation_success(self, gql_client, mock_prompt):
        # Mock the GraphQL response
        mock_response = {"createPrompt": {"prompt": mock_prompt}}
        gql_client.execute.return_value = mock_response

        # Execute the mutation
        result = CreatePromptMutation.run_graphql_mutation(
            gql_client,
            spaceId="space123",
            promptId="prompt123",
            name="test prompt",
            description="A test prompt",
            tags=["test", "prompt"],
            commitMessage="Initial version",
            messages=[{"role": "user", "content": "Tell me about {topic}"}],
            inputVariableFormat=PromptVersionInputVariableFormatEnum.F_STRING,
            provider=LLMIntegrationProvider.openAI,
            model="gpt-3.5-turbo",
        )

        # Assertions
        assert result.id == "123"
        assert result.name == "test"
        assert result.description == "test"
        assert result.tags == ["test"]
        assert result.messages == [{"role": "user", "content": "test"}]
        assert result.inputVariableFormat == PromptVersionInputVariableFormatEnum.F_STRING
        assert result.provider == LLMIntegrationProvider.openAI
        assert result.modelName == ExternalLLMProviderModel.GPT_3_5_TURBO
        assert isinstance(result.createdAt, datetime)
        assert isinstance(result.updatedAt, datetime)

    def test_create_prompt_mutation_failure(self, gql_client):
        # Mock a failed GraphQL response
        mock_response = {}  # Empty response to trigger exception
        gql_client.execute.return_value = mock_response

        # Execute the mutation and expect exception
        with pytest.raises(ArizeAPIException, match="Error in creating a prompt") as e:
            CreatePromptMutation.run_graphql_mutation(
                gql_client,
                spaceId="space123",
                promptId="prompt123",
                name="test prompt",
                commitMessage="Initial version",
                messages=[{"role": "user", "content": "Tell me about {topic}"}],
            )
        assert str(e.value).endswith("No prompt created")


class TestCreatePromptVersionMutation:
    def test_create_prompt_version_mutation_success(self, gql_client, mock_prompt_version):
        # Mock the GraphQL response
        mock_response = {"createPromptVersion": {"promptVersion": mock_prompt_version}}
        gql_client.execute.return_value = mock_response

        # Execute the mutation
        result = CreatePromptVersionMutation.run_graphql_mutation(
            gql_client,
            spaceId="space123",
            promptId="prompt123",
            commitMessage="Version 2",
            messages=[{"role": "user", "content": "Tell me about {topic} in detail"}],
            inputVariableFormat=PromptVersionInputVariableFormatEnum.F_STRING,
            provider=LLMIntegrationProvider.openAI,
            model="gpt-3.5-turbo",
        )

        # Assertions
        assert result.id == "123"
        assert result.commitMessage == "test"
        assert result.messages == [{"role": "user", "content": "test"}]
        assert result.inputVariableFormat == PromptVersionInputVariableFormatEnum.F_STRING
        assert result.provider == LLMIntegrationProvider.openAI
        assert result.modelName == ExternalLLMProviderModel.GPT_3_5_TURBO
        assert isinstance(result.createdAt, datetime)

    def test_create_prompt_version_mutation_failure(self, gql_client):
        # Mock a failed GraphQL response
        mock_response = {}  # Empty response to trigger exception
        gql_client.execute.return_value = mock_response

        # Execute the mutation and expect exception
        with pytest.raises(ArizeAPIException, match="Error in creating a prompt version") as e:
            CreatePromptVersionMutation.run_graphql_mutation(
                gql_client,
                spaceId="space123",
                promptId="prompt123",
                commitMessage="Version 2",
                messages=[{"role": "user", "content": "Tell me about {topic}"}],
            )
        assert str(e.value).endswith("No prompt version created")


class TestGetPromptByIDQuery:
    def test_get_prompt_by_id(self, gql_client, mock_prompt):
        mock_response = {"node": mock_prompt}
        gql_client.execute.return_value = mock_response
        result = GetPromptByIDQuery.run_graphql_query(gql_client, prompt_id="123")
        assert result.id == "123"
        assert result.name == "test"
        assert result.description == "test"
        assert result.tags == ["test"]
        assert result.createdBy.id == "123"
        assert result.createdBy.name == "test"
        assert result.createdBy.email == "test@test.com"
        assert result.messages == [{"role": "user", "content": "test"}]
        assert result.inputVariableFormat == PromptVersionInputVariableFormatEnum.F_STRING
        assert result.toolCalls == [
            {
                "id": "123",
                "name": "test",
                "description": "test",
                "parameters": "test",
                "function": {"name": "test", "description": "test"},
            }
        ]
        assert isinstance(result.createdAt, datetime)
        assert isinstance(result.updatedAt, datetime)
        assert result.commitMessage == "test"
        assert result.provider == LLMIntegrationProvider.openAI
        assert result.modelName == ExternalLLMProviderModel.GPT_3_5_TURBO

    def test_get_prompt_by_id_failure(self, gql_client):
        mock_response = {"node": None}
        gql_client.execute.return_value = mock_response
        with pytest.raises(ArizeAPIException, match="Error in getting a prompt by ID") as e:
            GetPromptByIDQuery.run_graphql_query(gql_client, prompt_id="123")
        assert str(e.value).endswith("Object not found")


class TestGetPromptQuery:
    def test_get_prompt(self, gql_client, mock_prompt):
        mock_response = {"node": {"prompts": {"edges": [{"node": mock_prompt}]}}}
        gql_client.execute.return_value = mock_response
        result = GetPromptQuery.run_graphql_query(gql_client, space_id="123", prompt_name="test")
        assert result.id == "123"
        assert result.name == "test"
        assert result.description == "test"
        assert result.tags == ["test"]
        assert result.createdBy.id == "123"
        assert result.createdBy.name == "test"
        assert result.createdBy.email == "test@test.com"
        assert result.messages == [{"role": "user", "content": "test"}]
        assert result.inputVariableFormat == PromptVersionInputVariableFormatEnum.F_STRING
        assert result.toolCalls == [
            {
                "id": "123",
                "name": "test",
                "description": "test",
                "parameters": "test",
                "function": {"name": "test", "description": "test"},
            }
        ]
        assert isinstance(result.createdAt, datetime)
        assert isinstance(result.updatedAt, datetime)
        assert result.commitMessage == "test"
        assert result.provider == LLMIntegrationProvider.openAI
        assert result.modelName == ExternalLLMProviderModel.GPT_3_5_TURBO

    def test_get_prompt_failure(self, gql_client):
        mock_response = {"node": {"prompts": {"edges": []}}}
        gql_client.execute.return_value = mock_response
        with pytest.raises(ArizeAPIException, match="Error in getting a prompt by name") as e:
            GetPromptQuery.run_graphql_query(gql_client, space_id="123", prompt_name="test")
        assert str(e.value).endswith("No prompts found")


class TestGetAllPromptVersionsQuery:
    def test_get_all_prompt_versions(self, gql_client, mock_prompt_version):
        prompt_version2 = mock_prompt_version.copy()
        prompt_version2.update(
            {
                "id": "1234",
                "commitMessage": "test2",
                "createdAt": "2024-01-02T00:00:00Z",
                "provider": "awsBedrock",
                "modelName": None,
            }
        )
        mock_response = [
            {
                "node": {
                    "prompts": {
                        "edges": [
                            {
                                "node": {
                                    "versionHistory": {
                                        "edges": [{"node": mock_prompt_version}],
                                        "pageInfo": {
                                            "hasNextPage": True,
                                            "endCursor": "123",
                                        },
                                    },
                                },
                            }
                        ]
                    }
                }
            },
            {
                "node": {
                    "prompts": {
                        "edges": [
                            {
                                "node": {
                                    "versionHistory": {
                                        "edges": [{"node": prompt_version2}],
                                        "pageInfo": {
                                            "hasNextPage": False,
                                            "endCursor": None,
                                        },
                                    }
                                }
                            }
                        ]
                    }
                }
            },
        ]
        gql_client.execute.side_effect = mock_response
        result = GetAllPromptVersionsQuery.iterate_over_pages(gql_client, space_id="123", prompt_name="test")
        assert len(result) == 2
        prompt_version1 = result[0]
        assert prompt_version1.id == "123"
        assert prompt_version1.commitMessage == "test"
        assert prompt_version1.createdAt == datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        assert prompt_version1.provider == LLMIntegrationProvider.openAI
        assert prompt_version1.modelName == ExternalLLMProviderModel.GPT_3_5_TURBO
        prompt_version2 = result[1]
        assert prompt_version2.id == "1234"
        assert prompt_version2.commitMessage == "test2"
        assert prompt_version2.createdAt == datetime(2024, 1, 2, 0, 0, 0, tzinfo=timezone.utc)
        assert prompt_version2.provider == LLMIntegrationProvider.awsBedrock
        assert prompt_version2.modelName is None

    def test_get_all_prompt_versions_failure(self, gql_client):
        mock_response = {"node": {"prompts": {"edges": []}}}
        gql_client.execute.return_value = mock_response
        with pytest.raises(ArizeAPIException, match="Error in getting all prompt versions"):
            GetAllPromptVersionsQuery.iterate_over_pages(gql_client, space_id="123", prompt_name="test")

    def test_get_all_prompt_versions_failure_no_prompts(self, gql_client):
        mock_response = {
            "node": {
                "prompts": {
                    "edges": [
                        {
                            "node": {
                                "versionHistory": {
                                    "pageInfo": {
                                        "hasNextPage": False,
                                        "endCursor": None,
                                    },
                                    "edges": [],
                                }
                            }
                        }
                    ]
                }
            }
        }
        gql_client.execute.return_value = mock_response
        with pytest.raises(ArizeAPIException, match="No versions found"):
            GetAllPromptVersionsQuery.iterate_over_pages(gql_client, space_id="123", prompt_name="test")


class TestGetPromptVersionByIDQuery:
    def test_get_prompt_version_by_id(self, gql_client, mock_prompt_version):
        mock_response = {"node": mock_prompt_version}
        gql_client.execute.return_value = mock_response
        result = GetPromptVersionByIDQuery.run_graphql_query(gql_client, prompt_version_id="123")
        assert result.id == "123"
        assert result.commitMessage == "test"
        assert result.createdAt == datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        assert result.provider == LLMIntegrationProvider.openAI
        assert result.modelName == ExternalLLMProviderModel.GPT_3_5_TURBO

    def test_get_prompt_version_by_id_failure(self, gql_client):
        mock_response = {"node": None}
        gql_client.execute.return_value = mock_response
        with pytest.raises(ArizeAPIException, match="Error in getting a prompt version by ID") as e:
            GetPromptVersionByIDQuery.run_graphql_query(gql_client, prompt_version_id="123")
        assert str(e.value).endswith("Object not found")


class TestUpdatePromptMutation:
    def test_update_prompt(self, gql_client, mock_prompt):
        mock_response = {"editPrompt": {"prompt": mock_prompt}}
        gql_client.execute.return_value = mock_response
        result = UpdatePromptMutation.run_graphql_mutation(
            gql_client,
            spaceId="123",
            promptId="123",
            name="test",
            description="test",
            tags=["test"],
        )
        assert result.id == "123"
        assert result.name == "test"
        assert result.description == "test"
        assert result.tags == ["test"]

    def test_update_prompt_failure(self, gql_client):
        mock_response = {"editPrompt": {"prompt": None}}
        gql_client.execute.return_value = mock_response
        with pytest.raises(ArizeAPIException, match="Error in updating a prompt"):
            UpdatePromptMutation.run_graphql_mutation(gql_client, spaceId="123", promptId="123")


class TestDeletePromptMutation:
    def test_delete_prompt(self, gql_client):
        mock_response = {"deletePrompt": {"success": True}}
        gql_client.execute.return_value = mock_response
        result = DeletePromptMutation.run_graphql_mutation(gql_client, spaceId="123", promptId="123")
        assert result.success is True

    def test_delete_prompt_failure(self, gql_client):
        mock_response = {"deletePrompt": None}
        gql_client.execute.return_value = mock_response
        with pytest.raises(ArizeAPIException, match="Error in deleting a prompt"):
            DeletePromptMutation.run_graphql_mutation(gql_client, spaceId="123", promptId="123")
