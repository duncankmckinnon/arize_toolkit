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
    prompt="Answer: {question}",
)
```

**Method 2: Direct Parameter**
You can also pass in the key directly within the function.

```python
# Pass the API key directly
optimizer = MetaPromptOptimizer(
    prompt="Answer: {question}",
    openai_api_key="your-api-key-here",
)
```

______________________________________________________________________

## `MetaPromptOptimizer`

### Overview

```python
optimizer = MetaPromptOptimizer(
    prompt: Union[PromptVersion, str, List[Dict[str, str]]],
    model_choice: str = "gpt-4",
    openai_api_key: Optional[str] = None,
)
```

**Parameters**

- `prompt` – The prompt to optimize. Can be:

  A string prompt template with `{variable}` placeholders

  A list of message dictionaries for chat-based prompts

  A Phoenix `PromptVersion` object

- `model_choice` *(optional)* – OpenAI model to use for optimization. Defaults to "gpt-4"

- `openai_api_key` *(optional)* – OpenAI API key.

  If not provided, uses `OPENAI_API_KEY` environment variable

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
    model_choice="gpt-4",
)

# Generate optimized prompt
optimized_prompt = optimizer.optimize(
    dataset=data,
    output_column="answer",
    feedback_columns=["accuracy", "relevance"],
)
print(optimized_prompt)
```

### `run_evaluators`

```python
evaluated_dataset, feedback_columns = optimizer.run_evaluators(
    dataset: Union[pd.DataFrame, str],
    evaluators: List[Callable],
    feedback_columns: List[str] = [],
)
```

Runs evaluators on the dataset to generate or augment feedback columns. This can be used as a separate preprocessing step before optimization.

**Parameters**

- `dataset` – The dataset to evaluate. Can be:

  A pandas DataFrame

  A path to a JSON file

- `evaluators` – List of Phoenix evaluators to run on the dataset

- `feedback_columns` *(optional)* – List of existing feedback column names to preserve

**Returns**

- A tuple containing:

  The dataset with new evaluation columns added

  Complete list of all feedback columns (existing + new)

**Example**

```python
from phoenix.evals import llm_classify

# Define evaluator
evaluator = llm_classify(
    template=RAG_RELEVANCY_PROMPT_TEMPLATE,
    model=model,
    rails=["relevant", "irrelevant"],
)

# Run evaluation
evaluated_data, all_feedback_cols = optimizer.run_evaluators(
    dataset=data,
    evaluators=[evaluator],
    feedback_columns=[
        "existing_score"
    ],  # Preserve existing annotation and feedback columns
)
```

### `optimize`

```python
optimized_prompt = optimizer.optimize(
    dataset: Union[pd.DataFrame, str],
    output_column: str,
    evaluators: List[Callable] = [],
    feedback_columns: List[str] = [],
    context_size_k: int = 8000,
)
```

Runs the optimization process to generate an improved prompt based on historical data and feedback.

**Parameters**

- `dataset` – Historical performance data. Can be:

  A pandas DataFrame with input, output, and feedback columns

  A path to a JSON file containing the data

- `output_column` – Column name containing model outputs

- `evaluators` *(optional)* – List of Phoenix evaluators to run before optimization.

  If provided, these will be executed automatically as part of the optimization process

- `feedback_columns` *(optional)* – List of existing feedback/evaluation column names in the dataset.

  Required if not using evaluators

- `context_size_k` *(optional)* – Maximum context size in thousands of tokens. Defaults to 8000

**Returns**

The optimized prompt in the same format as the input (string, list, or PromptVersion)

**Example**

```python
# Optimization with existing feedback
optimized_prompt = optimizer.optimize(
    dataset=data,
    output_column="answer",
    feedback_columns=["accuracy", "relevance"],
)

# Optimization with evaluators
optimized_prompt = optimizer.optimize(
    dataset=data,
    output_column="answer",
    evaluators=[relevance_evaluator, quality_evaluator],
)

# With custom context size
optimized_prompt = optimizer.optimize(
    dataset=data,
    output_column="answer",
    feedback_columns=["score"],
    context_size_k=4000,
)
```

______________________________________________________________________

## `TiktokenSplitter`

### Overview

```python
splitter = TiktokenSplitter(
    model: str = "gpt-4"
)
```

A utility class for splitting large datasets into token-limited batches. Essential for processing datasets that exceed model context limits.

**Parameters**

- `model` *(optional)* – The model name for tokenization. Defaults to "gpt-4"

**Example**

