from datetime import datetime, timezone

import pytest

from arize_toolkit.models import (
    AnnotationInput,
    CreatePromptBaseMutationInput,
    CreatePromptMutationInput,
    CreatePromptVersionMutationInput,
    Dimension,
    DimensionFilterInput,
    DimensionValue,
    FunctionDetailsInput,
    LLMMessageInput,
    MetricFilterItem,
    MetricWindow,
    Prompt,
    PromptVersion,
    ToolInput,
    User,
)
from arize_toolkit.types import ExternalLLMProviderModel, LLMIntegrationProvider, PromptVersionInputVariableFormatEnum
from arize_toolkit.utils import FormattedPrompt


class TestPromptVersion:
    def test_init(self):
        """Test that PromptVersion can be initialized with valid parameters"""
        prompt_version = PromptVersion(
            id="12345",
            commitMessage="Initial version",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Tell me about {topic}"},
            ],
            inputVariableFormat=PromptVersionInputVariableFormatEnum.F_STRING,
            toolChoice=None,
            toolCalls=None,
            llmParameters={"temperature": 0.7},
            provider=LLMIntegrationProvider.openAI,
            modelName=ExternalLLMProviderModel.GPT_4o_MINI,
            createdAt=datetime(2023, 1, 1, tzinfo=timezone.utc),
            createdBy=User(id="user123", name="Test User", email="test@example.com"),
        )

        assert prompt_version.id == "12345"
        assert prompt_version.commitMessage == "Initial version"
        assert prompt_version.messages[0]["role"] == "system"
        assert prompt_version.messages[1]["content"] == "Tell me about {topic}"
        assert prompt_version.inputVariableFormat == PromptVersionInputVariableFormatEnum.F_STRING
        assert prompt_version.llmParameters == {"temperature": 0.7}
        assert prompt_version.provider == LLMIntegrationProvider.openAI
        assert prompt_version.modelName == ExternalLLMProviderModel.GPT_4o_MINI
        assert prompt_version.createdAt == datetime(2023, 1, 1, tzinfo=timezone.utc)
        assert prompt_version.createdBy.name == "Test User"

    def test_format_method(self):
        """Test that the format method correctly formats messages with variables"""
        prompt_version = PromptVersion(
            id="12345",
            commitMessage="Initial version",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Tell me about {topic} in {format}"},
            ],
            inputVariableFormat=PromptVersionInputVariableFormatEnum.F_STRING,
            toolChoice=None,
            toolCalls=None,
            llmParameters={"temperature": 0.7},
            provider=LLMIntegrationProvider.openAI,
            modelName=ExternalLLMProviderModel.GPT_4o_MINI,
            createdAt=datetime(2023, 1, 1, tzinfo=timezone.utc),
        )

        formatted_prompt = prompt_version.format(topic="machine learning", format="simple terms")

        assert isinstance(formatted_prompt, FormattedPrompt)
        assert formatted_prompt.messages[0]["role"] == "system"
        assert formatted_prompt.messages[0]["content"] == "You are a helpful assistant."
        assert formatted_prompt.messages[1]["role"] == "user"
        assert formatted_prompt.messages[1]["content"] == "Tell me about machine learning in simple terms"
        assert formatted_prompt.kwargs == {"model": ExternalLLMProviderModel.GPT_4o_MINI}


class TestPrompt:
    def test_init(self):
        """Test that Prompt can be initialized with valid parameters"""
        prompt = Prompt(
            id="12345",
            name="ML Explainer",
            description="A prompt that explains ML concepts",
            tags=["education", "machine-learning"],
            commitMessage="Initial version",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Tell me about {topic}"},
            ],
            inputVariableFormat=PromptVersionInputVariableFormatEnum.F_STRING,
            toolChoice=None,
            toolCalls=None,
            llmParameters={"temperature": 0.7},
            provider=LLMIntegrationProvider.openAI,
            modelName=ExternalLLMProviderModel.GPT_4o_MINI,
            createdAt=datetime(2023, 1, 1, tzinfo=timezone.utc),
            updatedAt=datetime(2023, 1, 2, tzinfo=timezone.utc),
            createdBy=User(id="user123", name="Test User", email="test@example.com"),
        )

        assert prompt.id == "12345"
        assert prompt.name == "ML Explainer"
        assert prompt.description == "A prompt that explains ML concepts"
        assert "education" in prompt.tags
        assert "machine-learning" in prompt.tags
        assert prompt.commitMessage == "Initial version"
        assert prompt.messages[0]["role"] == "system"
        assert prompt.messages[1]["content"] == "Tell me about {topic}"
        assert prompt.inputVariableFormat == PromptVersionInputVariableFormatEnum.F_STRING
        assert prompt.llmParameters == {"temperature": 0.7}
        assert prompt.provider == LLMIntegrationProvider.openAI
        assert prompt.modelName == ExternalLLMProviderModel.GPT_4o_MINI
        assert prompt.createdAt == datetime(2023, 1, 1, tzinfo=timezone.utc)
        assert prompt.updatedAt == datetime(2023, 1, 2, tzinfo=timezone.utc)
        assert prompt.createdBy.name == "Test User"

    def test_format_method_inheritance(self):
        """Test that Prompt inherits format method from PromptVersion correctly"""
        prompt = Prompt(
            id="12345",
            name="ML Explainer",
            description="A prompt that explains ML concepts",
            tags=["education", "machine-learning"],
            commitMessage="Initial version",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Tell me about {topic} in {format}"},
            ],
            inputVariableFormat=PromptVersionInputVariableFormatEnum.F_STRING,
            toolChoice=None,
            toolCalls=None,
            llmParameters={"temperature": 0.7},
            provider=LLMIntegrationProvider.openAI,
            modelName=ExternalLLMProviderModel.GPT_4o_MINI,
            createdAt=datetime(2023, 1, 1, tzinfo=timezone.utc),
            updatedAt=datetime(2023, 1, 2, tzinfo=timezone.utc),
        )

        formatted_prompt = prompt.format(topic="machine learning", format="simple terms")

        assert isinstance(formatted_prompt, FormattedPrompt)
        assert formatted_prompt.messages[0]["role"] == "system"
        assert formatted_prompt.messages[0]["content"] == "You are a helpful assistant."
        assert formatted_prompt.messages[1]["role"] == "user"
        assert formatted_prompt.messages[1]["content"] == "Tell me about machine learning in simple terms"


