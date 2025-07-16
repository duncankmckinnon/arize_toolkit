import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from arize_toolkit.extensions.migrations.exporters.base_exporter import BaseExporter
from arize_toolkit.extensions.migrations.models import MigrationFilters

logger = logging.getLogger(__name__)


class EvaluationExporter(BaseExporter):
    """Exporter for Phoenix evaluations"""

    def export_data(
        self,
        project_name: str,
        output_dir: Path,
        filters: Optional[MigrationFilters] = None,
    ) -> Optional[Path]:
        """Export evaluations from Phoenix"""
        logger.info(f"Exporting evaluations for project: {project_name}")

        try:
            evaluations = self._fetch_evaluations(project_name, filters)

            if not evaluations:
                logger.warning(f"No evaluations found for project: {project_name}")
                return None

            # Save to file
            output_file = output_dir / f"{project_name}_evaluations.json"
            return self._save_data_to_file(evaluations, output_file)

        except Exception as e:
            logger.error(f"Failed to export evaluations: {e}")
            raise

    def estimate_record_count(self, project_name: str) -> int:
        """Estimate number of evaluations"""
        try:
            response = self._make_request_with_retry("GET", f"/v1/projects/{project_name}/evaluations/count")
            return response.json().get("count", 0)
        except Exception:
            return 0

    def _fetch_evaluations(self, project_name: str, filters: Optional[MigrationFilters]) -> List[Dict[str, Any]]:
        """Fetch evaluations from Phoenix API"""
        if filters and not filters.include_evaluations:
            return []

        evaluations = []
        page = 0
        page_size = 100

        # Build query parameters for filtering
        params = {"page_size": page_size}
        if filters and filters.date_range:
            if filters.date_range.start:
                params["start_time"] = filters.date_range.start  # type: ignore
            if filters.date_range.end:
                params["end_time"] = filters.date_range.end  # type: ignore

        while True:
            try:
                params["page"] = page
                response = self._make_request_with_retry("GET", f"/v1/projects/{project_name}/evaluations", params=params)

                data = response.json()
                page_evaluations = data.get("evaluations", [])

                if not page_evaluations:
                    break

                evaluations.extend(page_evaluations)
                page += 1

                # Apply max records limit
                if filters and filters.max_records_per_type:
                    if len(evaluations) >= filters.max_records_per_type:
                        evaluations = evaluations[: filters.max_records_per_type]
                        break

            except Exception as e:
                logger.error(f"Error fetching evaluations page {page}: {e}")
                break

        return evaluations
