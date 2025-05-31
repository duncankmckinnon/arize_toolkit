import json
import sys
from typing import Any, Dict, List
import re

# Add OpenTelemetry import for SpanProcessor
from opentelemetry.sdk.trace import SpanProcessor

"""Utility that converts OpenLLMetry span attributes to OpenInference attributes.

Usage
-----
python scripts/map_openll_to_openinference.py <openll_json_file>
cat openll_span.json | python scripts/map_openll_to_openinference.py

The script prints a JSON object with the mapped OpenInference attributes to stdout.
"""

# ---------------------------------------------------------------------------
# STATIC MAPPINGS
# ---------------------------------------------------------------------------

# Direct 1-to-1 key remapping.  Keys that should be merged into a single
# llm.invocation_parameters dict are expressed with the dotted prefix
# "llm.invocation_parameters.".
_DIRECT_MAPPING: Dict[str, str] = {
    # Identity / model
    "gen_ai.system": "llm.system",
    "gen_ai.request.model": "llm.model_name",
    "gen_ai.response.model": "llm.model_name",  # collapse to one key
    # Request type - preserve OpenLLMetry semantic convention
    "llm.request.type": "llm.request.type",
    # Prompt (handled separately to build llm.input_messages)
    # Token counts
    "gen_ai.usage.prompt_tokens": "llm.token_count.prompt",
    "gen_ai.usage.completion_tokens": "llm.token_count.completion",
    "llm.usage.total_tokens": "llm.token_count.total",
    "gen_ai.usage.cache_creation_input_tokens": "llm.token_count.prompt_details.cache_write",
    "gen_ai.usage.cache_read_input_tokens": "llm.token_count.prompt_details.cache_read",
    # System/user
    "llm.user": "user.id",
    # TraceLoop span kind
    "traceloop.span.kind": "openinference.span.kind",
}

# Mapping for TraceLoop span kind string → OpenInference enum value.
_SPAN_KIND_MAPPING: Dict[str, str] = {
    "workflow": "CHAIN",
    "task": "TOOL",
    "agent": "AGENT",
    "tool": "TOOL",
    "unknown": "UNKNOWN",
}

# Keys that should be packed inside llm.invocation_parameters regardless of
# their original prefix.
_INVOCATION_PARAMETER_KEYS: List[str] = [
    # Official OpenLLMetry gen_ai.request.*
    "gen_ai.request.max_tokens",
    "gen_ai.request.temperature",
    "gen_ai.request.top_p",
    # Generic llm.request.* keys
    "llm.request.repetition_penalty",
    # Additional numeric / control knobs
    "llm.frequency_penalty",
    "llm.presence_penalty",
    "llm.top_k",
    "llm.chat.stop_sequences",
]

# Key that carries the tool list in OpenLLMetry
_OPENLL_TOOL_LIST_KEY = "llm.request.functions"
# Corresponding OpenInference list key
_OPENINF_TOOL_LIST_KEY = "llm.tools"


# ---------------------------------------------------------------------------
# Helper to transform gen_ai.prompt / gen_ai.completion dict into list format
# ---------------------------------------------------------------------------