class TestFormattedPrompt:
    def test_mapping_interface(self):
        """Test that FormattedPrompt implements the Mapping interface"""
        formatted_prompt = FormattedPrompt()
        formatted_prompt.messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Tell me about machine learning"},
        ]
        formatted_prompt.kwargs = {"model": "gpt-4", "temperature": 0.7}

        # Test len
        assert len(formatted_prompt) == 3  # messages + 2 kwargs

        # Test getitem
        assert formatted_prompt["messages"] == formatted_prompt.messages
        assert formatted_prompt["model"] == "gpt-4"
        assert formatted_prompt["temperature"] == 0.7

        # Test iteration
        keys = list(formatted_prompt)
        assert "messages" in keys
        assert "model" in keys
        assert "temperature" in keys

        # Test unpacking for LLM provider use
        kwargs = {key: formatted_prompt[key] for key in formatted_prompt if key != "messages"}
        assert kwargs == {"model": "gpt-4", "temperature": 0.7}


class TestToolModels:
    def test_function_details_input(self):
        """Test FunctionDetailsInput model"""
        function = FunctionDetailsInput(
            name="get_weather",
            description="Get weather for a location",
            arguments='{"location": "San Francisco", "unit": "celsius"}',
            parameters={"location": "San Francisco", "unit": "celsius"},
        )

        assert function.name == "get_weather"
        assert function.description == "Get weather for a location"
        assert function.arguments == '{"location": "San Francisco", "unit": "celsius"}'
        assert function.parameters == {"location": "San Francisco", "unit": "celsius"}

    def test_tool_input(self):
        """Test ToolInput model"""
        tool = ToolInput(
            id="tool123",
            type="function",
            function=FunctionDetailsInput(
                name="get_weather",
                description="Get weather for a location",
                arguments='{"location": "San Francisco"}',
            ),
        )

        assert tool.id == "tool123"
        assert tool.type == "function"
        assert tool.function.name == "get_weather"
        assert tool.function.description == "Get weather for a location"

    def test_llm_message_input(self):
        """Test LLMMessageInput model with tool calls"""
        message = LLMMessageInput(
            role="assistant",
            content="I'll help you get the weather.",
            toolCalls=[
                ToolInput(
                    id="call123",
                    type="function",
                    function=FunctionDetailsInput(
                        name="get_weather",
                        arguments='{"location": "San Francisco"}',
                    ),
                )
            ],
        )

        assert message.role == "assistant"
        assert message.content == "I'll help you get the weather."
        assert len(message.toolCalls) == 1
        assert message.toolCalls[0].id == "call123"
        assert message.toolCalls[0].function.name == "get_weather"


class TestCreatePromptMutationInputs:
    def test_create_prompt_base_mutation_input(self):
        """Test CreatePromptBaseMutationInput model"""
        input_data = CreatePromptBaseMutationInput(
            spaceId="space123",
            commitMessage="Initial version",
            messages=[
                LLMMessageInput(role="system", content="You are a helpful assistant."),
                LLMMessageInput(role="user", content="Tell me about {topic}"),
            ],
            inputVariableFormat=PromptVersionInputVariableFormatEnum.F_STRING,
            provider=LLMIntegrationProvider.openAI,
            model="gpt-4",
        )

        assert input_data.spaceId == "space123"
        assert input_data.commitMessage == "Initial version"
        assert len(input_data.messages) == 2
        assert input_data.messages[0].role == "system"
        assert input_data.messages[1].content == "Tell me about {topic}"
        assert input_data.provider == LLMIntegrationProvider.openAI
        assert input_data.model == "gpt-4"

    def test_create_prompt_version_mutation_input(self):
        """Test CreatePromptVersionMutationInput model"""
        input_data = CreatePromptVersionMutationInput(
            spaceId="space123",
            promptId="prompt123",
            commitMessage="Updated version",
            messages=[
                LLMMessageInput(role="system", content="You are a helpful assistant."),
                LLMMessageInput(role="user", content="Tell me about {topic}"),
            ],
            inputVariableFormat=PromptVersionInputVariableFormatEnum.F_STRING,
            provider=LLMIntegrationProvider.openAI,
        )

        assert input_data.spaceId == "space123"
        assert input_data.promptId == "prompt123"
        assert input_data.commitMessage == "Updated version"
        assert len(input_data.messages) == 2

    def test_create_prompt_mutation_input(self):
        """Test CreatePromptMutationInput model"""
        input_data = CreatePromptMutationInput(
            spaceId="space123",
            name="ML Explainer",
            description="A prompt that explains ML concepts",
            tags=["education", "machine-learning"],
            commitMessage="Initial version",
            messages=[
                LLMMessageInput(role="system", content="You are a helpful assistant."),
                LLMMessageInput(role="user", content="Tell me about {topic}"),
            ],
            inputVariableFormat=PromptVersionInputVariableFormatEnum.F_STRING,
            provider=LLMIntegrationProvider.openAI,
        )

        assert input_data.spaceId == "space123"
        assert input_data.name == "ML Explainer"
        assert input_data.description == "A prompt that explains ML concepts"
        assert "education" in input_data.tags
        assert "machine-learning" in input_data.tags
        assert input_data.commitMessage == "Initial version"
        assert len(input_data.messages) == 2


class TestUser:
    def test_init(self):
        """Test that User can be initialized with valid parameters."""
        user = User(id="user123", name="Test User", email="test@example.com")

        assert user.id == "user123"
        assert user.name == "Test User"
        assert user.email == "test@example.com"

    def test_optional_fields(self):
        """Test that optional fields have correct defaults."""
        user = User(id="user123")

        assert user.id == "user123"
        assert user.name is None
        assert user.email is None


class TestDimension:
    def test_init(self):
        """Test that Dimension can be initialized with valid parameters."""
        from arize_toolkit.types import DimensionCategory, DimensionDataType

        dimension = Dimension(
            id="dim123",
            name="user_age",
            dataType=DimensionDataType.LONG,
            category=DimensionCategory.prediction,
        )

        assert dimension.id == "dim123"
        assert dimension.name == "user_age"
        assert dimension.dataType == DimensionDataType.LONG
        assert dimension.category == DimensionCategory.prediction

    def test_required_fields(self):
        """Test that required fields must be provided."""
        dimension = Dimension(name="test_dimension")

        assert dimension.name == "test_dimension"
        assert dimension.id is None
        assert dimension.dataType is None
        assert dimension.category is None


class TestAnnotationInput:
    def test_label_annotation(self):
        """Test label annotation type validation."""
        # Valid label annotation
        annotation = AnnotationInput(
            name="sentiment",
            updatedBy="user123",
            label="positive",
            annotationType="label",
        )

        assert annotation.name == "sentiment"
        assert annotation.label == "positive"
        assert annotation.annotationType == "label"

    def test_score_annotation(self):
        """Test score annotation type validation."""
        # Valid score annotation
        annotation = AnnotationInput(name="quality", updatedBy="user123", score=0.95, annotationType="score")

        assert annotation.name == "quality"
        assert annotation.score == 0.95
        assert annotation.annotationType == "score"

    def test_validation_label_missing(self):
        """Test that label is required for label annotation type."""
        with pytest.raises(ValueError, match="Label is required for label annotation type"):
            AnnotationInput(
                name="sentiment",
                updatedBy="user123",
                annotationType="label",
                # Missing label
            )

    def test_validation_score_missing(self):
        """Test that score is required for score annotation type."""
        with pytest.raises(ValueError, match="Score is required for score annotation type"):
            AnnotationInput(
                name="quality",
                updatedBy="user123",
                annotationType="score",
                # Missing score
            )


