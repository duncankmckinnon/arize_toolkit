import json
import os
from unittest.mock import MagicMock, patch

import pytest

from arize_toolkit.trace_converters.openllmetry.map_openllmetry_to_openinference import (
    OpenLLMetryToOpenInferenceSpanProcessor,
    _canonicalize_messages,
    _dot_to_bracket,
    _handle_tool_list,
    _is_bracket_conversion_disabled,
    _is_debug_enabled,
    _map_prompt_or_completion,
    _needs_bracket_conversion,
    _normalize,
    _transform_tool_calls_list,
    map_openll_to_openinference,
)


class TestDirectMapping:
    """Test direct key mapping functionality."""

    def test_basic_direct_mapping(self):
        """Test basic 1-to-1 key mapping."""
        input_attrs = {
            "gen_ai.system": "openai",
            "gen_ai.request.model": "gpt-4",
            "gen_ai.usage.prompt_tokens": 100,
            "gen_ai.usage.completion_tokens": 50,
        }
        
        result = map_openll_to_openinference(input_attrs)
        
        assert result["llm.system"] == "openai"
        assert result["llm.model_name"] == "gpt-4"
        assert result["llm.token_count.prompt"] == 100
        assert result["llm.token_count.completion"] == 50
        assert result["llm.provider"] == "openai"  # Auto-generated from system

    def test_span_kind_mapping(self):
        """Test TraceLoop span kind mapping to OpenInference enum."""
        test_cases = [
            ("workflow", "CHAIN"),
            ("task", "TOOL"),
            ("agent", "AGENT"),
            ("tool", "TOOL"),
            ("unknown", "UNKNOWN"),
            ("invalid", "UNKNOWN"),  # Default for unknown values
        ]
        
        for input_kind, expected_kind in test_cases:
            input_attrs = {"traceloop.span.kind": input_kind}
            result = map_openll_to_openinference(input_attrs)
            assert result["openinference.span.kind"] == expected_kind

    def test_invocation_parameters_consolidation(self):
        """Test that various parameter keys are consolidated into llm.invocation_parameters."""
        input_attrs = {
            "gen_ai.request.max_tokens": 100,
            "gen_ai.request.temperature": 0.7,
            "gen_ai.request.top_p": 0.9,
            "llm.frequency_penalty": 0.1,
            "llm.presence_penalty": 0.2,
            "llm.request.repetition_penalty": 1.1,
        }
        
        result = map_openll_to_openinference(input_attrs)
        
        invocation_params = json.loads(result["llm.invocation_parameters"])
        assert invocation_params["max_tokens"] == 100
        assert invocation_params["temperature"] == 0.7
        assert invocation_params["top_p"] == 0.9
        assert invocation_params["frequency_penalty"] == 0.1
        assert invocation_params["presence_penalty"] == 0.2
        assert invocation_params["repetition_penalty"] == 1.1


