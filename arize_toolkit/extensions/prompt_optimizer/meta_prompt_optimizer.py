import pandas as pd
from typing import List, Union, Optional, Tuple, Dict

from meta_prompt import MetaPrompt
from phoenix.evals.models import OpenAIModel
from phoenix.client.types import PromptVersion
from tiktoken_splitter import TiktokenSplitter
import copy
import re


class MetaPromptOptimizer:
    def __init__(
        self, 
        prompt: Union[PromptVersion, str, List[Dict[str, str]]], 
        dataset: Union[pd.DataFrame, str], 
        output_column: str, 
        feedback_columns: Optional[List[str]] = None, 
        evaluators: Optional[List] = None,
        model = OpenAIModel,
        model_choice = "gpt-4.1-2025-04-14",
        loop_idx = None
    ):
        """
        Initialize the MetaPromptOptimizer
        
        Args:
            prompt: Either an Arize Prompt object or list of messages
            dataset: DataFrame or path to JSON file containing the dataset
            output_column: Name of the column containing LLM outputs
            feedback_columns: List of column names containing existing feedback (must exist in dataset)
            evaluators: List of Phoenix evaluators to run (will update existing feedback columns)
        """
        self.prompt = prompt
        self.dataset = self._load_dataset(dataset)
        self.feedback_columns = feedback_columns or []
        self.evaluators = evaluators or []
        self.output_column = output_column
        self.model_choice = model_choice
        self.loop_idx = loop_idx
        
        # Validate inputs
        self._validate_inputs()
        
        # Initialize components
        self.meta_prompter = MetaPrompt()
        self.optimization_history = []
        
    def _load_dataset(self, dataset: Union[pd.DataFrame, str]) -> pd.DataFrame:
        """Load dataset from DataFrame or JSON file"""
        if isinstance(dataset, pd.DataFrame):
            return dataset
        elif isinstance(dataset, str):
            # Assume it's a JSON file path
            try:
                return pd.read_json(dataset)
            except Exception as e:
                raise ValueError(f"Failed to load dataset from {dataset}: {e}")
        else:
            raise ValueError("Dataset must be a DataFrame or path to JSON file")
    
    def _validate_inputs(self):
        """Validate that we have the necessary inputs for optimization"""
        # Check if we have either feedback columns or evaluators
        if not self.feedback_columns and not self.evaluators:
            raise ValueError(
                "Either feedback_columns or evaluators must be provided. "
                "Need some feedback for MetaPrompt optimization."
            )
        
        # Validate dataset has required columns
        required_columns = [self.output_column]
        if self.feedback_columns:
            required_columns.extend(self.feedback_columns)
        
        missing_columns = [col for col in required_columns if col not in self.dataset.columns]
        if missing_columns:
            raise ValueError(f"Dataset missing required columns: {missing_columns}")
    
    def _extract_prompt_messages(self) -> List[Dict[str, str]]:
        """Extract messages from prompt object or list"""
        if isinstance(self.prompt, PromptVersion):
            # Extract messages from PromptVersion template
            template = self.prompt._template
            if template["type"] == "chat":
                return template["messages"]
            else:
                raise ValueError("Only chat templates are supported")
        elif isinstance(self.prompt, list):
            return self.prompt
        elif isinstance(self.prompt, str): ## ADD FUNCTIONALITY FOR USER OR SYSTEM PROMPT
            return [{"role": "user", "content": self.prompt}]
        else:
            raise ValueError("Prompt must be either a PromptVersion object or list of messages")
    
    def _extract_prompt_content(self) -> str:
        """Extract the main prompt content from messages"""
        messages = self._extract_prompt_messages()
        
        # Look for system or developer message first
        for message in messages:
            if message.get("role") in ["user"]:
                return message.get("content", "")
        
        # Fall back to first message
        if messages:
            return messages[0].get("content", "")
        
        raise ValueError("No valid prompt content found in messages. CURRENTLY ONLY CHECKING FOR USER PROMPT")

    def _detect_template_variables(self, prompt_content: str) -> list[str]:
        _TEMPLATE_RE = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")
        """Return unique {placeholders} that look like template vars."""
        return list({m.group(1) for m in _TEMPLATE_RE.finditer(prompt_content)})
    
    def run_evaluators(self) -> pd.DataFrame:
        """
        Run evaluators on the dataset and update existing feedback columns with results
        
        Returns:
            DataFrame with evaluator results updated in existing feedback columns
        """
        if not self.evaluators:
            return self.dataset
            
        print(f"🔍 Running {len(self.evaluators)} evaluator(s)...")
        for i, evaluator in enumerate(self.evaluators):
            try:
                feedback_data, column_names = evaluator(self.dataset)
                for column_name in column_names:
                    if column_name in self.feedback_columns:
                        self.dataset[column_name] = feedback_data[column_name]
                        print(f"   ✅ Evaluator {i+1}: Updated column '{column_name}'")
                    else:
                        print(f"   ⚠️  Evaluator {i+1}: Column '{column_name}' not in feedback_columns, skipping")
            except Exception as e:
                print(f"   ❌ Evaluator {i+1} failed: {e}")
        
        return self.dataset
    
    def _create_dummy_dataframe(self) -> pd.DataFrame:
        """Create dummy DataFrame for llm_generate to preserve template variables"""
        # Create a dummy df to outsmart the mapping done in phoenix
        # Should replace {var} with {var} so meta prompt is correct
        dummy_data = {
            "var": ["{var}"],  # Add hardcoded var column like in prompt_optimizer.py
        }
        for var in self.template_variables:
            dummy_data[var] = ["{" + var + "}"]
        
        return pd.DataFrame(dummy_data)
    
    def _initialize_llm_model(self):
        """Initialize OpenAI client for generation"""
        import os
        from openai import OpenAI
        
        try:
            # Always use OpenAI GPT-4 for optimization
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set. Please set your OpenAI API key.")
            
            client = OpenAI(api_key=api_key)
            return client
        except Exception as e:
            raise ValueError(f"Failed to initialize OpenAI client: {e}")
    
    def optimize(self, context_size_k: int = 128000) -> Tuple[Union[PromptVersion, List[Dict[str, str]]], pd.DataFrame]:
        """
        Optimize the prompt using the meta-prompt approach
        
        Args:
            context_size_k: Context window size in thousands of tokens (default: 128000)
            
        Returns:
            Tuple of (optimized_prompt, dataset_with_feedback)
            
        Note:
            This method runs optimization on the dataset with existing feedback columns.
            To run evaluators and update feedback columns, call run_evaluators() separately.
        """
        # Extract prompt content
        prompt_content = self._extract_prompt_content()
        # Auto-detect template variables
        self.template_variables = self._detect_template_variables(prompt_content)
        # Initialize LLM model
        model = self._initialize_llm_model()
        
        # Initialize tiktoken splitter
        splitter = TiktokenSplitter(model="gpt-4o")
        
        # Determine which columns to include in token counting
        # columns_to_count = self.template_variables + self.feedback_columns + [self.output_column]
        columns_to_count = list(self.dataset.columns)
        
        # Create batches based on token count

        batch_dataframes = splitter.get_batch_dataframes(
            self.dataset, 
            columns_to_count, 
            context_size_k
        )
        
        print(f"📊 Processing {len(self.dataset)} examples in {len(batch_dataframes)} batches")
        
        # Process dataset in batches
        optimized_prompt_content = prompt_content
        
        for i, batch in enumerate(batch_dataframes):
            
            try:

                # Construct meta-prompt content
                meta_prompt_content = self.meta_prompter.construct_content(
                    batch_df=batch,
                    prompt_to_optimize_content=optimized_prompt_content,
                    template_variables=self.template_variables,
                    feedback_columns=self.feedback_columns,
                    output_column=self.output_column,
                )

                with open(f"meta_prompt_content_{self.loop_idx}.txt", 'w') as file:
                    file.write(meta_prompt_content)

                model = OpenAIModel(
                    model=self.model_choice,
                    temperature=0.7,
                    max_tokens=2000
                )

                import tiktoken

                tiktoken_encoder = tiktoken.encoding_for_model("gpt-4o")
                prompt_tokens = len(tiktoken_encoder.encode(meta_prompt_content))
                print(f"prompt_tokens: {prompt_tokens}")

                response = model(meta_prompt_content)

                potential_new_prompt = response
                
                # Validate that new prompt has same template variables
                
                print(f"   ✅ Batch {i + 1}/{len(batch_dataframes)}: Optimized")
                optimized_prompt_content = potential_new_prompt
                    
            except Exception as e:
                print(f"   ❌ Batch {i + 1}/{len(batch_dataframes)}: Failed - {e}")
                continue
        
        # Create optimized prompt object
        optimized_prompt = self._create_optimized_prompt(optimized_prompt_content)
        return optimized_prompt
    
    def _create_optimized_prompt(self, optimized_content: str) -> Union[PromptVersion, List[Dict[str, str]]]:
        """Create optimized prompt in the same format as input"""    
          
        if isinstance(self.prompt, PromptVersion):
            # Create new Prompt object with optimized content
            original_messages = self._extract_prompt_messages()
            optimized_messages = copy.deepcopy(original_messages)
            
            # Replace the main content (system or first message)
            for i, message in enumerate(optimized_messages):
                if message.get("role") in ["user"]: ## ADD FUNCTIONALITY FOR SYSTEM PROMPT
                    optimized_messages[i]["content"] = optimized_content
                    break
            else:
                print("No user prompt found in the original prompt")
            
            # Create a new PromptVersion with optimized content
            return PromptVersion(
                optimized_messages,
                model_name=self.prompt._model_name,
                model_provider=self.prompt._model_provider,
                description=f"Optimized version of {getattr(self.prompt, 'name', 'prompt')}"
            )

        elif isinstance(self.prompt, list):
            # Return optimized messages list
            original_messages = self._extract_prompt_messages()
            optimized_messages = copy.deepcopy(original_messages)
            
            # Replace the main content
            for i, message in enumerate(optimized_messages):
                if message.get("role") in ["user"]: ## ADD FUNCTIONALITY FOR SYSTEM PROMPT
                    optimized_messages[i]["content"] = optimized_content
                    break
            else:
                print("No user prompt found in the original prompt")
            
            return optimized_messages
        
        elif isinstance(self.prompt, str):
            return optimized_content
        
        else:
            raise ValueError("Prompt must be either a PromptVersion object or list of messages or string")
