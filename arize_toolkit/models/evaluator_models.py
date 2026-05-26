import re
from datetime import datetime
from typing import List, Optional

from pydantic import Field, model_validator

from arize_toolkit.models.base_models import User
from arize_toolkit.types import EvalDataGranularityType, OnlineTaskType, TemplateEvaluationConfigDirection
from arize_toolkit.utils import GraphQLModel

# Regex patterns for code evaluator validation
_CLASS_DEF_PATTERN = re.compile(r"class\s+([A-Za-z_]\w*)\s*\(.*?CodeEvaluator.*?\)\s*:")
_EVALUATE_METHOD_PATTERN = re.compile(r"def\s+evaluate\s*\(")


class TemplateEvaluationLlmConfig(GraphQLModel):
    """LLM configuration for a template evaluator"""

    integrationId: str = Field(description="The selected named LLM integration id (relay global id)")
    modelName: str = Field(description="The LLM model name")
    invocationParameters: dict = Field(description="Parameters used when running the LLM")
    providerParameters: dict = Field(description="Parameters used to initialize the LLM")


class TemplateEvaluationConfig(GraphQLModel):
    """A template evaluation config"""

    id: Optional[str] = Field(default=None, description="The ID of the template evaluation config")
    name: str = Field(description="The name of the template evaluation config")
    template: str = Field(description="The prompt template with {{variables}} for the LLM evaluator")
    position: int = Field(default=0, description="The position/order of the evaluator")
    includeExplanations: bool = Field(default=True, description="Whether to include explanations")
    useFunctionCallingIfAvailable: bool = Field(default=True, description="Whether to use function calling if available")
    rails: Optional[List[str]] = Field(default=None, description="The rails associated with the config")
    queryFilter: Optional[str] = Field(default=None, description="Optional query filter over a given data granularity")
    classificationChoices: Optional[dict] = Field(default=None, description="Maps labels to scores for categorical evaluations (e.g., {'Yes': 0, 'No': 1})")
    direction: Optional[TemplateEvaluationConfigDirection] = Field(default=None, description="Whether higher or lower scores are better (maximize or minimize)")
    dataGranularityType: Optional[EvalDataGranularityType] = Field(default=None, description="The granularity level for evaluation (span, trace, or session)")
    llmConfig: Optional[TemplateEvaluationLlmConfig] = Field(default=None, description="LLM configuration for this evaluator")
    createdAt: Optional[datetime] = Field(default=None, description="When the config was created")
    updatedAt: Optional[datetime] = Field(default=None, description="When the config was last updated")
    createdBy: Optional[User] = Field(default=None, description="The user who created the config")


class CodeEvaluationConfig(GraphQLModel):
    """A code evaluation config"""

    id: Optional[str] = Field(default=None, description="The ID of the code evaluation config")
    name: str = Field(description="The name of the evaluator metric")
    position: int = Field(default=0, description="The position/order of the evaluator")
    evalClassCodeBlock: Optional[str] = Field(default=None, description="Python code defining the evaluator class")
    evaluationClass: Optional[str] = Field(default=None, description="The name of the evaluator class in the code block")
    evaluationInputParams: Optional[dict] = Field(default=None, description="The evaluation input parameters")
    packageImports: Optional[str] = Field(default=None, description="Package imports for the evaluation class")
    queryFilter: Optional[str] = Field(default=None, description="Optional query filter over a given data granularity")
    spanAttributes: Optional[List[str]] = Field(default=None, description="Which span fields to pass as inputs (e.g., ['output', 'input'])")
    dataGranularityType: Optional[EvalDataGranularityType] = Field(default=None, description="The granularity level for evaluation (span, trace, or session)")
    createdAt: Optional[datetime] = Field(default=None, description="When the config was created")
    updatedAt: Optional[datetime] = Field(default=None, description="When the config was last updated")
    createdBy: Optional[User] = Field(default=None, description="The user who created the config")

    @model_validator(mode="after")
    def validate_code_evaluator(self):
        # Skip validation when reading from API (id is set, code block may not be present)
        if self.id is not None:
            return self

        if self.evalClassCodeBlock:
            # Validate that the code block contains a class extending CodeEvaluator
            class_matches = _CLASS_DEF_PATTERN.findall(self.evalClassCodeBlock)
            if not class_matches:
                raise ValueError("evalClassCodeBlock must define a class that extends CodeEvaluator " "(e.g., 'class MyEvaluator(CodeEvaluator):')")

            # Validate evaluationClass matches a class name in the code block
            if self.evaluationClass and self.evaluationClass not in class_matches:
                raise ValueError(f"evaluationClass '{self.evaluationClass}' does not match any CodeEvaluator " f"subclass in the code block. Found: {class_matches}")

            # Validate that the code block contains an evaluate method
            if not _EVALUATE_METHOD_PATTERN.search(self.evalClassCodeBlock):
                raise ValueError("evalClassCodeBlock must define an 'evaluate' method " "in the CodeEvaluator subclass")

        if self.packageImports is not None:
            stripped = self.packageImports.strip()
            if stripped:
                # Check that every non-empty, non-comment line is an import statement
                # Handles multi-line imports with parentheses by tracking open parens
                in_paren_import = False
                non_import_lines = []
                for line in stripped.splitlines():
                    line_stripped = line.strip()
                    if not line_stripped or line_stripped.startswith("#"):
                        continue
                    if in_paren_import:
                        if ")" in line_stripped:
                            in_paren_import = False
                        continue
                    if line_stripped.startswith("import ") or line_stripped.startswith("from "):
                        if "(" in line_stripped and ")" not in line_stripped:
                            in_paren_import = True
                        continue
                    non_import_lines.append(line_stripped)
                if non_import_lines:
                    raise ValueError(f"packageImports must contain only valid Python import statements. " f"Invalid lines: {non_import_lines}")

        if not self.spanAttributes:
            raise ValueError("spanAttributes is required and must specify which span fields to pass " "as inputs (e.g., ['output', 'input'])")

        return self


