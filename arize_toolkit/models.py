from datetime import datetime
from typing import List, Optional, Literal, Union, Dict, Any
from pydantic import Field, model_validator

from arize_toolkit.types import (
    MonitorCategory,
    PerformanceMetric,
    ModelType,
    DimensionCategory,
    ComparisonOperator,
    DriftMetric,
    DataQualityMetric,
    ModelEnvironment,
    DimensionDataType,
    PromptVersionInputVariableFormatEnum,
    LLMIntegrationProvider,
    ExternalLLMProviderModel,
)
from arize_toolkit.utils import GraphQLModel, FormattedPrompt

#### Common GraphQL Models ####


class User(GraphQLModel):
    id: str = Field(description="The ID of the user")
    name: Optional[str] = Field(default=None, description="The name of the user")
    email: Optional[str] = Field(default=None, description="The email of the user")


class Dimension(GraphQLModel):
    id: Optional[str] = Field(default=None)
    name: str
    dataType: Optional[DimensionDataType] = Field(default=None)
    category: Optional[DimensionCategory] = Field(default=None)


#### Space GraphQL Models ####


class Space(GraphQLModel):
    id: str
    name: str


#### Model GraphQL Models ####


class Model(GraphQLModel):
    id: str
    name: str
    modelType: ModelType
    createdAt: datetime
    isDemoModel: bool


#### Custom Metric GraphQL Models ####


class CustomMetric(GraphQLModel):
    id: Optional[str] = Field(default=None)
    name: str
    createdAt: Optional[datetime] = Field(default=None)
    description: Optional[str] = Field(default=None)
    metric: str
    requiresPositiveClass: bool


class CustomMetricInput(GraphQLModel):
    modelId: str
    name: str
    description: str = Field(default="a custom metric")
    metric: str
    modelEnvironmentName: ModelEnvironment = Field(default=ModelEnvironment.production)


#### Monitor GraphQL Models ####


class MonitorContact(GraphQLModel):
    id: Optional[str] = Field(default=None)
    notificationChannelType: Literal["email", "slack"]
    emailAddress: Optional[str] = Field(default=None)


class MetricWindow(GraphQLModel):
    id: Optional[str] = Field(default=None)
    type: Optional[Literal["moving", "fixed"]] = Field(default="moving")
    windowLengthMs: Optional[float] = Field(default=86400000)
    dimensionCategory: Optional[DimensionCategory] = Field(default=None)
    dimension: Optional[Dimension] = Field(default=None)


class DynamicAutoThreshold(GraphQLModel):
    stdDevMultiplier: Optional[float] = Field(default=2.0)


class Monitor(GraphQLModel):
    id: str
    name: str
    monitorCategory: MonitorCategory
    createdDate: Optional[datetime] = Field(default=None)
    evaluationIntervalSeconds: Optional[int] = Field(default=259200)
    evaluatedAt: Optional[datetime] = Field(default=None)
    creator: Optional[User] = Field(default=None)
    notes: Optional[str] = Field(default=None)
    contacts: Optional[List[MonitorContact]] = Field(default=None)
    dimensionCategory: Optional[DimensionCategory] = Field(default=None)
    status: Optional[Literal["triggered", "cleared", "noData"]] = Field(
        default="noData"
    )
    isTriggered: Optional[bool] = Field(default=False)
    isManaged: Optional[bool] = Field(default=None)
    threshold: Optional[float] = Field(default=None)
    thresholdMode: Optional[Literal["single", "range"]] = Field(default="single")
    threshold2: Optional[float] = Field(default=None)
    dynamicAutoThresholdEnabled: Optional[bool] = Field(default=False)
    stdDevMultiplier: Optional[float] = Field(default=2.0)
    stdDevMultiplier2: Optional[float] = Field(default=None)
    notificationsEnabled: Optional[bool] = Field(default=False)
    updatedAt: Optional[datetime] = Field(default=None)
    downtimeStart: Optional[datetime] = Field(default=None)
    downtimeDurationHrs: Optional[int] = Field(default=None)
    downtimeFrequencyDays: Optional[int] = Field(default=None)
    scheduledRuntimeEnabled: Optional[bool] = Field(default=False)
    scheduledRuntimeCadenceSeconds: Optional[int] = Field(default=None)
    scheduledRuntimeDaysOfWeek: Optional[List[int]] = Field(default_factory=list)
    latestComputedValue: Optional[float] = Field(default=None)
    performanceMetric: Optional[PerformanceMetric] = Field(default=None)
    dataQualityMetric: Optional[DataQualityMetric] = Field(default=None)
    driftMetric: Optional[DriftMetric] = Field(default=None)
    customMetric: Optional[CustomMetric] = Field(default=None)
    operator: ComparisonOperator = Field(default=ComparisonOperator.greaterThan)
    operator2: Optional[ComparisonOperator] = Field(default=None)
    topKPercentileValue: Optional[float] = Field(default=None)
    positiveClassValue: Optional[str] = Field(default=None)
    metricAtRankingKValue: Optional[int] = Field(default=None)
    primaryMetricWindow: Optional[MetricWindow] = Field(default=None)


