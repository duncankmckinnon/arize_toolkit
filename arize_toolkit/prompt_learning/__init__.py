"""
Prompt Learning SDK for Arize Toolkit

This module provides tools for automatically optimizing prompts using meta-prompt techniques.
Requires the 'prompt' optional dependency to be installed.
"""

try:
    from arize_toolkit.prompt_learning.meta_prompt_optimizer import MetaPromptOptimizer

    __all__ = [
        "MetaPromptOptimizer",
    ]
except ImportError as e:
    # If optional dependencies are not installed, provide helpful error message
    raise ImportError("The prompt learning functionality requires the 'prompt' optional dependency. " "Install it with: pip install arize_toolkit[prompt]") from e
