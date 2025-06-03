from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import Field, model_validator

from arize_toolkit.types import (
    BlobStore,
    ComparisonOperator,
    DataQualityMetric,
    DimensionCategory,
    DimensionDataType,
    DriftMetric,
    ExternalLLMProviderModel,
    FilterRowType,
    LLMIntegrationProvider,
    ModelEnvironment,
    ModelType,
    MonitorCategory,
    PerformanceMetric,
    PromptVersionInputVariableFormatEnum,
    TableStore,
)
from arize_toolkit.utils import FormattedPrompt, GraphQLModel

## Common GraphQL Models ##


class User(GraphQLModel):
    id: str = Field(description="The ID of the user")
    name: Optional[str] = Field(default=None, description="The name of the user")
    email: Optional[str] = Field(default=None, description="The email of the user")


class Dimension(GraphQLModel):
    id: Optional[str] = Field(default=None)
    name: str
    dataType: Optional[DimensionDataType] = Field(default=None)
    category: Optional[DimensionCategory] = Field(default=None)


## Space GraphQL Models ##


class Space(GraphQLModel):
    id: str
    name: str


## Model GraphQL Models ##


class Model(GraphQLModel):
    id: str
    name: str
    modelType: ModelType
    createdAt: datetime
    isDemoModel: bool


## Custom Metric GraphQL Models ##


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


## Monitor GraphQL Models ##


class IntegrationKey(GraphQLModel):
    id: Optional[str] = Field(default=None)
    name: str
    providerName: Literal["slack", "pagerduty", "opsgenie"]
    createdAt: Optional[datetime] = Field(default=None)
    channelName: Optional[str] = Field(default=None)
    alertSeverity: Optional[str] = Field(default=None)


class MonitorContact(GraphQLModel):
    id: Optional[str] = Field(default=None)
    notificationChannelType: Literal["email", "integration"]
    emailAddress: Optional[str] = Field(default=None)
    integration: Optional[IntegrationKey] = Field(default=None)


class MonitorContactInput(GraphQLModel):
    notificationChannelType: Literal["email", "integration"]
    emailAddress: Optional[str] = Field(default=None)
    integrationKeyId: Optional[str] = Field(default=None)


class DimensionValue(GraphQLModel):
    id: Optional[str] = Field(default=None)
    value: str


class MetricFilterItem(GraphQLModel):
    id: Optional[str] = Field(default=None)
    filterType: Optional[FilterRowType] = Field(default=None)
    operator: Optional[ComparisonOperator] = Field(default=None)
    dimension: Optional[Dimension] = Field(default=None)
    dimensionValues: Optional[List[DimensionValue]] = Field(default=None)
    binaryValues: Optional[List[str]] = Field(default=None)
    numericValues: Optional[List[str]] = Field(default=None)
    categoricalValues: Optional[List[str]] = Field(default=None)


class MetricWindow(GraphQLModel):
    id: Optional[str] = Field(default=None)
    type: Optional[Literal["moving", "fixed"]] = Field(default="moving")
    windowLengthMs: Optional[float] = Field(default=86400000)
    dimensionCategory: Optional[DimensionCategory] = Field(default=None)
    dimension: Optional[Dimension] = Field(default=None)
    filters: Optional[List[MetricFilterItem]] = Field(default_factory=list)


class DimensionFilterInput(GraphQLModel):
    dimensionType: FilterRowType
    operator: ComparisonOperator = Field(default=ComparisonOperator.equals)
    name: Optional[str] = Field(default=None)
    values: List[str] = Field(default=[])

    @model_validator(mode="after")
    def verify_values(self):
        if self.dimensionType == FilterRowType.featureLabel or self.dimensionType == FilterRowType.tagLabel:
            if self.name is None:
                raise ValueError("Name is required for feature label or tag label filter type")
        return self


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
    status: Optional[Literal["triggered", "cleared", "noData"]] = Field(default="noData")
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
    comparisonMetricWindow: Optional[MetricWindow] = Field(default=None)