class MonitorDetailedType(GraphQLModel):
    spaceId: str
    modelName: str
    name: str
    notes: Optional[str] = Field(default=None)
    contacts: Optional[List[MonitorContact]] = Field(default=None)
    downtimeStart: Optional[datetime] = Field(default=None)
    downtimeDurationHrs: Optional[int] = Field(default=None)
    downtimeFrequencyDays: Optional[int] = Field(default=None)
    scheduledRuntimeEnabled: Optional[bool] = Field(default=False)
    scheduledRuntimeCadenceSeconds: Optional[int] = Field(default=None)
    scheduledRuntimeDaysOfWeek: Optional[List[int]] = Field(default=None)
    evaluationWindowLengthSeconds: float = Field(default=259200)
    delaySeconds: float = Field(default=0)
    threshold: Optional[float] = Field(default=None)
    threshold2: Optional[float] = Field(default=None)
    thresholdMode: Literal["single", "range"] = Field(default="single")
    operator: ComparisonOperator = Field(default=ComparisonOperator.greaterThan)
    operator2: Optional[ComparisonOperator] = Field(default=None)
    dynamicAutoThreshold: Optional[DynamicAutoThreshold] = Field(default=None)
    stdDevMultiplier2: Optional[float] = Field(default=None)


class PerformanceMonitor(MonitorDetailedType):
    performanceMetric: Optional[PerformanceMetric] = Field(default=None)
    customMetricId: Optional[str] = Field(default=None)
    positiveClassValue: Optional[str] = Field(default=None)
    predictionClassValue: Optional[str] = Field(default=None)
    metricAtRankingKValue: Optional[int] = Field(default=None)
    topKPercentileValue: Optional[float] = Field(default=None)
    modelEnvironmentName: ModelEnvironment = Field(default=ModelEnvironment.production)


class DataQualityMonitor(MonitorDetailedType):
    dataQualityMetric: Optional[DataQualityMetric] = Field(default=None)
    dimensionCategory: Optional[DimensionCategory] = Field(default=None)
    dimensionName: Optional[str] = Field(default=None)
    modelEnvironmentName: ModelEnvironment = Field(default=ModelEnvironment.production)


class DriftMonitor(MonitorDetailedType):
    driftMetric: Optional[DriftMetric] = Field(default=DriftMetric.psi)
    dimensionCategory: Optional[DimensionCategory] = Field(default=None)
    dimensionName: Optional[str] = Field(default=None)


#### Language Model GraphQL Models ####


class NoteInput(GraphQLModel):
    text: str


class AnnotationInput(GraphQLModel):
    name: str
    updatedBy: str  # Assuming string, could be User ID
    label: Optional[str] = Field(default=None)
    score: Optional[float] = Field(default=None)
    annotationType: Literal["label", "score"]

    @model_validator(mode="after")
    def verify_type_and_value(self):
        if self.annotationType == "label" and self.label is None:
            raise ValueError("Label is required for label annotation type")
        if self.annotationType == "score" and self.score is None:
            raise ValueError("Score is required for score annotation type")
        return self


class AnnotationMutationInput(GraphQLModel):
    modelId: str
    note: Optional[NoteInput] = Field(default=None)  # Assuming note is optional
    annotations: Union[AnnotationInput, List[AnnotationInput]]
    modelEnvironment: ModelEnvironment = Field(default=ModelEnvironment.tracing)
    recordId: str
    startTime: datetime = Field(default=datetime.now())


class FunctionDetailsInput(GraphQLModel):
    name: str = Field(description="The name of the function to call")
    description: Optional[str] = Field(default=None)
    arguments: str = Field(
        description="The arguments to call the function with, as generated by the model in JSON format. Note that the model does not always generate valid JSON, and may hallucinate parameters not defined by your function schema. Validate the arguments in your code before calling your function."
    )
    parameters: Optional[Dict[str, Any]] = Field(default=None)


class ToolInput(GraphQLModel):
    id: Optional[str] = Field(default=None)
    type: Literal["function"] = Field(default="function")
    function: FunctionDetailsInput


class LLMMessageInput(GraphQLModel):
    role: Literal["user", "assistant", "system", "tool"]
    content: str
    imageUrls: Optional[List[str]] = Field(default=None)
    toolCalls: Optional[List[ToolInput]] = Field(default=None)
    toolCallId: Optional[str] = Field(default=None)


