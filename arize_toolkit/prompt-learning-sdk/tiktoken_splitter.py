#!/usr/bin/env python3
"""
Tiktoken-based Dataframe Splitter

Uses tiktoken for accurate token counting to split dataframes into batches
that fit within LLM context windows.
"""

import time
from typing import List, Tuple

import numpy as np
import pandas as pd

# Import tiktoken
import tiktoken


class TiktokenSplitter:
    """Split dataframes using tiktoken for accurate token counting."""

    def __init__(self, model: str = "gpt-4"):
        """
        Initialize splitter with tiktoken encoder.

        Args:
            model: The model to use for tokenization (default: gpt-4)
        """
        self.model = model
        self._setup_tiktoken()
        print(f"🔧 Initialized TiktokenSplitter with model: {self.model}")

    def _setup_tiktoken(self):
        """Setup tiktoken encoder."""
        self.tiktoken_encoder = tiktoken.encoding_for_model(self.model)

    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken."""
        if pd.isna(text) or text == "":
            return 0

        text_str = str(text)
        return len(self.tiktoken_encoder.encode(text_str))

    def count_row_tokens(self, df: pd.DataFrame, columns: List[str], row_idx: int) -> int:
        """Count total tokens for a specific row across selected columns."""
        row = df.iloc[row_idx]
        total_tokens = 0

        for col in columns:
            if col in df.columns:
                cell_value = row[col]
                total_tokens += self.count_tokens(str(cell_value))

        return total_tokens

    def create_batches(self, df: pd.DataFrame, columns: List[str], context_size_tokens: int, show_progress: bool = True) -> List[Tuple[int, int]]:
        """
        Create batches of dataframe rows that fit within the context window.

        Args:
            df: The dataframe to split
            columns: List of column names to include in token counting
            context_size_tokens: Maximum tokens per batch
            show_progress: Whether to show progress information

        Returns:
            List of (start_row, end_row) tuples for each batch
        """

        print(f"\n🔧 Creating batches with {context_size_tokens:,} token limit")
        print(f"   Total rows: {len(df):,}")
        print(f"   Columns: {columns}")

        # Validate columns exist
        missing_cols = [col for col in columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Columns not found in dataframe: {missing_cols}")

        start_time = time.time()

        # Count tokens for each row
        if show_progress:
            print("📊 Counting tokens for each row...")

        row_tokens = []
        for i in range(len(df)):
            tokens = self.count_row_tokens(df, columns, i)
            row_tokens.append(tokens)

            if show_progress and (i + 1) % 100 == 0:
                print(f"   Processed {i + 1:,}/{len(df):,} rows")

        # Create batches based on cumulative token count
        print("🔄 Creating batches...")

        batches = []
        current_start = 0
        current_tokens = 0

        for i, tokens in enumerate(row_tokens):
            # If adding this row would exceed context limit, start a new batch
            if current_tokens + tokens > context_size_tokens and current_start < i:
                batches.append((current_start, i - 1))
                current_start = i
                current_tokens = tokens
            else:
                current_tokens += tokens

        # Add the final batch if there are remaining rows
        if current_start < len(df):
            batches.append((current_start, len(df) - 1))

        total_time = time.time() - start_time

        # Print summary
        total_tokens = sum(row_tokens)
        avg_tokens_per_row = np.mean(row_tokens)

        print(f"✅ Created {len(batches)} batches in {total_time:.3f}s")
        print(f"   Total tokens: {total_tokens:,}")
        print(f"   Average tokens per row: {avg_tokens_per_row:.1f}")
        print(f"   Processing rate: {len(df) / total_time:.0f} rows/sec")

        return batches

    def get_batch_dataframes(self, df: pd.DataFrame, columns: List[str], context_size_tokens: int) -> List[pd.DataFrame]:
        """
        Get list of dataframe batches that fit within context window.

        Args:
            df: The dataframe to split
            columns: List of column names to include in token counting
            context_size_tokens: Maximum tokens per batch

        Returns:
            List of dataframe batches
        """
        batches = self.create_batches(df, columns, context_size_tokens)

        batch_dataframes = []
        for start, end in batches:
            batch_df = df.iloc[start: end + 1].copy()
            batch_dataframes.append(batch_df)

        return batch_dataframes