class MonitorDetailedType(GraphQLModel):
    spaceId: str
    modelName: str
    name: str
    notes: Optional[str] = Field(default=None)
    contacts: Optional[List[MonitorContactInput]] = Field(default=None)
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
    filters: Optional[List[DimensionFilterInput]] = Field(default=None)


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


## Language Model GraphQL Models ##


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
        description=(
            "The arguments to call the function with, as generated by the model in JSON format. "
            "Note that the model does not always generate valid JSON, and may hallucinate parameters not defined by your function schema. "
            "Validate the arguments in your code before calling your function."
        )
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
    commitMessage: str = Field(description="The commit message describing the changes in this version")
    messages: List[Dict[str, Any]] = Field(description="The list of messages making up the prompt template")
    inputVariableFormat: PromptVersionInputVariableFormatEnum = Field(description="The input variable format for determining prompt variables in the messages")
    toolCalls: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="The list of tool/function calls defined for this version",
    )
    llmParameters: Dict[str, Any] = Field(description="The LLM parameters for execution with the prompt")
    provider: LLMIntegrationProvider = Field(description="The LLM provider used for execution with the prompt")
    modelName: Optional[ExternalLLMProviderModel] = Field(default=None, description="The LLM model used for execution with the prompt")
    createdAt: datetime = Field(description="The datetime the version was created")
    createdBy: Optional[User] = Field(default=None, description="The user who created the version")

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
    description: Optional[str] = Field(default=None, description="The description of the saved prompt")
    tags: Optional[List[str]] = Field(default=None, description="Tags associated with the prompt")
    updatedAt: datetime = Field(description="The datetime the prompt was last updated")


class CreatePromptBaseMutationInput(GraphQLModel):
    spaceId: str = Field(description="The ID of the space to create the prompt version in")
    commitMessage: str = Field(description="The commit message for the prompt version")
    messages: List[LLMMessageInput] = Field(description="The messages for the prompt version")
    inputVariableFormat: PromptVersionInputVariableFormatEnum = Field(
        default=PromptVersionInputVariableFormatEnum.F_STRING,
        description="The input variable format for determining prompt variables in the messages",
    )
    provider: LLMIntegrationProvider = Field(default=LLMIntegrationProvider.openAI)
    model: Optional[str] = Field(default=None)
    invocationParams: InvocationParamsInput = Field(default_factory=lambda: InvocationParamsInput())
    providerParams: ProviderParamsInput = Field(default_factory=lambda: ProviderParamsInput())


class CreatePromptVersionMutationInput(CreatePromptBaseMutationInput):
    promptId: str = Field(description="The ID of the prompt to create the version for")


class CreatePromptMutationInput(CreatePromptBaseMutationInput):
    name: str = Field(description="The name of the prompt")
    description: Optional[str] = Field(default=None, description="The description of the prompt")
    tags: Optional[List[str]] = Field(default=None, description="Tags associated with the prompt")


## File Import GraphQL Models ##


class EmbeddingFeatureInput(GraphQLModel):
    """Input model for embedding features in file import."""

    featureName: str = Field(description="The embedding feature name")
    vectorCol: str = Field(description="The name of the vector column")
    rawDataCol: str = Field(description="The name of the raw data column for text")
    linkToDataCol: str = Field(description="The name of the link to data column for images")


class AzureStorageIdentifierInput(GraphQLModel):
    """Input model for Azure storage identifier in file import."""

    tenantId: str = Field(description="The tenant ID of the storage account")
    storageAccountName: str = Field(description="The name of the storage account")


class ObjectDetectionInput(GraphQLModel):
    """Input model for object detection file import."""

    boundingBoxesCoordinatesColumnName: str = Field(description="Column name for bounding box coordinates")
    boundingBoxesCategoriesColumnName: str = Field(description="Column name for bounding box categories")
    boundingBoxesScoresColumnName: Optional[str] = Field(default=None, description="Column name for bounding box scores")


