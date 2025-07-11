from typing import List, Mapping, Union

import pandas as pd

START_DELIM = "{"
END_DELIM = "}"


class MetaPrompt:
    def __init__(self) -> None:
        self.meta_prompt_messages = """
You are an expert in prompt optimization. Given the original baseline prompt and the following associated metadata (such as model inputs, outputs, evaluation labels and explanations), generate a revised version of the original prompt that would likely improve results with respect to the evaluation labels. Your goal is to align the prompt with the feedback and evaluation criteria.

BELOW IS THE ORIGINAL BASELINE PROMPT
************* start prompt *************


{baseline_prompt}
************* end prompt *************

BELOW ARE THE EXAMPLES USING THE ABOVE PROMPT
************* start example data *************


{examples}
************* end example data *************

FINAL INSTRUCTIONS
Iterate on the original prompt (above) with a new prompt that will improve the results, based on the examples and feedback above.

A common best practice in prompt optimization is to add guidelines and the most helpful few shot examples.

Note: Make sure to include the variables from the original prompt, which are wrapped in either single brackets or double brackets (e.g. 
{var}). If you fail to include these variables, the LLM will not be able to access the required data.

YOUR NEW PROMPT:
"""

    def construct_content(
        self,
        batch_df: pd.DataFrame,
        prompt_to_optimize_content: str,
        template_variables: List[str],
        feedback_columns: List[str],
        output_column: str,
    ) -> str:
        content = self.meta_prompt_messages
        content = content.replace(
            "{baseline_prompt}", prompt_to_optimize_content
        )
        examples = ""
        # iterate over the batch of data and populate the template with the actual values from the dataframe
        # need to populate the template customer is optimizing with template variables
        # add the output from the LLM, add the feedback (will be from evaluator or annotator)
        for ind, row in batch_df.iterrows():
            populated_template = self.format_template_with_vars(
                prompt_to_optimize_content,
                template_variables,
                {temp_var: row[temp_var] for temp_var in template_variables},
            )
            output_value = (
                row[output_column]
                .replace(START_DELIM, " ")
                .replace(END_DELIM, " ")
                if row[output_column] is not None
                else "None"
            )
            current_example = f"""\n
                Example {str(ind)}
                
                Original Template With Variables from the Baseline Prompt Populated: {populated_template}

                Output from the LLM using the template above: {output_value}

                Feedback from the evaluator using the template above and the output above:
            """
            
            for feedback_column in feedback_columns:
                feedback_value = row[feedback_column]
                if feedback_value is not None:
                    # Cast to string to handle integers and other types
                    feedback_value = str(feedback_value)
                    feedback_value = feedback_value.replace(
                        START_DELIM, " "
                    ).replace(END_DELIM, " ")
                else:
                    feedback_value = "None"
                current_example += f"\n{feedback_column}: {feedback_value}"
            examples += current_example
        content = content.replace("{examples}", examples)
        return content

    def format_template_with_vars(
        self,
        template: str,
        template_variables: List[str],
        variable_values: Mapping[str, Union[bool, int, float, str]],
    ) -> str:
        for template_var in template_variables:
            var_value = str(variable_values[template_var])
            if var_value is not None:
                var_value = var_value.replace(START_DELIM, " ")
                var_value = var_value.replace(END_DELIM, " ")
            template = template.replace(
                START_DELIM + template_var + END_DELIM,
                var_value,
            )
        return template