def _normalize(msg: Dict[str, Any]) -> Dict[str, Any]:
    """Convert message.* keys to bare keys (role, content, etc.)."""
    normalized = {}

    # First pass: split out dotted tool_call keys and everything else.
    tool_call_parts: Dict[int, Dict[str, Any]] = {}

    for k, v in msg.items():
        # We keep the original key as-is to preserve the "message." prefix
        # that Arize's UI expects.  However we still need to reconstruct the
        # list form for tool calls that may come in dotted or dict notation.

        # 1. Handle dotted form "tool_calls.<idx>.<field>" (without message. prefix).
        if k.startswith("tool_calls."):
            parts = k.split(".")
            if len(parts) >= 3 and parts[1].isdigit():
                idx = int(parts[1])
                field = ".".join(parts[2:])
                tool_call_parts.setdefault(idx, {})[field] = v
                continue

        # 2. Handle raw "tool_calls" (without message. prefix) - need to transform and prefix
        if k == "tool_calls":
            if isinstance(v, list):
                normalized["message.tool_calls"] = _transform_tool_calls_list(v)
            elif isinstance(v, dict) and all(str(i).isdigit() for i in v):
                ordered = [v[idx] for idx in sorted(v, key=lambda x: int(x))]
                normalized["message.tool_calls"] = _transform_tool_calls_list(ordered)
            else:
                # Fallback: add prefix but don't transform
                normalized[f"message.{k}"] = v
            continue

        # Default: copy as-is, but if the key has no "message." prefix and
        # is a typical message-level field, add the prefix so that the final
        # output uses the canonical OpenInference dotted names.
        if not k.startswith("message.") and k in ("role", "content", "name", "tool_call_id", "function_call", "finish_reason"):
            normalized[f"message.{k}"] = v
        else:
            normalized[k] = v

    # Build tool_calls list from dotted parts if we captured any.
    if tool_call_parts and "message.tool_calls" not in normalized:
        tool_calls_list: List[Dict[str, Any]] = []
        for idx in sorted(tool_call_parts):
            raw = tool_call_parts[idx]
            converted: Dict[str, Any] = {}
            for tk, tv in raw.items():
                if tk == "name":
                    converted["tool_call.function.name"] = tv
                elif tk == "arguments":
                    converted["tool_call.function.arguments"] = tv
                elif tk == "id":
                    converted["tool_call.id"] = tv
                else:
                    converted[tk] = tv
            tool_calls_list.append(converted)
        normalized["message.tool_calls"] = tool_calls_list

    return normalized


def _transform_tool_calls_list(tool_calls: List[Any]) -> List[Dict[str, Any]]:
    """Transform a list of tool calls to proper OpenInference structure."""
    transformed = []
    
    for tool_call in tool_calls:
        if not isinstance(tool_call, dict):
            transformed.append(tool_call)
            continue
            
        converted: Dict[str, Any] = {}
        
        # Handle different input formats and convert to OpenInference structure
        for key, value in tool_call.items():
            if key == "name":
                converted["tool_call.function.name"] = value
            elif key == "arguments":
                converted["tool_call.function.arguments"] = value
            elif key == "id":
                converted["tool_call.id"] = value
            elif key == "function" and isinstance(value, dict):
                # Handle nested function object
                for func_key, func_value in value.items():
                    if func_key == "name":
                        converted["tool_call.function.name"] = func_value
                    elif func_key == "arguments":
                        converted["tool_call.function.arguments"] = func_value
                    else:
                        converted[f"tool_call.function.{func_key}"] = func_value
            elif key.startswith("tool_call."):
                # Already in OpenInference format
                converted[key] = value
            else:
                # Copy other fields as-is
                converted[key] = value
                
        transformed.append(converted)
    
    return transformed


def _canonicalize_messages(raw: Any) -> List[Dict[str, Any]]:
    """Turn the TraceLoop gen_ai.prompt/ completion structure into a list.

    Expected formats:
    1. Dict indexed by string numbers: {"0": {...}, "1": {...}}
    2. Already a list of dicts
    """

    if isinstance(raw, list):
        return [_normalize(m) if isinstance(m, dict) else m for m in raw]

    if isinstance(raw, dict):
        # Determine if keys are all numeric strings
        if all(str(k).isdigit() for k in raw.keys()):
            ordered = sorted(raw.items(), key=lambda kv: int(kv[0]))
            # Convert each entry's flat keys to OpenInference style
            conv_list = []
            for idx_str, v in ordered:
                if isinstance(v, dict):
                    # Use _normalize to ensure consistent tool call handling
                    conv_list.append(_normalize(v))
                else:
                    conv_list.append(v)
            return conv_list
        else:
            # treat as single message dict
            return [_normalize(raw)]  # type: ignore[list-item]

    # Fallback: wrap whatever it is in a list
    return [_normalize(raw)]  # type: ignore[list-item]


