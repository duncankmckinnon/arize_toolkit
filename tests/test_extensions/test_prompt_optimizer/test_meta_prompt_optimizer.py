"""Tests for MetaPromptOptimizer class."""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest


class TestMetaPromptOptimizer:
    """Test suite for MetaPromptOptimizer."""

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

    @patch("arize_toolkit.extensions.prompt_optimizer.meta_prompt_optimizer.get_key_value")
    def test_init_with_dataframe(self, mock_get_key, sample_dataset):
        """Test initialization with DataFrame."""
        mock_get_key.return_value = MagicMock(get_secret_value=lambda: "test-api-key")

        from arize_toolkit.extensions.prompt_optimizer.meta_prompt_optimizer import MetaPromptOptimizer

        optimizer = MetaPromptOptimizer(
            prompt="Answer: {question}",
            dataset=sample_dataset,
            output_column="answer",
            feedback_columns=["correct", "score"],
        )

        assert optimizer.output_column == "answer"
        assert optimizer.feedback_columns == ["correct", "score"]
        assert len(optimizer.dataset) == 2
        assert optimizer.model_choice == "gpt-4"

    @patch("arize_toolkit.extensions.prompt_optimizer.meta_prompt_optimizer.get_key_value")
    def test_init_with_json_file(self, mock_get_key, tmp_path):
        """Test initialization with JSON file path."""
        mock_get_key.return_value = MagicMock(get_secret_value=lambda: "test-api-key")

        # Create a temporary JSON file
        json_file = tmp_path / "test_data.json"
        df = pd.DataFrame({"question": ["test"], "answer": ["response"], "feedback": [1]})
        df.to_json(json_file)

        from arize_toolkit.extensions.prompt_optimizer.meta_prompt_optimizer import MetaPromptOptimizer

        optimizer = MetaPromptOptimizer(
            prompt="Test prompt",
            dataset=str(json_file),
            output_column="answer",
            feedback_columns=["feedback"],
        )

        assert len(optimizer.dataset) == 1
        assert optimizer.dataset["question"].iloc[0] == "test"

    @patch("arize_toolkit.extensions.prompt_optimizer.meta_prompt_optimizer.get_key_value")
    def test_init_validation_errors(self, mock_get_key, sample_dataset):
        """Test validation errors during initialization."""
        mock_get_key.return_value = MagicMock(get_secret_value=lambda: "test-api-key")

        from arize_toolkit.extensions.prompt_optimizer.meta_prompt_optimizer import MetaPromptOptimizer

        # Test without feedback columns or evaluators
        with pytest.raises(ValueError, match="Either feedback_columns or evaluators"):
            MetaPromptOptimizer(prompt="Test", dataset=sample_dataset, output_column="answer")

        # Test with missing columns
        with pytest.raises(ValueError, match="Dataset missing required columns"):
            MetaPromptOptimizer(
                prompt="Test",
                dataset=sample_dataset,
                output_column="missing_column",
                feedback_columns=["correct"],
            )

    @patch("arize_toolkit.extensions.prompt_optimizer.meta_prompt_optimizer.get_key_value")
    def test_extract_prompt_messages_from_list(self, mock_get_key, sample_prompt_messages):
        """Test extracting messages from list."""
        mock_get_key.return_value = MagicMock(get_secret_value=lambda: "test-api-key")

        from arize_toolkit.extensions.prompt_optimizer.meta_prompt_optimizer import MetaPromptOptimizer

        optimizer = MetaPromptOptimizer(
            prompt=sample_prompt_messages,
            dataset=pd.DataFrame({"q": ["test"], "a": ["ans"], "f": [1]}),
            output_column="a",
            feedback_columns=["f"],
        )

        messages = optimizer._extract_prompt_messages()
        assert messages == sample_prompt_messages

    @patch("arize_toolkit.extensions.prompt_optimizer.meta_prompt_optimizer.get_key_value")
    def test_extract_prompt_messages_from_string(self, mock_get_key):
        """Test extracting messages from string."""
        mock_get_key.return_value = MagicMock(get_secret_value=lambda: "test-api-key")

        from arize_toolkit.extensions.prompt_optimizer.meta_prompt_optimizer import MetaPromptOptimizer

        optimizer = MetaPromptOptimizer(
            prompt="Simple prompt",
            dataset=pd.DataFrame({"q": ["test"], "a": ["ans"], "f": [1]}),
            output_column="a",
            feedback_columns=["f"],
        )

        messages = optimizer._extract_prompt_messages()
        assert messages == [{"role": "user", "content": "Simple prompt"}]

    @patch("arize_toolkit.extensions.prompt_optimizer.meta_prompt_optimizer.get_key_value")
    def test_extract_prompt_messages_from_prompt_version(self, mock_get_key):
        """Test extracting messages from PromptVersion object."""
        mock_get_key.return_value = MagicMock(get_secret_value=lambda: "test-api-key")

        # Skip this test if phoenix is not available
        try:
            from phoenix.client.types import PromptVersion
        except ImportError:
            pytest.skip("phoenix not available")

        from arize_toolkit.extensions.prompt_optimizer.meta_prompt_optimizer import MetaPromptOptimizer

        # Create a real PromptVersion instance
        prompt_version = PromptVersion(
            [{"role": "user", "content": "Test prompt"}],
            model_name="gpt-4o-mini",
        )

        optimizer = MetaPromptOptimizer(
            prompt=prompt_version,
            dataset=pd.DataFrame({"q": ["test"], "a": ["ans"], "f": [1]}),
            output_column="a",
            feedback_columns=["f"],
        )

        messages = optimizer._extract_prompt_messages()
        assert messages == [{"role": "user", "content": "Test prompt"}]

    @patch("arize_toolkit.extensions.prompt_optimizer.meta_prompt_optimizer.get_key_value")
    def test_extract_prompt_content(self, mock_get_key, sample_prompt_messages):
        """Test extracting prompt content from messages."""
        mock_get_key.return_value = MagicMock(get_secret_value=lambda: "test-api-key")

        from arize_toolkit.extensions.prompt_optimizer.meta_prompt_optimizer import MetaPromptOptimizer

        optimizer = MetaPromptOptimizer(
            prompt=sample_prompt_messages,
            dataset=pd.DataFrame({"q": ["test"], "a": ["ans"], "f": [1]}),
            output_column="a",
            feedback_columns=["f"],
        )

        content = optimizer._extract_prompt_content()
        assert content == "Answer: {question}"

    @patch("arize_toolkit.extensions.prompt_optimizer.meta_prompt_optimizer.get_key_value")
    def test_detect_template_variables(self, mock_get_key):
        """Test template variable detection."""
        mock_get_key.return_value = MagicMock(get_secret_value=lambda: "test-api-key")

        from arize_toolkit.extensions.prompt_optimizer.meta_prompt_optimizer import MetaPromptOptimizer

        optimizer = MetaPromptOptimizer(
            prompt="Hello {name}, your age is {age} and {name} again",
            dataset=pd.DataFrame({"q": ["test"], "a": ["ans"], "f": [1]}),
            output_column="a",
            feedback_columns=["f"],
        )

        variables = optimizer._detect_template_variables("Hello {name}, your age is {age}")
        assert set(variables) == {"name", "age"}

        # Test with no variables
        variables = optimizer._detect_template_variables("No variables here")
        assert variables == []

    def test_run_evaluators(self, sample_dataset):
        """Test running evaluators on dataset."""
        from arize_toolkit.extensions.prompt_optimizer.meta_prompt_optimizer import MetaPromptOptimizer

        # Mock evaluator that returns matching column names
        def mock_evaluator(df):
            feedback_df = pd.DataFrame({"correct": ["good", "excellent"]})
            return feedback_df, ["correct"]

        optimizer = MetaPromptOptimizer(
            prompt="Test",
            dataset=sample_dataset.copy(),
            output_column="answer",
            feedback_columns=["correct"],
            evaluators=[mock_evaluator],
        )

        result_df = optimizer.run_evaluators()

        # Check that existing column was updated
        assert result_df["correct"].tolist() == ["good", "excellent"]
        # Check that no new columns were added
        assert set(result_df.columns) == set(sample_dataset.columns)

    @patch("arize_toolkit.extensions.prompt_optimizer.meta_prompt_optimizer.OpenAIModel")
    @patch("arize_toolkit.extensions.prompt_optimizer.meta_prompt_optimizer.TiktokenSplitter")
    @patch("arize_toolkit.extensions.prompt_optimizer.meta_prompt_optimizer.get_key_value")
    def test_optimize_basic(self, mock_get_key, mock_splitter, mock_openai_model):
        """Test basic optimize functionality."""
        mock_get_key.return_value = MagicMock(get_secret_value=lambda: "test-api-key")

        # Mock tiktoken splitter
        mock_splitter_instance = MagicMock()
        mock_splitter_instance.get_batch_dataframes.return_value = [
            pd.DataFrame(
                {
                    "question": ["What is 2+2?"],
                    "answer": ["4"],
                    "feedback": ["correct"],
                }
            )
        ]
        mock_splitter.return_value = mock_splitter_instance

        # Mock OpenAI model
        mock_model_instance = MagicMock()
        mock_model_instance.return_value = "Improved prompt: {question}"
        mock_openai_model.return_value = mock_model_instance

        from arize_toolkit.extensions.prompt_optimizer.meta_prompt_optimizer import MetaPromptOptimizer

        optimizer = MetaPromptOptimizer(
            prompt="Answer: {question}",
            dataset=pd.DataFrame(
                {
                    "question": ["What is 2+2?"],
                    "answer": ["4"],
                    "feedback": ["correct"],
                }
            ),
            output_column="answer",
            feedback_columns=["feedback"],
        )

        optimized_prompt, dataset = optimizer.optimize(context_size_k=8000)

        # Verify the optimization was called
        assert mock_splitter_instance.get_batch_dataframes.called
        assert mock_model_instance.called

        # Verify the result
        assert optimized_prompt == "Improved prompt: {question}"

    @patch("arize_toolkit.extensions.prompt_optimizer.meta_prompt_optimizer.get_key_value")
    def test_create_optimized_prompt_from_string(self, mock_get_key):
        """Test creating optimized prompt from string input."""
        mock_get_key.return_value = MagicMock(get_secret_value=lambda: "test-api-key")

        from arize_toolkit.extensions.prompt_optimizer.meta_prompt_optimizer import MetaPromptOptimizer

        optimizer = MetaPromptOptimizer(
            prompt="Original prompt",
            dataset=pd.DataFrame({"q": ["test"], "a": ["ans"], "f": [1]}),
            output_column="a",
            feedback_columns=["f"],
        )

        result = optimizer._create_optimized_prompt("Optimized prompt")
        assert result == "Optimized prompt"

    @patch("arize_toolkit.extensions.prompt_optimizer.meta_prompt_optimizer.get_key_value")
    def test_create_optimized_prompt_from_list(self, mock_get_key):
        """Test creating optimized prompt from list input."""
        mock_get_key.return_value = MagicMock(get_secret_value=lambda: "test-api-key")

        from arize_toolkit.extensions.prompt_optimizer.meta_prompt_optimizer import MetaPromptOptimizer

        original_messages = [
            {"role": "system", "content": "System message"},
            {"role": "user", "content": "Original user prompt"},
        ]

        optimizer = MetaPromptOptimizer(
            prompt=original_messages,
            dataset=pd.DataFrame({"q": ["test"], "a": ["ans"], "f": [1]}),
            output_column="a",
            feedback_columns=["f"],
        )

        result = optimizer._create_optimized_prompt("Optimized user prompt")

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["content"] == "System message"
        assert result[1]["content"] == "Optimized user prompt"

    @patch("arize_toolkit.extensions.prompt_optimizer.meta_prompt_optimizer.get_key_value")
    def test_create_optimized_prompt_from_prompt_version(self, mock_get_key):
        """Test creating optimized prompt from PromptVersion input."""
        mock_get_key.return_value = MagicMock(get_secret_value=lambda: "test-api-key")

        # Skip this test if phoenix is not available
        try:
            from phoenix.client.types import PromptVersion
        except ImportError:
            pytest.skip("phoenix not available")

        from arize_toolkit.extensions.prompt_optimizer.meta_prompt_optimizer import MetaPromptOptimizer

        # Create a real PromptVersion instance
        original_prompt = PromptVersion(
            [{"role": "user", "content": "Original prompt"}],
            model_name="gpt-4",
            model_provider="OPENAI",
        )

        optimizer = MetaPromptOptimizer(
            prompt=original_prompt,
            dataset=pd.DataFrame({"q": ["test"], "a": ["ans"], "f": [1]}),
            output_column="a",
            feedback_columns=["f"],
        )

        result = optimizer._create_optimized_prompt("Optimized prompt")

        # Verify the result is a PromptVersion
        assert isinstance(result, PromptVersion)

        # Verify the content was updated
        assert result._template["messages"][0]["content"] == "Optimized prompt"
        assert result._model_name == "gpt-4"
        assert result._model_provider == "OPENAI"

    @patch("arize_toolkit.extensions.prompt_optimizer.meta_prompt_optimizer.get_key_value")
    def test_create_dummy_dataframe(self, mock_get_key):
        """Test creation of dummy dataframe for template variables."""
        mock_get_key.return_value = MagicMock(get_secret_value=lambda: "test-api-key")

        from arize_toolkit.extensions.prompt_optimizer.meta_prompt_optimizer import MetaPromptOptimizer

        optimizer = MetaPromptOptimizer(
            prompt="Hello {name}, your {attribute} is {value}",
            dataset=pd.DataFrame({"q": ["test"], "a": ["ans"], "f": [1]}),
            output_column="a",
            feedback_columns=["f"],
        )

        optimizer.template_variables = ["name", "attribute", "value"]
        dummy_df = optimizer._create_dummy_dataframe()

        assert "var" in dummy_df.columns
        assert dummy_df["var"].iloc[0] == "{var}"
        assert dummy_df["name"].iloc[0] == "{name}"
        assert dummy_df["attribute"].iloc[0] == "{attribute}"
        assert dummy_df["value"].iloc[0] == "{value}"

    @patch("arize_toolkit.extensions.prompt_optimizer.meta_prompt_optimizer.OpenAIModel")
    @patch("arize_toolkit.extensions.prompt_optimizer.meta_prompt_optimizer.TiktokenSplitter")
    @patch("arize_toolkit.extensions.prompt_optimizer.meta_prompt_optimizer.get_key_value")
    def test_optimize_with_evaluators(self, mock_get_key, mock_splitter, mock_openai_model, sample_dataset):
        """Test optimize with evaluators called separately."""
        mock_get_key.return_value = MagicMock(get_secret_value=lambda: "test-api-key")

        # Mock evaluator
        def mock_evaluator(df):
            feedback_df = pd.DataFrame({"correct": ["good", "good"]})
            return feedback_df, ["correct"]

        # Mock tiktoken splitter
        mock_splitter_instance = MagicMock()
        mock_splitter_instance.get_batch_dataframes.return_value = [sample_dataset]
        mock_splitter.return_value = mock_splitter_instance

        # Mock OpenAI model
        mock_model_instance = MagicMock()
        mock_model_instance.return_value = "Improved: {question}"
        mock_openai_model.return_value = mock_model_instance

        from arize_toolkit.extensions.prompt_optimizer.meta_prompt_optimizer import MetaPromptOptimizer

        optimizer = MetaPromptOptimizer(
            prompt="Answer: {question}",
            dataset=sample_dataset.copy(),
            output_column="answer",
            feedback_columns=["correct"],
            evaluators=[mock_evaluator],
        )

        # First run evaluators
        dataset_with_feedback = optimizer.run_evaluators()
        assert dataset_with_feedback["correct"].tolist() == ["good", "good"]

        # Then optimize (should not call evaluators again)
        optimized_prompt = optimizer.optimize()
        assert optimized_prompt == "Improved: {question}"

    @patch("arize_toolkit.extensions.prompt_optimizer.meta_prompt_optimizer.OpenAIModel")
    @patch("arize_toolkit.extensions.prompt_optimizer.meta_prompt_optimizer.TiktokenSplitter")
    @patch("arize_toolkit.extensions.prompt_optimizer.meta_prompt_optimizer.get_key_value")
    def test_optimize_error_handling(self, mock_get_key, mock_splitter, mock_openai_model):
        """Test error handling in optimize method."""
        mock_get_key.return_value = MagicMock(get_secret_value=lambda: "test-api-key")

        # Mock tiktoken splitter
        mock_splitter_instance = MagicMock()
        mock_splitter_instance.get_batch_dataframes.return_value = [pd.DataFrame({"q": ["test"], "a": ["ans"], "f": [1]})]
        mock_splitter.return_value = mock_splitter_instance

        # Mock OpenAI model to raise an error
        mock_model_instance = MagicMock()
        mock_model_instance.side_effect = Exception("API Error")
        mock_openai_model.return_value = mock_model_instance

        from arize_toolkit.extensions.prompt_optimizer.meta_prompt_optimizer import MetaPromptOptimizer

        optimizer = MetaPromptOptimizer(
            prompt="Test: {q}",
            dataset=pd.DataFrame({"q": ["test"], "a": ["ans"], "f": [1]}),
            output_column="a",
            feedback_columns=["f"],
        )

        # Should not raise, but return original prompt
        optimized_prompt, dataset = optimizer.optimize()
        assert optimized_prompt == "Test: {q}"
