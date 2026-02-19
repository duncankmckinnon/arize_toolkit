from datetime import datetime

import pytest

from arize_toolkit.exceptions import ArizeAPIException
from arize_toolkit.models.evaluator_models import CodeEvaluationConfig
from arize_toolkit.queries.evaluator_queries import (
    CreateEvaluatorMutation,
    CreateEvaluatorVersionMutation,
    DeleteEvaluatorMutation,
    EditEvaluatorMutation,
    GetEvaluatorByNameQuery,
    GetEvaluatorQuery,
    GetEvaluatorsQuery,
)
from arize_toolkit.types import EvalDataGranularityType, TemplateEvaluationConfigDirection


@pytest.fixture
def mock_evaluator():
    return {
        "id": "eval123",
        "name": "Hallucination Detector",
        "description": "Detects hallucinations in LLM responses",
        "taskType": "template_evaluation",
        "commitHash": "abc123",
        "commitMessage": "Initial version",
        "tags": ["llm", "quality"],
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-02T00:00:00Z",
        "createdBy": {
            "id": "user123",
            "name": "Test User",
            "email": "test@example.com",
        },
    }


class TestGetEvaluatorsQuery:
    def test_get_evaluators_success(self, gql_client, mock_evaluator):
        """Test listing evaluators for a space."""
        mock_response = {
            "node": {
                "evaluators": {
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                    "edges": [{"node": mock_evaluator}],
                }
            }
        }
        gql_client.execute.return_value = mock_response

        results = GetEvaluatorsQuery.iterate_over_pages(
            gql_client,
            space_id="space123",
        )

        assert len(results) == 1
        assert results[0].id == "eval123"
        assert results[0].name == "Hallucination Detector"
        assert results[0].taskType.name == "template_evaluation"
        assert results[0].tags == ["llm", "quality"]

    def test_get_evaluators_empty(self, gql_client):
        """Test listing evaluators when none exist."""
        mock_response = {
            "node": {
                "evaluators": {
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                    "edges": [],
                }
            }
        }
        gql_client.execute.return_value = mock_response

        results = GetEvaluatorsQuery.iterate_over_pages(
            gql_client,
            space_id="space123",
        )

        assert len(results) == 0

    def test_get_evaluators_with_pagination(self, gql_client, mock_evaluator):
        """Test listing evaluators with pagination."""
        second_evaluator = {**mock_evaluator, "id": "eval456", "name": "Second Evaluator"}
        mock_response_page1 = {
            "node": {
                "evaluators": {
                    "pageInfo": {"hasNextPage": True, "endCursor": "cursor1"},
                    "edges": [{"node": mock_evaluator}],
                }
            }
        }
        mock_response_page2 = {
            "node": {
                "evaluators": {
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                    "edges": [{"node": second_evaluator}],
                }
            }
        }
        gql_client.execute.side_effect = [mock_response_page1, mock_response_page2]

        results = GetEvaluatorsQuery.iterate_over_pages(
            gql_client,
            space_id="space123",
        )

        assert len(results) == 2
        assert results[0].id == "eval123"
        assert results[1].id == "eval456"

    def test_get_evaluators_with_filters(self, gql_client, mock_evaluator):
        """Test listing evaluators with search and taskType filters."""
        mock_response = {
            "node": {
                "evaluators": {
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                    "edges": [{"node": mock_evaluator}],
                }
            }
        }
        gql_client.execute.return_value = mock_response

        results = GetEvaluatorsQuery.iterate_over_pages(
            gql_client,
            space_id="space123",
            search="hallucination",
            taskType="template_evaluation",
        )

        assert len(results) == 1

    def test_get_evaluators_space_not_found(self, gql_client):
        """Test listing evaluators when space not found."""
        mock_response = {"node": None}
        gql_client.execute.return_value = mock_response

        with pytest.raises(ArizeAPIException, match="Error getting evaluators"):
            GetEvaluatorsQuery.iterate_over_pages(
                gql_client,
                space_id="bad_space",
            )