class TestMessageCanonicalization:
    """Test message canonicalization functionality."""

    def test_normalize_basic_message(self):
        """Test basic message normalization."""
        msg = {
            "role": "user",
            "content": "Hello world",
            "name": "test_user"
        }
        
        result = _normalize(msg)
        
        assert result["message.role"] == "user"
        assert result["message.content"] == "Hello world"
        assert result["message.name"] == "test_user"

    def test_normalize_tool_calls_list(self):
        """Test normalization of tool calls in list format."""
        msg = {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": "call_123",
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "arguments": '{"city": "SF"}'
                    }
                }
            ]
        }
        
        result = _normalize(msg)
        
        assert result["message.role"] == "assistant"
        assert result["message.content"] is None
        assert isinstance(result["message.tool_calls"], list)
        tool_call = result["message.tool_calls"][0]
        assert tool_call["tool_call.id"] == "call_123"
        assert tool_call["tool_call.function.name"] == "get_weather"
        assert tool_call["tool_call.function.arguments"] == '{"city": "SF"}'

    def test_normalize_tool_calls_dotted(self):
        """Test normalization of tool calls in dotted format."""
        msg = {
            "role": "assistant",
            "content": None,
            "tool_calls.0.id": "call_123",
            "tool_calls.0.function.name": "get_weather",
            "tool_calls.0.function.arguments": '{"city": "SF"}',
            "tool_calls.1.id": "call_456",
            "tool_calls.1.function.name": "get_temperature",
            "tool_calls.1.function.arguments": '{"location": "NYC"}'
        }
        
        result = _normalize(msg)
        
        assert result["message.role"] == "assistant"
        assert isinstance(result["message.tool_calls"], list)
        assert len(result["message.tool_calls"]) == 2
        
        tool_call_0 = result["message.tool_calls"][0]
        assert tool_call_0["tool_call.id"] == "call_123"
        assert tool_call_0["function.name"] == "get_weather"
        
        tool_call_1 = result["message.tool_calls"][1]
        assert tool_call_1["tool_call.id"] == "call_456"
        assert tool_call_1["function.name"] == "get_temperature"

    def test_canonicalize_messages_dict_format(self):
        """Test canonicalizing messages from dict format."""
        raw_messages = {
            "0": {"role": "user", "content": "Hello"},
            "1": {"role": "assistant", "content": "Hi there"}
        }
        
        result = _canonicalize_messages(raw_messages)
        
        assert len(result) == 2
        assert result[0]["message.role"] == "user"
        assert result[0]["message.content"] == "Hello"
        assert result[1]["message.role"] == "assistant"
        assert result[1]["message.content"] == "Hi there"

    def test_canonicalize_messages_list_format(self):
        """Test canonicalizing messages from list format."""
        raw_messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"}
        ]
        
        result = _canonicalize_messages(raw_messages)
        
        assert len(result) == 2
        assert result[0]["message.role"] == "user"
        assert result[0]["message.content"] == "Hello"
        assert result[1]["message.role"] == "assistant"
        assert result[1]["message.content"] == "Hi there"

    def test_transform_tool_calls_list(self):
        """Test transformation of tool calls list."""
        tool_calls = [
            {
                "id": "call_123",
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "arguments": '{"city": "SF"}'
                }
            },
            {
                "name": "get_temperature",  # Different format
                "arguments": '{"location": "NYC"}',
                "id": "call_456"
            }
        ]
        
        result = _transform_tool_calls_list(tool_calls)
        
        assert len(result) == 2
        
        # First tool call (nested function format)
        assert result[0]["tool_call.id"] == "call_123"
        assert result[0]["tool_call.function.name"] == "get_weather"
        assert result[0]["tool_call.function.arguments"] == '{"city": "SF"}'
        
        # Second tool call (flat format)
        assert result[1]["tool_call.function.name"] == "get_temperature"
        assert result[1]["tool_call.function.arguments"] == '{"location": "NYC"}'
        assert result[1]["tool_call.id"] == "call_456"


class TestPromptCompletionMapping:
    """Test prompt and completion mapping functionality."""

    def test_map_prompt_or_completion_basic(self):
        """Test basic prompt/completion mapping."""
        messages = [
            {"role": "user", "content": "Hello"}
        ]
        dst = {}
        
        _map_prompt_or_completion(messages, dst, is_prompt=True)
        
        assert "llm.input_messages" in dst
        parsed_messages = json.loads(dst["llm.input_messages"])
        assert len(parsed_messages) == 1
        assert parsed_messages[0]["message.role"] == "user"
        assert parsed_messages[0]["message.content"] == "Hello"
        
        # Check dotted attributes
        assert dst["llm.input_messages.0.message.role"] == "user"
        assert dst["llm.input_messages.0.message.content"] == "Hello"

    def test_map_prompt_or_completion_with_tool_calls(self):
        """Test mapping with tool calls."""
        messages = [
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_123",
                        "function": {
                            "name": "get_weather",
                            "arguments": '{"city": "SF"}'
                        }
                    }
                ]
            }
        ]
        dst = {}
        
        _map_prompt_or_completion(messages, dst, is_prompt=False)
        
        assert "llm.output_messages" in dst
        # Check that tool calls are properly exploded
        assert dst["llm.output_messages.0.message.tool_calls.0.tool_call.id"] == "call_123"
        assert dst["llm.output_messages.0.message.tool_calls.0.tool_call.function.name"] == "get_weather"

    @patch.dict(os.environ, {"DEBUG_OPENINF": "true"})
    def test_map_prompt_with_debug_enabled(self, capsys):
        """Test prompt mapping with debug output enabled."""
        messages = [{"role": "user", "content": "Test"}]
        dst = {}
        
        _map_prompt_or_completion(messages, dst, is_prompt=True)
        
        captured = capsys.readouterr()
        assert "[DEBUG] Set llm.input_messages (is_prompt=True)" in captured.err