class TestFileImportModels:
    def test_embedding_feature_input(self):
        """Test EmbeddingFeatureInput model."""
        from arize_toolkit.models import EmbeddingFeatureInput

        embedding = EmbeddingFeatureInput(
            featureName="text_embedding",
            vectorCol="embedding_vector",
            rawDataCol="text_content",
            linkToDataCol="image_url",
        )

        assert embedding.featureName == "text_embedding"
        assert embedding.vectorCol == "embedding_vector"
        assert embedding.rawDataCol == "text_content"
        assert embedding.linkToDataCol == "image_url"

    def test_classification_schema_input(self):
        """Test ClassificationSchemaInput model."""
        from arize_toolkit.models import ClassificationSchemaInput, EmbeddingFeatureInput

        schema = ClassificationSchemaInput(
            predictionLabel="prediction",
            actualLabel="actual",
            predictionScores="pred_scores",
            predictionId="id",
            timestamp="ts",
            featuresList=["feature1", "feature2"],
            embeddingFeatures=[
                EmbeddingFeatureInput(
                    featureName="embedding",
                    vectorCol="vector",
                    rawDataCol="text",
                    linkToDataCol="url",
                )
            ],
        )

        assert schema.predictionLabel == "prediction"
        assert schema.actualLabel == "actual"
        assert schema.predictionScores == "pred_scores"
        assert schema.predictionId == "id"
        assert schema.timestamp == "ts"
        assert schema.featuresList == ["feature1", "feature2"]
        assert len(schema.embeddingFeatures) == 1

    def test_file_import_job_input(self):
        """Test FileImportJobInput model."""
        from arize_toolkit.models import FileImportJobInput, FullSchema
        from arize_toolkit.types import BlobStore, ModelEnvironment, ModelType

        job_input = FileImportJobInput(
            blobStore=BlobStore.S3,
            prefix="data/",
            bucketName="my-bucket",
            spaceId="space123",
            modelName="my-model",
            modelType=ModelType.score_categorical,
            modelEnvironmentName=ModelEnvironment.production,
            modelSchema=FullSchema(predictionLabel="prediction", actualLabel="actual"),
        )

        assert job_input.blobStore == BlobStore.S3
        assert job_input.prefix == "data/"
        assert job_input.bucketName == "my-bucket"
        assert job_input.spaceId == "space123"
        assert job_input.modelName == "my-model"
        assert job_input.modelType == ModelType.score_categorical
        assert job_input.modelEnvironmentName == ModelEnvironment.production
        assert job_input.modelSchema.predictionLabel == "prediction"
        assert job_input.dryRun is False  # Default value

    def test_file_import_job_input_serialization(self):
        """Test FileImportJobInput serialization with alias."""
        from arize_toolkit.models import FileImportJobInput, FullSchema
        from arize_toolkit.types import BlobStore, ModelEnvironment, ModelType

        job_input = FileImportJobInput(
            blobStore=BlobStore.S3,
            prefix="data/",
            bucketName="my-bucket",
            spaceId="space123",
            modelName="my-model",
            modelType=ModelType.score_categorical,
            modelEnvironmentName=ModelEnvironment.production,
            modelSchema=FullSchema(predictionLabel="prediction"),
        )

        data = job_input.model_dump(by_alias=True)
        assert "schema" in data  # Check alias is used
        assert "modelSchema" not in data


class TestTableImportModels:
    def test_bigquery_table_config(self):
        """Test BigQueryTableConfig model."""
        from arize_toolkit.models import BigQueryTableConfig

        config = BigQueryTableConfig(projectId="my-project", dataset="my-dataset", tableName="my-table")

        assert config.projectId == "my-project"
        assert config.dataset == "my-dataset"
        assert config.tableName == "my-table"

    def test_snowflake_table_config(self):
        """Test SnowflakeTableConfig model with alias."""
        from arize_toolkit.models import SnowflakeTableConfig

        config = SnowflakeTableConfig(
            accountID="my-account",
            snowflakeSchema="my-schema",
            database="my-database",
            tableName="my-table",
        )

        assert config.accountID == "my-account"
        assert config.snowflakeSchema == "my-schema"
        assert config.database == "my-database"
        assert config.tableName == "my-table"

        # Test serialization with alias
        data = config.model_dump(by_alias=True)
        assert "schema" in data
        assert data["schema"] == "my-schema"
        assert "snowflakeSchema" not in data

    def test_table_import_job_input_validation(self):
        """Test TableImportJobInput validation."""
        from arize_toolkit.models import BigQueryTableConfig, FullSchema, TableImportJobInput
        from arize_toolkit.types import ModelEnvironment, ModelType, TableStore

        # Valid case with BigQuery
        job_input = TableImportJobInput(
            tableStore=TableStore.BigQuery,
            bigQueryTableConfig=BigQueryTableConfig(projectId="project", dataset="dataset", tableName="table"),
            spaceId="space123",
            modelName="model",
            modelType=ModelType.score_categorical,
            modelEnvironmentName=ModelEnvironment.production,
            modelSchema=FullSchema(predictionLabel="pred"),
        )

        assert job_input.tableStore == TableStore.BigQuery
        assert job_input.bigQueryTableConfig.projectId == "project"

    def test_table_import_job_input_validation_error(self):
        """Test TableImportJobInput validation error."""
        from arize_toolkit.models import FullSchema, TableImportJobInput
        from arize_toolkit.types import ModelEnvironment, ModelType, TableStore

        # Invalid case - missing required config
        with pytest.raises(ValueError, match="bigQueryTableConfig is required for BigQuery table store"):
            TableImportJobInput(
                tableStore=TableStore.BigQuery,
                # Missing bigQueryTableConfig
                spaceId="space123",
                modelName="model",
                modelType=ModelType.score_categorical,
                modelEnvironmentName=ModelEnvironment.production,
                modelSchema=FullSchema(predictionLabel="pred"),
            )


