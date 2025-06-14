import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from arize_toolkit.migrations.exporters.base_exporter import BaseExporter
from arize_toolkit.migrations.models import MigrationFilters

logger = logging.getLogger(__name__)


class PromptExporter(BaseExporter):
    """Exporter for Phoenix prompts"""

    def export_data(
        self,
        project_name: str,
        output_dir: Path,
        filters: Optional[MigrationFilters] = None,
    ) -> Optional[Path]:
        """Export prompts from Phoenix"""
        logger.info(f"Exporting prompts for project: {project_name}")

        try:
            prompts = self._fetch_prompts(project_name)

            if not prompts:
                logger.warning(f"No prompts found for project: {project_name}")
                return None

            # Apply filters
            prompts = self._apply_filters(prompts, filters)

            # Save to file
            output_file = output_dir / f"{project_name}_prompts.json"
            return self._save_data_to_file(prompts, output_file)

        except Exception as e:
            logger.error(f"Failed to export prompts: {e}")
            raise

    def estimate_record_count(self, project_name: str) -> int:
        """Estimate number of prompts"""
        try:
            response = self._make_request_with_retry("GET", f"/v1/projects/{project_name}/prompts/count")
            return response.json().get("count", 0)
        except Exception:
            return 0

    def _fetch_prompts(self, project_name: str) -> List[Dict[str, Any]]:
        """Fetch prompts from Phoenix API"""
        prompts = []
        page = 0
        page_size = 100

        while True:
            try:
                response = self._make_request_with_retry(
                    "GET",
                    f"/v1/projects/{project_name}/prompts",
                    params={"page": page, "page_size": page_size},
                )

                data = response.json()
                page_prompts = data.get("prompts", [])

                if not page_prompts:
                    break

                # Fetch detailed prompt information including versions
                for prompt in page_prompts:
                    detailed_prompt = self._fetch_prompt_details(project_name, prompt["id"])
                    if detailed_prompt:
                        prompts.append(detailed_prompt)

                page += 1

            except Exception as e:
                logger.error(f"Error fetching prompts page {page}: {e}")
                break

        return prompts

    def _fetch_prompt_details(self, project_name: str, prompt_id: str) -> Optional[Dict[str, Any]]:
        """Fetch detailed prompt information including versions"""
        try:
            # Get prompt metadata
            response = self._make_request_with_retry("GET", f"/v1/projects/{project_name}/prompts/{prompt_id}")
            prompt = response.json()

            # Get prompt versions
            versions_response = self._make_request_with_retry("GET", f"/v1/projects/{project_name}/prompts/{prompt_id}/versions")
            prompt["versions"] = versions_response.json().get("versions", [])

            return prompt

        except Exception as e:
            logger.error(f"Error fetching prompt details for {prompt_id}: {e}")
            return None
