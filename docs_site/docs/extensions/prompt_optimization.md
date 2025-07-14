# Prompt Optimization Extension

## Overview

The Prompt Optimization Extension provides automated tools for improving prompt templates based on historical performance data. Using OpenAI's meta-prompting technique, it analyzes past interactions (inputs, outputs, and feedback) to generate optimized prompt versions that can improve performance on your specific use cases.

**Installation**: `pip install arize_toolkit[prompt_optimizer]`

This extension is particularly useful for:

1. **Iterative Prompt Improvement** – Analyze historical performance to generate better prompts
1. **Batch Processing** – Handle large datasets efficiently with automatic token management
1. **Multi-dimensional Feedback** – Incorporate multiple feedback signals for comprehensive optimization
1. **Template Preservation** – Maintain variable structures while optimizing content

## Key Components

| Component | Purpose |
|-----------|---------|
| [`MetaPromptOptimizer`](#metapromptoptimizer) | Main class for prompt optimization workflow |
| [`TiktokenSplitter`](#tiktokensplitter) | Utility for token counting and dataset batching |

**Note:** This extension requires additional dependencies. Install with:

```bash
pip install arize_toolkit[prompt_optimizer]
```

______________________________________________________________________

## Installation & Setup

The prompt optimization extension has optional dependencies that must be installed:

```bash
# Install with prompt_optimizer extras
pip install arize_toolkit[prompt_optimizer]
```

This installs the following dependencies:

- `tiktoken` - For token counting and batching
- `arize-phoenix-evals` - For evaluation capabilities
- `arize-phoenix-client` - For Phoenix integration

Once installed, import the extension:

```python
from arize_toolkit.extensions.prompt_optimizer import (
    MetaPromptOptimizer,
    TiktokenSplitter,
)
```

______________________________________________________________________

## `MetaPromptOptimizer`

### Overview

```python
optimizer = MetaPromptOptimizer(
    prompt: str | list[dict] | PromptVersion,
    dataset: pd.DataFrame | str,
    output_column: str,
    feedback_columns: list[str] | None = None,
    evaluators: list[callable] | None = None,
    input_columns: list[str] | None = None,
    openai_api_key: str | None = None,
    openai_model: str = "gpt-4o-mini",
    context_size: int = 40000
)
```

The main class for optimizing prompts based on historical performance data. It analyzes past interactions and generates improved prompt templates.

**Parameters**

- `prompt` – The prompt to optimize. Can be:
  - A string template (e.g., "Answer the question: {question}")
  - A list of message dictionaries (e.g., `[{"role": "system", "content": "..."}]`)
  - A Phoenix `PromptVersion` object
- `dataset` – Historical performance data. Can be:
  - A pandas DataFrame with input, output, and feedback columns
  - A path to a JSON file containing the data
- `output_column` – Column name containing model outputs
- `feedback_columns` *(optional)* – List of column names containing feedback/evaluation data
- `evaluators` *(optional)* – List of functions to compute additional feedback
- `input_columns` *(optional)* – List of column names for template variables. Auto-detected if not provided
- `openai_api_key` *(optional)* – OpenAI API key. Uses environment variable if not provided
- `openai_model` *(optional)* – Model to use for optimization. Defaults to "gpt-4o-mini"
- `context_size` *(optional)* – Maximum tokens per optimization batch. Defaults to 40000

**Returns**

A `MetaPromptOptimizer` instance ready to optimize prompts.

**Example**

```python
import pandas as pd
from arize_toolkit.extensions.prompt_optimizer import MetaPromptOptimizer

# Load historical data
data = pd.DataFrame(
    {
        "question": ["What is 2+2?", "What is the capital of France?"],
        "answer": ["4", "Paris"],
        "accuracy": [1.0, 1.0],
        "relevance": ["high", "high"],
    }
)

# Create optimizer
optimizer = MetaPromptOptimizer(
    prompt="Answer the question: {question}",
    dataset=data,
    output_column="answer",
    feedback_columns=["accuracy", "relevance"],
)

# Generate optimized prompt
optimized = optimizer.optimize()
print(optimized)
```

### `optimize`

```python
optimized_prompt: str | list[dict] | PromptVersion = optimizer.optimize(
    max_examples: int | None = None,
    show_progress: bool = True
)
```

Runs the optimization process to generate an improved prompt based on the historical data.

**Parameters**

- `max_examples` *(optional)* – Maximum number of examples to use. Uses all if not specified
- `show_progress` *(optional)* – Whether to show progress bars. Defaults to True

**Returns**

The optimized prompt in the same format as the input (string, list, or PromptVersion).

**Example**

```python
# Basic optimization
optimized = optimizer.optimize()

# Limit examples for faster processing
optimized = optimizer.optimize(max_examples=100)

# Quiet mode
optimized = optimizer.optimize(show_progress=False)
```

______________________________________________________________________

## `TiktokenSplitter`

### Overview

```python
splitter = TiktokenSplitter(
    model_name: str = "gpt-4"
)
```

A utility class for counting tokens and creating batches that fit within context limits. Essential for processing large datasets.

**Parameters**

- `model_name` *(optional)* – The model name for tokenization. Defaults to "gpt-4"

**Example**

```python
from arize_toolkit.extensions.prompt_optimizer import TiktokenSplitter

splitter = TiktokenSplitter(model_name="gpt-4o-mini")
```

### `count_tokens`

```python
token_count: int = splitter.count_tokens(text: str)
```

Counts the number of tokens in a text string.

**Parameters**

- `text` – The text to tokenize

**Returns**

The number of tokens in the text.

**Example**

```python
count = splitter.count_tokens("Hello, world!")
print(f"Token count: {count}")  # Token count: 4
```

### `create_batches`

```python
batches: list[tuple[int, int]] = splitter.create_batches(
    dataframe: pd.DataFrame,
    text_columns: list[str],
    context_size: int,
    show_progress: bool = True
)
```

Creates batches of dataframe rows that fit within a token limit.

**Parameters**

- `dataframe` – The DataFrame to batch
- `text_columns` – Column names containing text to count tokens for
- `context_size` – Maximum tokens per batch
- `show_progress` *(optional)* – Whether to show progress bar. Defaults to True

**Returns**

A list of tuples (start_idx, end_idx) representing row ranges for each batch.

**Example**

```python
df = pd.DataFrame(
    {
        "prompt": ["Short text", "Medium length text here", "Very long text..."],
        "response": ["Yes", "Detailed response...", "Extended answer..."],
    }
)

batches = splitter.create_batches(
    dataframe=df, text_columns=["prompt", "response"], context_size=1000
)

# Process each batch
for start, end in batches:
    batch_df = df.iloc[start : end + 1]
    # Process batch...
```

______________________________________________________________________

## Advanced Usage

### Using Custom Evaluators

You can provide custom evaluation functions to compute additional feedback:

```python
def custom_evaluator(row):
    """Custom evaluation logic"""
    score = len(row["answer"]) / len(row["question"])
    return {"length_ratio": score}


optimizer = MetaPromptOptimizer(
    prompt=prompt_template,
    dataset=data,
    output_column="answer",
    evaluators=[custom_evaluator],
)
```

### Working with Phoenix PromptVersion

If you're using Phoenix for prompt versioning:

```python
from phoenix.client.types import PromptVersion

# Create a prompt version
prompt_v1 = PromptVersion(
    [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "{question}"},
    ],
    model_name="gpt-4o-mini",
    model_provider="OPENAI",
)

# Optimize it
optimizer = MetaPromptOptimizer(
    prompt=prompt_v1,
    dataset=historical_data,
    output_column="response",
    feedback_columns=["rating", "feedback"],
)

optimized_v2 = optimizer.optimize()
```

### Handling Large Datasets

For datasets that exceed context limits:

```python
# The optimizer automatically handles batching
optimizer = MetaPromptOptimizer(
    prompt=template,
    dataset=large_df,  # e.g., 10,000 rows
    output_column="output",
    context_size=20000,  # Smaller context for more batches
)

# Progress bars show batch processing
optimized = optimizer.optimize()
```

______________________________________________________________________

## Best Practices

1. **Data Quality**: Ensure your historical data has meaningful feedback signals
1. **Feedback Diversity**: Use multiple feedback columns for better optimization
1. **Template Variables**: Keep variable names consistent between prompt and data
1. **Batch Size**: Adjust `context_size` based on your model's limits
1. **Iteration**: Run optimization multiple times with refined data for best results

______________________________________________________________________

## Error Handling

Common errors and solutions:

```python
# Missing API Key
try:
    optimizer = MetaPromptOptimizer(...)
except Exception as e:
    # Set OPENAI_API_KEY environment variable or pass openai_api_key parameter
    
# Template Variable Mismatch
# Ensure your prompt variables match column names:
# prompt: "Answer {question}" requires a "question" column in dataset

# Token Limit Exceeded
# Reduce context_size or max_examples:
optimizer = MetaPromptOptimizer(..., context_size=10000, ...)
result = optimizer.optimize(max_examples=50)
```

______________________________________________________________________

## Complete Example

Here's a full workflow for optimizing a customer support prompt:

```python
import pandas as pd
from arize_toolkit.extensions.prompt_optimizer import MetaPromptOptimizer

# Historical support interactions
support_data = pd.DataFrame(
    {
        "customer_query": [
            "How do I reset my password?",
            "My order hasn't arrived yet",
            "Can I change my subscription plan?",
        ],
        "agent_response": [
            "To reset your password, go to Settings > Security > Reset Password",
            "I'll check your order status. Can you provide your order number?",
            "Yes, you can change your plan in Account > Subscription",
        ],
        "customer_satisfaction": [5, 3, 5],
        "resolution_time": [2, 10, 3],
        "resolved": [True, False, True],
    }
)

# Current prompt template
current_prompt = """You are a helpful customer support agent.
Customer Query: {customer_query}
Please provide a clear, concise response."""

# Create optimizer with multiple feedback signals
optimizer = MetaPromptOptimizer(
    prompt=current_prompt,
    dataset=support_data,
    output_column="agent_response",
    feedback_columns=["customer_satisfaction", "resolution_time", "resolved"],
    openai_model="gpt-4o-mini",
)

# Generate optimized prompt
optimized_prompt = optimizer.optimize()

print("Original prompt:")
print(current_prompt)
print("\nOptimized prompt:")
print(optimized_prompt)

# The optimized prompt will incorporate patterns from high-performing responses
```
