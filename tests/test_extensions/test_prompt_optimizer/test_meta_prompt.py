"""Tests for MetaPrompt class."""

import pandas as pd
import pytest

from arize_toolkit.extensions.prompt_optimizer.constants import END_DELIM, META_PROMPT_TEMPLATE, START_DELIM
from arize_toolkit.extensions.prompt_optimizer.meta_prompt import MetaPrompt


class TestMetaPrompt:
    """Test suite for MetaPrompt."""

    def test_init(self):
        """Test that MetaPrompt can be initialized."""
        meta_prompt = MetaPrompt()
        assert meta_prompt.meta_prompt_messages == META_PROMPT_TEMPLATE

    def test_construct_content_basic(self):
        """Test basic content construction with simple data."""
        meta_prompt = MetaPrompt()

        # Create test dataframe
        df = pd.DataFrame(
            {
                "user_input": ["What is 2+2?", "What is the capital of France?"],
                "output": ["4", "Paris"],
                "feedback": ["correct", "correct"],
            }
        )

        prompt_to_optimize = "Answer the question: {user_input}"
        template_variables = ["user_input"]
        feedback_columns = ["feedback"]
        output_column = "output"

        content = meta_prompt.construct_content(
            batch_df=df,
            prompt_to_optimize_content=prompt_to_optimize,
            template_variables=template_variables,
            feedback_columns=feedback_columns,
            output_column=output_column,
        )

        # Verify the structure
        assert "{baseline_prompt}" not in content
        assert "Answer the question: {user_input}" in content
        assert "Example 0" in content
        assert "Example 1" in content
        assert "What is 2+2?" in content
        assert "4" in content
        assert "feedback: correct" in content

    def test_construct_content_with_multiple_feedback_columns(self):
        """Test content construction with multiple feedback columns."""
        meta_prompt = MetaPrompt()

        df = pd.DataFrame(
            {
                "query": ["hello", "world"],
                "response": ["hi", "earth"],
                "accuracy": ["good", "poor"],
                "relevance": ["high", "low"],
                "score": [0.9, 0.3],
            }
        )

        content = meta_prompt.construct_content(
            batch_df=df,
            prompt_to_optimize_content="Respond to: {query}",
            template_variables=["query"],
            feedback_columns=["accuracy", "relevance", "score"],
            output_column="response",
        )

        # Check all feedback columns are included
        assert "accuracy: good" in content
        assert "relevance: high" in content
        assert "score: 0.9" in content
        assert "accuracy: poor" in content
        assert "relevance: low" in content
        assert "score: 0.3" in content

    def test_construct_content_with_null_values(self):
        """Test handling of null values in dataframe."""
        meta_prompt = MetaPrompt()

        df = pd.DataFrame(
            {
                "input": ["test", None, "data"],
                "output": ["result", None, "output"],
                "feedback": [None, "bad", "good"],
            }
        )

        content = meta_prompt.construct_content(
            batch_df=df,
            prompt_to_optimize_content="Process: {input}",
            template_variables=["input"],
            feedback_columns=["feedback"],
            output_column="output",
        )

        # Check None values are handled
        assert "None" in content
        assert "feedback: None" in content
        assert "Output from the LLM using the template above: None" in content

    def test_construct_content_with_delimiters_in_text(self):
        """Test that delimiters in text are properly escaped."""
        meta_prompt = MetaPrompt()

        df = pd.DataFrame(
            {
                "text": [f"test {START_DELIM}var{END_DELIM} text"],
                "output": [f"output {START_DELIM}result{END_DELIM}"],
                "feedback": [f"feedback {START_DELIM}good{END_DELIM}"],
            }
        )

        content = meta_prompt.construct_content(
            batch_df=df,
            prompt_to_optimize_content="Process: {text}",
            template_variables=["text"],
            feedback_columns=["feedback"],
            output_column="output",
        )

        # Verify delimiters are replaced with spaces in the examples section
        # Note: The template itself contains {baseline_prompt} and {examples} which are expected
        # We need to check that our test data delimiters were replaced
        examples_section = content.split("************* start example data *************")[-1]
        assert "test  var  text" in examples_section
        assert "output  result " in examples_section
        assert "feedback  good " in examples_section

    def test_format_template_with_vars(self):
        """Test template variable formatting."""
        meta_prompt = MetaPrompt()

        template = "Hello {name}, your age is {age} and location is {location}."
        template_variables = ["name", "age", "location"]
        variable_values = {"name": "John", "age": 25, "location": "NYC"}

        result = meta_prompt.format_template_with_vars(template, template_variables, variable_values)

        assert result == "Hello John, your age is 25 and location is NYC."

    def test_format_template_with_vars_special_characters(self):
        """Test template formatting with special characters."""
        meta_prompt = MetaPrompt()

        template = f"Process {START_DELIM}input{END_DELIM} data"
        template_variables = ["input"]
        variable_values = {"input": f"test{START_DELIM}value{END_DELIM}"}

        result = meta_prompt.format_template_with_vars(template, template_variables, variable_values)

        # Delimiters in values should be replaced with spaces
        assert result == "Process test value  data"

    def test_format_template_with_missing_variable(self):
        """Test template formatting when variable value is missing."""
        meta_prompt = MetaPrompt()

        template = "Hello {name}, your age is {age}."
        template_variables = ["name", "age"]
        variable_values = {"name": "John"}  # age is missing

        # Should raise KeyError when trying to access missing variable
        with pytest.raises(KeyError):
            meta_prompt.format_template_with_vars(template, template_variables, variable_values)

    def test_construct_content_empty_dataframe(self):
        """Test content construction with empty dataframe."""
        meta_prompt = MetaPrompt()

        df = pd.DataFrame({"input": [], "output": [], "feedback": []})

        content = meta_prompt.construct_content(
            batch_df=df,
            prompt_to_optimize_content="Process: {input}",
            template_variables=["input"],
            feedback_columns=["feedback"],
            output_column="output",
        )

        # Should have the baseline prompt but no examples
        assert "Process: {input}" in content
        assert "Example" not in content

    def test_construct_content_with_numeric_feedback(self):
        """Test handling of numeric feedback values."""
        meta_prompt = MetaPrompt()

        df = pd.DataFrame(
            {
                "question": ["What is 2+2?"],
                "answer": ["4"],
                "score": [1.0],
                "rating": [5],
            }
        )

        content = meta_prompt.construct_content(
            batch_df=df,
            prompt_to_optimize_content="Answer: {question}",
            template_variables=["question"],
            feedback_columns=["score", "rating"],
            output_column="answer",
        )

        # Numeric values should be converted to strings
        assert "score: 1.0" in content
        assert "rating: 5" in content

    def test_construct_content_preserves_template_structure(self):
        """Test that the meta prompt template structure is preserved."""
        meta_prompt = MetaPrompt()

        df = pd.DataFrame({"input": ["test"], "output": ["result"], "feedback": ["good"]})

        content = meta_prompt.construct_content(
            batch_df=df,
            prompt_to_optimize_content="Simple prompt: {input}",
            template_variables=["input"],
            feedback_columns=["feedback"],
            output_column="output",
        )

        # Check key sections of the template are present
        assert "BELOW IS THE ORIGINAL BASELINE PROMPT" in content
        assert "************* start prompt *************" in content
        assert "************* end prompt *************" in content
        assert "BELOW ARE THE EXAMPLES USING THE ABOVE PROMPT" in content
        assert "************* start example data *************" in content
        assert "************* end example data *************" in content
        assert "FINAL INSTRUCTIONS" in content
        assert "YOUR NEW PROMPT:" in content
