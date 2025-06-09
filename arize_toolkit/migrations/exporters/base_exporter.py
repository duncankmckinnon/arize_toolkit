import json
import logging
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

from arize_toolkit.migrations.models import ExportFormat, MigrationFilters

logger = logging.getLogger(__name__)


class BaseExporter(ABC):
    """Base class for Phoenix data exporters"""

    def __init__(self, phoenix_client):
        self.phoenix_client = phoenix_client
        self.max_retries = 3
        self.retry_delay = 1.0

    @abstractmethod
    def export_data(
        self,
        project_name: str,
        output_dir: Path,
        filters: Optional[MigrationFilters] = None,
    ) -> Optional[Path]:
        """Export data from Phoenix"""
        pass

    @abstractmethod
    def estimate_record_count(self, project_name: str) -> int:
        """Estimate number of records for this data type"""
        pass

    def _make_request_with_retry(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Make HTTP request with retry logic"""
        for attempt in range(self.max_retries):
            try:
                response = self.phoenix_client.request(method, url, **kwargs)
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError as e:
                if attempt == self.max_retries - 1:
                    raise
                logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                time.sleep(self.retry_delay * (2**attempt))
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                logger.warning(f"Request error (attempt {attempt + 1}): {e}")
                time.sleep(self.retry_delay)

        raise Exception("Max retries exceeded")

    def _save_data_to_file(
        self,
        data: List[Dict[str, Any]],
        output_file: Path,
        format: ExportFormat = ExportFormat.json,
    ) -> Path:
        """Save data to file in specified format"""
        output_file.parent.mkdir(parents=True, exist_ok=True)

        if format == ExportFormat.json:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
        elif format == ExportFormat.csv:
            import pandas as pd

            df = pd.DataFrame(data)
            df.to_csv(output_file, index=False)
        elif format == ExportFormat.parquet:
            import pandas as pd

            df = pd.DataFrame(data)
            df.to_parquet(output_file, index=False)
        else:
            raise ValueError(f"Unsupported export format: {format}")

        logger.info(f"Saved {len(data)} records to {output_file}")
        return output_file

    def _apply_filters(self, data: List[Dict[str, Any]], filters: Optional[MigrationFilters]) -> List[Dict[str, Any]]:
        """Apply filters to exported data"""
        if not filters:
            return data

        filtered_data = data

        # Apply date range filter
        if filters.date_range:
            # Implementation depends on data structure
            # This is a placeholder for date filtering logic
            pass

        # Apply max records limit
        if filters.max_records_per_type:
            filtered_data = filtered_data[: filters.max_records_per_type]

        return filtered_data