def _map_prompt_or_completion(value: Any, dst: Dict[str, Any], *, is_prompt: bool) -> None:
    """Map gen_ai.prompt / completion to llm.input_messages / output_messages.

    The result is stored as a JSON string to keep consistency with other
    OpenInference attributes that store complex payloads as strings.
    """

    key = "llm.input_messages" if is_prompt else "llm.output_messages"
    messages = _canonicalize_messages(value)
    # OTLP exporters only accept scalar or list-of-scalar attribute values.
    # A list of dicts triggers a validation warning and the attribute is
    # dropped.  Until a richer transport is available, store the canonical
    # list as a compact JSON string so downstream systems (e.g., Arize UI)
    # can still parse it.  Remove once OpenTelemetry adds support for
    # complex attribute types.
    dst[key] = json.dumps(messages, separators=(",", ":"))

    # ------------------------------------------------------------------
    # Additionally explode individual message entries so that back-ends
    # (e.g., the Arize UI) that rely on dotted llm.input_messages.<idx>.*
    # attributes can render prompt / completion panels even when they do
    # not parse the JSON list.  Each field already carries the
    # "message." prefix (produced by _canonicalize_messages), so we just
    # prepend the list index.
    # ------------------------------------------------------------------
    base_prefix = "llm.input_messages" if is_prompt else "llm.output_messages"
    for idx, msg in enumerate(messages):
        if not isinstance(msg, dict):
            continue
        for sub_key, sub_val in msg.items():
            dotted = f"{base_prefix}.{idx}.{sub_key}"
            # Avoid overwriting if key already exists
            if dotted not in dst:
                # Special handling for message.tool_calls - expand into individual attributes
                if sub_key == "message.tool_calls" and isinstance(sub_val, list):
                    # Expand tool_calls array into individual dotted attributes
                    for tool_idx, tool_call in enumerate(sub_val):
                        if isinstance(tool_call, dict):
                            for tool_key, tool_val in tool_call.items():
                                tool_dotted = f"{base_prefix}.{idx}.{sub_key}.{tool_idx}.{tool_key}"
                                dst[tool_dotted] = tool_val
                # Serialize other complex values (like non-tool_calls arrays) as JSON strings
                elif isinstance(sub_val, (list, dict)):
                    try:
                        dst[dotted] = json.dumps(sub_val, separators=(",", ":"))
                    except Exception:
                        dst[dotted] = str(sub_val)
                else:
                    dst[dotted] = sub_val

    # ----------------------------------------------------------------------------
    # Debugging aid – when the environment variable DEBUG_OPENINF is set to a
    # truthy value we emit progress information so that users can verify what
    # was produced.  This prints *once* per mapping call.
    # ----------------------------------------------------------------------------
    if _is_debug_enabled():
        print(f"[DEBUG] Set {key} (is_prompt={is_prompt}) to: {dst[key]}", file=sys.stderr)


# ---------------------------------------------------------------------------
# MAPPING LOGIC
# ---------------------------------------------------------------------------

def _ensure_json_serialisable(value: Any) -> Any:
    """Ensure value can be JSON-serialised. Convert complex types to strings."""
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _is_debug_enabled() -> bool:
    """Return True if the environment variable DEBUG_OPENINF is set to truthy."""
    import os
    return os.getenv("DEBUG_OPENINF", "").lower() not in ("", "0", "false", "no")


def _is_bracket_conversion_disabled() -> bool:
    """Return True if the environment variable DISABLE_BRACKET_CONVERSION is set to truthy."""
    import os
    return os.getenv("DISABLE_BRACKET_CONVERSION", "").lower() not in ("", "0", "false", "no")


_DOT_NUM_RE = re.compile(r"\.([0-9]+)(\.|$)")


def _needs_bracket_conversion(key: str) -> bool:
    """Return True when the key contains .<digits>. pattern."""
    return bool(_DOT_NUM_RE.search(key))