class BaseModelSchema(GraphQLModel):
    """Base model schema."""

    predictionId: Optional[str] = Field(default=None, description="Column name for prediction ID")
    timestamp: Optional[str] = Field(default=None, description="Column name for timestamp")

    tags: Optional[str] = Field(default=None, description="Prefix for tag column names")
    tagsList: Optional[List[str]] = Field(default=None, description="List of tag column names")

    features: Optional[str] = Field(default=None, description="Prefix for feature column names")

    featuresList: Optional[List[str]] = Field(default=None, description="List of feature column names")

    embeddingFeatures: Optional[Union[List[EmbeddingFeatureInput], EmbeddingFeatureInput]] = Field(default=None, description="List of embedding feature configurations")

    version: Optional[str] = Field(default=None, description="Version of the schema")

    exclude: Optional[List[str]] = Field(default=None, description="List of column names to exclude")

    batchId: Optional[str] = Field(default=None, description="Batch ID of the schema for validation data")

    shapValues: Optional[str] = Field(default=None, description="Column prefix for SHAP value columns")

    changeTimestamp: Optional[str] = Field(default=None, description="Column name for change timestamp")


class ClassificationSchemaInput(BaseModelSchema):
    """Input model for classification file import schema."""

    predictionLabel: str = Field(description="Column name for prediction label")

    predictionScores: Optional[str] = Field(default=None, description="Column name for prediction scores")

    actualLabel: Optional[str] = Field(default=None, description="Column name for actual label")


class RegressionSchemaInput(BaseModelSchema):
    """Input model for regression file import schema."""

    predictionScore: str = Field(description="Column name for prediction score")

    actualScore: Optional[str] = Field(default=None, description="Column name for actual score")


class RankSchemaInput(BaseModelSchema):
    """Input model for ranking file import schema."""

    predictionGroupId: str = Field(description="Column name for prediction group ID")

    rank: str = Field(description="Column name for rank")

    predictionScores: Optional[str] = Field(default=None, description="Column name for prediction scores")

    relevanceScore: Optional[str] = Field(default=None, description="Column name for relevance score")

    relevanceLabel: Optional[str] = Field(default=None, description="Column name for relevance label")


class MultiClassSchemaInput(BaseModelSchema):
    """Input model for multi-class file import schema."""

    predictionScores: str = Field(description="Column name for prediction scores")

    actualScores: Optional[str] = Field(default=None, description="Column name for actual scores")

    thresholdScores: Optional[str] = Field(default=None, description="Column name for threshold scores")


class ObjectDetectionSchemaInput(BaseModelSchema):
    """Input model for object detection file import schema."""

    predictionObjectDetection: ObjectDetectionInput = Field(description="Object detection prediction")
    actualObjectDetection: Optional[ObjectDetectionInput] = Field(default=None, description="Object detection actual")


class FullSchema(
    ClassificationSchemaInput,
    RegressionSchemaInput,
    RankSchemaInput,
    MultiClassSchemaInput,
    ObjectDetectionSchemaInput,
):
    """Input model for full file import schema."""

    # Override required fields from ClassificationSchemaInput
    predictionLabel: Optional[str] = Field(default=None, description="Column name for prediction label")

    # Override required fields from RegressionSchemaInput
    predictionScore: Optional[str] = Field(default=None, description="Column name for prediction score")

    # Override required fields from RankSchemaInput
    predictionGroupId: Optional[str] = Field(default=None, description="Column name for prediction group ID")
    rank: Optional[str] = Field(default=None, description="Column name for rank")

    # Override required fields from MultiClassSchemaInput
    predictionScores: Optional[str] = Field(default=None, description="Column name for prediction scores")

    # Override required fields from ObjectDetectionSchemaInput
    predictionObjectDetection: Optional[ObjectDetectionInput] = Field(default=None, description="Object detection prediction")