class TestToolHandling:
    """Test tool list handling functionality."""

    def test_handle_tool_list_basic(self):
        """Test basic tool list handling."""
        tools = [
            {
                "name": "get_weather",
                "description": "Get current weather",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {"type": "string"}
                    }
                }
            }
        ]
        dst = {}
        
        _handle_tool_list(tools, dst)
        
        assert dst["llm.tools.0.name"] == "get_weather"
        assert dst["llm.tools.0.description"] == "Get current weather"
        assert isinstance(dst["llm.tools.0.parameters"], str)  # JSON encoded
        
        params = json.loads(dst["llm.tools.0.parameters"])
        assert params["type"] == "object"

    def test_handle_tool_list_json_string(self):
        """Test tool list handling with JSON string input."""
        tools_json = json.dumps([
            {"name": "test_tool", "description": "A test tool"}
        ])
        dst = {}
        
        _handle_tool_list(tools_json, dst)
        
        assert dst["llm.tools.0.name"] == "test_tool"
        assert dst["llm.tools.0.description"] == "A test tool"

    def test_handle_tool_list_invalid_json(self):
        """Test tool list handling with invalid JSON."""
        dst = {}
        
        _handle_tool_list("invalid json", dst)
        
        # Should not add any tool attributes on failure
        assert not any(key.startswith("llm.tools.") for key in dst.keys())


class TestHelperFunctions:
    """Test various helper functions."""

    def test_needs_bracket_conversion(self):
        """Test bracket conversion detection."""
        assert _needs_bracket_conversion("field.0.subfield")
        assert _needs_bracket_conversion("a.123.b")
        assert not _needs_bracket_conversion("field.subfield")
        assert not _needs_bracket_conversion("field")

    def test_dot_to_bracket(self):
        """Test dot to bracket conversion."""
        assert _dot_to_bracket("field.0.subfield") == "field[0].subfield"
        assert _dot_to_bracket("a.123.b.456.c") == "a[123].b[456].c"
        assert _dot_to_bracket("field.subfield") == "field.subfield"

    @patch.dict(os.environ, {"DEBUG_OPENINF": "true"})
    def test_is_debug_enabled_true(self):
        """Test debug detection when enabled."""
        assert _is_debug_enabled()

    @patch.dict(os.environ, {"DEBUG_OPENINF": "false"})
    def test_is_debug_enabled_false(self):
        """Test debug detection when disabled."""
        assert not _is_debug_enabled()

    @patch.dict(os.environ, {"DISABLE_BRACKET_CONVERSION": "true"})
    def test_is_bracket_conversion_disabled_true(self):
        """Test bracket conversion disable detection when enabled."""
        assert _is_bracket_conversion_disabled()

    @patch.dict(os.environ, {"DISABLE_BRACKET_CONVERSION": "false"})
    def test_is_bracket_conversion_disabled_false(self):
        """Test bracket conversion disable detection when disabled."""
        assert not _is_bracket_conversion_disabled()