class ToolChoiceTool(GraphQLModel):
    tool: ToolInput

class ToolChoiceChoice(GraphQLModel):
    choice: Literal["auto", "none", "required"]

class ToolChoiceInput(GraphQLModel):
    choice: Optional[Literal["auto", "none", "required"]] = Field(default=None)
    tool: Optional[ToolInput] = Field(default=None)


class ToolConfigInput(GraphQLModel):
    tools: List[ToolInput]
    toolChoice: Optional[ToolChoiceInput] = Field(default=None)


class InvocationParamsInput(GraphQLModel):
    temperature: Optional[float] = Field(default=None)
    top_p: Optional[float] = Field(default=None)
    stop: Optional[List[str]] = Field(default=None)
    max_tokens: Optional[int] = Field(default=None)
    max_completion_tokens: Optional[int] = Field(default=None)
    presence_penalty: Optional[float] = Field(default=None)
    frequency_penalty: Optional[float] = Field(default=None)
    top_k: Optional[int] = Field(default=None)
    tool_config: Optional[ToolConfigInput] = Field(default=None)


class ProviderParamsInput(GraphQLModel):
    azureParams: Optional[Dict] = Field(default=None)
    anthropicHeaders: Optional[Dict] = Field(default=None)
    customProviderParams: Optional[Dict] = Field(default=None)
    anthropic_version: Optional[str] = Field(default=None)
    region: Optional[str] = Field(default=None)


class PromptVersion(GraphQLModel):
    """Version of a prompt template"""

    id: str = Field(description="The ID of the prompt version")
    commitMessage: str = Field(
        description="The commit message describing the changes in this version"
    )
    messages: List[Dict[str, Any]] = Field(
        description="The list of messages making up the prompt template"
    )
    inputVariableFormat: PromptVersionInputVariableFormatEnum = Field(
        description="The input variable format for determining prompt variables in the messages"
    )
    toolCalls: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="The list of tool/function calls defined for this version",
    )
    llmParameters: Dict[str, Any] = Field(
        description="The LLM parameters for execution with the prompt"
    )
    provider: LLMIntegrationProvider = Field(
        description="The LLM provider used for execution with the prompt"
    )
    modelName: Optional[ExternalLLMProviderModel] = Field(
        default=None, description="The LLM model used for execution with the prompt"
    )
    createdAt: datetime = Field(description="The datetime the version was created")
    createdBy: Optional[User] = Field(
        default=None, description="The user who created the version"
    )

    def format(self, **variables) -> FormattedPrompt:
        """Convert the prompt version to an OpenAI formatted prompt"""
        formatted_prompt = FormattedPrompt()
        formatted_messages = []
        for message in self.messages:
            formatted_message = message.copy()
            if "content" in formatted_message:
                formatted_message["content"] = message["content"].format(**variables)
            formatted_messages.append(formatted_message)
        formatted_prompt.messages = formatted_messages
        formatted_prompt.kwargs = {"model": self.modelName}
        return formatted_prompt


class Prompt(PromptVersion):
    """A prompt template that can be saved and versioned"""

    name: str = Field(description="The name of the prompt")
    description: Optional[str] = Field(
        default=None, description="The description of the saved prompt"
    )
    tags: Optional[List[str]] = Field(
        default=None, description="Tags associated with the prompt"
    )
    updatedAt: datetime = Field(description="The datetime the prompt was last updated")


class CreatePromptBaseMutationInput(GraphQLModel):
    spaceId: str = Field(
        description="The ID of the space to create the prompt version in"
    )
    commitMessage: str = Field(description="The commit message for the prompt version")
    messages: List[LLMMessageInput] = Field(
        description="The messages for the prompt version"
    )
    inputVariableFormat: PromptVersionInputVariableFormatEnum = Field(
        default=PromptVersionInputVariableFormatEnum.F_STRING,
        description="The input variable format for determining prompt variables in the messages",
    )
    provider: LLMIntegrationProvider = Field(default=LLMIntegrationProvider.openAI)
    model: Optional[str] = Field(default=None)
    invocationParams: InvocationParamsInput = Field(
        default_factory=lambda: InvocationParamsInput()
    )
    providerParams: ProviderParamsInput = Field(
        default_factory=lambda: ProviderParamsInput()
    )


class CreatePromptVersionMutationInput(CreatePromptBaseMutationInput):
    promptId: str = Field(description="The ID of the prompt to create the version for")


class CreatePromptMutationInput(CreatePromptBaseMutationInput):
    name: str = Field(description="The name of the prompt")
    description: Optional[str] = Field(
        default=None, description="The description of the prompt"
    )
    tags: Optional[List[str]] = Field(
        default=None, description="Tags associated with the prompt"
    )
