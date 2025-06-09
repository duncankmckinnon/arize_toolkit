import logging
import time
from pathlib import Path
from typing import Any, Dict, List

from arize_toolkit.migrations.importers.base_importer import BaseImporter

logger = logging.getLogger(__name__)


class TraceImporter(BaseImporter):
    """Importer for Phoenix traces to Arize"""

    def import_data(self, export_file: Path, project_name: str) -> Dict[str, Any]:
        """Import traces from Phoenix export to Arize"""
        logger.info(f"Importing traces from {export_file} for project {project_name}")

        try:
            traces = self._load_export_data(export_file)

            if not traces:
                return {
                    "success_count": 0,
                    "error_count": 0,
                    "skipped_count": 0,
                    "errors": ["No traces found in export file"],
                }

            return self._batch_process(traces, self._import_trace_batch)

        except Exception as e:
            logger.error(f"Failed to import traces: {e}")
            return {
                "success_count": 0,
                "error_count": len(traces) if "traces" in locals() else 1,
                "skipped_count": 0,
                "errors": [str(e)],
            }

    def _import_trace_batch(self, traces: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Import a batch of traces"""
        results = {
            "success_count": 0,
            "error_count": 0,
            "skipped_count": 0,
            "errors": [],
        }

        for trace in traces:
            try:
                # Check for duplicates
                item_hash = self._generate_item_hash(trace, ["trace_id", "project_name"])
                if self._is_duplicate(item_hash):
                    results["skipped_count"] += 1
                    continue

                # Validate required fields
                if not self._validate_required_fields(trace, ["trace_id"]):
                    results["error_count"] += 1
                    continue

                # Convert Phoenix trace to Arize format
                arize_trace = self._convert_phoenix_trace(trace)

                # Import trace to Arize
                success = self._import_arize_trace(arize_trace)

                if success:
                    results["success_count"] += 1
                    self._mark_as_imported(item_hash)

                    # Import spans if present
                    if "spans" in trace and trace["spans"]:
                        span_results = self._import_trace_spans(trace["trace_id"], trace["spans"])
                        results["success_count"] += span_results["success_count"]
                        results["error_count"] += span_results["error_count"]
                        results["errors"].extend(span_results["errors"])
                else:
                    results["error_count"] += 1

            except Exception as e:
                error_msg = f"Failed to import trace {trace.get('trace_id', 'unknown')}: {str(e)}"
                logger.error(error_msg)
                results["error_count"] += 1
                results["errors"].append(error_msg)

        return results

    def _convert_phoenix_trace(self, phoenix_trace: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Phoenix trace format to Arize format"""
        arize_trace = {
            "trace_id": phoenix_trace["trace_id"],
            "project_name": phoenix_trace.get("project_name", "imported_project"),
            "start_time": self._convert_phoenix_timestamp(phoenix_trace.get("start_time")),
            "end_time": self._convert_phoenix_timestamp(phoenix_trace.get("end_time")),
            "status_code": phoenix_trace.get("status_code", "OK"),
            "metadata": {},
        }

        # Add Phoenix-specific metadata
        if "project_id" in phoenix_trace:
            arize_trace["metadata"]["phoenix_project_id"] = phoenix_trace["project_id"]

        if "duration_ms" in phoenix_trace:
            arize_trace["metadata"]["duration_ms"] = phoenix_trace["duration_ms"]

        # Handle attributes
        if "attributes" in phoenix_trace:
            arize_trace["attributes"] = self._sanitize_for_arize(phoenix_trace["attributes"])

        # Handle tags
        if "tags" in phoenix_trace:
            arize_trace["tags"] = phoenix_trace["tags"]

        return arize_trace

    def _import_arize_trace(self, trace: Dict[str, Any]) -> bool:
        """Import trace to Arize"""
        try:
            # Use Arize client to import trace
            self._retry_operation(self._call_arize_import_trace_api, trace)

            logger.debug(f"Successfully imported trace: {trace['trace_id']}")
            return True

        except Exception as e:
            logger.error(f"Failed to import trace {trace['trace_id']}: {e}")
            return False

    def _call_arize_import_trace_api(self, trace: Dict[str, Any]) -> bool:
        """Call Arize API to import trace"""
        # This would integrate with the actual Arize tracing API
        logger.debug(f"Importing trace to Arize: {trace['trace_id']}")

        # In practice, this would use OpenTelemetry or Arize's tracing SDK
        # For example:
        # from arize.otel import register
        # tracer = register(space_id=self.arize_space_id, api_key=self.arize_api_key)

        # Simulate API call
        time.sleep(0.1)
        return True

    def _import_trace_spans(self, trace_id: str, spans: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Import trace spans to Arize"""
        results = {"success_count": 0, "error_count": 0, "errors": []}

        for span in spans:
            try:
                # Convert Phoenix span to Arize format
                arize_span = self._convert_phoenix_span(span, trace_id)

                # Import span to Arize
                success = self._import_arize_span(arize_span)

                if success:
                    results["success_count"] += 1
                else:
                    results["error_count"] += 1

            except Exception as e:
                error_msg = f"Failed to import span: {str(e)}"
                logger.error(error_msg)
                results["error_count"] += 1
                results["errors"].append(error_msg)

        return results

    def _convert_phoenix_span(self, phoenix_span: Dict[str, Any], trace_id: str) -> Dict[str, Any]:
        """Convert Phoenix span to Arize format"""
        arize_span = {
            "span_id": phoenix_span.get("span_id"),
            "trace_id": trace_id,
            "parent_span_id": phoenix_span.get("parent_span_id"),
            "name": phoenix_span.get("name", "unknown_span"),
            "kind": phoenix_span.get("span_kind", "INTERNAL"),
            "start_time": self._convert_phoenix_timestamp(phoenix_span.get("start_time")),
            "end_time": self._convert_phoenix_timestamp(phoenix_span.get("end_time")),
            "status_code": phoenix_span.get("status_code", "OK"),
            "metadata": {},
        }

        # Handle span attributes
        if "attributes" in phoenix_span:
            arize_span["attributes"] = self._sanitize_for_arize(phoenix_span["attributes"])

        # Handle LLM-specific attributes
        llm_fields = ["input_messages", "output_messages", "model_name", "provider"]
        for field in llm_fields:
            if field in phoenix_span:
                arize_span["metadata"][f"llm_{field}"] = phoenix_span[field]

        # Handle retrieval-specific attributes
        retrieval_fields = ["input_query", "retrieved_documents", "embedding_model"]
        for field in retrieval_fields:
            if field in phoenix_span:
                arize_span["metadata"][f"retrieval_{field}"] = phoenix_span[field]

        return arize_span

    def _import_arize_span(self, span: Dict[str, Any]) -> bool:
        """Import span to Arize"""
        try:
            logger.debug(f"Importing span to Arize: {span['span_id']}")

            # This would use OpenTelemetry span creation
            # Simulate API call
            time.sleep(0.02)
            return True

        except Exception as e:
            logger.error(f"Failed to import span {span['span_id']}: {e}")
            return False