class TestMainConversionFunction:
    """Test the main conversion function."""

    def test_complete_llm_span_conversion(self):
        """Test complete LLM span conversion."""
        input_attrs = {
            "gen_ai.system": "openai",
            "gen_ai.request.model": "gpt-4",
            "gen_ai.usage.prompt_tokens": 100,
            "gen_ai.usage.completion_tokens": 50,
            "gen_ai.request.temperature": 0.7,
            "gen_ai.prompt": {
                "0": {"role": "user", "content": "Hello world"}
            },
            "gen_ai.completion": {
                "0": {"role": "assistant", "content": "Hi there!"}
            },
            "traceloop.span.kind": "workflow"
        }
        
        result = map_openll_to_openinference(input_attrs)
        
        # Basic mappings
        assert result["llm.system"] == "openai"
        assert result["llm.model_name"] == "gpt-4"
        assert result["llm.provider"] == "openai"
        assert result["llm.token_count.prompt"] == 100
        assert result["llm.token_count.completion"] == 50
        assert result["openinference.span.kind"] == "CHAIN"
        
        # Invocation parameters
        assert "llm.invocation_parameters" in result
        params = json.loads(result["llm.invocation_parameters"])
        assert params["temperature"] == 0.7
        
        # Messages
        assert "llm.input_messages" in result
        assert "llm.output_messages" in result
        
        # Input/output composite structures
        assert "input.value" in result
        assert "output.value" in result
        
        input_value = json.loads(result["input.value"])
        assert input_value["model"] == "gpt-4"
        assert input_value["messages"][0]["content"] == "Hello world"
        
        output_value = json.loads(result["output.value"])
        assert output_value["choices"][0]["message"]["content"] == "Hi there!"

    def test_dotted_prompt_completion_reconstruction(self):
        """Test reconstruction of prompt/completion from dotted attributes."""
        input_attrs = {
            "gen_ai.prompt.0.role": "user",
            "gen_ai.prompt.0.content": "Hello",
            "gen_ai.completion.0.role": "assistant",
            "gen_ai.completion.0.content": "Hi"
        }
        
        result = map_openll_to_openinference(input_attrs)
        
        assert "llm.input_messages" in result
        assert "llm.output_messages" in result
        
        input_messages = json.loads(result["llm.input_messages"])
        assert len(input_messages) == 1
        assert input_messages[0]["message.role"] == "user"
        assert input_messages[0]["message.content"] == "Hello"

    def test_tool_reconstruction_from_dotted(self):
        """Test tool reconstruction from dotted attributes."""
        input_attrs = {
            "llm.request.functions.0.name": "get_weather",
            "llm.request.functions.0.description": "Get weather info",
            "llm.request.functions.1.name": "get_time",
            "llm.request.functions.1.description": "Get current time"
        }
        
        result = map_openll_to_openinference(input_attrs)
        
        assert "llm.tools.0.name" in result
        assert "llm.tools.0.description" in result
        assert "llm.tools.1.name" in result
        assert "llm.tools.1.description" in result
        
        assert result["llm.tools.0.name"] == "get_weather"
        assert result["llm.tools.1.name"] == "get_time"

    def test_metadata_collection(self):
        """Test that unknown attributes are collected in metadata."""
        input_attrs = {
            "custom.attribute": "value",
            "another.unknown": 123,
            "gen_ai.system": "openai"  # This should map directly
        }
        
        result = map_openll_to_openinference(input_attrs)
        
        assert result["llm.system"] == "openai"
        assert "metadata" in result
        
        metadata = json.loads(result["metadata"])
        assert metadata["custom.attribute"] == "value"
        assert metadata["another.unknown"] == 123

    def test_context_attributes_preservation(self):
        """Test that context attributes are preserved at top level."""
        input_attrs = {
            "session.id": "session_123",
            "user.id": "user_456",
            "metadata": "existing_metadata",
            "openinference.span.kind": "LLM"
        }
        
        result = map_openll_to_openinference(input_attrs)
        
        # These should stay at top level, not in metadata
        assert result["session.id"] == "session_123"
        assert result["user.id"] == "user_456"
        assert result["openinference.span.kind"] == "LLM"
        assert result["metadata"] == "existing_metadata"

    @patch.dict(os.environ, {"DISABLE_BRACKET_CONVERSION": "true"})
    def test_bracket_conversion_disabled(self):
        """Test behavior when bracket conversion is disabled."""
        input_attrs = {
            "custom.0.field": "value",
            "gen_ai.system": "openai"
        }
        
        result = map_openll_to_openinference(input_attrs)
        
        # Should preserve dot notation when bracket conversion is disabled
        # Unknown attributes still go to metadata but without bracket conversion
        assert "metadata" in result
        metadata = json.loads(result["metadata"])
        assert metadata["custom.0.field"] == "value"
        assert result["llm.system"] == "openai"

    def test_flattening_behavior(self):
        """Test one-level flattening behavior."""
        input_attrs = {
            "gen_ai": {
                "system": "openai",
                "request": {
                    "model": "gpt-4"
                }
            }
        }
        
        result = map_openll_to_openinference(input_attrs)
        
        assert result["llm.system"] == "openai"
        # Nested dict should be flattened and stored as JSON in metadata
        assert "metadata" in result