class TestGetEvaluatorQuery:
    def test_query_structure(self):
        """Test that the query structure includes expected elements."""
        query = GetEvaluatorQuery.graphql_query
        assert "query getEvaluator" in query
        assert "$eval_id: ID!" in query
        assert "node(id: $eval_id)" in query
        assert "... on Evaluator" in query
        assert "id" in query
        assert "name" in query

    def test_get_evaluator_success(self, gql_client, mock_evaluator):
        """Test getting an evaluator by ID."""
        mock_response = {"node": mock_evaluator}
        gql_client.execute.return_value = mock_response

        result = GetEvaluatorQuery.run_graphql_query(
            gql_client,
            eval_id="eval123",
        )

        assert result.id == "eval123"
        assert result.name == "Hallucination Detector"
        assert result.description == "Detects hallucinations in LLM responses"
        assert result.taskType.name == "template_evaluation"
        assert result.commitHash == "abc123"
        assert result.commitMessage == "Initial version"
        assert result.tags == ["llm", "quality"]
        assert isinstance(result.createdAt, datetime)
        assert result.createdBy.id == "user123"
        assert result.createdBy.name == "Test User"
        gql_client.execute.assert_called_once()

    def test_get_evaluator_minimal_fields(self, gql_client):
        """Test getting an evaluator with only required fields."""
        mock_response = {"node": {"id": "eval_min", "name": "Minimal Evaluator"}}
        gql_client.execute.return_value = mock_response

        result = GetEvaluatorQuery.run_graphql_query(
            gql_client,
            eval_id="eval_min",
        )

        assert result.id == "eval_min"
        assert result.name == "Minimal Evaluator"
        assert result.description is None
        assert result.tags is None

    def test_get_evaluator_not_found(self, gql_client):
        """Test error when evaluator node is None."""
        mock_response = {"node": None}
        gql_client.execute.return_value = mock_response

        with pytest.raises(ArizeAPIException, match="Error getting evaluator by id"):
            GetEvaluatorQuery.run_graphql_query(
                gql_client,
                eval_id="nonexistent",
            )

    def test_get_evaluator_missing_node(self, gql_client):
        """Test error when node key is missing from response."""
        mock_response = {}
        gql_client.execute.return_value = mock_response

        with pytest.raises(ArizeAPIException, match="Error getting evaluator by id"):
            GetEvaluatorQuery.run_graphql_query(
                gql_client,
                eval_id="nonexistent",
            )


class TestGetEvaluatorByNameQuery:
    def test_get_evaluator_by_name_success(self, gql_client, mock_evaluator):
        """Test getting an evaluator by name."""
        mock_response = {
            "node": {
                "evaluators": {
                    "edges": [{"node": mock_evaluator}],
                }
            }
        }
        gql_client.execute.return_value = mock_response

        result = GetEvaluatorByNameQuery.run_graphql_query(
            gql_client,
            space_id="space123",
            name="Hallucination Detector",
        )

        assert result.id == "eval123"
        assert result.name == "Hallucination Detector"
        assert result.commitHash == "abc123"

    def test_get_evaluator_by_name_not_found(self, gql_client):
        """Test getting an evaluator that doesn't exist."""
        mock_response = {
            "node": {
                "evaluators": {
                    "edges": [],
                }
            }
        }
        gql_client.execute.return_value = mock_response

        with pytest.raises(ArizeAPIException, match="Error getting evaluator by name"):
            GetEvaluatorByNameQuery.run_graphql_query(
                gql_client,
                space_id="space123",
                name="Nonexistent",
            )