class FileImportJobInput(GraphQLModel):
    """Input model for creating a file import job."""

    blobStore: BlobStore = Field(description="Type of blob store (s3, gcs, or azure)")
    prefix: str = Field(description="Prefix path in the bucket")
    azureStorageIdentifier: Optional[AzureStorageIdentifierInput] = Field(default=None, description="Azure storage identifier")
    bucketName: str = Field(description="Name of the bucket")
    spaceId: str = Field(description="ID of the space")
    modelName: str = Field(description="Name of the model")
    modelVersion: Optional[str] = Field(default=None, description="Version of the model")
    batchId: Optional[str] = Field(default=None, description="Batch ID of the schema")

    modelType: ModelType = Field(description="Type of the model")
    modelEnvironmentName: ModelEnvironment = Field(description="Environment of the model")
    modelSchema: FullSchema = Field(
        alias="schema",
        alias_priority=1,
        description="Schema configuration for the import",
    )
    dryRun: Optional[bool] = Field(default=False, description="Whether to run the import as a dry run")


class FileImportJobCheck(GraphQLModel):
    """Model representing a file import status check."""

    id: str = Field(description="The import job's unique identifier")
    jobId: str = Field(description="The import job's unique identifier")
    jobStatus: Union[Literal["active", "inactive", "deleted"], None] = Field(description="The status of the import job")
    totalFilesPendingCount: int = Field(description="Number of files pending import")
    totalFilesSuccessCount: int = Field(description="Number of files successfully imported")
    totalFilesFailedCount: int = Field(description="Number of files that failed to import")


class FileImportJob(FileImportJobCheck):
    """Model representing a file import job."""

    jobId: str = Field(description="The import job's unique identifier")
    createdAt: datetime = Field(description="The time the import job was created")
    modelName: str = Field(description="The name of the model")
    modelId: str = Field(description="The ID of the model")
    modelVersion: Optional[str] = Field(default=None, description="The version of the model")
    modelType: ModelType = Field(description="The type of the model")
    modelEnvironmentName: ModelEnvironment = Field(description="The environment of the model")
    modelSchema: FullSchema = Field(
        alias="schema",
        alias_priority=1,
        description="Schema configuration for the import",
    )
    batchId: Optional[str] = Field(default=None, description="Batch ID of the schema")
    blobStore: BlobStore = Field(description="Type of blob store (s3, gcs, or azure)")
    bucketName: str = Field(description="Name of the bucket")
    prefix: str = Field(description="Prefix path in the bucket")


class BigQueryTableConfig(GraphQLModel):
    """Input model for BigQuery table configuration."""

    projectId: str = Field(description="Project ID of the BigQuery table")
    dataset: str = Field(description="Dataset of the BigQuery table")
    tableName: str = Field(description="Table name of the BigQuery table")


class SnowflakeTableConfig(GraphQLModel):
    """Input model for Snowflake table configuration."""

    accountID: str = Field(description="Database of the Snowflake table")
    snowflakeSchema: str = Field(
        alias="schema",
        alias_priority=1,
        description="Schema of the Snowflake table",
    )
    database: str = Field(description="Database of the Snowflake table")
    tableName: str = Field(description="Table name of the Snowflake table")


class DatabricksTableConfig(GraphQLModel):
    """Input model for Databricks table configuration."""

    hostName: str = Field(description="Host name of the Databricks table")
    endpoint: str = Field(description="Endpoint of the Databricks table")
    port: str = Field(description="Port of the Databricks table")
    token: Optional[str] = Field(default=None, description="Token of the Databricks table")
    azureResourceId: Optional[str] = Field(default=None, description="Azure resource ID of the Databricks table")
    azureTenantId: Optional[str] = Field(default=None, description="Azure tenant ID of the Databricks table")
    catalog: str = Field(description="Catalog of the Databricks table")
    databricksSchema: str = Field(description="Databricks schema of the table")
    tableName: str = Field(description="Table name of the Databricks table")