class TestSpanProcessor:
    """Test the SpanProcessor class."""

    def test_span_processor_initialization(self):
        """Test span processor can be initialized."""
        processor = OpenLLMetryToOpenInferenceSpanProcessor()
        assert processor is not None

    def test_span_processor_on_start(self):
        """Test on_start method does nothing."""
        processor = OpenLLMetryToOpenInferenceSpanProcessor()
        mock_span = MagicMock()
        
        # Should not raise any exception
        processor.on_start(mock_span)

    def test_span_processor_on_end_success(self):
        """Test successful span transformation on end."""
        processor = OpenLLMetryToOpenInferenceSpanProcessor()
        mock_span = MagicMock()
        mock_span.name = "test_span"
        mock_span._attributes = {
            "gen_ai.system": "openai",
            "gen_ai.request.model": "gpt-4"
        }
        
        processor.on_end(mock_span)
        
        # Check that attributes were transformed
        assert mock_span._attributes["llm.system"] == "openai"
        assert mock_span._attributes["llm.model_name"] == "gpt-4"
        assert "llm.provider" in mock_span._attributes

    def test_span_processor_on_end_no_attributes(self):
        """Test span processor handles spans without attributes."""
        processor = OpenLLMetryToOpenInferenceSpanProcessor()
        mock_span = MagicMock()
        mock_span._attributes = None
        
        # Should not raise any exception
        processor.on_end(mock_span)

    def test_span_processor_on_end_empty_attributes(self):
        """Test span processor handles spans with empty attributes."""
        processor = OpenLLMetryToOpenInferenceSpanProcessor()
        mock_span = MagicMock()
        mock_span._attributes = {}
        
        # Should not raise any exception
        processor.on_end(mock_span)

    def test_span_processor_on_end_transformation_error(self):
        """Test span processor handles transformation errors gracefully."""
        processor = OpenLLMetryToOpenInferenceSpanProcessor()
        mock_span = MagicMock()
        mock_span.name = "test_span"
        original_attrs = {"gen_ai.system": "openai"}
        mock_span._attributes = original_attrs.copy()
        
        # Mock the transformation to raise an exception
        with patch('map_openllmetry_to_openinference.map_openll_to_openinference', 
                   side_effect=Exception("Transformation error")):
            processor.on_end(mock_span)
            
            # Should preserve original attributes on error
            assert mock_span._attributes == original_attrs

    @patch.dict(os.environ, {"DEBUG_OPENINF": "true"})
    def test_span_processor_debug_output(self, capsys):
        """Test span processor debug output."""
        processor = OpenLLMetryToOpenInferenceSpanProcessor()
        mock_span = MagicMock()
        mock_span.name = "test_span"
        mock_span._attributes = {"gen_ai.system": "openai"}
        
        processor.on_end(mock_span)
        
        captured = capsys.readouterr()
        assert "Transformed span 'test_span'" in captured.err

    def test_span_processor_shutdown(self):
        """Test shutdown method."""
        processor = OpenLLMetryToOpenInferenceSpanProcessor()
        # Should not raise any exception
        processor.shutdown()

    def test_span_processor_force_flush(self):
        """Test force_flush method."""
        processor = OpenLLMetryToOpenInferenceSpanProcessor()
        result = processor.force_flush()
        assert result is True
        
        result = processor.force_flush(timeout_millis=1000)
        assert result is True


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_input(self):
        """Test conversion with empty input."""
        result = map_openll_to_openinference({})
        assert isinstance(result, dict)

    def test_non_dict_values(self):
        """Test handling of non-dict values in complex structures."""
        input_attrs = {
            "gen_ai.prompt": "not a dict",
            "gen_ai.completion": ["not", "a", "dict"]
        }
        
        result = map_openll_to_openinference(input_attrs)
        
        # Should handle gracefully and still produce valid output
        assert isinstance(result, dict)
        
        # Check that the non-dict values were handled gracefully
        assert "llm.input_messages" in result
        input_messages = json.loads(result["llm.input_messages"])
        assert len(input_messages) == 1
        assert input_messages[0]["message.content"] == "not a dict"
        
        assert "llm.output_messages" in result
        output_messages = json.loads(result["llm.output_messages"])
        # List should be processed element by element
        assert len(output_messages) == 3  # ["not", "a", "dict"]

    def test_invalid_message_structures(self):
        """Test handling of invalid message structures."""
        input_attrs = {
            "gen_ai.prompt": {
                "invalid": "structure"
            }
        }
        
        result = map_openll_to_openinference(input_attrs)
        
        # Should handle gracefully
        assert isinstance(result, dict)

    def test_malformed_tool_calls(self):
        """Test handling of malformed tool calls."""
        messages = [{
            "role": "assistant",
            "tool_calls": [
                {"invalid": "structure"},
                None,
                "not a dict"
            ]
        }]
        
        result = _transform_tool_calls_list(messages[0]["tool_calls"])
        
        # Should handle gracefully without raising exceptions
        assert isinstance(result, list)

    def test_very_large_attribute_values(self):
        """Test handling of very large attribute values."""
        large_dict = {f"key_{i}": f"value_{i}" for i in range(1000)}
        input_attrs = {
            "gen_ai.system": "openai",
            "large_attribute": large_dict
        }
        
        result = map_openll_to_openinference(input_attrs)
        
        # Should handle large values by JSON encoding them
        assert result["llm.system"] == "openai"
        assert "metadata" in result