class TestCreateEvaluatorMutation:
    def test_create_template_evaluator_success(self, gql_client, mock_evaluator):
        """Test creating a template (LLM-based) evaluator successfully."""
        mock_response = {"createEvaluator": {"evaluator": mock_evaluator}}
        gql_client.execute.return_value = mock_response

        result = CreateEvaluatorMutation.run_graphql_mutation(
            gql_client,
            spaceId="space123",
            name="Hallucination Detector",
            description="Detects hallucinations in LLM responses",
            commitMessage="Initial version",
            templateEvaluator={
                "name": "hallucination_score",
                "template": "Does the response contain any factual errors?\n\nContext: {{context}}\nResponse: {{output}}",
                "position": 0,
                "includeExplanations": True,
                "useFunctionCallingIfAvailable": True,
                "classificationChoices": {"Yes": 0, "No": 1},
                "direction": TemplateEvaluationConfigDirection.maximize,
                "dataGranularityType": EvalDataGranularityType.span,
            },
        )

        assert result.id == "eval123"
        assert result.name == "Hallucination Detector"
        assert result.description == "Detects hallucinations in LLM responses"
        assert isinstance(result.createdAt, datetime)
        assert result.createdBy.id == "user123"
        assert result.createdBy.name == "Test User"

    def test_create_template_evaluator_with_llm_config(self, gql_client, mock_evaluator):
        """Test creating a template evaluator with custom LLM config."""
        mock_response = {"createEvaluator": {"evaluator": mock_evaluator}}
        gql_client.execute.return_value = mock_response

        result = CreateEvaluatorMutation.run_graphql_mutation(
            gql_client,
            spaceId="space123",
            name="Custom LLM Evaluator",
            commitMessage="Initial version",
            templateEvaluator={
                "name": "custom_score",
                "template": "Evaluate: {{output}}",
                "position": 0,
                "includeExplanations": True,
                "useFunctionCallingIfAvailable": True,
                "llmConfig": {
                    "integrationId": "integration123",
                    "modelName": "gpt-4o",
                    "invocationParameters": {"temperature": 0.0},
                    "providerParameters": {"api_key": "test"},
                },
            },
        )

        assert result.id == "eval123"

    def test_create_template_evaluator_with_rails(self, gql_client, mock_evaluator):
        """Test creating a template evaluator with rails."""
        mock_response = {"createEvaluator": {"evaluator": mock_evaluator}}
        gql_client.execute.return_value = mock_response

        result = CreateEvaluatorMutation.run_graphql_mutation(
            gql_client,
            spaceId="space123",
            name="Rails Evaluator",
            commitMessage="Initial version",
            templateEvaluator={
                "name": "rails_score",
                "template": "Is this safe? {{output}}",
                "position": 0,
                "includeExplanations": True,
                "useFunctionCallingIfAvailable": True,
                "rails": ["safe", "unsafe"],
            },
        )

        assert result.id == "eval123"

    def test_create_code_evaluator_success(self, gql_client, mock_evaluator):
        """Test creating a code (Python-based) evaluator successfully."""
        mock_response = {"createEvaluator": {"evaluator": mock_evaluator}}
        gql_client.execute.return_value = mock_response

        code_block = """class ResponseLengthEvaluator(CodeEvaluator):
    def evaluate(self, *, dataset_row=None, **kwargs):
        output = dataset_row.get("attributes.output.value") if dataset_row else None
        length = len(output) if output else 0
        if length < 50:
            return EvaluationResult(score=0, label="too_short")
        elif length > 500:
            return EvaluationResult(score=0, label="too_long")
        else:
            return EvaluationResult(score=1, label="appropriate")"""

        result = CreateEvaluatorMutation.run_graphql_mutation(
            gql_client,
            spaceId="space123",
            name="Response Length Checker",
            description="Checks if response length is appropriate",
            commitMessage="Initial version",
            codeEvaluator={
                "name": "response_length_score",
                "evalClassCodeBlock": code_block,
                "evaluationClass": "ResponseLengthEvaluator",
                "position": 0,
                "spanAttributes": ["output"],
                "dataGranularityType": EvalDataGranularityType.span,
            },
        )

        assert result.id == "eval123"
        assert isinstance(result.createdAt, datetime)

    def test_create_code_evaluator_with_package_imports(self, gql_client, mock_evaluator):
        """Test creating a code evaluator with package imports."""
        mock_response = {"createEvaluator": {"evaluator": mock_evaluator}}
        gql_client.execute.return_value = mock_response

        result = CreateEvaluatorMutation.run_graphql_mutation(
            gql_client,
            spaceId="space123",
            name="Advanced Evaluator",
            commitMessage="Initial version",
            codeEvaluator={
                "name": "advanced_score",
                "evalClassCodeBlock": "class Eval(CodeEvaluator):\n    def evaluate(self, **kwargs):\n        pass",
                "evaluationClass": "Eval",
                "position": 0,
                "packageImports": "import numpy as np",
                "evaluationInputParams": {"threshold": 0.5},
                "spanAttributes": ["output"],
            },
        )

        assert result.id == "eval123"

    def test_create_evaluator_with_tags(self, gql_client, mock_evaluator):
        """Test creating an evaluator with tags."""
        mock_response = {"createEvaluator": {"evaluator": mock_evaluator}}
        gql_client.execute.return_value = mock_response

        result = CreateEvaluatorMutation.run_graphql_mutation(
            gql_client,
            spaceId="space123",
            name="Tagged Evaluator",
            commitMessage="Initial version",
            tags=["llm", "quality", "production"],
            templateEvaluator={
                "name": "tagged_score",
                "template": "Evaluate: {{output}}",
                "position": 0,
                "includeExplanations": True,
                "useFunctionCallingIfAvailable": True,
            },
        )

        assert result.id == "eval123"

    def test_create_evaluator_no_response(self, gql_client):
        """Test creating an evaluator with missing createEvaluator in response."""
        gql_client.execute.return_value = {}

        with pytest.raises(ArizeAPIException, match="Error in creating an evaluator") as e:
            CreateEvaluatorMutation.run_graphql_mutation(
                gql_client,
                spaceId="space123",
                name="Test Evaluator",
                commitMessage="Initial version",
                templateEvaluator={
                    "name": "test_score",
                    "template": "Test template",
                    "dataGranularityType": EvalDataGranularityType.span,
                },
            )
        assert str(e.value).endswith("No evaluator created")

    def test_create_evaluator_null_evaluator(self, gql_client):
        """Test creating an evaluator with null evaluator in response."""
        gql_client.execute.return_value = {"createEvaluator": {"evaluator": None}}

        with pytest.raises(ArizeAPIException, match="Error in creating an evaluator") as e:
            CreateEvaluatorMutation.run_graphql_mutation(
                gql_client,
                spaceId="space123",
                name="Test Evaluator",
                commitMessage="Initial version",
                templateEvaluator={
                    "name": "test_score",
                    "template": "Test template",
                },
            )
        assert str(e.value).endswith("No evaluator returned in response")

    @pytest.mark.parametrize(
        "direction,granularity",
        [
            (TemplateEvaluationConfigDirection.maximize, EvalDataGranularityType.span),
            (TemplateEvaluationConfigDirection.minimize, EvalDataGranularityType.trace),
            (TemplateEvaluationConfigDirection.maximize, EvalDataGranularityType.session),
        ],
    )
    def test_create_evaluator_different_configs(self, gql_client, mock_evaluator, direction, granularity):
        """Test creating evaluators with different direction and granularity configurations."""
        mock_response = {"createEvaluator": {"evaluator": mock_evaluator}}
        gql_client.execute.return_value = mock_response

        result = CreateEvaluatorMutation.run_graphql_mutation(
            gql_client,
            spaceId="space123",
            name="Test Evaluator",
            commitMessage="Initial version",
            templateEvaluator={
                "name": "test_score",
                "template": "Test template",
                "direction": direction,
                "dataGranularityType": granularity,
            },
        )

        assert result.id == "eval123"


