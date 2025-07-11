#!/usr/bin/env python3
"""
Simple test for TiktokenSplitter
"""

import pandas as pd
from tiktoken_splitter import TiktokenSplitter
def test_tiktoken_splitter():
    """Test the tiktoken splitter with a small context window."""
    
    print("🧪 Testing TiktokenSplitter with 500 token context window")
    print("=" * 60)
    
    # Create a dummy dataset with about 2000 tokens
    # Each row will have roughly 200-300 tokens
    dataset = pd.read_csv("train_15.csv")
    
    print(f"📊 Created dataset with {len(dataset)} rows")
    print(f"   Columns: {list(dataset.columns)}")
    
    # Initialize the splitter with a small context window
    splitter = TiktokenSplitter(model="gpt-4")
    
    # Set context window to 500 tokens
    context_size_tokens = 8192
    
    # Get batches
    batch_dataframes = splitter.get_batch_dataframes(
        dataset, 
        list(dataset.columns), 
        context_size_tokens
    )
    
    print(f"\n📦 Results:")
    print(f"   Context window: {context_size_tokens:,} tokens")
    print(f"   Number of batches: {len(batch_dataframes)}")
    
    # Show details of each batch
    for i, batch_df in enumerate(batch_dataframes):
        print(f"\n   Batch {i + 1}:")
        print(f"      Rows: {len(batch_df)}")
        print(f"      Sample query: {batch_df['input'].iloc[0][:100]}...")
        
        # Count tokens in this batch
        total_tokens = 0
        for _, row in batch_df.iterrows():
            for col in batch_df.columns:
                total_tokens += splitter.count_tokens(str(row[col]))
        
        print(f"      Estimated tokens: {total_tokens:,}")
    
    print(f"\n✅ Test completed!")



if __name__ == "__main__":
    test_tiktoken_splitter() 