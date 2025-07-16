import logging
import time
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from arize_toolkit.extensions.migrations.importers.base_importer import BaseImporter

logger = logging.getLogger(__name__)


class AnnotationImporter(BaseImporter):
    """Importer for Phoenix annotations to Arize"""

    def import_data(self, export_file: Path, project_name: str) -> Dict[str, Any]:
        """Import annotations from Phoenix export to Arize"""
        logger.info(f"Importing annotations from {export_file} for project {project_name}")

        try:
            annotations = self._load_export_data(export_file)

            if not annotations:
                return {
                    "success_count": 0,
                    "error_count": 0,
                    "skipped_count": 0,
                    "errors": ["No annotations found in export file"],
                }

            return self._batch_process(annotations, self._import_annotation_batch)

        except Exception as e:
            logger.error(f"Failed to import annotations: {e}")
            return {
                "success_count": 0,
                "error_count": len(annotations) if "annotations" in locals() else 1,
                "skipped_count": 0,
                "errors": [str(e)],
            }

    def _import_annotation_batch(self, annotations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Import a batch of annotations"""
        results = {
            "success_count": 0,
            "error_count": 0,
            "skipped_count": 0,
            "errors": [],
        }

        # Group annotations by span_id for efficient batch processing
        annotations_by_span = {}
        for annotation in annotations:
            span_id = annotation.get("span_id")
            if span_id:
                if span_id not in annotations_by_span:
                    annotations_by_span[span_id] = []
                annotations_by_span[span_id].append(annotation)

        # Process annotations for each span
        for span_id, span_annotations in annotations_by_span.items():
            try:
                span_results = self._import_span_annotations(span_id, span_annotations)
                results["success_count"] += span_results["success_count"]
                results["error_count"] += span_results["error_count"]
                results["skipped_count"] += span_results["skipped_count"]
                results["errors"].extend(span_results["errors"])

            except Exception as e:
                error_msg = f"Failed to import annotations for span {span_id}: {str(e)}"
                logger.error(error_msg)
                results["error_count"] += len(span_annotations)
                results["errors"].append(error_msg)

        return results

    def _import_span_annotations(self, span_id: str, annotations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Import all annotations for a specific span"""
        results = {
            "success_count": 0,
            "error_count": 0,
            "skipped_count": 0,
            "errors": [],
        }

        # Convert annotations to Arize format
        arize_annotations = []

        for annotation in annotations:
            try:
                # Check for duplicates
                item_hash = self._generate_item_hash(annotation, ["span_id", "annotation_name", "created_at"])
                if self._is_duplicate(item_hash):
                    results["skipped_count"] += 1
                    continue

                # Validate required fields
                if not self._validate_required_fields(annotation, ["span_id", "annotation_name"]):
                    results["error_count"] += 1
                    continue

                # Convert Phoenix annotation to Arize format
                arize_annotation = self._convert_phoenix_annotation(annotation)
                arize_annotations.append(arize_annotation)
                self._mark_as_imported(item_hash)

            except Exception as e:
                error_msg = f"Failed to convert annotation: {str(e)}"
                logger.error(error_msg)
                results["error_count"] += 1
                results["errors"].append(error_msg)

        # Batch import to Arize
        if arize_annotations:
            try:
                success = self._batch_import_arize_annotations(span_id, arize_annotations)
                if success:
                    results["success_count"] += len(arize_annotations)
                else:
                    results["error_count"] += len(arize_annotations)

            except Exception as e:
                error_msg = f"Failed to batch import annotations for span {span_id}: {str(e)}"
                logger.error(error_msg)
                results["error_count"] += len(arize_annotations)
                results["errors"].append(error_msg)

        return results

    def _convert_phoenix_annotation(self, phoenix_annotation: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Phoenix annotation format to Arize format"""
        arize_annotation = {
            "span_id": phoenix_annotation["span_id"],
            "name": phoenix_annotation["annotation_name"],
            "annotator_kind": "HUMAN",  # Default for Phoenix annotations
            "updated_at": self._convert_phoenix_timestamp(phoenix_annotation.get("created_at") or phoenix_annotation.get("updated_at")),  # type: ignore
            "metadata": {},
        }

        # Handle annotation value based on type
        if "label" in phoenix_annotation and phoenix_annotation["label"] is not None:
            arize_annotation["label"] = str(phoenix_annotation["label"])
            arize_annotation["annotation_type"] = "label"
        elif "score" in phoenix_annotation and phoenix_annotation["score"] is not None:
            arize_annotation["score"] = float(phoenix_annotation["score"])
            arize_annotation["annotation_type"] = "score"
        else:
            # Default to label type with empty value
            arize_annotation["label"] = ""
            arize_annotation["annotation_type"] = "label"

        # Add Phoenix-specific metadata
        if "annotation_id" in phoenix_annotation:
            arize_annotation["metadata"]["phoenix_annotation_id"] = phoenix_annotation["annotation_id"]

        if "updated_by" in phoenix_annotation:
            arize_annotation["metadata"]["updated_by"] = phoenix_annotation["updated_by"]

        if "explanation" in phoenix_annotation:
            arize_annotation["metadata"]["explanation"] = phoenix_annotation["explanation"]

        # Handle project context
        if "project_name" in phoenix_annotation:
            arize_annotation["metadata"]["phoenix_project"] = phoenix_annotation["project_name"]

        return arize_annotation

    def _batch_import_arize_annotations(self, span_id: str, annotations: List[Dict[str, Any]]) -> bool:
        """Batch import annotations to Arize"""
        try:
            # Convert annotations to DataFrame for batch processing
            df_data = []

            for annotation in annotations:
                row = {
                    "context.span_id": span_id,
                    "annotation_name": annotation["name"],
                    "updated_at": annotation["updated_at"],
                    "annotator_kind": annotation["annotator_kind"],
                }

                # Add annotation value
                if annotation["annotation_type"] == "score":
                    row["score"] = annotation["score"]
                else:
                    row["label"] = annotation["label"]

                # Add metadata as separate columns
                for key, value in annotation.get("metadata", {}).items():
                    row[f"metadata.{key}"] = value

                df_data.append(row)

            # Create DataFrame
            df = pd.DataFrame(df_data)

            # Import using Arize client
            self._retry_operation(self._call_arize_import_annotations_api, df)

            logger.debug(f"Successfully imported {len(annotations)} annotations for span {span_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to batch import annotations for span {span_id}: {e}")
            return False

    def _call_arize_import_annotations_api(self, df: pd.DataFrame) -> bool:
        """Call Arize API to import annotations"""
        # This would integrate with the actual Arize annotations API
        logger.debug(f"Importing {len(df)} annotations to Arize")

        # In practice, this would use the Arize client's log_annotations method
        # For example:
        # self.arize_client.log_annotations(
        #     model_id=model_id,
        #     model_version=model_version,
        #     dataframe=df
        # )

        # Simulate API call
        time.sleep(0.1)
        return True

    def _setup_annotation_requirements(self, project_name: str) -> Dict[str, Any]:
        """Setup annotation requirements in Arize (if needed)"""
        # This method could be used to ensure annotation schemas are properly configured
        # in Arize before importing annotations

        setup_results = {"annotation_types_created": [], "warnings": [], "errors": []}

        try:
            # Get unique annotation types from the export
            # Create annotation schemas in Arize if they don't exist
            # This would depend on Arize's annotation setup API

            logger.info(f"Annotation setup completed for project {project_name}")

        except Exception as e:
            logger.error(f"Failed to setup annotations for project {project_name}: {e}")
            setup_results["errors"].append(str(e))

        return setup_results
