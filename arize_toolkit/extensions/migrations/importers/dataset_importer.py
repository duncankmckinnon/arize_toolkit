import logging
import time
from pathlib import Path
from typing import Any, Dict, List

from arize_toolkit.extensions.migrations.importers.base_importer import BaseImporter

logger = logging.getLogger(__name__)


class DatasetImporter(BaseImporter):
    """Importer for Phoenix datasets to Arize"""

    def import_data(self, export_file: Path, project_name: str) -> Dict[str, Any]:
        """Import datasets from Phoenix export to Arize"""
        logger.info(f"Importing datasets from {export_file} for project {project_name}")

        try:
            datasets = self._load_export_data(export_file)

            if not datasets:
                return {
                    "success_count": 0,
                    "error_count": 0,
                    "skipped_count": 0,
                    "errors": ["No datasets found in export file"],
                }

            return self._batch_process(datasets, self._import_dataset_batch)

        except Exception as e:
            logger.error(f"Failed to import datasets: {e}")
            return {
                "success_count": 0,
                "error_count": len(datasets) if "datasets" in locals() else 1,
                "skipped_count": 0,
                "errors": [str(e)],
            }

    def _import_dataset_batch(self, datasets: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Import a batch of datasets"""
        results = {
            "success_count": 0,
            "error_count": 0,
            "skipped_count": 0,
            "errors": [],
        }

        for dataset in datasets:
            try:
                # Check for duplicates
                item_hash = self._generate_item_hash(dataset, ["id", "name"])
                if self._is_duplicate(item_hash):
                    results["skipped_count"] += 1
                    continue

                # Validate required fields
                if not self._validate_required_fields(dataset, ["name"]):
                    results["error_count"] += 1
                    continue

                # Convert Phoenix dataset to Arize format
                arize_dataset = self._convert_phoenix_dataset(dataset)

                # Create dataset in Arize
                success = self._create_arize_dataset(arize_dataset)

                if success:
                    results["success_count"] += 1
                    self._mark_as_imported(item_hash)

                    # Import dataset examples if present
                    if "examples" in dataset and dataset["examples"]:
                        example_results = self._import_dataset_examples(arize_dataset["name"], dataset["examples"])
                        results["success_count"] += example_results["success_count"]
                        results["error_count"] += example_results["error_count"]
                        results["errors"].extend(example_results["errors"])
                else:
                    results["error_count"] += 1

            except Exception as e:
                error_msg = f"Failed to import dataset {dataset.get('name', 'unknown')}: {str(e)}"
                logger.error(error_msg)
                results["error_count"] += 1
                results["errors"].append(error_msg)

        return results

    def _convert_phoenix_dataset(self, phoenix_dataset: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Phoenix dataset format to Arize format"""
        arize_dataset = {
            "name": phoenix_dataset["name"],
            "description": phoenix_dataset.get("description", ""),
            "version": phoenix_dataset.get("version", "1.0"),
            "metadata": {},
        }

        # Add Phoenix-specific metadata
        if "id" in phoenix_dataset:
            arize_dataset["metadata"]["phoenix_id"] = phoenix_dataset["id"]

        if "created_at" in phoenix_dataset:
            arize_dataset["metadata"]["phoenix_created_at"] = phoenix_dataset["created_at"]

        if "updated_at" in phoenix_dataset:
            arize_dataset["metadata"]["phoenix_updated_at"] = phoenix_dataset["updated_at"]

        # Add any custom metadata
        if "metadata" in phoenix_dataset:
            arize_dataset["metadata"].update(phoenix_dataset["metadata"])

        return arize_dataset

    def _create_arize_dataset(self, dataset: Dict[str, Any]) -> bool:
        """Create dataset in Arize"""
        try:
            # Use Arize client to create dataset
            # This would use the actual Arize dataset creation API
            # For now, we'll simulate the creation

            self._retry_operation(self._call_arize_create_dataset_api, dataset)

            logger.info(f"Successfully created dataset: {dataset['name']}")
            return True

        except Exception as e:
            logger.error(f"Failed to create dataset {dataset['name']}: {e}")
            return False

    def _call_arize_create_dataset_api(self, dataset: Dict[str, Any]) -> bool:
        """Call Arize API to create dataset"""
        # This would integrate with the actual Arize dataset API
        # Using the arize_client to create the dataset

        # Placeholder for actual Arize dataset creation
        # In practice, this would use the Arize SDK or API
        logger.debug(f"Creating dataset in Arize: {dataset['name']}")

        # Simulate API call
        time.sleep(0.1)  # Simulate API latency
        return True

    def _import_dataset_examples(self, dataset_name: str, examples: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Import dataset examples to Arize"""
        results = {"success_count": 0, "error_count": 0, "errors": []}

        for example in examples:
            try:
                # Convert Phoenix example to Arize format
                arize_example = self._convert_phoenix_example(example, dataset_name)

                # Add example to dataset
                success = self._add_example_to_dataset(dataset_name, arize_example)

                if success:
                    results["success_count"] += 1
                else:
                    results["error_count"] += 1

            except Exception as e:
                error_msg = f"Failed to import example: {str(e)}"
                logger.error(error_msg)
                results["error_count"] += 1
                results["errors"].append(error_msg)

        return results

    def _convert_phoenix_example(self, phoenix_example: Dict[str, Any], dataset_name: str) -> Dict[str, Any]:
        """Convert Phoenix example to Arize format"""
        arize_example = {
            "dataset_name": dataset_name,
            "input": phoenix_example.get("input", {}),
            "output": phoenix_example.get("output", {}),
            "metadata": {},
        }

        # Add Phoenix-specific metadata
        if "id" in phoenix_example:
            arize_example["metadata"]["phoenix_example_id"] = phoenix_example["id"]

        if "created_at" in phoenix_example:
            arize_example["metadata"]["phoenix_created_at"] = phoenix_example["created_at"]

        # Handle additional Phoenix fields
        for field in ["tags", "labels", "annotations"]:
            if field in phoenix_example:
                arize_example["metadata"][f"phoenix_{field}"] = phoenix_example[field]

        return arize_example

    def _add_example_to_dataset(self, dataset_name: str, example: Dict[str, Any]) -> bool:
        """Add example to Arize dataset"""
        try:
            # This would use the Arize dataset example API
            logger.debug(f"Adding example to dataset {dataset_name}")

            # Simulate API call
            time.sleep(0.05)
            return True

        except Exception as e:
            logger.error(f"Failed to add example to dataset {dataset_name}: {e}")
            return False