class TestMonitorModels:
    def test_monitor_contact_input(self):
        """Test MonitorContactInput model."""
        from arize_toolkit.models import MonitorContactInput

        # Email contact
        email_contact = MonitorContactInput(notificationChannelType="email", emailAddress="user@example.com")

        assert email_contact.notificationChannelType == "email"
        assert email_contact.emailAddress == "user@example.com"
        assert email_contact.integrationKeyId is None

        # Integration contact
        integration_contact = MonitorContactInput(notificationChannelType="integration", integrationKeyId="key123")

        assert integration_contact.notificationChannelType == "integration"
        assert integration_contact.integrationKeyId == "key123"
        assert integration_contact.emailAddress is None

    def test_performance_monitor(self):
        """Test PerformanceMonitor model."""
        from arize_toolkit.models import PerformanceMonitor
        from arize_toolkit.types import ComparisonOperator, ModelEnvironment, PerformanceMetric

        monitor = PerformanceMonitor(
            spaceId="space123",
            modelName="my-model",
            name="Accuracy Monitor",
            performanceMetric=PerformanceMetric.accuracy,
            operator=ComparisonOperator.lessThan,
            threshold=0.9,
            modelEnvironmentName=ModelEnvironment.production,
        )

        assert monitor.spaceId == "space123"
        assert monitor.modelName == "my-model"
        assert monitor.name == "Accuracy Monitor"
        assert monitor.performanceMetric == PerformanceMetric.accuracy
        assert monitor.operator == ComparisonOperator.lessThan
        assert monitor.threshold == 0.9
        assert monitor.modelEnvironmentName == ModelEnvironment.production

        # Check defaults
        assert monitor.evaluationWindowLengthSeconds == 259200
        assert monitor.delaySeconds == 0
        assert monitor.thresholdMode == "single"


class TestCustomMetricModels:
    def test_custom_metric_input(self):
        """Test CustomMetricInput model."""
        from arize_toolkit.models import CustomMetricInput
        from arize_toolkit.types import ModelEnvironment

        metric = CustomMetricInput(
            modelId="model123",
            name="Custom F1 Score",
            description="Custom implementation of F1 score",
            metric="(2 * precision * recall) / (precision + recall)",
        )

        assert metric.modelId == "model123"
        assert metric.name == "Custom F1 Score"
        assert metric.description == "Custom implementation of F1 score"
        assert metric.metric == "(2 * precision * recall) / (precision + recall)"
        assert metric.modelEnvironmentName == ModelEnvironment.production  # Default

    def test_custom_metric_input_defaults(self):
        """Test CustomMetricInput default values."""
        from arize_toolkit.models import CustomMetricInput

        metric = CustomMetricInput(modelId="model123", name="Metric", metric="value")

        assert metric.description == "a custom metric"  # Default description


class TestSpaceAndModel:
    def test_space_init(self):
        """Test Space model initialization."""
        from arize_toolkit.models import Space

        space = Space(id="space123", name="Production Space")

        assert space.id == "space123"
        assert space.name == "Production Space"

    def test_model_init(self):
        """Test Model initialization."""
        from datetime import datetime, timezone

        from arize_toolkit.models import Model
        from arize_toolkit.types import ModelType

        created_time = datetime(2024, 1, 1, tzinfo=timezone.utc)
        model = Model(
            id="model123",
            name="Customer Churn Model",
            modelType=ModelType.score_categorical,
            createdAt=created_time,
            isDemoModel=False,
        )

        assert model.id == "model123"
        assert model.name == "Customer Churn Model"
        assert model.modelType == ModelType.score_categorical
        assert model.createdAt == created_time
        assert model.isDemoModel is False


class TestSchemaInputModels:
    def test_regression_schema_input(self):
        """Test RegressionSchemaInput model."""
        from arize_toolkit.models import RegressionSchemaInput

        schema = RegressionSchemaInput(
            predictionScore="pred_score",
            actualScore="actual_score",
            predictionId="id",
            timestamp="ts",
            featuresList=["f1", "f2"],
            version="v1.0",
        )

        assert schema.predictionScore == "pred_score"
        assert schema.actualScore == "actual_score"
        assert schema.predictionId == "id"
        assert schema.timestamp == "ts"
        assert len(schema.featuresList) == 2
        assert schema.version == "v1.0"

    def test_rank_schema_input(self):
        """Test RankSchemaInput model."""
        from arize_toolkit.models import RankSchemaInput

        schema = RankSchemaInput(
            predictionGroupId="group_id",
            rank="rank_col",
            predictionScores="scores",
            relevanceScore="relevance",
            relevanceLabel="rel_label",
        )

        assert schema.predictionGroupId == "group_id"
        assert schema.rank == "rank_col"
        assert schema.predictionScores == "scores"
        assert schema.relevanceScore == "relevance"
        assert schema.relevanceLabel == "rel_label"

    def test_multiclass_schema_input(self):
        """Test MultiClassSchemaInput model."""
        from arize_toolkit.models import MultiClassSchemaInput

        schema = MultiClassSchemaInput(
            predictionScores="pred_scores",
            actualScores="actual_scores",
            thresholdScores="thresholds",
            tags="tag_",
            tagsList=["tag_1", "tag_2"],
        )

        assert schema.predictionScores == "pred_scores"
        assert schema.actualScores == "actual_scores"
        assert schema.thresholdScores == "thresholds"
        assert schema.tags == "tag_"
        assert len(schema.tagsList) == 2

    def test_object_detection_schema_input(self):
        """Test ObjectDetectionSchemaInput model."""
        from arize_toolkit.models import ObjectDetectionInput, ObjectDetectionSchemaInput

        pred_detection = ObjectDetectionInput(
            boundingBoxesCoordinatesColumnName="pred_coords",
            boundingBoxesCategoriesColumnName="pred_categories",
            boundingBoxesScoresColumnName="pred_scores",
        )

        actual_detection = ObjectDetectionInput(
            boundingBoxesCoordinatesColumnName="actual_coords",
            boundingBoxesCategoriesColumnName="actual_categories",
        )

        schema = ObjectDetectionSchemaInput(
            predictionObjectDetection=pred_detection,
            actualObjectDetection=actual_detection,
        )

        assert schema.predictionObjectDetection.boundingBoxesCoordinatesColumnName == "pred_coords"
        assert schema.predictionObjectDetection.boundingBoxesScoresColumnName == "pred_scores"
        assert schema.actualObjectDetection.boundingBoxesScoresColumnName is None

    def test_full_schema_flexibility(self):
        """Test FullSchema model with mixed fields."""
        from arize_toolkit.models import FullSchema, ObjectDetectionInput

        # Test that FullSchema can be used with different model types
        # Classification fields
        schema1 = FullSchema(predictionLabel="pred", actualLabel="actual")
        assert schema1.predictionLabel == "pred"
        assert schema1.predictionScore is None  # Regression field

        # Regression fields
        schema2 = FullSchema(predictionScore="score", actualScore="actual_score")
        assert schema2.predictionScore == "score"
        assert schema2.predictionLabel is None  # Classification field

        # Mixed fields
        schema3 = FullSchema(
            predictionLabel="class",
            predictionScore="score",
            rank="rank_col",
            predictionObjectDetection=ObjectDetectionInput(
                boundingBoxesCoordinatesColumnName="coords",
                boundingBoxesCategoriesColumnName="categories",
            ),
        )
        assert schema3.predictionLabel == "class"
        assert schema3.predictionScore == "score"
        assert schema3.rank == "rank_col"
        assert schema3.predictionObjectDetection is not None


