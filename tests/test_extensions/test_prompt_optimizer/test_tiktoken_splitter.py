"""Tests for TiktokenSplitter class."""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest


class TestTiktokenSplitter:
    """Test suite for TiktokenSplitter."""

    @patch("arize_toolkit.extensions.prompt_optimizer.tiktoken_splitter.tiktoken")
    def test_init(self, mock_tiktoken):
        """Test that TiktokenSplitter can be initialized with model name."""
        # Setup mock
        mock_encoder = MagicMock()
        mock_tiktoken.encoding_for_model.return_value = mock_encoder

        # Import after patching
        from arize_toolkit.extensions.prompt_optimizer.tiktoken_splitter import TiktokenSplitter

        # Test default model
        splitter = TiktokenSplitter()
        mock_tiktoken.encoding_for_model.assert_called_with("gpt-4o")
        assert splitter.tiktoken_encoder == mock_encoder

        # Test custom model
        splitter = TiktokenSplitter(model="gpt-3.5-turbo")
        mock_tiktoken.encoding_for_model.assert_called_with("gpt-3.5-turbo")

    @patch("arize_toolkit.extensions.prompt_optimizer.tiktoken_splitter.tiktoken")
    def test_count_tokens(self, mock_tiktoken):
        """Test token counting for various inputs."""
        # Setup mock
        mock_encoder = MagicMock()
        mock_encoder.encode.side_effect = lambda text: list(range(len(text)))
        mock_tiktoken.encoding_for_model.return_value = mock_encoder

        from arize_toolkit.extensions.prompt_optimizer.tiktoken_splitter import TiktokenSplitter

        splitter = TiktokenSplitter()

        # Test normal text
        assert splitter._count_tokens("hello") == 5
        mock_encoder.encode.assert_called_with("hello")

        # Test empty string
        assert splitter._count_tokens("") == 0

        # Test None/NaN - count_tokens handles these internally
        assert splitter._count_tokens(None) == 0  # type: ignore
        assert splitter._count_tokens(pd.NA) == 0  # type: ignore

        # Test numeric values converted to string
        assert splitter._count_tokens(123) == 3  # type: ignore
        mock_encoder.encode.assert_called_with("123")

    @patch("arize_toolkit.extensions.prompt_optimizer.tiktoken_splitter.tiktoken")
    def test_count_row_tokens(self, mock_tiktoken):
        """Test counting tokens for a specific row across columns."""
        # Setup mock
        mock_encoder = MagicMock()
        mock_encoder.encode.side_effect = lambda text: list(range(len(str(text))))
        mock_tiktoken.encoding_for_model.return_value = mock_encoder

        from arize_toolkit.extensions.prompt_optimizer.tiktoken_splitter import TiktokenSplitter

        splitter = TiktokenSplitter()

        # Create test dataframe
        df = pd.DataFrame(
            {
                "col1": ["hello", "world"],
                "col2": ["test", "data"],
                "col3": [123, 456],
            }
        )

        # Test counting tokens for row 0
        tokens = splitter._count_row_tokens(df, ["col1", "col2"], 0)
        # "hello" (5) + "test" (4) = 9
        assert tokens == 9

        # Test counting all columns for row 1
        tokens = splitter._count_row_tokens(df, ["col1", "col2", "col3"], 1)
        # "world" (5) + "data" (4) + "456" (3) = 12
        assert tokens == 12

        # Test with non-existent column (should be ignored)
        tokens = splitter._count_row_tokens(df, ["col1", "missing_col"], 0)
        assert tokens == 5  # Only "hello"

    @patch("arize_toolkit.extensions.prompt_optimizer.tiktoken_splitter.tiktoken")
    def test_create_batches(self, mock_tiktoken):
        """Test batch creation based on token limits."""
        # Setup mock - each character counts as 1 token
        mock_encoder = MagicMock()
        mock_encoder.encode.side_effect = lambda text: list(range(len(str(text))))
        mock_tiktoken.encoding_for_model.return_value = mock_encoder

        from arize_toolkit.extensions.prompt_optimizer.tiktoken_splitter import TiktokenSplitter

        splitter = TiktokenSplitter()

        # Create test dataframe with varying token counts
        df = pd.DataFrame(
            {
                "text": [
                    "short",  # 5 tokens
                    "medium text",  # 11 tokens
                    "this is a longer text",  # 21 tokens
                    "tiny",  # 4 tokens
                    "another medium length",  # 21 tokens
                ],
            }
        )

        # Test with context size of 20 tokens
        batches = splitter._create_batches(df, ["text"], 20, show_progress=False)

        # Expected batches:
        # Batch 1: rows 0-1 (5 + 11 = 16 tokens)
        # Batch 2: row 2 (21 tokens - exceeds limit alone)
        # Batch 3: row 3 (4 tokens)
        # Batch 4: row 4 (21 tokens - exceeds limit alone)
        assert len(batches) == 4
        assert batches[0] == (0, 1)
        assert batches[1] == (2, 2)
        assert batches[2] == (3, 3)
        assert batches[3] == (4, 4)

        # Test with larger context size
        batches = splitter._create_batches(df, ["text"], 50, show_progress=False)
        # The actual implementation might include row 3 in the first batch if it fits
        # 5 + 11 + 21 + 4 = 41 tokens, which is less than 50
        assert len(batches) == 2
        assert batches[0] == (0, 3)  # All rows except the last one fit
        assert batches[1] == (4, 4)  # Last row alone

    @patch("arize_toolkit.extensions.prompt_optimizer.tiktoken_splitter.tiktoken")
    def test_create_batches_with_missing_columns(self, mock_tiktoken):
        """Test that create_batches raises error for missing columns."""
        mock_encoder = MagicMock()
        mock_tiktoken.encoding_for_model.return_value = mock_encoder

        from arize_toolkit.extensions.prompt_optimizer.tiktoken_splitter import TiktokenSplitter

        splitter = TiktokenSplitter()

        df = pd.DataFrame({"col1": ["data"]})

        with pytest.raises(ValueError, match="Columns not found in dataframe"):
            splitter._create_batches(df, ["col1", "missing_col"], 100)

    @patch("arize_toolkit.extensions.prompt_optimizer.tiktoken_splitter.tiktoken")
    def test_get_batch_dataframes(self, mock_tiktoken):
        """Test getting list of dataframe batches."""
        # Setup mock
        mock_encoder = MagicMock()
        mock_encoder.encode.side_effect = lambda text: list(range(len(str(text))))
        mock_tiktoken.encoding_for_model.return_value = mock_encoder

        from arize_toolkit.extensions.prompt_optimizer.tiktoken_splitter import TiktokenSplitter

        splitter = TiktokenSplitter()

        # Create test dataframe
        df = pd.DataFrame(
            {
                "id": [1, 2, 3, 4, 5],
                "text": [
                    "short",  # 5 tokens
                    "medium text",  # 11 tokens
                    "this is a longer text",  # 21 tokens
                    "tiny",  # 4 tokens
                    "another medium length",  # 21 tokens
                ],
            }
        )

        # Get batches with 20 token limit
        batch_dfs = splitter.get_batch_dataframes(df, ["text"], 20)

        # Verify we get correct number of batches
        assert len(batch_dfs) == 4

        # Verify first batch
        assert len(batch_dfs[0]) == 2
        assert batch_dfs[0]["id"].tolist() == [1, 2]
        assert batch_dfs[0]["text"].tolist() == ["short", "medium text"]

        # Verify second batch (single row that exceeds limit)
        assert len(batch_dfs[1]) == 1
        assert batch_dfs[1]["id"].tolist() == [3]

        # Verify batches are copies, not views
        batch_dfs[0].loc[0, "text"] = "modified"
        assert df.loc[0, "text"] == "short"  # Original unchanged

    @patch("arize_toolkit.extensions.prompt_optimizer.tiktoken_splitter.tiktoken")
    def test_edge_cases(self, mock_tiktoken):
        """Test edge cases for TiktokenSplitter."""
        # Setup mock
        mock_encoder = MagicMock()
        mock_encoder.encode.return_value = [1, 2, 3]
        mock_tiktoken.encoding_for_model.return_value = mock_encoder

        from arize_toolkit.extensions.prompt_optimizer.tiktoken_splitter import TiktokenSplitter

        splitter = TiktokenSplitter()

        # Test empty dataframe
        df = pd.DataFrame({"text": []})
        batches = splitter._create_batches(df, ["text"], 100, show_progress=False)
        assert batches == []

        batch_dfs = splitter.get_batch_dataframes(df, ["text"], 100)
        assert batch_dfs == []

        # Test single row dataframe
        df = pd.DataFrame({"text": ["single row"]})
        batches = splitter._create_batches(df, ["text"], 100, show_progress=False)
        assert batches == [(0, 0)]

        # Test all rows exceed context limit individually
        mock_encoder.encode.side_effect = lambda text: list(range(200))
        df = pd.DataFrame({"text": ["row1", "row2", "row3"]})
        batches = splitter._create_batches(df, ["text"], 100, show_progress=False)
        # Each row should be its own batch
        assert len(batches) == 3
        assert batches == [(0, 0), (1, 1), (2, 2)]
