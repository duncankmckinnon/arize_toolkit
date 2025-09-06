from datetime import datetime, timezone

import pytest

from arize_toolkit.models import (
    AnnotationInput,
    AnnotationWithConfigIdInput,
    CreatePromptBaseMutationInput,
    CreatePromptMutationInput,
    CreatePromptVersionMutationInput,
    FunctionDetailsInput,
    InvocationParamsInput,
    LLMMessageInput,
    NoteInput,
    Prompt,
    PromptVersion,
    ProviderParamsInput,
    ToolChoiceInput,
    ToolConfigInput,
    ToolInput,
    UpdateAnnotationsInput,
    User,
)
from arize_toolkit.types import ExternalLLMProviderModel, LLMIntegrationProvider, ModelEnvironment, PromptVersionInputVariableFormatEnum
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


class TestLanguageModelInputs:
    def test_note_input(self):
        """Test NoteInput model."""
        note = NoteInput(text="This is a test note")
        assert note.text == "This is a test note"

    def test_tool_choice_input(self):
        """Test ToolChoiceInput model."""
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
        """Test UpdateAnnotationsInput model."""
        start_time = datetime(2024, 1, 1, tzinfo=timezone.utc)

        # Single annotation update
        mutation1 = UpdateAnnotationsInput(
            modelId="model123",
            note=NoteInput(text="Test note"),
            annotationUpdates=AnnotationWithConfigIdInput(
                annotationConfigId="config123",
                annotation=AnnotationInput(
                    name="quality",
                    updatedBy="user123",
                    score=0.9,
                    annotationType="score",
                ),
            ),
            recordId="record123",
            startTime=start_time,
        )

        assert mutation1.modelId == "model123"
        assert mutation1.note.text == "Test note"
        assert mutation1.recordId == "record123"
        assert mutation1.modelEnvironment == ModelEnvironment.tracing  # Default
        assert mutation1.annotationUpdates.annotationConfigId == "config123"
        assert mutation1.annotationUpdates.annotation.name == "quality"

        # Multiple annotation updates
        mutation2 = UpdateAnnotationsInput(
            modelId="model123",
            annotationUpdates=[
                AnnotationWithConfigIdInput(
                    annotationConfigId="config456",
                    annotation=AnnotationInput(
                        name="sentiment",
                        updatedBy="user1",
                        label="positive",
                        annotationType="label",
                    ),
                ),
                AnnotationWithConfigIdInput(
                    annotationConfigId="config789",
                    annotation=AnnotationInput(
                        name="quality",
                        updatedBy="user2",
                        score=0.8,
                        annotationType="score",
                    ),
                ),
            ],
            recordId="record456",
            modelEnvironment=ModelEnvironment.production,
            startTime=start_time,
        )

        assert len(mutation2.annotationUpdates) == 2
        assert mutation2.modelEnvironment == ModelEnvironment.production
        assert mutation2.annotationUpdates[0].annotationConfigId == "config456"
        assert mutation2.annotationUpdates[1].annotationConfigId == "config789"

    def test_annotation_with_config_id_input(self):
        """Test AnnotationWithConfigIdInput model."""
        annotation_update = AnnotationWithConfigIdInput(
            annotationConfigId="config123",
            annotation=AnnotationInput(
                name="quality",
                updatedBy="user123",
                text="This is good quality",
                annotationType="text",
            ),
        )

        assert annotation_update.annotationConfigId == "config123"
        assert annotation_update.annotation.name == "quality"
        assert annotation_update.annotation.text == "This is good quality"
        assert annotation_update.annotation.annotationType == "text"

    def test_annotation_input_text_type(self):
        """Test AnnotationInput with text annotation type."""
        annotation = AnnotationInput(
            name="feedback",
            updatedBy="user123",
            text="Great job!",
            annotationType="text",
        )

        assert annotation.name == "feedback"
        assert annotation.updatedBy == "user123"
        assert annotation.text == "Great job!"
        assert annotation.annotationType == "text"
        assert annotation.label is None
        assert annotation.score is None

        # Test validation - text required for text type
        with pytest.raises(ValueError, match="Text is required for text annotation type"):
            AnnotationInput(
                name="feedback",
                updatedBy="user123",
                annotationType="text",
                # Missing text field
            )
