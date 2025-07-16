import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from arize_toolkit.extensions.migrations.exporters.base_exporter import BaseExporter
from arize_toolkit.extensions.migrations.models import MigrationFilters

logger = logging.getLogger(__name__)


class DatasetExporter(BaseExporter):
    """Exporter for Phoenix datasets"""

    def export_data(
        self,
        project_name: str,
        output_dir: Path,
        filters: Optional[MigrationFilters] = None,
    ) -> Optional[Path]:
        """Export datasets from Phoenix"""
        logger.info(f"Exporting datasets for project: {project_name}")

        try:
            # Get datasets from Phoenix API
            datasets = self._fetch_datasets(project_name)

            if not datasets:
                logger.warning(f"No datasets found for project: {project_name}")
                return None

            # Apply filters
            datasets = self._apply_filters(datasets, filters)

            # Save to file
            output_file = output_dir / f"{project_name}_datasets.json"
            return self._save_data_to_file(datasets, output_file)

        except Exception as e:
            logger.error(f"Failed to export datasets: {e}")
            raise

    def estimate_record_count(self, project_name: str) -> int:
        """Estimate number of datasets"""
        try:
            response = self._make_request_with_retry("GET", f"/v1/projects/{project_name}/datasets/count")
            return response.json().get("count", 0)
        except Exception:
            return 0

    def _fetch_datasets(self, project_name: str) -> List[Dict[str, Any]]:
        """Fetch datasets from Phoenix API"""
        datasets = []
        page = 0
        page_size = 100

        while True:
            try:
                response = self._make_request_with_retry(
                    "GET",
                    f"/v1/projects/{project_name}/datasets",
                    params={"page": page, "page_size": page_size},
                )

                data = response.json()
                page_datasets = data.get("datasets", [])

                if not page_datasets:
                    break

                # Fetch detailed dataset information
                for dataset in page_datasets:
                    detailed_dataset = self._fetch_dataset_details(project_name, dataset["id"])
                    if detailed_dataset:
                        datasets.append(detailed_dataset)

                page += 1

            except Exception as e:
                logger.error(f"Error fetching datasets page {page}: {e}")
                break

        return datasets

    def _fetch_dataset_details(self, project_name: str, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Fetch detailed dataset information including examples"""
        try:
            # Get dataset metadata
            response = self._make_request_with_retry("GET", f"/v1/projects/{project_name}/datasets/{dataset_id}")
            dataset = response.json()

            # Get dataset examples
            examples_response = self._make_request_with_retry("GET", f"/v1/projects/{project_name}/datasets/{dataset_id}/examples")
            dataset["examples"] = examples_response.json().get("examples", [])

            # Get dataset experiments if available
            try:
                experiments_response = self._make_request_with_retry(
                    "GET",
                    f"/v1/projects/{project_name}/datasets/{dataset_id}/experiments",
                )
                dataset["experiments"] = experiments_response.json().get("experiments", [])
            except Exception:
                dataset["experiments"] = []

            return dataset

        except Exception as e:
            logger.error(f"Error fetching dataset details for {dataset_id}: {e}")
            return None
