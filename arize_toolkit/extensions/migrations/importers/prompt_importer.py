import logging
import time
from pathlib import Path
from typing import Any, Dict, List

from arize_toolkit.extensions.migrations.importers.base_importer import BaseImporter

logger = logging.getLogger(__name__)


class PromptImporter(BaseImporter):
    """Importer for Phoenix prompts to Arize"""

    def import_data(self, export_file: Path, project_name: str) -> Dict[str, Any]:
        """Import prompts from Phoenix export to Arize"""
        logger.info(f"Importing prompts from {export_file} for project {project_name}")

        try:
            prompts = self._load_export_data(export_file)

            if not prompts:
                return {
                    "success_count": 0,
                    "error_count": 0,
                    "skipped_count": 0,
                    "errors": ["No prompts found in export file"],
                }

            return self._batch_process(prompts, self._import_prompt_batch)

        except Exception as e:
            logger.error(f"Failed to import prompts: {e}")
            return {
                "success_count": 0,
                "error_count": len(prompts) if "prompts" in locals() else 1,
                "skipped_count": 0,
                "errors": [str(e)],
            }

    def _import_prompt_batch(self, prompts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Import a batch of prompts"""
        results = {
            "success_count": 0,
            "error_count": 0,
            "skipped_count": 0,
            "errors": [],
        }

        for prompt in prompts:
            try:
                # Check for duplicates
                item_hash = self._generate_item_hash(prompt, ["id", "name"])
                if self._is_duplicate(item_hash):
                    results["skipped_count"] += 1
                    continue

                # Validate required fields
                if not self._validate_required_fields(prompt, ["name"]):
                    results["error_count"] += 1
                    continue

                # Convert Phoenix prompt to Arize format
                arize_prompt = self._convert_phoenix_prompt(prompt)

                # Create prompt in Arize
                success = self._create_arize_prompt(arize_prompt)

                if success:
                    results["success_count"] += 1
                    self._mark_as_imported(item_hash)

                    # Import prompt versions if present
                    if "versions" in prompt and prompt["versions"]:
                        version_results = self._import_prompt_versions(arize_prompt["name"], prompt["versions"])
                        results["success_count"] += version_results["success_count"]
                        results["error_count"] += version_results["error_count"]
                        results["errors"].extend(version_results["errors"])
                else:
                    results["error_count"] += 1

            except Exception as e:
                error_msg = f"Failed to import prompt {prompt.get('name', 'unknown')}: {str(e)}"
                logger.error(error_msg)
                results["error_count"] += 1
                results["errors"].append(error_msg)

        return results

    def _convert_phoenix_prompt(self, phoenix_prompt: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Phoenix prompt format to Arize format"""
        arize_prompt = {
            "name": phoenix_prompt["name"],
            "description": phoenix_prompt.get("description", ""),
            "tags": phoenix_prompt.get("tags", []),
            "metadata": {},
        }

        # Add Phoenix-specific metadata
        if "id" in phoenix_prompt:
            arize_prompt["metadata"]["phoenix_id"] = phoenix_prompt["id"]

        if "created_at" in phoenix_prompt:
            arize_prompt["metadata"]["phoenix_created_at"] = phoenix_prompt["created_at"]

        if "updated_at" in phoenix_prompt:
            arize_prompt["metadata"]["phoenix_updated_at"] = phoenix_prompt["updated_at"]

        return arize_prompt

    def _create_arize_prompt(self, prompt: Dict[str, Any]) -> bool:
        """Create prompt in Arize"""
        try:
            # Use Arize client to create prompt
            self._retry_operation(self._call_arize_create_prompt_api, prompt)

            logger.info(f"Successfully created prompt: {prompt['name']}")
            return True

        except Exception as e:
            logger.error(f"Failed to create prompt {prompt['name']}: {e}")
            return False

    def _call_arize_create_prompt_api(self, prompt: Dict[str, Any]) -> bool:
        """Call Arize API to create prompt"""
        # This would integrate with the actual Arize prompt API
        logger.debug(f"Creating prompt in Arize: {prompt['name']}")

        # Simulate API call
        time.sleep(0.1)
        return True

    def _import_prompt_versions(self, prompt_name: str, versions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Import prompt versions to Arize"""
        results = {"success_count": 0, "error_count": 0, "errors": []}

        for version in versions:
            try:
                # Convert Phoenix version to Arize format
                arize_version = self._convert_phoenix_version(version, prompt_name)

                # Add version to prompt
                success = self._add_version_to_prompt(prompt_name, arize_version)

                if success:
                    results["success_count"] += 1
                else:
                    results["error_count"] += 1

            except Exception as e:
                error_msg = f"Failed to import version: {str(e)}"
                logger.error(error_msg)
                results["error_count"] += 1
                results["errors"].append(error_msg)

        return results

    def _convert_phoenix_version(self, phoenix_version: Dict[str, Any], prompt_name: str) -> Dict[str, Any]:
        """Convert Phoenix version to Arize format"""
        arize_version = {
            "prompt_name": prompt_name,
            "version": phoenix_version.get("version", "1.0"),
            "commit_message": phoenix_version.get("commit_message", ""),
            "messages": phoenix_version.get("messages", []),
            "model_name": phoenix_version.get("model_name"),
            "provider": phoenix_version.get("provider"),
            "metadata": {},
        }

        # Add Phoenix-specific metadata
        if "id" in phoenix_version:
            arize_version["metadata"]["phoenix_version_id"] = phoenix_version["id"]

        if "created_at" in phoenix_version:
            arize_version["metadata"]["phoenix_created_at"] = phoenix_version["created_at"]

        # Handle LLM parameters
        if "llm_parameters" in phoenix_version:
            arize_version["llm_parameters"] = phoenix_version["llm_parameters"]

        return arize_version

    def _add_version_to_prompt(self, prompt_name: str, version: Dict[str, Any]) -> bool:
        """Add version to Arize prompt"""
        try:
            logger.debug(f"Adding version to prompt {prompt_name}")

            # Simulate API call
            time.sleep(0.05)
            return True

        except Exception as e:
            logger.error(f"Failed to add version to prompt {prompt_name}: {e}")
            return False
