import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from arize_toolkit.migrations.exporters.base_exporter import BaseExporter
from arize_toolkit.migrations.models import MigrationFilters

logger = logging.getLogger(__name__)


class TraceExporter(BaseExporter):
    """Exporter for Phoenix traces"""

    def export_data(
        self,
        project_name: str,
        output_dir: Path,
        filters: Optional[MigrationFilters] = None,
    ) -> Optional[Path]:
        """Export traces from Phoenix"""
        logger.info(f"Exporting traces for project: {project_name}")

        try:
            traces = self._fetch_traces(project_name, filters)

            if not traces:
                logger.warning(f"No traces found for project: {project_name}")
                return None

            # Save to file
            output_file = output_dir / f"{project_name}_traces.json"
            return self._save_data_to_file(traces, output_file)

        except Exception as e:
            logger.error(f"Failed to export traces: {e}")
            raise

    def estimate_record_count(self, project_name: str) -> int:
        """Estimate number of traces"""
        try:
            response = self._make_request_with_retry("GET", f"/v1/projects/{project_name}/traces/count")
            return response.json().get("count", 0)
        except Exception:
            return 0

    def _fetch_traces(self, project_name: str, filters: Optional[MigrationFilters]) -> List[Dict[str, Any]]:
        """Fetch traces from Phoenix API"""
        traces = []
        page = 0
        page_size = 100

        # Build query parameters for filtering
        params = {"page_size": page_size}
        if filters:
            if filters.date_range:
                if filters.date_range.start:
                    params["start_time"] = filters.date_range.start
                if filters.date_range.end:
                    params["end_time"] = filters.date_range.end
            if filters.trace_min_duration:
                params["min_duration"] = filters.trace_min_duration

        while True:
            try:
                params["page"] = page
                response = self._make_request_with_retry("GET", f"/v1/projects/{project_name}/traces", params=params)

                data = response.json()
                page_traces = data.get("traces", [])

                if not page_traces:
                    break

                # Fetch detailed trace information including spans
                for trace in page_traces:
                    detailed_trace = self._fetch_trace_details(project_name, trace["trace_id"])
                    if detailed_trace:
                        traces.append(detailed_trace)

                page += 1

                # Apply max records limit
                if filters and filters.max_records_per_type:
                    if len(traces) >= filters.max_records_per_type:
                        traces = traces[: filters.max_records_per_type]
                        break

            except Exception as e:
                logger.error(f"Error fetching traces page {page}: {e}")
                break

        return traces

    def _fetch_trace_details(self, project_name: str, trace_id: str) -> Optional[Dict[str, Any]]:
        """Fetch detailed trace information including spans"""
        try:
            # Get trace metadata
            response = self._make_request_with_retry("GET", f"/v1/projects/{project_name}/traces/{trace_id}")
            trace = response.json()

            # Get trace spans
            spans_response = self._make_request_with_retry("GET", f"/v1/projects/{project_name}/traces/{trace_id}/spans")
            trace["spans"] = spans_response.json().get("spans", [])

            return trace

        except Exception as e:
            logger.error(f"Error fetching trace details for {trace_id}: {e}")
            return None
