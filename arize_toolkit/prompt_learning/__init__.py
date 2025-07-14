"""
Prompt Learning SDK for Arize Toolkit

This module provides tools for automatically optimizing prompts using meta-prompt techniques.
Requires the 'prompt' optional dependency to be installed.
"""

try:
    from .meta_prompt_optimizer import MetaPromptOptimizer
    from .meta_prompt import MetaPrompt
    from .tiktoken_splitter import TikTokenSplitter
    from .constants import *
    
    __all__ = [
        "MetaPromptOptimizer",
        "MetaPrompt", 
        "TikTokenSplitter",
    ]
except ImportError as e:
    # If optional dependencies are not installed, provide helpful error message
    raise ImportError(
        "The prompt learning functionality requires the 'prompt' optional dependency. "
        "Install it with: pip install arize_toolkit[prompt]"
    ) from e 