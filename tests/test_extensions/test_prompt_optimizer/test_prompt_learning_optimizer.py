"""Tests for PromptLearningOptimizer class."""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest


class TestPromptLearningOptimizer:
    """Test suite for PromptLearningOptimizer."""

    @pytest.fixture
    def sample_dataset(self):
        """Create a sample dataset for testing."""
        return pd.DataFrame(
            {
                "question": ["What is 2+2?", "What is the capital of France?"],
                "answer": ["4", "Paris"],
                "correct": [True, True],
                "score": [1.0, 1.0],
            }
        )

    @pytest.fixture
    def sample_prompt_messages(self):
        """Create sample prompt messages."""
        return [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Answer: {question}"},
        ]

    @patch(
        "arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer.get_key_value"
    )
    def test_init_basic(self, mock_get_key):
        """Test basic initialization."""
        mock_get_key.return_value = MagicMock(get_secret_value=lambda: "test-api-key")

        from arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer import (
            PromptLearningOptimizer,
        )

        optimizer = PromptLearningOptimizer(
            prompt="Answer: {question}",
            model_choice="gpt-4",
        )

        assert optimizer.prompt == "Answer: {question}"
        assert optimizer.model_choice == "gpt-4"
        assert optimizer.optimization_history == []

    @patch(
        "arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer.get_key_value"
    )
    def test_init_with_custom_model(self, mock_get_key):
        """Test initialization with custom model."""
        mock_get_key.return_value = MagicMock(get_secret_value=lambda: "test-api-key")

        from arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer import (
            PromptLearningOptimizer,
        )

        optimizer = PromptLearningOptimizer(
            prompt="Test prompt",
            model_choice="gpt-4o",
            openai_api_key="custom-key",
        )

        assert optimizer.model_choice == "gpt-4o"

    @patch(
        "arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer.get_key_value"
    )
    def test_load_dataset_from_dataframe(self, mock_get_key, sample_dataset):
        """Test loading dataset from DataFrame."""
        mock_get_key.return_value = MagicMock(get_secret_value=lambda: "test-api-key")

        from arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer import (
            PromptLearningOptimizer,
        )

        optimizer = PromptLearningOptimizer(prompt="Test")

        result = optimizer._load_dataset(sample_dataset)
        assert result.equals(sample_dataset)

    @patch(
        "arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer.get_key_value"
    )
    def test_load_dataset_from_json(self, mock_get_key, tmp_path):
        """Test loading dataset from JSON file."""
        mock_get_key.return_value = MagicMock(get_secret_value=lambda: "test-api-key")

        # Create a temporary JSON file
        json_file = tmp_path / "test_data.json"
        df = pd.DataFrame(
            {"question": ["test"], "answer": ["response"], "feedback": [1]}
        )
        df.to_json(json_file)

        from arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer import (
            PromptLearningOptimizer,
        )

        optimizer = PromptLearningOptimizer(prompt="Test")

        result = optimizer._load_dataset(str(json_file))
        assert len(result) == 1
        assert result["question"].iloc[0] == "test"

    @patch(
        "arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer.get_key_value"
    )
    def test_validate_inputs_with_feedback_columns(self, mock_get_key, sample_dataset):
        """Test input validation with feedback columns."""
        mock_get_key.return_value = MagicMock(get_secret_value=lambda: "test-api-key")

        from arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer import (
            PromptLearningOptimizer,
        )

        optimizer = PromptLearningOptimizer(prompt="Test")

        # Should pass with feedback columns
        optimizer._validate_inputs(
            dataset=sample_dataset,
            feedback_columns=["correct", "score"],
            output_column="answer",
            output_required=True,
        )

        # Should fail without feedback columns or evaluators
        with pytest.raises(ValueError, match="Either feedback_columns or evaluators"):
            optimizer._validate_inputs(
                dataset=sample_dataset,
                feedback_columns=[],
                evaluators=[],
            )

        # Should fail with missing columns
        with pytest.raises(ValueError, match="Dataset missing required columns"):
            optimizer._validate_inputs(
                dataset=sample_dataset,
                feedback_columns=["missing_column"],
            )

    @patch(
        "arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer.get_key_value"
    )
    def test_validate_inputs_with_evaluators(self, mock_get_key, sample_dataset):
        """Test input validation with evaluators."""
        mock_get_key.return_value = MagicMock(get_secret_value=lambda: "test-api-key")

        from arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer import (
            PromptLearningOptimizer,
        )

        optimizer = PromptLearningOptimizer(prompt="Test")

        # Should pass with evaluators (no feedback columns needed)
        optimizer._validate_inputs(
            dataset=sample_dataset,
            evaluators=[lambda x: x],
            output_column="answer",
            output_required=True,
        )

    @patch(
        "arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer.get_key_value"
    )
    def test_extract_prompt_messages_from_list(
        self, mock_get_key, sample_prompt_messages
    ):
        """Test extracting messages from list."""
        mock_get_key.return_value = MagicMock(get_secret_value=lambda: "test-api-key")

        from arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer import (
            PromptLearningOptimizer,
        )

        optimizer = PromptLearningOptimizer(prompt=sample_prompt_messages)

        messages = optimizer._extract_prompt_messages()
        assert messages == sample_prompt_messages

    @patch(
        "arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer.get_key_value"
    )
    def test_extract_prompt_messages_from_string(self, mock_get_key):
        """Test extracting messages from string."""
        mock_get_key.return_value = MagicMock(get_secret_value=lambda: "test-api-key")

        from arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer import (
            PromptLearningOptimizer,
        )

        optimizer = PromptLearningOptimizer(prompt="Simple prompt")

        messages = optimizer._extract_prompt_messages()
        assert messages == [{"role": "user", "content": "Simple prompt"}]

    @patch(
        "arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer.get_key_value"
    )
    def test_extract_prompt_messages_from_prompt_version(self, mock_get_key):
        """Test extracting messages from PromptVersion object."""
        mock_get_key.return_value = MagicMock(get_secret_value=lambda: "test-api-key")

        # Skip this test if phoenix is not available
        try:
            from phoenix.client.types import PromptVersion
        except ImportError:
            pytest.skip("phoenix not available")

        from arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer import (
            PromptLearningOptimizer,
        )

        # Create a real PromptVersion instance
        prompt_version = PromptVersion(
            [{"role": "user", "content": "Test prompt"}],
            model_name="gpt-4o-mini",
        )

        optimizer = PromptLearningOptimizer(prompt=prompt_version)

        messages = optimizer._extract_prompt_messages()
        assert messages == [{"role": "user", "content": "Test prompt"}]

    @patch(
        "arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer.get_key_value"
    )
    def test_extract_prompt_content(self, mock_get_key, sample_prompt_messages):
        """Test extracting prompt content from messages."""
        mock_get_key.return_value = MagicMock(get_secret_value=lambda: "test-api-key")

        from arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer import (
            PromptLearningOptimizer,
        )

        optimizer = PromptLearningOptimizer(prompt=sample_prompt_messages)

        content = optimizer._extract_prompt_content()
        assert content == "Answer: {question}"

    @patch(
        "arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer.get_key_value"
    )
    def test_detect_template_variables(self, mock_get_key):
        """Test template variable detection."""
        mock_get_key.return_value = MagicMock(get_secret_value=lambda: "test-api-key")

        from arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer import (
            PromptLearningOptimizer,
        )

        optimizer = PromptLearningOptimizer(
            prompt="Hello {name}, your age is {age} and {name} again"
        )

        variables = optimizer._detect_template_variables(
            "Hello {name}, your age is {age}"
        )
        assert set(variables) == {"name", "age"}

        # Test with no variables
        variables = optimizer._detect_template_variables("No variables here")
        assert variables == []

    @patch(
        "arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer.get_key_value"
    )
    def test_run_evaluators_standalone(self, mock_get_key, sample_dataset):
        """Test running evaluators as standalone method."""
        mock_get_key.return_value = MagicMock(get_secret_value=lambda: "test-api-key")

        # Mock evaluator
        def mock_evaluator(df):
            feedback_df = pd.DataFrame({"evaluation": ["good", "excellent"]})
            return feedback_df, ["evaluation"]

        from arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer import (
            PromptLearningOptimizer,
        )

        optimizer = PromptLearningOptimizer(prompt="Test")

        # Run evaluators separately
        result_df, feedback_columns = optimizer.run_evaluators(
            dataset=sample_dataset.copy(),
            evaluators=[mock_evaluator],
        )

        assert "evaluation" in result_df.columns
        assert result_df["evaluation"].tolist() == ["good", "excellent"]
        assert "evaluation" in feedback_columns

    @patch(
        "arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer.get_key_value"
    )
    def test_run_evaluators_with_existing_feedback(self, mock_get_key, sample_dataset):
        """Test running evaluators with existing feedback columns."""
        mock_get_key.return_value = MagicMock(get_secret_value=lambda: "test-api-key")

        # Mock evaluator
        def mock_evaluator(df):
            feedback_df = pd.DataFrame({"new_eval": ["pass", "pass"]})
            return feedback_df, ["new_eval"]

        from arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer import (
            PromptLearningOptimizer,
        )

        optimizer = PromptLearningOptimizer(prompt="Test")

        # Run evaluators with existing feedback columns
        result_df, feedback_columns = optimizer.run_evaluators(
            dataset=sample_dataset.copy(),
            evaluators=[mock_evaluator],
            feedback_columns=["correct", "score"],
        )

        assert "new_eval" in result_df.columns
        assert set(feedback_columns) == {"correct", "score", "new_eval"}

    @patch(
        "arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer.get_key_value"
    )
    def test_run_evaluators_error_handling(self, mock_get_key, sample_dataset):
        """Test error handling in run_evaluators."""
        mock_get_key.return_value = MagicMock(get_secret_value=lambda: "test-api-key")

        # Mock evaluator that raises error
        def failing_evaluator(df):
            raise Exception("Evaluator failed")

        from arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer import (
            PromptLearningOptimizer,
        )

        optimizer = PromptLearningOptimizer(prompt="Test")

        # Should not raise, but print warning
        result_df, feedback_columns = optimizer.run_evaluators(
            dataset=sample_dataset.copy(),
            evaluators=[failing_evaluator],
            feedback_columns=["correct"],
        )

        # Original columns should remain
        assert "correct" in feedback_columns
        assert len(feedback_columns) == 1

    @patch(
        "arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer.OpenAIModel"
    )
    @patch(
        "arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer.TiktokenSplitter"
    )
    @patch(
        "arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer.get_key_value"
    )
    def test_optimize_basic(
        self, mock_get_key, mock_splitter, mock_openai_model, sample_dataset
    ):
        """Test basic optimize functionality."""
        mock_get_key.return_value = MagicMock(get_secret_value=lambda: "test-api-key")

        # Mock tiktoken splitter
        mock_splitter_instance = MagicMock()
        mock_splitter_instance.get_batch_dataframes.return_value = [
            pd.DataFrame(
                {
                    "question": ["What is 2+2?"],
                    "answer": ["4"],
                    "correct": [True],
                    "score": [1.0],
                }
            )
        ]
        mock_splitter.return_value = mock_splitter_instance

        # Mock OpenAI model
        mock_model_instance = MagicMock()
        mock_model_instance.return_value = "Improved prompt: {question}"
        mock_openai_model.return_value = mock_model_instance

        from arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer import (
            PromptLearningOptimizer,
        )

        optimizer = PromptLearningOptimizer(prompt="Answer: {question}")

        optimized_prompt = optimizer.optimize(
            dataset=sample_dataset,
            output_column="answer",
            feedback_columns=["correct", "score"],
            context_size_k=8000,
        )

        # Verify the optimization was called
        assert mock_splitter_instance.get_batch_dataframes.called
        assert mock_model_instance.called

        # Verify the result
        assert optimized_prompt == "Improved prompt: {question}"

    @patch(
        "arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer.OpenAIModel"
    )
    @patch(
        "arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer.TiktokenSplitter"
    )
    @patch(
        "arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer.get_key_value"
    )
    def test_optimize_with_evaluators(
        self, mock_get_key, mock_splitter, mock_openai_model, sample_dataset
    ):
        """Test optimize with evaluators."""
        mock_get_key.return_value = MagicMock(get_secret_value=lambda: "test-api-key")

        # Mock evaluator
        def mock_evaluator(df):
            feedback_df = pd.DataFrame({"auto_eval": ["good", "good"]})
            return feedback_df, ["auto_eval"]

        # Create a copy of sample dataset with the evaluator column
        test_dataset = sample_dataset.copy()
        test_dataset["auto_eval"] = ["good", "good"]

        # Mock tiktoken splitter
        mock_splitter_instance = MagicMock()
        mock_splitter_instance.get_batch_dataframes.return_value = [test_dataset]
        mock_splitter.return_value = mock_splitter_instance

        # Mock OpenAI model
        mock_model_instance = MagicMock()
        mock_model_instance.return_value = "Improved: {question}"
        mock_openai_model.return_value = mock_model_instance

        from arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer import (
            PromptLearningOptimizer,
        )

        optimizer = PromptLearningOptimizer(prompt="Answer: {question}")

        optimized_prompt = optimizer.optimize(
            dataset=sample_dataset.copy(),
            output_column="answer",
            evaluators=[mock_evaluator],
        )

        # Verify the result
        assert optimized_prompt == "Improved: {question}"

    @patch(
        "arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer.get_key_value"
    )
    def test_create_optimized_prompt_from_string(self, mock_get_key):
        """Test creating optimized prompt from string input."""
        mock_get_key.return_value = MagicMock(get_secret_value=lambda: "test-api-key")

        from arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer import (
            PromptLearningOptimizer,
        )

        optimizer = PromptLearningOptimizer(prompt="Original prompt")

        result = optimizer._create_optimized_prompt("Optimized prompt")
        assert result == "Optimized prompt"

    @patch(
        "arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer.get_key_value"
    )
    def test_create_optimized_prompt_from_list(self, mock_get_key):
        """Test creating optimized prompt from list input."""
        mock_get_key.return_value = MagicMock(get_secret_value=lambda: "test-api-key")

        from arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer import (
            PromptLearningOptimizer,
        )

        original_messages = [
            {"role": "system", "content": "System message"},
            {"role": "user", "content": "Original user prompt"},
        ]

        optimizer = PromptLearningOptimizer(prompt=original_messages)

        result = optimizer._create_optimized_prompt("Optimized user prompt")

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["content"] == "System message"
        assert result[1]["content"] == "Optimized user prompt"

    @patch(
        "arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer.get_key_value"
    )
    def test_create_optimized_prompt_from_prompt_version(self, mock_get_key):
        """Test creating optimized prompt from PromptVersion input."""
        mock_get_key.return_value = MagicMock(get_secret_value=lambda: "test-api-key")

        # Skip this test if phoenix is not available
        try:
            from phoenix.client.types import PromptVersion
        except ImportError:
            pytest.skip("phoenix not available")

        from arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer import (
            PromptLearningOptimizer,
        )

        # Create a real PromptVersion instance
        original_prompt = PromptVersion(
            [{"role": "user", "content": "Original prompt"}],
            model_name="gpt-4",
            model_provider="OPENAI",
        )

        optimizer = PromptLearningOptimizer(prompt=original_prompt)

        result = optimizer._create_optimized_prompt("Optimized prompt")

        # Verify the result is a PromptVersion
        assert isinstance(result, PromptVersion)

        # Verify the content was updated
        assert result._template["messages"][0]["content"] == "Optimized prompt"
        assert result._model_name == "gpt-4"
        assert result._model_provider == "OPENAI"

    @patch(
        "arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer.get_key_value"
    )
    def test_create_dummy_dataframe(self, mock_get_key):
        """Test creation of dummy dataframe for template variables."""
        mock_get_key.return_value = MagicMock(get_secret_value=lambda: "test-api-key")

        from arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer import (
            PromptLearningOptimizer,
        )

        optimizer = PromptLearningOptimizer(
            prompt="Hello {name}, your {attribute} is {value}"
        )

        optimizer.template_variables = ["name", "attribute", "value"]
        dummy_df = optimizer._create_dummy_dataframe()

        assert "var" in dummy_df.columns
        assert dummy_df["var"].iloc[0] == "{var}"
        assert dummy_df["name"].iloc[0] == "{name}"
        assert dummy_df["attribute"].iloc[0] == "{attribute}"
        assert dummy_df["value"].iloc[0] == "{value}"

    @patch(
        "arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer.OpenAIModel"
    )
    @patch(
        "arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer.TiktokenSplitter"
    )
    @patch(
        "arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer.get_key_value"
    )
    def test_optimize_error_handling(
        self, mock_get_key, mock_splitter, mock_openai_model
    ):
        """Test error handling in optimize method."""
        mock_get_key.return_value = MagicMock(get_secret_value=lambda: "test-api-key")

        # Mock tiktoken splitter
        mock_splitter_instance = MagicMock()
        mock_splitter_instance.get_batch_dataframes.return_value = [
            pd.DataFrame({"q": ["test"], "a": ["ans"], "f": [1]})
        ]
        mock_splitter.return_value = mock_splitter_instance

        # Mock OpenAI model to raise an error
        mock_model_instance = MagicMock()
        mock_model_instance.side_effect = Exception("API Error")
        mock_openai_model.return_value = mock_model_instance

        from arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer import (
            PromptLearningOptimizer,
        )

        optimizer = PromptLearningOptimizer(prompt="Test: {q}")

        # Should not raise, but return original prompt
        optimized_prompt = optimizer.optimize(
            dataset=pd.DataFrame({"q": ["test"], "a": ["ans"], "f": [1]}),
            output_column="a",
            feedback_columns=["f"],
        )
        assert optimized_prompt == "Test: {q}"

    @patch(
        "arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer.get_key_value"
    )
    def test_optimize_json_file_input(self, mock_get_key, tmp_path):
        """Test optimize with JSON file input."""
        mock_get_key.return_value = MagicMock(get_secret_value=lambda: "test-api-key")

        # Create test data
        json_file = tmp_path / "test_data.json"
        df = pd.DataFrame(
            {
                "question": ["What is 2+2?"],
                "answer": ["4"],
                "feedback": ["correct"],
            }
        )
        df.to_json(json_file)

        from arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer import (
            PromptLearningOptimizer,
        )

        optimizer = PromptLearningOptimizer(prompt="Test: {question}")

        # Mock the optimization process
        with patch.object(
            optimizer, "_extract_prompt_content", return_value="Test: {question}"
        ):
            with patch.object(
                optimizer, "_detect_template_variables", return_value=["question"]
            ):
                with patch.object(
                    optimizer,
                    "_create_optimized_prompt",
                    return_value="Optimized: {question}",
                ):
                    with patch(
                        "arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer.TiktokenSplitter"
                    ):
                        with patch(
                            "arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer.OpenAIModel"
                        ):
                            optimized_prompt = optimizer.optimize(
                                dataset=str(json_file),
                                output_column="answer",
                                feedback_columns=["feedback"],
                            )

        assert optimized_prompt == "Optimized: {question}"

    @patch(
        "arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer.get_key_value"
    )
    def test_optimize_with_only_evaluators_no_feedback(
        self, mock_get_key, sample_dataset
    ):
        """Test optimize with only evaluators and no feedback columns."""
        mock_get_key.return_value = MagicMock(get_secret_value=lambda: "test-api-key")

        # Mock evaluator
        def mock_evaluator(df):
            feedback_df = pd.DataFrame({"eval_result": ["pass", "pass"]})
            return feedback_df, ["eval_result"]

        from arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer import (
            PromptLearningOptimizer,
        )

        optimizer = PromptLearningOptimizer(prompt="Test: {question}")

        # Mock the optimization components
        with patch(
            "arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer.TiktokenSplitter"
        ):
            with patch(
                "arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer.OpenAIModel"
            ):
                # Should work with only evaluators
                optimized_prompt = optimizer.optimize(
                    dataset=sample_dataset,
                    output_column="answer",
                    evaluators=[mock_evaluator],
                    feedback_columns=[],  # Empty feedback columns
                )

        # Just verify that it returns something (the mocked response)
        assert optimized_prompt is not None
