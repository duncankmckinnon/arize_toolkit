import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from arize_toolkit.migrations.exporters.base_exporter import BaseExporter
from arize_toolkit.migrations.models import MigrationFilters

logger = logging.getLogger(__name__)


class AnnotationExporter(BaseExporter):
    """Exporter for Phoenix annotations"""

    def export_data(
        self,
        project_name: str,
        output_dir: Path,
        filters: Optional[MigrationFilters] = None,
    ) -> Optional[Path]:
        """Export annotations from Phoenix"""
        logger.info(f"Exporting annotations for project: {project_name}")

        try:
            annotations = self._fetch_annotations(project_name, filters)

            if not annotations:
                logger.warning(f"No annotations found for project: {project_name}")
                return None

            # Save to file
            output_file = output_dir / f"{project_name}_annotations.json"
            return self._save_data_to_file(annotations, output_file)

        except Exception as e:
            logger.error(f"Failed to export annotations: {e}")
            raise

    def estimate_record_count(self, project_name: str) -> int:
        """Estimate number of annotations"""
        try:
            response = self._make_request_with_retry("GET", f"/v1/projects/{project_name}/annotations/count")
            return response.json().get("count", 0)
        except Exception:
            return 0

    def _fetch_annotations(self, project_name: str, filters: Optional[MigrationFilters]) -> List[Dict[str, Any]]:
        """Fetch annotations from Phoenix API"""
        annotations = []
        page = 0
        page_size = 100

        # Build query parameters for filtering
        params = {"page_size": page_size}
        if filters:
            if filters.annotation_types:
                params["annotation_types"] = ",".join(filters.annotation_types)
            if filters.date_range:
                if filters.date_range.start:
                    params["start_time"] = filters.date_range.start
                if filters.date_range.end:
                    params["end_time"] = filters.date_range.end

        while True:
            try:
                params["page"] = page
                response = self._make_request_with_retry("GET", f"/v1/projects/{project_name}/annotations", params=params)

                data = response.json()
                page_annotations = data.get("annotations", [])

                if not page_annotations:
                    break

                annotations.extend(page_annotations)
                page += 1

                # Apply max records limit
                if filters and filters.max_records_per_type:
                    if len(annotations) >= filters.max_records_per_type:
                        annotations = annotations[: filters.max_records_per_type]
                        break

            except Exception as e:
                logger.error(f"Error fetching annotations page {page}: {e}")
                break

        return annotations