class TestLanguageModelInputs:
    def test_note_input(self):
        """Test NoteInput model."""
        from arize_toolkit.models import NoteInput

        note = NoteInput(text="This is a test note")
        assert note.text == "This is a test note"

    def test_tool_choice_input(self):
        """Test ToolChoiceInput model."""
        from arize_toolkit.models import FunctionDetailsInput, ToolChoiceInput, ToolInput

        # Test with choice only
        tool_choice1 = ToolChoiceInput(choice="auto")
        assert tool_choice1.choice == "auto"
        assert tool_choice1.tool is None

        # Test with tool
        tool = ToolInput(
            id="tool123",
            function=FunctionDetailsInput(name="get_weather", arguments='{"location": "SF"}'),
        )
        tool_choice2 = ToolChoiceInput(tool=tool)
        assert tool_choice2.tool.id == "tool123"
        assert tool_choice2.choice is None

    def test_tool_config_input(self):
        """Test ToolConfigInput model."""
        from arize_toolkit.models import FunctionDetailsInput, ToolChoiceInput, ToolConfigInput, ToolInput

        tools = [
            ToolInput(function=FunctionDetailsInput(name="tool1", description="First tool", arguments="{}")),
            ToolInput(function=FunctionDetailsInput(name="tool2", description="Second tool", arguments="{}")),
        ]

        tool_config = ToolConfigInput(tools=tools, toolChoice=ToolChoiceInput(choice="required"))

        assert len(tool_config.tools) == 2
        assert tool_config.tools[0].function.name == "tool1"
        assert tool_config.toolChoice.choice == "required"

    def test_invocation_params_input(self):
        """Test InvocationParamsInput model."""
        from arize_toolkit.models import InvocationParamsInput

        params = InvocationParamsInput(
            temperature=0.7,
            top_p=0.9,
            stop=["\\n", "END"],
            max_tokens=1000,
            presence_penalty=0.1,
            frequency_penalty=0.2,
            top_k=50,
        )

        assert params.temperature == 0.7
        assert params.top_p == 0.9
        assert len(params.stop) == 2
        assert params.max_tokens == 1000
        assert params.presence_penalty == 0.1
        assert params.frequency_penalty == 0.2
        assert params.top_k == 50

    def test_provider_params_input(self):
        """Test ProviderParamsInput model."""
        from arize_toolkit.models import ProviderParamsInput

        params = ProviderParamsInput(
            azureParams={"deployment": "gpt4"},
            anthropicHeaders={"x-api-key": "key123"},
            customProviderParams={"custom": "value"},
            anthropic_version="2023-06-01",
            region="us-east-1",
        )

        assert params.azureParams["deployment"] == "gpt4"
        assert params.anthropicHeaders["x-api-key"] == "key123"
        assert params.customProviderParams["custom"] == "value"
        assert params.anthropic_version == "2023-06-01"
        assert params.region == "us-east-1"

    def test_annotation_mutation_input(self):
        """Test AnnotationMutationInput model."""
        from datetime import datetime, timezone

        from arize_toolkit.models import AnnotationInput, AnnotationMutationInput, NoteInput
        from arize_toolkit.types import ModelEnvironment

        start_time = datetime(2024, 1, 1, tzinfo=timezone.utc)

        # Single annotation
        mutation1 = AnnotationMutationInput(
            modelId="model123",
            note=NoteInput(text="Test note"),
            annotations=AnnotationInput(name="quality", updatedBy="user123", score=0.9, annotationType="score"),
            recordId="record123",
            startTime=start_time,
        )

        assert mutation1.modelId == "model123"
        assert mutation1.note.text == "Test note"
        assert mutation1.recordId == "record123"
        assert mutation1.modelEnvironment == ModelEnvironment.tracing  # Default

        # Multiple annotations
        mutation2 = AnnotationMutationInput(
            modelId="model123",
            annotations=[
                AnnotationInput(
                    name="sentiment",
                    updatedBy="user1",
                    label="positive",
                    annotationType="label",
                ),
                AnnotationInput(name="quality", updatedBy="user2", score=0.8, annotationType="score"),
            ],
            recordId="record456",
            modelEnvironment=ModelEnvironment.production,
            startTime=start_time,
        )

        assert len(mutation2.annotations) == 2
        assert mutation2.modelEnvironment == ModelEnvironment.production