class TestCreateEvaluatorVersionMutation:
    def test_create_version_success(self, gql_client, mock_evaluator):
        """Test creating a new version of an evaluator."""
        mock_response = {"createEvaluatorVersion": {"evaluator": mock_evaluator}}
        gql_client.execute.return_value = mock_response

        result = CreateEvaluatorVersionMutation.run_graphql_mutation(
            gql_client,
            evaluatorId="eval123",
            commitMessage="Updated template",
            templateEvaluator={
                "name": "hallucination_score",
                "template": "Updated template: {{output}}",
                "position": 0,
                "includeExplanations": True,
                "useFunctionCallingIfAvailable": True,
            },
        )

        assert result.id == "eval123"
        assert result.name == "Hallucination Detector"

    def test_create_version_no_response(self, gql_client):
        """Test creating a version with missing response."""
        gql_client.execute.return_value = {}

        with pytest.raises(ArizeAPIException, match="Error in creating an evaluator version") as e:
            CreateEvaluatorVersionMutation.run_graphql_mutation(
                gql_client,
                evaluatorId="eval123",
                commitMessage="Updated",
                templateEvaluator={
                    "name": "test_score",
                    "template": "Test",
                    "position": 0,
                    "includeExplanations": True,
                    "useFunctionCallingIfAvailable": True,
                },
            )
        assert str(e.value).endswith("No evaluator version created")