```python
from arize_toolkit.extensions.prompt_optimizer import TiktokenSplitter

splitter = TiktokenSplitter(model="gpt-4.1")
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

### Running Evaluations Separately

The `MetaPromptOptimizer` allows you to run evaluations either as part of the optimization process or as a separate step. This flexibility is useful when you want to:

1. Pre-process your dataset with evaluations before optimization
1. Add additional evaluations to an existing dataset
1. Inspect evaluation results before proceeding with optimization

- Example: Separate Evaluation Step

```python
from arize_toolkit.extensions.prompt_optimizer import MetaPromptOptimizer
from phoenix.evals import llm_classify, RAG_RELEVANCY_PROMPT_TEMPLATE

# Initialize optimizer
optimizer = MetaPromptOptimizer(
    prompt="Answer the question: {question}",
    model_choice="gpt-4",
)

# Define evaluators
relevance_evaluator = llm_classify(
    template=RAG_RELEVANCY_PROMPT_TEMPLATE,
    model=model,
    rails=["relevant", "irrelevant"],
)

# Step 1: Run evaluations separately
evaluated_dataset, feedback_columns = optimizer.run_evaluators(
    dataset=original_dataset,
    evaluators=[relevance_evaluator],
    feedback_columns=["existing_feedback"],  # Optional existing columns
)

# Inspect the results
print(f"Feedback columns: {feedback_columns}")
print(evaluated_dataset[feedback_columns].head())

# Step 2: Run optimization with the evaluated dataset
optimized_prompt = optimizer.optimize(
    dataset=evaluated_dataset,
    output_column="answer",
    feedback_columns=feedback_columns,
)
```

- Example: Running Evaluations Within Optimization

You can also run evaluations as part of the optimization process:

```python
# Run evaluations and optimization in one step
optimized_prompt = optimizer.optimize(
    dataset=original_dataset,
    output_column="answer",
    evaluators=[relevance_evaluator],  # Evaluations run automatically
    feedback_columns=["existing_feedback"],  # Optional existing columns
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
    model_choice="gpt-4",
)

optimized_v2 = optimizer.optimize(
    dataset=historical_data,
    output_column="response",
    feedback_columns=["rating", "feedback"],
)
```

### Handling Large Datasets

For datasets that exceed context limits:

```python
# The optimizer automatically handles batching
optimizer = MetaPromptOptimizer(
    prompt=template,
    model_choice="gpt-4",
)

# Specify smaller context size for more batches
optimized_prompt = optimizer.optimize(
    dataset=large_df,  # e.g., 10,000 rows
    output_column="output",
    feedback_columns=["score"],
    context_size_k=4000,
)
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
optimized_prompt = optimizer.optimize(
    dataset=data,
    output_column="output", 
    feedback_columns=["score"],
    context_size_k=2000
)
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
    model_choice="gpt-4",
)

# Run optimization
optimized_prompt = optimizer.optimize(
    dataset=support_data,
    output_column="agent_response",
    feedback_columns=["customer_satisfaction", "resolution_time", "resolved"],
)

# The optimized prompt will incorporate patterns from high-performing responses
```

## API Reference

### MetaPromptOptimizer

```python
class MetaPromptOptimizer:
    def __init__(
        self,
        prompt: Union[PromptVersion, str, List[Dict[str, str]]],
        model_choice: str = "gpt-4",
        openai_api_key: Optional[str] = None,
    ):
        """
        Initialize the MetaPromptOptimizer.

        Args:
            prompt: The prompt to optimize (PromptVersion, string, or list of messages)
            model_choice: OpenAI model to use for optimization (default: "gpt-4")
            openai_api_key: OpenAI API key (optional, can use env var)
        """

    def run_evaluators(
        self,
        dataset: Union[pd.DataFrame, str],
        evaluators: List[Callable],
        feedback_columns: List[str] = [],
    ) -> Tuple[pd.DataFrame, List[str]]:
        """
        Run evaluators on the dataset and add results to feedback columns.

        Args:
            dataset: DataFrame or path to JSON file
            evaluators: List of Phoenix evaluators to run
            feedback_columns: Existing feedback columns to preserve

        Returns:
            Tuple of (evaluated_dataset, all_feedback_columns)
        """

    def optimize(
        self,
        dataset: Union[pd.DataFrame, str],
        output_column: str,
        evaluators: List[Callable] = [],
        feedback_columns: List[str] = [],
        context_size_k: int = 8000,
    ) -> Union[PromptVersion, Sequence]:
        """
        Optimize the prompt using the meta-prompt approach.

        Args:
            dataset: DataFrame or path to JSON file
            output_column: Column containing LLM outputs
            evaluators: Optional evaluators to run before optimization
            feedback_columns: Existing feedback columns
            context_size_k: Context window size in thousands of tokens

        Returns:
            Optimized prompt in the same format as input
        """
```