class Evaluator(GraphQLModel):
    """An evaluator configuration"""

    id: str = Field(description="The ID of the evaluator")
    name: str = Field(description="The name of the evaluator")
    description: Optional[str] = Field(default=None, description="The description of the evaluator")
    taskType: Optional[OnlineTaskType] = Field(default=None, description="The type of online task")
    commitHash: Optional[str] = Field(default=None, description="The commit hash of the evaluator version")
    commitMessage: Optional[str] = Field(default=None, description="The commit message")
    tags: Optional[List[str]] = Field(default=None, description="Tags associated with the evaluator")
    createdAt: Optional[datetime] = Field(default=None, description="When the evaluator was created")
    updatedAt: Optional[datetime] = Field(default=None, description="When the evaluator was last updated")
    createdBy: Optional[User] = Field(default=None, description="The user who created the evaluator")


class CreateEvaluatorMutationInput(GraphQLModel):
    """Input for creating an evaluator (either template or code)"""

    spaceId: str = Field(description="The ID of the space to create the evaluator in")
    name: str = Field(description="The name of the evaluator")
    description: Optional[str] = Field(default=None, description="The description of the evaluator")
    tags: Optional[List[str]] = Field(default=None, description="Tags for the evaluator")
    commitMessage: str = Field(description="Version control message for this evaluator")
    templateEvaluator: Optional[TemplateEvaluationConfig] = Field(default=None, description="Template evaluator configuration (LLM-based)")
    codeEvaluator: Optional[CodeEvaluationConfig] = Field(default=None, description="Code evaluator configuration (Python-based)")


class CreateEvaluatorVersionMutationInput(GraphQLModel):
    """Input for creating a new version of an existing evaluator"""

    evaluatorId: str = Field(description="The evaluator ID to create a version for")
    commitMessage: Optional[str] = Field(default=None, description="The commit message for this version")
    templateEvaluator: Optional[TemplateEvaluationConfig] = Field(default=None, description="Template evaluator configuration")
    codeEvaluator: Optional[CodeEvaluationConfig] = Field(default=None, description="Code evaluator configuration")


class EditEvaluatorMutationInput(GraphQLModel):
    """Input for editing an evaluator's metadata"""

    evaluatorId: str = Field(description="The evaluator ID to edit")
    name: Optional[str] = Field(default=None, description="The new name for the evaluator")
    description: Optional[str] = Field(default=None, description="The new description for the evaluator")
    tags: Optional[List[str]] = Field(default=None, description="The new tags for the evaluator")


class DeleteEvaluatorMutationInput(GraphQLModel):
    """Input for deleting an evaluator"""

    evaluatorId: str = Field(description="The evaluator ID to delete")