class TestEditEvaluatorMutation:
    def test_edit_evaluator_success(self, gql_client, mock_evaluator):
        """Test editing an evaluator's metadata."""
        updated = {**mock_evaluator, "name": "Updated Name", "description": "Updated desc"}
        mock_response = {"editEvaluator": {"evaluator": updated}}
        gql_client.execute.return_value = mock_response

        result = EditEvaluatorMutation.run_graphql_mutation(
            gql_client,
            evaluatorId="eval123",
            name="Updated Name",
            description="Updated desc",
        )

        assert result.id == "eval123"
        assert result.name == "Updated Name"
        assert result.description == "Updated desc"

    def test_edit_evaluator_tags(self, gql_client, mock_evaluator):
        """Test editing an evaluator's tags."""
        updated = {**mock_evaluator, "tags": ["new-tag"]}
        mock_response = {"editEvaluator": {"evaluator": updated}}
        gql_client.execute.return_value = mock_response

        result = EditEvaluatorMutation.run_graphql_mutation(
            gql_client,
            evaluatorId="eval123",
            tags=["new-tag"],
        )

        assert result.tags == ["new-tag"]

    def test_edit_evaluator_no_response(self, gql_client):
        """Test editing an evaluator with missing response."""
        gql_client.execute.return_value = {}

        with pytest.raises(ArizeAPIException, match="Error in editing an evaluator") as e:
            EditEvaluatorMutation.run_graphql_mutation(
                gql_client,
                evaluatorId="eval123",
                name="New Name",
            )
        assert str(e.value).endswith("No evaluator edited")


class TestDeleteEvaluatorMutation:
    def test_delete_evaluator_success(self, gql_client):
        """Test deleting an evaluator."""
        mock_response = {"deleteEvaluator": {"success": True}}
        gql_client.execute.return_value = mock_response

        result = DeleteEvaluatorMutation.run_graphql_mutation(
            gql_client,
            evaluatorId="eval123",
        )

        assert result.success is True

    def test_delete_evaluator_failure(self, gql_client):
        """Test deleting an evaluator that fails."""
        mock_response = {"deleteEvaluator": {"success": False}}
        gql_client.execute.return_value = mock_response

        with pytest.raises(ArizeAPIException, match="Error in deleting an evaluator") as e:
            DeleteEvaluatorMutation.run_graphql_mutation(
                gql_client,
                evaluatorId="eval123",
            )
        assert str(e.value).endswith("Failed to delete evaluator")

    def test_delete_evaluator_no_response(self, gql_client):
        """Test deleting an evaluator with missing response."""
        gql_client.execute.return_value = {}

        with pytest.raises(ArizeAPIException, match="Error in deleting an evaluator") as e:
            DeleteEvaluatorMutation.run_graphql_mutation(
                gql_client,
                evaluatorId="eval123",
            )
        assert str(e.value).endswith("No response from delete evaluator")