class TestRegressionCases:
    """Test specific regression cases that have been problematic."""

    def test_mixed_tool_call_formats(self):
        """Test handling of mixed tool call formats in the same message."""
        input_attrs = {
            "gen_ai.completion": {
                "0": {
                    "role": "assistant",
                    "content": None,
                    "tool_calls.0.id": "call_1",
                    "tool_calls.0.function.name": "func_1",
                    "tool_calls": [
                        {
                            "id": "call_2",
                            "function": {"name": "func_2"}
                        }
                    ]
                }
            }
        }
        
        result = map_openll_to_openinference(input_attrs)
        
        # Should handle mixed formats gracefully
        assert "llm.output_messages" in result

    def test_unicode_content(self):
        """Test handling of unicode content in messages."""
        input_attrs = {
            "gen_ai.prompt": {
                "0": {
                    "role": "user",
                    "content": "Hello 世界! 🌍 Emoji test 😀"
                }
            }
        }
        
        result = map_openll_to_openinference(input_attrs)
        
        assert "llm.input_messages" in result
        messages = json.loads(result["llm.input_messages"])
        assert "世界" in messages[0]["message.content"]
        assert "🌍" in messages[0]["message.content"]

    def test_null_and_none_values(self):
        """Test handling of null and None values."""
        input_attrs = {
            "gen_ai.system": "openai",
            "null_value": None,
            "gen_ai.prompt": {
                "0": {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": None
                }
            }
        }
        
        result = map_openll_to_openinference(input_attrs)
        
        # Should handle None values gracefully
        assert result["llm.system"] == "openai"
        assert "llm.input_messages" in result