class TestImportJobModels:
    def test_file_import_job_check(self):
        """Test FileImportJobCheck model."""
        from arize_toolkit.models import FileImportJobCheck

        check = FileImportJobCheck(
            id="job123",
            jobId="job123",
            jobStatus="active",
            totalFilesPendingCount=10,
            totalFilesSuccessCount=5,
            totalFilesFailedCount=1,
        )

        assert check.id == "job123"
        assert check.jobId == "job123"
        assert check.jobStatus == "active"
        assert check.totalFilesPendingCount == 10
        assert check.totalFilesSuccessCount == 5
        assert check.totalFilesFailedCount == 1

    def test_file_import_job(self):
        """Test FileImportJob model."""
        from datetime import datetime, timezone

        from arize_toolkit.models import FileImportJob, FullSchema
        from arize_toolkit.types import BlobStore, ModelEnvironment, ModelType

        created_time = datetime(2024, 1, 1, tzinfo=timezone.utc)

        job = FileImportJob(
            id="job123",
            jobId="job123",
            jobStatus="active",
            totalFilesPendingCount=10,
            totalFilesSuccessCount=5,
            totalFilesFailedCount=1,
            createdAt=created_time,
            modelName="my-model",
            modelId="model123",
            modelVersion="v1.0",
            modelType=ModelType.score_categorical,
            modelEnvironmentName=ModelEnvironment.production,
            modelSchema=FullSchema(predictionLabel="pred"),
            batchId="batch123",
            blobStore=BlobStore.S3,
            bucketName="my-bucket",
            prefix="data/",
        )

        assert job.id == "job123"
        assert job.createdAt == created_time
        assert job.modelName == "my-model"
        assert job.modelVersion == "v1.0"
        assert job.batchId == "batch123"
        assert job.blobStore == BlobStore.S3
        assert job.bucketName == "my-bucket"
        assert job.prefix == "data/"

    def test_table_import_job_check(self):
        """Test TableImportJobCheck model."""
        from arize_toolkit.models import TableImportJobCheck

        check = TableImportJobCheck(
            id="job456",
            jobId="job456",
            jobStatus="inactive",
            totalQueriesSuccessCount=100,
            totalQueriesFailedCount=2,
            totalQueriesPendingCount=0,
        )

        assert check.id == "job456"
        assert check.jobStatus == "inactive"
        assert check.totalQueriesSuccessCount == 100
        assert check.totalQueriesFailedCount == 2
        assert check.totalQueriesPendingCount == 0

    def test_table_import_job(self):
        """Test TableImportJob model."""
        from datetime import datetime, timezone

        from arize_toolkit.models import FullSchema, TableImportJob, TableIngestionParameters
        from arize_toolkit.types import ModelEnvironment, ModelType, TableStore

        created_time = datetime(2024, 1, 1, tzinfo=timezone.utc)

        job = TableImportJob(
            id="job789",
            jobStatus="active",
            jobId="job789",
            createdAt=created_time,
            modelName="table-model",
            modelId="model789",
            modelType=ModelType.numeric,
            modelEnvironmentName=ModelEnvironment.validation,
            modelSchema=FullSchema(predictionScore="score"),
            table="my_table",
            tableStore=TableStore.BigQuery,
            projectId="my-project",
            dataset="my-dataset",
            totalQueriesSuccessCount=50,
            totalQueriesFailedCount=0,
            totalQueriesPendingCount=10,
            tableIngestionParameters=TableIngestionParameters(refreshIntervalSeconds=3600, queryWindowSizeSeconds=86400),
        )

        assert job.id == "job789"
        assert job.table == "my_table"
        assert job.tableStore == TableStore.BigQuery
        assert job.projectId == "my-project"
        assert job.dataset == "my-dataset"
        assert job.tableIngestionParameters.refreshIntervalSeconds == 3600
        assert job.tableIngestionParameters.queryWindowSizeSeconds == 86400

    def test_azure_storage_identifier_input(self):
        """Test AzureStorageIdentifierInput model."""
        from arize_toolkit.models import AzureStorageIdentifierInput

        azure_id = AzureStorageIdentifierInput(tenantId="tenant123", storageAccountName="mystorageaccount")

        assert azure_id.tenantId == "tenant123"
        assert azure_id.storageAccountName == "mystorageaccount"

    def test_databricks_table_config(self):
        """Test DatabricksTableConfig model."""
        from arize_toolkit.models import DatabricksTableConfig

        config = DatabricksTableConfig(
            hostName="my-databricks.cloud.databricks.com",
            endpoint="/sql/1.0/endpoints/123",
            port="443",
            token="dapi123",
            azureResourceId="resource123",
            azureTenantId="tenant456",
            catalog="my_catalog",
            databricksSchema="my_schema",
            tableName="my_table",
        )

        assert config.hostName == "my-databricks.cloud.databricks.com"
        assert config.endpoint == "/sql/1.0/endpoints/123"
        assert config.port == "443"
        assert config.token == "dapi123"
        assert config.azureResourceId == "resource123"
        assert config.azureTenantId == "tenant456"
        assert config.catalog == "my_catalog"
        assert config.databricksSchema == "my_schema"
        assert config.tableName == "my_table"


