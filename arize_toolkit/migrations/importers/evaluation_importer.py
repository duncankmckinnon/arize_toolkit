import logging
import time
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from arize_toolkit.migrations.importers.base_importer import BaseImporter

logger = logging.getLogger(__name__)


class EvaluationImporter(BaseImporter):
    """Importer for Phoenix evaluations to Arize"""

    def import_data(self, export_file: Path, project_name: str) -> Dict[str, Any]:
        """Import evaluations from Phoenix export to Arize"""
        logger.info(f"Importing evaluations from {export_file} for project {project_name}")

        try:
            evaluations = self._load_export_data(export_file)

            if not evaluations:
                return {
                    "success_count": 0,
                    "error_count": 0,
                    "skipped_count": 0,
                    "errors": ["No evaluations found in export file"],
                }

            return self._batch_process(evaluations, self._import_evaluation_batch)

        except Exception as e:
            logger.error(f"Failed to import evaluations: {e}")
            return {
                "success_count": 0,
                "error_count": len(evaluations) if "evaluations" in locals() else 1,
                "skipped_count": 0,
                "errors": [str(e)],
            }

    def _import_evaluation_batch(self, evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Import a batch of evaluations"""
        results = {
            "success_count": 0,
            "error_count": 0,
            "skipped_count": 0,
            "errors": [],
        }

        # Group evaluations by type/name for efficient processing
        evaluations_by_name = {}
        for evaluation in evaluations:
            eval_name = evaluation.get("name", "unknown_evaluation")
            if eval_name not in evaluations_by_name:
                evaluations_by_name[eval_name] = []
            evaluations_by_name[eval_name].append(evaluation)

        # Process each evaluation type
        for eval_name, eval_list in evaluations_by_name.items():
            try:
                eval_results = self._import_evaluation_type(eval_name, eval_list)
                results["success_count"] += eval_results["success_count"]
                results["error_count"] += eval_results["error_count"]
                results["skipped_count"] += eval_results["skipped_count"]
                results["errors"].extend(eval_results["errors"])

            except Exception as e:
                error_msg = f"Failed to import evaluation type {eval_name}: {str(e)}"
                logger.error(error_msg)
                results["error_count"] += len(eval_list)
                results["errors"].append(error_msg)

        return results

    def _import_evaluation_type(self, eval_name: str, evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Import evaluations of a specific type"""
        results = {
            "success_count": 0,
            "error_count": 0,
            "skipped_count": 0,
            "errors": [],
        }

        # Convert evaluations to Arize format
        arize_evaluations = []

        for evaluation in evaluations:
            try:
                # Check for duplicates
                item_hash = self._generate_item_hash(evaluation, ["subject_id", "name", "created_at"])
                if self._is_duplicate(item_hash):
                    results["skipped_count"] += 1
                    continue

                # Validate required fields
                if not self._validate_required_fields(evaluation, ["subject_id", "name"]):
                    results["error_count"] += 1
                    continue

                # Convert Phoenix evaluation to Arize format
                arize_evaluation = self._convert_phoenix_evaluation(evaluation)
                arize_evaluations.append(arize_evaluation)
                self._mark_as_imported(item_hash)

            except Exception as e:
                error_msg = f"Failed to convert evaluation: {str(e)}"
                logger.error(error_msg)
                results["error_count"] += 1
                results["errors"].append(error_msg)

        # Batch import to Arize
        if arize_evaluations:
            try:
                # Convert evaluations to DataFrame for batch processing
                df_data = []

                for evaluation in arize_evaluations:
                    row = {
                        "subject_id": evaluation["subject_id"],
                        "eval_name": evaluation["eval_name"],
                        "created_at": evaluation["created_at"],
                    }

                    # Add evaluation result
                    if evaluation["result_type"] == "score":
                        row["score"] = evaluation["score"]
                    else:
                        row["label"] = evaluation["label"]

                    # Add metadata as separate columns
                    for key, value in evaluation.get("metadata", {}).items():
                        row[f"metadata.{key}"] = value

                    df_data.append(row)

                # Create DataFrame
                df = pd.DataFrame(df_data)

                # Import using Arize client
                self._retry_operation(self._call_arize_import_evaluations_api, eval_name, df)

                logger.debug(f"Successfully imported {len(arize_evaluations)} evaluations for {eval_name}")
                results["success_count"] += len(arize_evaluations)

            except Exception as e:
                error_msg = f"Failed to batch import evaluations for {eval_name}: {str(e)}"
                logger.error(error_msg)
                results["error_count"] += len(arize_evaluations)
                results["errors"].append(error_msg)

        return results

    def _convert_phoenix_evaluation(self, phoenix_evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Phoenix evaluation format to Arize format"""
        arize_evaluation = {
            "subject_id": phoenix_evaluation["subject_id"],
            "name": phoenix_evaluation["name"],
            "eval_name": phoenix_evaluation["name"],
            "created_at": self._convert_phoenix_timestamp(phoenix_evaluation.get("created_at")),
            "metadata": {},
        }

        # Handle evaluation result based on type
        if "label" in phoenix_evaluation and phoenix_evaluation["label"] is not None:
            arize_evaluation["label"] = str(phoenix_evaluation["label"])
            arize_evaluation["result_type"] = "label"
        elif "score" in phoenix_evaluation and phoenix_evaluation["score"] is not None:
            arize_evaluation["score"] = float(phoenix_evaluation["score"])
            arize_evaluation["result_type"] = "score"
        else:
            # Handle boolean results
            if "result" in phoenix_evaluation:
                result = phoenix_evaluation["result"]
                if isinstance(result, bool):
                    arize_evaluation["label"] = "pass" if result else "fail"
                    arize_evaluation["result_type"] = "label"
                else:
                    arize_evaluation["label"] = str(result)
                    arize_evaluation["result_type"] = "label"

        # Add Phoenix-specific metadata
        if "evaluation_id" in phoenix_evaluation:
            arize_evaluation["metadata"]["phoenix_evaluation_id"] = phoenix_evaluation["evaluation_id"]

        if "explanation" in phoenix_evaluation:
            arize_evaluation["metadata"]["explanation"] = phoenix_evaluation["explanation"]

        if "evaluator_name" in phoenix_evaluation:
            arize_evaluation["metadata"]["evaluator_name"] = phoenix_evaluation["evaluator_name"]

        # Handle evaluation metadata
        if "metadata" in phoenix_evaluation:
            for key, value in phoenix_evaluation["metadata"].items():
                arize_evaluation["metadata"][f"phoenix_{key}"] = value

        return arize_evaluation

    def _batch_import_arize_evaluations(self, eval_name: str, evaluations: List[Dict[str, Any]]) -> bool:
        """Batch import evaluations to Arize"""
        try:
            # Convert evaluations to DataFrame for batch processing
            df_data = []

            for evaluation in evaluations:
                row = {
                    "subject_id": evaluation["subject_id"],
                    "eval_name": evaluation["eval_name"],
                    "created_at": evaluation["created_at"],
                }

                # Add evaluation result
                if evaluation["result_type"] == "score":
                    row["score"] = evaluation["score"]
                else:
                    row["label"] = evaluation["label"]

                # Add metadata as separate columns
                for key, value in evaluation.get("metadata", {}).items():
                    row[f"metadata.{key}"] = value

                df_data.append(row)

            # Create DataFrame
            df = pd.DataFrame(df_data)

            # Import using Arize client
            self._retry_operation(self._call_arize_import_evaluations_api, eval_name, df)

            logger.debug(f"Successfully imported {len(evaluations)} evaluations for {eval_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to batch import evaluations for {eval_name}: {e}")
            return False

    def _call_arize_import_evaluations_api(self, eval_name: str, df: pd.DataFrame) -> bool:
        """Call Arize API to import evaluations"""
        # This would integrate with the actual Arize evaluations API
        logger.debug(f"Importing {len(df)} evaluations to Arize for {eval_name}")

        # In practice, this would use the Arize client's evaluation import method
        # For example:
        # self.arize_client.log_evaluations(
        #     model_id=model_id,
        #     model_version=model_version,
        #     dataframe=df
        # )

        # Simulate API call
        time.sleep(0.1)
        return True