class TestCodeEvaluationConfigValidation:
    """Tests for CodeEvaluationConfig model validation."""

    def _valid_code_block(self, class_name="MyEvaluator"):
        return f"""class {class_name}(CodeEvaluator):
    def evaluate(self, *, dataset_row=None, **kwargs):
        return EvaluationResult(score=1.0, label="pass")"""

    def test_valid_code_evaluator(self):
        """Test that a valid code evaluator config passes validation."""
        config = CodeEvaluationConfig(
            name="test_metric",
            evalClassCodeBlock=self._valid_code_block(),
            evaluationClass="MyEvaluator",
            spanAttributes=["output"],
        )
        assert config.evaluationClass == "MyEvaluator"

    def test_valid_code_evaluator_with_underscore_class_name(self):
        """Test that class names with underscores are accepted."""
        config = CodeEvaluationConfig(
            name="test_metric",
            evalClassCodeBlock=self._valid_code_block("My_Custom_Evaluator"),
            evaluationClass="My_Custom_Evaluator",
            spanAttributes=["output"],
        )
        assert config.evaluationClass == "My_Custom_Evaluator"

    def test_missing_code_evaluator_base_class(self):
        """Test that code block without CodeEvaluator base class fails."""
        bad_code = """class MyEvaluator:
    def evaluate(self, **kwargs):
        pass"""
        with pytest.raises(ValueError, match="must define a class that extends CodeEvaluator"):
            CodeEvaluationConfig(
                name="test_metric",
                evalClassCodeBlock=bad_code,
                evaluationClass="MyEvaluator",
                spanAttributes=["output"],
            )

    def test_evaluation_class_mismatch(self):
        """Test that evaluationClass not matching code block class fails."""
        with pytest.raises(ValueError, match="does not match any CodeEvaluator subclass"):
            CodeEvaluationConfig(
                name="test_metric",
                evalClassCodeBlock=self._valid_code_block("ActualEvaluator"),
                evaluationClass="WrongName",
                spanAttributes=["output"],
            )

    def test_missing_evaluate_method(self):
        """Test that code block without evaluate method fails."""
        bad_code = """class MyEvaluator(CodeEvaluator):
    def run(self, **kwargs):
        pass"""
        with pytest.raises(ValueError, match="must define an 'evaluate' method"):
            CodeEvaluationConfig(
                name="test_metric",
                evalClassCodeBlock=bad_code,
                evaluationClass="MyEvaluator",
                spanAttributes=["output"],
            )

    def test_invalid_package_imports(self):
        """Test that non-import lines in packageImports fails."""
        with pytest.raises(ValueError, match="must contain only valid Python import statements"):
            CodeEvaluationConfig(
                name="test_metric",
                evalClassCodeBlock=self._valid_code_block(),
                evaluationClass="MyEvaluator",
                spanAttributes=["output"],
                packageImports="x = 1",
            )

    def test_valid_package_imports_simple(self):
        """Test that valid simple imports pass."""
        config = CodeEvaluationConfig(
            name="test_metric",
            evalClassCodeBlock=self._valid_code_block(),
            evaluationClass="MyEvaluator",
            spanAttributes=["output"],
            packageImports="import numpy as np",
        )
        assert config.packageImports == "import numpy as np"

    def test_valid_package_imports_from(self):
        """Test that valid from-imports pass."""
        config = CodeEvaluationConfig(
            name="test_metric",
            evalClassCodeBlock=self._valid_code_block(),
            evaluationClass="MyEvaluator",
            spanAttributes=["output"],
            packageImports="from typing import Any, Optional, Mapping",
        )
        assert config.packageImports is not None

    def test_valid_package_imports_multiline_parens(self):
        """Test that multi-line parenthesized imports pass."""
        imports = """from arize.experimental.datasets.experiments.evaluators.base import (
    EvaluationResult,
    CodeEvaluator,
    JSONSerializable,
)"""
        config = CodeEvaluationConfig(
            name="test_metric",
            evalClassCodeBlock=self._valid_code_block(),
            evaluationClass="MyEvaluator",
            spanAttributes=["output"],
            packageImports=imports,
        )
        assert config.packageImports is not None

    def test_valid_package_imports_with_comments(self):
        """Test that imports with comments pass."""
        imports = """# Required imports
import numpy as np
from collections import defaultdict"""
        config = CodeEvaluationConfig(
            name="test_metric",
            evalClassCodeBlock=self._valid_code_block(),
            evaluationClass="MyEvaluator",
            spanAttributes=["output"],
            packageImports=imports,
        )
        assert config.packageImports is not None

    def test_missing_span_attributes(self):
        """Test that missing spanAttributes fails."""
        with pytest.raises(ValueError, match="spanAttributes is required"):
            CodeEvaluationConfig(
                name="test_metric",
                evalClassCodeBlock=self._valid_code_block(),
                evaluationClass="MyEvaluator",
            )

    def test_empty_span_attributes(self):
        """Test that empty spanAttributes list fails."""
        with pytest.raises(ValueError, match="spanAttributes is required"):
            CodeEvaluationConfig(
                name="test_metric",
                evalClassCodeBlock=self._valid_code_block(),
                evaluationClass="MyEvaluator",
                spanAttributes=[],
            )

    def test_skip_validation_when_id_present(self):
        """Test that validation is skipped for API responses (id is set)."""
        config = CodeEvaluationConfig(
            id="existing-id",
            name="test_metric",
        )
        assert config.id == "existing-id"

    def test_multiple_span_attributes(self):
        """Test that multiple span attributes are accepted."""
        config = CodeEvaluationConfig(
            name="test_metric",
            evalClassCodeBlock=self._valid_code_block(),
            evaluationClass="MyEvaluator",
            spanAttributes=["output", "input"],
        )
        assert config.spanAttributes == ["output", "input"]