class TestMonitorDetailedModels:
    def test_custom_metric(self):
        """Test CustomMetric model."""
        from datetime import datetime, timezone

        from arize_toolkit.models import CustomMetric

        created_time = datetime(2024, 1, 1, tzinfo=timezone.utc)

        metric = CustomMetric(
            id="metric123",
            name="Custom F1",
            createdAt=created_time,
            description="Custom F1 score implementation",
            metric="(2 * precision * recall) / (precision + recall)",
            requiresPositiveClass=True,
        )

        assert metric.id == "metric123"
        assert metric.name == "Custom F1"
        assert metric.createdAt == created_time
        assert metric.description == "Custom F1 score implementation"
        assert metric.requiresPositiveClass is True

    def test_integration_key(self):
        """Test IntegrationKey model."""
        from datetime import datetime, timezone

        from arize_toolkit.models import IntegrationKey

        created_time = datetime(2024, 1, 1, tzinfo=timezone.utc)

        key = IntegrationKey(
            id="key123",
            name="Slack Integration",
            providerName="slack",
            createdAt=created_time,
            channelName="#alerts",
            alertSeverity="high",
        )

        assert key.id == "key123"
        assert key.name == "Slack Integration"
        assert key.providerName == "slack"
        assert key.channelName == "#alerts"
        assert key.alertSeverity == "high"

    def test_monitor_contact(self):
        """Test MonitorContact model."""
        from arize_toolkit.models import IntegrationKey, MonitorContact

        # Email contact
        email_contact = MonitorContact(
            id="contact1",
            notificationChannelType="email",
            emailAddress="user@example.com",
        )

        assert email_contact.notificationChannelType == "email"
        assert email_contact.emailAddress == "user@example.com"

        # Integration contact
        integration = IntegrationKey(id="key123", name="PagerDuty", providerName="pagerduty")

        integration_contact = MonitorContact(
            id="contact2",
            notificationChannelType="integration",
            integration=integration,
        )

        assert integration_contact.notificationChannelType == "integration"
        assert integration_contact.integration.providerName == "pagerduty"

    def test_metric_window(self):
        """Test MetricWindow model."""
        from arize_toolkit.models import Dimension, MetricWindow
        from arize_toolkit.types import DimensionCategory

        dimension = Dimension(name="user_age")

        window = MetricWindow(
            id="window123",
            type="moving",
            windowLengthMs=86400000,  # 24 hours
            dimensionCategory=DimensionCategory.featureLabel,
            dimension=dimension,
        )

        assert window.id == "window123"
        assert window.type == "moving"
        assert window.windowLengthMs == 86400000
        assert window.dimensionCategory == DimensionCategory.featureLabel
        assert window.dimension.name == "user_age"

    def test_dynamic_auto_threshold(self):
        """Test DynamicAutoThreshold model."""
        from arize_toolkit.models import DynamicAutoThreshold

        threshold = DynamicAutoThreshold(stdDevMultiplier=3.0)
        assert threshold.stdDevMultiplier == 3.0

        # Test default
        threshold_default = DynamicAutoThreshold()
        assert threshold_default.stdDevMultiplier == 2.0

    def test_data_quality_monitor(self):
        """Test DataQualityMonitor model."""
        from arize_toolkit.models import DataQualityMonitor
        from arize_toolkit.types import ComparisonOperator, DataQualityMetric, DimensionCategory, ModelEnvironment

        monitor = DataQualityMonitor(
            spaceId="space123",
            modelName="my-model",
            name="Missing Values Monitor",
            dataQualityMetric=DataQualityMetric.percentEmpty,
            dimensionCategory=DimensionCategory.featureLabel,
            dimensionName="user_age",
            operator=ComparisonOperator.greaterThan,
            threshold=0.1,
            modelEnvironmentName=ModelEnvironment.production,
        )

        assert monitor.spaceId == "space123"
        assert monitor.modelName == "my-model"
        assert monitor.name == "Missing Values Monitor"
        assert monitor.dataQualityMetric == DataQualityMetric.percentEmpty
        assert monitor.dimensionCategory == DimensionCategory.featureLabel
        assert monitor.dimensionName == "user_age"
        assert monitor.operator == ComparisonOperator.greaterThan
        assert monitor.threshold == 0.1

    def test_drift_monitor(self):
        """Test DriftMonitor model."""
        from arize_toolkit.models import DriftMonitor
        from arize_toolkit.types import ComparisonOperator, DimensionCategory, DriftMetric

        monitor = DriftMonitor(
            spaceId="space123",
            modelName="my-model",
            name="PSI Monitor",
            driftMetric=DriftMetric.psi,
            dimensionCategory=DimensionCategory.prediction,
            dimensionName="prediction_score",
            operator=ComparisonOperator.greaterThan,
            threshold=0.2,
        )

        assert monitor.spaceId == "space123"
        assert monitor.name == "PSI Monitor"
        assert monitor.driftMetric == DriftMetric.psi
        assert monitor.dimensionCategory == DimensionCategory.prediction
        assert monitor.dimensionName == "prediction_score"
        assert monitor.operator == ComparisonOperator.greaterThan
        assert monitor.threshold == 0.2

    def test_monitor_comprehensive(self):
        """Test Monitor model with comprehensive fields."""
        from datetime import datetime, timezone

        from arize_toolkit.models import CustomMetric, MetricWindow, Monitor, MonitorContact, User
        from arize_toolkit.types import ComparisonOperator, DimensionCategory, MonitorCategory, PerformanceMetric

        created_time = datetime(2024, 1, 1, tzinfo=timezone.utc)
        evaluated_time = datetime(2024, 1, 2, tzinfo=timezone.utc)

        user = User(id="user123", name="Test User")
        contact = MonitorContact(
            id="contact1",
            notificationChannelType="email",
            emailAddress="alert@example.com",
        )
        custom_metric = CustomMetric(
            id="metric123",
            name="Custom Metric",
            metric="custom_formula",
            requiresPositiveClass=False,
        )
        metric_window = MetricWindow(id="window123", type="moving", windowLengthMs=86400000)

        monitor = Monitor(
            id="monitor123",
            name="Performance Monitor",
            monitorCategory=MonitorCategory.performance,
            createdDate=created_time,
            evaluationIntervalSeconds=3600,
            evaluatedAt=evaluated_time,
            creator=user,
            notes="Monitor for tracking model performance",
            contacts=[contact],
            dimensionCategory=DimensionCategory.prediction,
            status="cleared",
            isTriggered=False,
            isManaged=False,
            threshold=0.9,
            thresholdMode="single",
            threshold2=None,
            dynamicAutoThresholdEnabled=True,
            stdDevMultiplier=2.5,
            notificationsEnabled=True,
            updatedAt=evaluated_time,
            scheduledRuntimeEnabled=True,
            scheduledRuntimeCadenceSeconds=86400,
            scheduledRuntimeDaysOfWeek=[1, 2, 3, 4, 5],  # Weekdays
            latestComputedValue=0.92,
            performanceMetric=PerformanceMetric.accuracy,
            customMetric=custom_metric,
            operator=ComparisonOperator.greaterThan,
            positiveClassValue="1",
            primaryMetricWindow=metric_window,
        )

        assert monitor.id == "monitor123"
        assert monitor.name == "Performance Monitor"
        assert monitor.monitorCategory == MonitorCategory.performance
        assert monitor.creator.name == "Test User"
        assert len(monitor.contacts) == 1
        assert monitor.status == "cleared"
        assert monitor.isTriggered is False
        assert monitor.threshold == 0.9
        assert monitor.dynamicAutoThresholdEnabled is True
        assert monitor.stdDevMultiplier == 2.5
        assert monitor.notificationsEnabled is True
        assert monitor.scheduledRuntimeCadenceSeconds == 86400
        assert len(monitor.scheduledRuntimeDaysOfWeek) == 5
        assert monitor.latestComputedValue == 0.92
        assert monitor.performanceMetric == PerformanceMetric.accuracy
        assert monitor.positiveClassValue == "1"


class TestDimensionValue:
    """Test DimensionValue model"""

    def test_init(self):
        """Test DimensionValue initialization"""
        # Test with all fields
        dim_value = DimensionValue(id="dim_val_123", value="category_1")
        assert dim_value.id == "dim_val_123"
        assert dim_value.value == "category_1"

    def test_required_fields(self):
        """Test DimensionValue with only required fields"""
        dim_value = DimensionValue(value="test_value")
        assert dim_value.value == "test_value"
        assert dim_value.id is None

    def test_missing_required_field(self):
        """Test DimensionValue without required value field"""
        with pytest.raises(ValueError):
            DimensionValue()


class TestMetricFilterItem:
    """Test MetricFilterItem model"""

    def test_init(self):
        """Test MetricFilterItem initialization with all fields"""
        from arize_toolkit.types import ComparisonOperator, FilterRowType

        dimension = Dimension(id="dim123", name="test_dim")
        dim_values = [
            DimensionValue(id="val1", value="value1"),
            DimensionValue(id="val2", value="value2"),
        ]

        filter_item = MetricFilterItem(
            id="filter123",
            filterType=FilterRowType.featureLabel,
            operator=ComparisonOperator.equals,
            dimension=dimension,
            dimensionValues=dim_values,
            binaryValues=["true", "false"],
            numericValues=["1.0", "2.0", "3.0"],
            categoricalValues=["cat1", "cat2", "cat3"],
        )

        assert filter_item.id == "filter123"
        assert filter_item.filterType == FilterRowType.featureLabel
        assert filter_item.operator == ComparisonOperator.equals
        assert filter_item.dimension.name == "test_dim"
        assert len(filter_item.dimensionValues) == 2
        assert filter_item.binaryValues == ["true", "false"]
        assert filter_item.numericValues == ["1.0", "2.0", "3.0"]
        assert filter_item.categoricalValues == ["cat1", "cat2", "cat3"]

    def test_all_optional_fields(self):
        """Test MetricFilterItem with all fields as None"""
        filter_item = MetricFilterItem()

        assert filter_item.id is None
        assert filter_item.filterType is None
        assert filter_item.operator is None
        assert filter_item.dimension is None
        assert filter_item.dimensionValues is None
        assert filter_item.binaryValues is None
        assert filter_item.numericValues is None
        assert filter_item.categoricalValues is None

    def test_partial_fields(self):
        """Test MetricFilterItem with partial fields"""
        from arize_toolkit.types import ComparisonOperator, FilterRowType

        filter_item = MetricFilterItem(
            filterType=FilterRowType.predictionValue,
            operator=ComparisonOperator.greaterThan,
            numericValues=["100", "200"],
        )

        assert filter_item.filterType == FilterRowType.predictionValue
        assert filter_item.operator == ComparisonOperator.greaterThan
        assert filter_item.numericValues == ["100", "200"]
        assert filter_item.id is None
        assert filter_item.dimension is None


