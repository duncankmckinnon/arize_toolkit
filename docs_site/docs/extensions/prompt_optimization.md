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

| Component | Function | Purpose |
|-----------|----------|---------|
| [`MetaPromptOptimizer`](#metapromptoptimizer) | | Main class for prompt optimization workflow |
| | [`optimize`](#optimize) | Generate optimized prompt from historical data |
| | [`run_evaluators`](#run_evaluators) | Run evaluators to add feedback columns |
| [`TiktokenSplitter`](#tiktokensplitter) | | Utility for splitting datasets into token-limited batches |
| | [`get_batch_dataframes`](#get_batch_dataframes) | Split DataFrame into token-limited batches |

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

Once installed, import the extension like this:

```python
from arize_toolkit.extensions.prompt_optimizer import MetaPromptOptimizer
```

### API Key Configuration

The MetaPromptOptimizer requires an OpenAI API key. You can provide it in two ways:

**Method 1: Environment Variable (Recommended)**
Either set the environment variable in your notebook or project directly (as shown), or provide it in a docker `env` configuration or local `.env` file. As long as the name is `OPENAI_API_KEY`, it will be picked up automatically.

```python
import os

# Set the environment variable
os.environ["OPENAI_API_KEY"] = "your-api-key-here"

# The optimizer will automatically use the environment variable
optimizer = MetaPromptOptimizer(
    prompt="Answer: {question}", dataset=data, output_column="answer"
)
```

**Method 2: Direct Parameter**
You can also pass in the key directly within the function.

```python
# Pass the API key directly
optimizer = MetaPromptOptimizer(
    prompt="Answer: {question}",
    dataset=data,
    output_column="answer",
    openai_api_key="your-api-key-here",
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
    model_choice: str = "gpt-4",
    openai_api_key: str | None = None,
)
```

The main class for optimizing prompts based on historical performance data. It analyzes past interactions and generates improved prompt templates.

**Parameters**

- `prompt` – The prompt to optimize. Can be:

  A string template (e.g., "Answer the question: {question}")

  A list of message dictionaries (e.g., `[{"role": "system", "content": "..."}]`)

  A Phoenix `PromptVersion` object

- `dataset` – Historical performance data. Can be:

  A pandas DataFrame with input, output, and feedback columns

  A path to a JSON file containing the data

- `output_column` – Column name containing model outputs

- `feedback_columns` *(optional)* – List of column names containing feedback/evaluation data

- `evaluators` *(optional)* – List of Phoenix evaluators to run on the dataset

- `model_choice` *(optional)* – OpenAI model to use for optimization. Defaults to "gpt-4"

- `openai_api_key` *(optional)* – OpenAI API key.

  Required for optimization runs with LLM to generate new prompts.

  If not provided will attempt to use `OPENAI_API_KEY` environment variable

**Returns**

A `MetaPromptOptimizer` instance ready to optimize prompts.

**Example**

```python
import os
import pandas as pd
from arize_toolkit.extensions.prompt_optimizer import MetaPromptOptimizer

# Set OpenAI API key (if not already set)
os.environ["OPENAI_API_KEY"] = "your-api-key-here"

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
optimized_prompt, updated_dataset = optimizer.optimize()
print(optimized_prompt)
```

### `optimize`

```python
optimized_prompt, updated_dataset = optimizer.optimize(
    context_size_k: int = 8000
)
```

Runs the optimization process to generate an improved prompt based on the historical data.

**Parameters**

- `context_size_k` *(optional)* – Maximum context size in thousands of tokens. Defaults to 8000

**Returns**

A tuple containing:

- The optimized prompt in the same format as the input (string, list, or PromptVersion)
- Updated dataset with additional feedback columns from evaluators

**Example**

```python
# Basic optimization
optimized_prompt, dataset = optimizer.optimize()

# With smaller context size
optimized_prompt, dataset = optimizer.optimize(context_size_k=4000)
```

### `run_evaluators`

```python
updated_dataset: pd.DataFrame = optimizer.run_evaluators()
```

Runs the configured evaluators on the dataset to generate additional feedback columns.

**Parameters**

None

**Returns**

DataFrame with additional feedback columns added by the evaluators.

**Example**

```python
# Define evaluators
def length_evaluator(row):
    return {"response_length": len(row["answer"])}


def quality_evaluator(row):
    score = 1.0 if row["answer"].lower() in row["question"].lower() else 0.5
    return {"relevance_score": score}


# Create optimizer with evaluators
optimizer = MetaPromptOptimizer(
    prompt="Answer: {question}",
    dataset=data,
    output_column="answer",
    evaluators=[length_evaluator, quality_evaluator],
)

# Run evaluators to add feedback columns
evaluated_data = optimizer.run_evaluators()
print(evaluated_data.columns)  # Includes 'response_length' and 'relevance_score'
```

______________________________________________________________________

## `TiktokenSplitter`

### Overview

```python
splitter = TiktokenSplitter(
    model: str = "gpt-4o"
)
```

A utility class for splitting large datasets into token-limited batches. Essential for processing datasets that exceed model context limits.

**Parameters**

- `model` *(optional)* – The model name for tokenization. Defaults to "gpt-4o"

**Example**

```python
from arize_toolkit.extensions.prompt_optimizer import TiktokenSplitter

splitter = TiktokenSplitter(model="gpt-4o-mini")
```

### `get_batch_dataframes`

```python
batch_dataframes: list[pd.DataFrame] = splitter.get_batch_dataframes(
    df: pd.DataFrame,
    columns: list[str],
    context_size_tokens: int
)
```

Splits a DataFrame into batches that fit within a token limit, returning a list of DataFrame chunks.

**Parameters**

- `df` – The DataFrame to split into batches
- `columns` – Column names containing text to count tokens for
- `context_size_tokens` – Maximum tokens per batch

**Returns**

A list of DataFrame chunks, each containing rows that fit within the context size.

**Example**

```python
df = pd.DataFrame(
    {
        "prompt": ["Short text", "Medium length text here", "Very long text..."],
        "response": ["Yes", "Detailed response...", "Extended answer..."],
        "feedback": ["good", "excellent", "needs improvement"],
    }
)

# Get batches that fit within token limit
batches = splitter.get_batch_dataframes(
    df=df, columns=["prompt", "response"], context_size_tokens=1000
)

# Process each batch DataFrame
for i, batch_df in enumerate(batches):
    print(f"Batch {i}: {len(batch_df)} rows")
    # Each batch_df is a DataFrame with all original columns
    process_batch(batch_df)
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

optimized_v2, updated_dataset = optimizer.optimize()
```

### Handling Large Datasets

For datasets that exceed context limits:

```python
# The optimizer automatically handles batching
optimizer = MetaPromptOptimizer(
    prompt=template,
    dataset=large_df,  # e.g., 10,000 rows
    output_column="output",
    model_choice="gpt-4",
)

# Specify smaller context size for more batches
optimized_prompt, dataset = optimizer.optimize(context_size_k=4000)
```

______________________________________________________________________

## Best Practices

1. **Data Quality**: Ensure your historical data has meaningful feedback signals
1. **Feedback Diversity**: Use multiple feedback columns for better optimization
1. **Template Variables**: Keep variable names consistent between prompt and data
1. **Context Size**: Adjust `context_size_k` based on your model's limits
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
# Reduce context_size_k:
optimized_prompt, dataset = optimizer.optimize(context_size_k=2000)
```

______________________________________________________________________

## Complete Example

Here's a full workflow for optimizing a customer support prompt:

```python
import os
import pandas as pd
from arize_toolkit.extensions.prompt_optimizer import MetaPromptOptimizer

# Configure OpenAI API key
# Option 1: Environment variable (recommended for production)
os.environ["OPENAI_API_KEY"] = "your-api-key-here"

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
    model_choice="gpt-4",
)

# Generate optimized prompt
optimized_prompt, updated_dataset = optimizer.optimize()

print("Original prompt:")
print(current_prompt)
print("\nOptimized prompt:")
print(optimized_prompt)

# The optimized prompt will incorporate patterns from high-performing responses
```