class TableIngestionParameters(GraphQLModel):
    """Input model for table ingestion parameters."""

    refreshIntervalSeconds: int = Field(description="Refresh interval in seconds")
    queryWindowSizeSeconds: int = Field(description="Query window size in seconds")


class TableImportJobInput(GraphQLModel):
    """Input model for creating a table import job."""

    tableStore: TableStore = Field(description="Type of table store (bigquery, snowflake, or databricks)")
    bigQueryTableConfig: Optional[BigQueryTableConfig] = Field(default=None, description="BigQuery table configuration")
    snowflakeTableConfig: Optional[SnowflakeTableConfig] = Field(default=None, description="Snowflake table configuration")
    databricksTableConfig: Optional[DatabricksTableConfig] = Field(default=None, description="Databricks table configuration")
    batchId: Optional[str] = Field(default=None, description="Batch ID of the schema")
    spaceId: str = Field(description="ID of the space")
    modelName: str = Field(description="Name of the model")
    modelVersion: Optional[str] = Field(default=None, description="Version of the model")
    modelType: ModelType = Field(description="Type of the model")
    modelEnvironmentName: ModelEnvironment = Field(description="Environment of the model")
    modelSchema: FullSchema = Field(
        alias="schema",
        alias_priority=1,
        description="Schema configuration for the import",
    )
    dryRun: Optional[bool] = Field(default=False, description="Whether to run the import as a dry run")

    @model_validator(mode="after")
    def validate_table_config(self) -> "TableImportJobInput":
        """Validate that the appropriate table config is provided based on tableStore."""
        if self.tableStore == TableStore.BigQuery and not self.bigQueryTableConfig:
            raise ValueError("bigQueryTableConfig is required for BigQuery table store")
        if self.tableStore == TableStore.Snowflake and not self.snowflakeTableConfig:
            raise ValueError("snowflakeTableConfig is required for Snowflake table store")
        if self.tableStore == TableStore.Databricks and not self.databricksTableConfig:
            raise ValueError("databricksTableConfig is required for Databricks table store")
        return self


class TableImportJob(GraphQLModel):
    id: str = Field(description="The import job's unique identifier")
    jobStatus: Union[Literal["active", "inactive", "deleted"], None] = Field(description="The status of the import job")
    jobId: str = Field(description="The import job's unique identifier")
    createdAt: datetime = Field(description="The time the import job was created")
    modelName: str = Field(description="The name of the model")
    modelId: str = Field(description="The ID of the model")
    modelVersion: Optional[str] = Field(default=None, description="The version of the model")
    modelType: ModelType = Field(description="The type of the model")
    modelEnvironmentName: ModelEnvironment = Field(description="The environment of the model")
    modelSchema: FullSchema = Field(
        alias="schema",
        alias_priority=1,
        description="Schema configuration for the import",
    )
    batchId: Optional[str] = Field(default=None, description="Batch ID for validation data")
    table: str = Field(description="The name of the table")
    tableStore: TableStore = Field(description="The type of table store")
    projectId: str = Field(description="Project ID of the table")
    dataset: str = Field(description="Dataset of the table")
    totalQueriesSuccessCount: int = Field(description="Number of queries successfully executed")
    totalQueriesFailedCount: int = Field(description="Number of queries failed to execute")
    totalQueriesPendingCount: int = Field(description="Number of queries pending execution")
    tableIngestionParameters: Optional[TableIngestionParameters] = Field(default=None, description="Table ingestion parameters")


class TableImportJobCheck(GraphQLModel):
    """Model representing a table import job status check."""

    id: str = Field(description="The import job's unique identifier")
    jobId: str = Field(description="The import job's unique identifier")
    jobStatus: Union[Literal["active", "inactive", "deleted"], None] = Field(description="The status of the import job")
    totalQueriesSuccessCount: int = Field(description="Number of queries successfully executed")
    totalQueriesFailedCount: int = Field(description="Number of queries failed to execute")
    totalQueriesPendingCount: int = Field(description="Number of queries pending execution")