class TestMetricWindow:
    """Test MetricWindow model"""

    def test_init(self):
        """Test MetricWindow initialization with all fields"""
        from arize_toolkit.types import DimensionCategory, FilterRowType

        dimension = Dimension(id="dim456", name="window_dim")
        filter_items = [
            MetricFilterItem(
                id="f1",
                filterType=FilterRowType.predictionScore,
                numericValues=["10", "20"],
            ),
            MetricFilterItem(
                id="f2",
                filterType=FilterRowType.featureLabel,
                categoricalValues=["cat1", "cat2"],
            ),
        ]

        window = MetricWindow(
            id="window123",
            type="fixed",
            windowLengthMs=172800000,  # 2 days in ms
            dimensionCategory=DimensionCategory.featureLabel,
            dimension=dimension,
            filters=filter_items,
        )

        assert window.id == "window123"
        assert window.type == "fixed"
        assert window.windowLengthMs == 172800000
        assert window.dimensionCategory == DimensionCategory.featureLabel
        assert window.dimension.name == "window_dim"
        assert len(window.filters) == 2
        assert window.filters[0].id == "f1"

    def test_default_values(self):
        """Test MetricWindow default values"""
        window = MetricWindow()

        assert window.id is None
        assert window.type == "moving"  # Default value
        assert window.windowLengthMs == 86400000  # Default value (1 day in ms)
        assert window.dimensionCategory is None
        assert window.dimension is None
        assert window.filters == []  # Default empty list

    def test_partial_initialization(self):
        """Test MetricWindow with partial fields"""
        from arize_toolkit.types import DimensionCategory

        window = MetricWindow(
            id="window456",
            type="fixed",
            dimensionCategory=DimensionCategory.prediction,
        )

        assert window.id == "window456"
        assert window.type == "fixed"
        assert window.windowLengthMs == 86400000  # Default value
        assert window.dimensionCategory == DimensionCategory.prediction
        assert window.dimension is None
        assert window.filters == []

    def test_filters_list_operations(self):
        """Test that filters list can be modified"""
        window = MetricWindow()
        assert window.filters == []

        # Add a filter
        new_filter = MetricFilterItem(id="filter1")
        window.filters.append(new_filter)
        assert len(window.filters) == 1
        assert window.filters[0].id == "filter1"


class TestDimensionFilterInput:
    """Test DimensionFilterInput model"""

    def test_init(self):
        """Test DimensionFilterInput initialization"""
        from arize_toolkit.types import ComparisonOperator, FilterRowType

        filter_input = DimensionFilterInput(
            dimensionType=FilterRowType.predictionValue,
            operator=ComparisonOperator.lessThan,
            name="test_dimension",
            values=["value1", "value2", "value3"],
        )

        assert filter_input.dimensionType == FilterRowType.predictionValue
        assert filter_input.operator == ComparisonOperator.lessThan
        assert filter_input.name == "test_dimension"
        assert filter_input.values == ["value1", "value2", "value3"]

    def test_default_values(self):
        """Test DimensionFilterInput default values"""
        from arize_toolkit.types import ComparisonOperator, FilterRowType

        filter_input = DimensionFilterInput(dimensionType=FilterRowType.predictionValue)

        assert filter_input.dimensionType == FilterRowType.predictionValue
        assert filter_input.operator == ComparisonOperator.equals  # Default
        assert filter_input.name is None
        assert filter_input.values == []  # Default empty list

    def test_validation_feature_label_requires_name(self):
        """Test validation that featureLabel filter type requires name"""
        from arize_toolkit.types import FilterRowType

        # Should raise error without name
        with pytest.raises(
            ValueError,
            match="Name is required for feature label or tag label filter type",
        ):
            DimensionFilterInput(
                dimensionType=FilterRowType.featureLabel,
                values=["value1"],
            )

    def test_validation_tag_label_requires_name(self):
        """Test validation that tagLabel filter type requires name"""
        from arize_toolkit.types import FilterRowType

        # Should raise error without name
        with pytest.raises(
            ValueError,
            match="Name is required for feature label or tag label filter type",
        ):
            DimensionFilterInput(
                dimensionType=FilterRowType.tagLabel,
                values=["tag1", "tag2"],
            )

    def test_valid_feature_label_with_name(self):
        """Test valid featureLabel filter with name"""
        from arize_toolkit.types import FilterRowType

        filter_input = DimensionFilterInput(
            dimensionType=FilterRowType.featureLabel,
            name="feature_name",
            values=["value1", "value2"],
        )

        assert filter_input.dimensionType == FilterRowType.featureLabel
        assert filter_input.name == "feature_name"
        assert filter_input.values == ["value1", "value2"]

    def test_valid_tag_label_with_name(self):
        """Test valid tagLabel filter with name"""
        from arize_toolkit.types import ComparisonOperator, FilterRowType

        filter_input = DimensionFilterInput(
            dimensionType=FilterRowType.tagLabel,
            name="tag_name",
            operator=ComparisonOperator.notEquals,
            values=["tag1"],
        )

        assert filter_input.dimensionType == FilterRowType.tagLabel
        assert filter_input.name == "tag_name"
        assert filter_input.operator == ComparisonOperator.notEquals
        assert filter_input.values == ["tag1"]

    def test_other_filter_types_without_name(self):
        """Test that other filter types don't require name"""
        from arize_toolkit.types import FilterRowType

        # These should work without name
        filter_types = [
            FilterRowType.predictionValue,
            FilterRowType.actuals,
            FilterRowType.actualScore,
            FilterRowType.predictionScore,
            FilterRowType.modelVersion,
            FilterRowType.batchId,
        ]

        for filter_type in filter_types:
            filter_input = DimensionFilterInput(
                dimensionType=filter_type,
                values=["test_value"],
            )
            assert filter_input.dimensionType == filter_type
            assert filter_input.name is None
            assert filter_input.values == ["test_value"]