def _dot_to_bracket(key: str) -> str:
    """Convert dot-number-dot to bracket index notation."""
    return re.sub(r"\.([0-9]+)(\.|$)", lambda m: f"[{m.group(1)}]{m.group(2)}", key)


def map_openll_to_openinference(src: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a dict of OpenLLMetry span attributes into OpenInference ones."""
    # ------------------------------------------------------------------
    # 0) Pre-processing: flatten a *single* top-level of nesting so that
    #    structures like {"gen_ai": {"completion": {...}}} become
    #    "gen_ai.completion": {...}.  We purposefully do *not* flatten deeper
    #    than one level so that the value (a dict with numeric keys, etc.) is
    #    still available intact for _map_prompt_or_completion().
    # ------------------------------------------------------------------
    
    flat_src: Dict[str, Any] = {}
    
    # Important context attributes that should be preserved as-is
    context_attributes = {
        "session.id", "user.id", "openinference.span.kind", 
        "metadata", "tag.tags", "llm.prompt_template.template",
        "llm.prompt_template.version", "llm.prompt_template.variables"
    }
    
    # Keys that should be preserved as-is and not flattened
    preserve_keys = {
        "gen_ai.prompt", "gen_ai.completion"
    }
    
    for key, value in src.items():
        if key in context_attributes:
            # Preserve context attributes directly without flattening
            flat_src[key] = value
        elif key in preserve_keys:
            # Preserve prompt/completion structures directly without flattening
            flat_src[key] = value
        elif isinstance(value, dict):
            # Flatten one level for other attributes
            for sub_key, sub_val in value.items():
                flat_src[f"{key}.{sub_key}"] = sub_val
        else:
            flat_src[key] = value

    dst: Dict[str, Any] = {}

    metadata: Dict[str, Any] = {}
    invocation_params: Dict[str, Any] = {}
    prompt_parts: Dict[int, Dict[str, Any]] = {}
    completion_parts: Dict[int, Dict[str, Any]] = {}
    tool_parts: Dict[int, Dict[str, Any]] = {}

    if _is_debug_enabled():
        print("[DEBUG] ---- MAPPING START ----", file=sys.stderr)

    # ------------------------------------------------------------------
    # Main processing loop
    # ------------------------------------------------------------------
    for key, val in flat_src.items():
        # Don't serialize prompt/completion data - it needs to stay as structured data
        if key not in ("gen_ai.prompt", "gen_ai.completion"):
            val = _ensure_json_serialisable(val)

        # 0.5) Always emit bracket-index form for keys containing .<digits>.
        #      BUT: exclude message and tool keys that need dotted format for OpenInference
        #      ALSO: exclude llm.request.functions.* and llm.request.tools.* keys since we only want llm.tools.* output
        #      ALSO: exclude gen_ai.* keys since they're intermediate data that gets converted to llm.input_messages/llm.output_messages
        #      ALSO: skip if bracket conversion is disabled (for Arize compatibility)
        if (_needs_bracket_conversion(key) and 
            not _is_bracket_conversion_disabled() and 
            not (
                key.startswith("llm.input_messages.") or 
                key.startswith("llm.output_messages.") or
                key.startswith("llm.tools.") or
                key.startswith("gen_ai.")
            )):
            bkey = _dot_to_bracket(key)
            if bkey not in dst:  # don't overwrite if already set
                # Ensure OTLP-compatible scalar / string value
                if isinstance(val, (str, int, float, bool)) or val is None:
                    dst[bkey] = val
                else:
                    try:
                        dst[bkey] = json.dumps(val, separators=(",", ":"))
                    except Exception:
                        dst[bkey] = str(val)

        # 1) Direct key remapping.
        if key in _DIRECT_MAPPING:
            target_key = _DIRECT_MAPPING[key]
            # Special case: span kind has further mapping to enum strings.
            if target_key == "openinference.span.kind":
                mapped_val = _SPAN_KIND_MAPPING.get(str(val).lower(), "UNKNOWN")
                dst[target_key] = mapped_val
            else:
                dst[target_key] = val
            continue

        # 2) Invocation parameters accumulation.
        if key in _INVOCATION_PARAMETER_KEYS or key.startswith("gen_ai.request.") or (
            key.startswith("llm.request.")
            and key != _OPENLL_TOOL_LIST_KEY
            and key != "llm.request.tools"
            and not key.startswith("llm.request.functions.")
            and not key.startswith("llm.request.tools.")
        ):
            # Remove the prefix that is not relevant for OpenInference.
            trimmed = (
                key.split(".", 2)[-1] if key.startswith("gen_ai.request.") else key.split(".", 2)[-1]
            )
            invocation_params[trimmed] = val
            continue

        # 3) Tool list special handling — map & explode.
        #    Handle both llm.request.functions and llm.request.tools keys
        if key == _OPENLL_TOOL_LIST_KEY or key == "llm.request.tools":
            _handle_tool_list(val, dst)
            continue

        # 4.0) Direct mapping when full prompt/completion dict present
        if key == "gen_ai.prompt":
            _map_prompt_or_completion(val, dst, is_prompt=True)
            continue
        if key == "gen_ai.completion":
            _map_prompt_or_completion(val, dst, is_prompt=False)
            continue

        # 4.1) Accumulate prompt/completion pieces for reconstruction.
        #       Handle dotted form (gen_ai.prompt.0.content)
        if key.startswith("gen_ai.prompt.") or key.startswith("gen_ai.completion."):
            parts = key.split(".")
            if len(parts) >= 4 and parts[2].isdigit():
                container = prompt_parts if parts[1] == "prompt" else completion_parts
                idx = int(parts[2])
                field = ".".join(parts[3:])
                container.setdefault(idx, {})[field] = val
            # Don't copy to metadata - these are processed into llm.input_messages/llm.output_messages
            continue

        # 4.2) Accumulate dotted tool schema pieces e.g. llm.request.functions.0.name
        #      Also handle llm.request.tools.* format that some instrumentations use
        if (key.startswith("llm.request.functions.") or
            key.startswith("llm.request.tools.") or key.startswith("gen_ai.request.tools.")):
            parts = key.split(".")
            if len(parts) >= 5 and parts[3].isdigit():
                idx = int(parts[3])
                field = ".".join(parts[4:])
                tool_parts.setdefault(idx, {})[field] = val
            # Remove: don't copy to metadata anymore, only process for llm.tools generation
            continue

        # 4.3) Handle pre-existing llm.input_messages/output_messages dotted attributes
        #      These are already in OpenInference format, so pass them through directly
        if (key.startswith("llm.input_messages.") or key.startswith("llm.output_messages.")):
            # Copy directly to dst - these are already in the right format
            dst[key] = val
            continue

        # 4) Anything else is copied to metadata to avoid information loss.
        #    BUT: exclude important context attributes that should stay top-level
        if key not in context_attributes:
            metadata[key] = val
        else:
            # Context attributes go directly to dst, not metadata
            dst[key] = val

    # ------------------------------------------------------------------
    # After main loop, if we collected dotted prompt/completion pieces but
    # did not get canonical lists via gen_ai.prompt / gen_ai.completion keys,
    # build them now.
    if prompt_parts and "llm.input_messages" not in dst:
        _map_prompt_or_completion(prompt_parts, dst, is_prompt=True)
    if completion_parts and "llm.output_messages" not in dst:
        _map_prompt_or_completion(completion_parts, dst, is_prompt=False)

    # Build tool list from dotted parts if no llm.tools yet
    if tool_parts and "llm.tools" not in dst:
        # Simple reconstruction: just pass the collected parts to the handler
        _handle_tool_list(list(tool_parts.values()), dst)

    if invocation_params:
        # Store as JSON string per OpenInference recommendation.
        dst["llm.invocation_parameters"] = json.dumps(invocation_params, separators=(",", ":"))

    if metadata:
        dst.setdefault("metadata", json.dumps(metadata, separators=(",", ":")))

    # ------------------------------------------------------------------
    # Post-processing defaults
    # ------------------------------------------------------------------
    # 1) If we have llm.system but no llm.provider, set provider to lowercase(system)
    if "llm.system" in dst and "llm.provider" not in dst:
        dst["llm.provider"] = str(dst["llm.system"]).lower()

    # 2) If openinference.span.kind was not set but span looks like an LLM span,
    #    default it to "LLM" so that back-ends can categorize.
    if "openinference.span.kind" not in dst:
        if any(key in dst for key in ("llm.model_name", "gen_ai.request.model")):
            dst["openinference.span.kind"] = "LLM"

    # ------------------------------------------------------------------
    # 3) Add input.value and output.value composite JSON structures
    #    (same logic as in openllmetry_conversion_simple.py)
    # ------------------------------------------------------------------
    
    # Create input.value composite structure
    prompt_content = dst.get("llm.input_messages.0.message.content")
    prompt_role = dst.get("llm.input_messages.0.message.role", "user")
    model_name = dst.get("llm.model_name") or invocation_params.get("model")
    max_tokens = invocation_params.get("max_tokens")

    if prompt_content and model_name:
        dst.setdefault("input.mime_type", "application/json")
        dst.setdefault(
            "input.value",
            json.dumps(
                {
                    "messages": [{"role": prompt_role, "content": prompt_content}],
                    "model": model_name,
                    "max_tokens": max_tokens,
                }
            ),
        )

    # Create output.value composite structure
    completion_content = dst.get("llm.output_messages.0.message.content")
    completion_role = dst.get("llm.output_messages.0.message.role", "assistant")
    finish_reason = dst.get("llm.output_messages.0.message.finish_reason", "stop")
    usage_prompt = dst.get("llm.token_count.prompt")
    usage_completion = dst.get("llm.token_count.completion")
    usage_total = dst.get("llm.token_count.total")
    resp_id = dst.get("gen_ai.response.id")

    if completion_content:
        dst.setdefault("output.mime_type", "application/json")
        dst.setdefault(
            "output.value",
            json.dumps(
                {
                    "id": resp_id,
                    "choices": [
                        {
                            "finish_reason": finish_reason,
                            "index": 0,
                            "logprobs": None,
                            "message": {
                                "content": completion_content,
                                "role": completion_role,
                                "refusal": None,
                                "annotations": [],
                            },
                        }
                    ],
                    "model": dst.get("llm.model_name"),
                    "usage": {
                        "completion_tokens": usage_completion,
                        "prompt_tokens": usage_prompt,
                        "total_tokens": usage_total,
                    },
                }
            ),
        )

    # ------------------------------------------------------------------
    # 4) Convert dot-number-dot paths → bracket-index notation for non-OpenInference keys
    #    OpenInference keys (llm.input_messages.*, llm.output_messages.*, llm.tools.*) 
    #    stay in dotted format as required by the spec.
    #    Skip bracket conversion if disabled (for Arize compatibility)
    # ------------------------------------------------------------------

    if _is_bracket_conversion_disabled():
        # When bracket conversion is disabled, return dst as-is
        return dst

    bracketised: Dict[str, Any] = {}
    for key, value in dst.items():
        # OpenInference keys stay dotted
        if (key.startswith("llm.input_messages.") or 
            key.startswith("llm.output_messages.") or
            key.startswith("llm.tools.") or
            key.startswith("gen_ai.")):
            bracketised[key] = value
        # Convert other keys to bracket notation if they have numeric indices
        elif _needs_bracket_conversion(key):
            bracket_key = _dot_to_bracket(key)
            bracketised[bracket_key] = value
        else:
            bracketised[key] = value

    return bracketised


# ---------------------------------------------------------------------------
# TOOL LIST TRANSFORMATION
# ---------------------------------------------------------------------------

def _handle_tool_list(raw_value: Any, dst: Dict[str, Any]) -> None:
    """Convert OpenLLMetry llm.request.functions → OpenInference tool attrs."""
    # Accept JSON string or Python list/dict.
    try:
        tools = json.loads(raw_value) if isinstance(raw_value, str) else raw_value
    except Exception:
        # On failure, skip processing rather than storing raw value
        return

    # Keep only the flattened dotted attributes, not the full JSON list
    # dst[_OPENINF_TOOL_LIST_KEY] = json.dumps(tools, separators=(",", ":"))  # REMOVED

    # ------------------------------------------------------------------
    # EXPLODE list so each entry is also available as dotted attributes
    # e.g. llm.tools.0.name = "get_weather", llm.tools.0.description = "..."
    # ------------------------------------------------------------------
    if isinstance(tools, list):
        for idx, tool in enumerate(tools):
            base = f"llm.tools.{idx}"

            # Emit basic tool fields as dotted attributes
            if isinstance(tool, dict):
                for k, v in tool.items():
                    key = f"{base}.{k}"
                    if isinstance(v, (str, int, float, bool)) or v is None:
                        dst.setdefault(key, v)
                    else:
                        # Complex values -> JSON encode
                        try:
                            dst.setdefault(key, json.dumps(v, separators=(",", ":")))
                        except Exception:
                            dst.setdefault(key, str(v))


# ---------------------------------------------------------------------------
# SPAN PROCESSOR CLASS
# ---------------------------------------------------------------------------

class OpenLLMetryToOpenInferenceSpanProcessor(SpanProcessor):
    """SpanProcessor that converts OpenLLMetry span attributes to OpenInference format.
    
    This processor should be added to your TracerProvider to automatically
    transform span attributes during export. It uses the comprehensive mapping
    logic from map_openll_to_openinference() to handle complex transformations
    including tool calls, message structures, and attribute formatting.
    
    Example:
        tracer_provider = register(space_id=SPACE_ID, api_key=API_KEY, project_name="my-project")
        tracer_provider.add_span_processor(OpenLLMetryToOpenInferenceSpanProcessor())
    """
    
    def __init__(self):
        """Initialize the processor."""
        super().__init__()
    
    def on_start(self, span, parent_context=None):
        """Called when a span is started. No action needed."""
        pass
    
    def on_end(self, span):
        """Called when a span ends. Transform the span attributes."""
        if not hasattr(span, '_attributes') or not span._attributes:
            return
            
        # Create a copy of the original attributes
        original_attrs = dict(span._attributes)
        
        try:
            # Apply the comprehensive mapping transformation
            transformed_attrs = map_openll_to_openinference(original_attrs)
            
            # Replace the span's attributes with the transformed ones
            span._attributes.clear()
            span._attributes.update(transformed_attrs)
            
            if _is_debug_enabled():
                print(f"[DEBUG] Transformed span '{span.name}': {len(original_attrs)} -> {len(transformed_attrs)} attributes", file=sys.stderr)
                
        except Exception as e:
            # If transformation fails, keep original attributes and log error
            if _is_debug_enabled():
                print(f"[DEBUG] Failed to transform span '{span.name}': {e}", file=sys.stderr)
            # Keep original attributes on failure
            span._attributes.clear()
            span._attributes.update(original_attrs)
    
    def shutdown(self):
        """Called when the processor is shutdown. No cleanup needed."""
        pass
    
    def force_flush(self, timeout_millis=None):
        """Called to force flush. Always return True since no buffering."""
        return True


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _load_source_attrs() -> Dict[str, Any]:
    """Load JSON dict from a file passed as first CLI arg or stdin."""
    if len(sys.argv) > 1 and sys.argv[1] != "-":
        with open(sys.argv[1], "r", encoding="utf-8") as fh:
            return json.load(fh)
    return json.load(sys.stdin)


def main() -> None:
    src_attrs = _load_source_attrs()
    dst_attrs = map_openll_to_openinference(src_attrs)
    json.dump(dst_attrs, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main() 