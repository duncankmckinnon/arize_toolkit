import hashlib
import json
import logging
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from arize_toolkit.extensions.migrations.models import MigrationConfig

logger = logging.getLogger(__name__)


class BaseImporter(ABC):
    """Base class for Arize data importers"""

    def __init__(
        self,
        arize_api_key: str,
        arize_space_id: str,
        developer_key: Optional[str] = None,
        config: Optional[MigrationConfig] = None,
    ):
        self.arize_api_key = arize_api_key
        self.arize_space_id = arize_space_id
        self.developer_key = developer_key
        self.config = config or MigrationConfig()

        # Track imported items to avoid duplicates
        self._imported_items: Set[str] = set()
        self.max_retries = self.config.max_retries
        self.retry_delay = self.config.retry_delay

    @abstractmethod
    def import_data(self, export_file: Path, project_name: str) -> Dict[str, Any]:
        """Import data from exported file to Arize"""
        pass

    def _load_export_data(self, export_file: Path) -> List[Dict[str, Any]]:
        """Load data from export file"""
        try:
            if not export_file.exists():
                raise FileNotFoundError(f"Export file not found: {export_file}")

            with open(export_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, dict):
                # Handle single item
                return [data]
            elif isinstance(data, list):
                return data
            else:
                raise ValueError(f"Unexpected data format in {export_file}")

        except Exception as e:
            logger.error(f"Failed to load export data from {export_file}: {e}")
            raise

    def _generate_item_hash(self, item: Dict[str, Any], unique_fields: List[str]) -> str:
        """Generate hash for item to detect duplicates"""
        hash_data = {}
        for field in unique_fields:
            if field in item:
                hash_data[field] = item[field]

        hash_string = json.dumps(hash_data, sort_keys=True)
        return hashlib.md5(hash_string.encode()).hexdigest()

    def _is_duplicate(self, item_hash: str) -> bool:
        """Check if item is a duplicate"""
        if self.config.skip_duplicates:
            return item_hash in self._imported_items
        return False

    def _mark_as_imported(self, item_hash: str) -> None:
        """Mark item as imported"""
        self._imported_items.add(item_hash)

    def _batch_process(
        self,
        items: List[Dict[str, Any]],
        process_func,
        batch_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Process items in batches with progress tracking"""
        batch_size = batch_size or self.config.batch_size
        total_items = len(items)

        results = {
            "success_count": 0,
            "error_count": 0,
            "skipped_count": 0,
            "errors": [],
        }

        for i in range(0, total_items, batch_size):
            batch = items[i : i + batch_size]  # noqa: E203
            batch_start = i + 1
            batch_end = min(i + batch_size, total_items)

            logger.info(f"Processing batch {batch_start}-{batch_end} of {total_items}")

            try:
                batch_result = process_func(batch)

                results["success_count"] += batch_result.get("success_count", 0)
                results["error_count"] += batch_result.get("error_count", 0)
                results["skipped_count"] += batch_result.get("skipped_count", 0)
                results["errors"].extend(batch_result.get("errors", []))

            except Exception as e:
                error_msg = f"Batch {batch_start}-{batch_end} failed: {str(e)}"
                logger.error(error_msg)
                results["error_count"] += len(batch)
                results["errors"].append(error_msg)

            # Brief pause between batches to avoid overwhelming the API
            if i + batch_size < total_items:
                time.sleep(0.1)

        return results

    def _retry_operation(self, operation, *args, **kwargs):
        """Execute operation with retry logic"""
        for attempt in range(self.max_retries):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise

                wait_time = self.retry_delay * (2**attempt)
                logger.warning(f"Operation failed (attempt {attempt + 1}), retrying in {wait_time}s: {e}")
                time.sleep(wait_time)

        raise Exception("Max retries exceeded")

    def _convert_phoenix_timestamp(self, timestamp_str: str) -> Optional[int]:
        """Convert Phoenix timestamp to Arize format (nanoseconds since epoch)"""
        try:
            if not timestamp_str:
                return None

            # Parse ISO format timestamp
            from datetime import datetime

            dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))

            # Convert to nanoseconds since epoch
            return int(dt.timestamp() * 1_000_000_000)

        except Exception as e:
            logger.warning(f"Failed to convert timestamp {timestamp_str}: {e}")
            return None

    def _validate_required_fields(self, item: Dict[str, Any], required_fields: List[str]) -> bool:
        """Validate that item has all required fields"""
        missing_fields = [field for field in required_fields if field not in item or item[field] is None]

        if missing_fields:
            logger.warning(f"Item missing required fields: {missing_fields}")
            return False

        return True

    def _sanitize_for_arize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize data for Arize import"""
        sanitized = {}

        for key, value in data.items():
            # Convert None values to empty strings or appropriate defaults
            if value is None:
                sanitized[key] = ""
            elif isinstance(value, (list, dict)):
                # Convert complex types to JSON strings
                sanitized[key] = json.dumps(value)
            else:
                sanitized[key] = str(value)

        return sanitized
