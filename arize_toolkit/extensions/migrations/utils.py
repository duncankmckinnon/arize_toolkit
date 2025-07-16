import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union

import httpx

logger = logging.getLogger(__name__)


class PhoenixClient:
    """Client for interacting with Phoenix API"""

    def __init__(self, endpoint: str):
        self.endpoint = endpoint.rstrip("/")
        self.client = httpx.Client(base_url=self.endpoint, timeout=30.0)

    def request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Make HTTP request to Phoenix API"""
        return self.client.request(method, url, **kwargs)

    def project_exists(self, project_name: str) -> bool:
        """Check if a project exists in Phoenix"""
        try:
            response = self.request("GET", f"/v1/projects/{project_name}")
            return response.status_code == 200
        except Exception:
            return False

    def get_project_info(self, project_name: str) -> Optional[Dict[str, Any]]:
        """Get project information"""
        try:
            response = self.request("GET", f"/v1/projects/{project_name}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get project info: {e}")
            return None

    def list_projects(self) -> list:
        """List all projects"""
        try:
            response = self.request("GET", "/v1/projects")
            response.raise_for_status()
            return response.json().get("projects", [])
        except Exception as e:
            logger.error(f"Failed to list projects: {e}")
            return []

    def close(self):
        """Close the HTTP client"""
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def create_results_directory(base_dir: str, project_name: str) -> Path:
    """Create results directory for migration output"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = Path(base_dir) / "phoenix_export" / project_name / timestamp
    results_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectories for different data types
    for subdir in ["datasets", "prompts", "traces", "annotations", "evaluations"]:
        (results_dir / subdir).mkdir(exist_ok=True)

    logger.info(f"Created results directory: {results_dir}")
    return results_dir


def save_migration_results(migration_job, results_dir: Path) -> None:
    """Save migration job results to file"""
    try:
        results_file = results_dir / "migration_results.json"

        # Convert migration job to dict for serialization
        job_dict = migration_job.dict()

        # Convert datetime objects to strings
        if job_dict.get("created_at"):
            job_dict["created_at"] = job_dict["created_at"].isoformat()
        if job_dict.get("completed_at"):
            job_dict["completed_at"] = job_dict["completed_at"].isoformat()

        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(job_dict, f, indent=2, default=str)

        logger.info(f"Saved migration results to: {results_file}")

    except Exception as e:
        logger.error(f"Failed to save migration results: {e}")


def load_migration_results(results_file: Path) -> Optional[Dict[str, Any]]:
    """Load migration results from file"""
    try:
        if not results_file.exists():
            return None

        with open(results_file, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception as e:
        logger.error(f"Failed to load migration results: {e}")
        return None


def validate_phoenix_connection(endpoint: str) -> tuple[bool, str]:
    """Validate connection to Phoenix instance"""
    try:
        with PhoenixClient(endpoint) as client:
            response = client.request("GET", "/arize_phoenix_version")
            response.raise_for_status()
            version = response.json().get("version", "unknown")
            return True, f"Connected to Phoenix v{version}"

    except httpx.ConnectError:
        return False, f"Cannot connect to Phoenix at {endpoint}"
    except httpx.HTTPStatusError as e:
        return False, f"Phoenix returned error: {e.response.status_code}"
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def validate_arize_connection(api_key: str, space_id: str) -> tuple[bool, str]:
    """Validate connection to Arize"""
    try:
        # This would use the actual Arize client to validate connection
        # For now, just check if credentials are provided
        if not api_key or not space_id:
            return False, "Missing Arize API key or space ID"

        # TODO: Add actual Arize connection validation
        return True, "Arize connection validated"

    except Exception as e:
        return False, f"Arize connection error: {str(e)}"


def estimate_migration_time(record_counts: Dict[str, int], batch_size: int = 1000) -> float:
    """Estimate migration time in minutes"""
    total_records = sum(record_counts.values())

    # Rough estimates based on data type processing time
    time_per_record = {
        "datasets": 0.1,  # 0.1 seconds per dataset record
        "prompts": 0.05,  # 0.05 seconds per prompt
        "traces": 0.2,  # 0.2 seconds per trace (includes spans)
        "annotations": 0.02,  # 0.02 seconds per annotation
        "evaluations": 0.1,  # 0.1 seconds per evaluation
    }

    total_time = 0
    for data_type, count in record_counts.items():
        processing_time = time_per_record.get(data_type, 0.1)
        total_time += count * processing_time

    # Add overhead for API calls and batch processing
    batch_overhead = (total_records / batch_size) * 2  # 2 seconds per batch
    total_time += batch_overhead

    return total_time / 60  # Convert to minutes


def format_file_size(size_bytes: Union[float, int]) -> str:
    """Format file size in human readable format"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system usage"""
    import re

    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', "_", filename)
    # Limit length
    return sanitized[:200]


def create_migration_summary(migration_job) -> Dict[str, Any]:
    """Create a summary of migration results"""
    total_success = sum(result.success_count for result in migration_job.results)
    total_errors = sum(result.error_count for result in migration_job.results)
    total_skipped = sum(result.skipped_count for result in migration_job.results)

    duration = None
    if migration_job.completed_at and migration_job.created_at:
        duration = (migration_job.completed_at - migration_job.created_at).total_seconds()

    return {
        "job_id": migration_job.id,
        "project_name": migration_job.project_name,
        "status": migration_job.status.value,
        "data_types": [dt.value for dt in migration_job.data_types],
        "total_records_processed": total_success + total_errors + total_skipped,
        "successful_records": total_success,
        "failed_records": total_errors,
        "skipped_records": total_skipped,
        "success_rate": total_success / max(1, total_success + total_errors) * 100,
        "duration_minutes": duration / 60 if duration else None,
        "results_by_type": [
            {
                "data_type": result.data_type.value,
                "success_count": result.success_count,
                "error_count": result.error_count,
                "skipped_count": result.skipped_count,
                "duration_seconds": result.duration_seconds,
            }
            for result in migration_job.results
        ],
    }


def setup_logging(log_level: str = "INFO", log_file: Optional[Path] = None) -> None:
    """Setup logging for migration operations"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            *([] if log_file is None else [logging.FileHandler(log_file)]),
        ],
    )


# Environment variable helpers
def get_env_or_prompt(env_var: str, prompt_text: str, required: bool = True) -> Optional[str]:
    """Get environment variable or prompt user for input"""
    import os

    value = os.getenv(env_var)
    if value:
        return value

    if required:
        value = input(f"{prompt_text}: ").strip()
        if not value:
            raise ValueError(f"{env_var} is required")
        return value

    return input(f"{prompt_text} (optional): ").strip() or None


def load_config_from_env() -> Dict[str, Any]:
    """Load migration configuration from environment variables"""
    import os

    return {
        "phoenix_endpoint": os.getenv("PHOENIX_ENDPOINT"),
        "arize_api_key": os.getenv("ARIZE_API_KEY"),
        "arize_space_id": os.getenv("ARIZE_SPACE_ID"),
        "developer_key": os.getenv("ARIZE_DEVELOPER_KEY"),
        "batch_size": int(os.getenv("MIGRATION_BATCH_SIZE", "1000")),
        "max_retries": int(os.getenv("MIGRATION_MAX_RETRIES", "3")),
        "output_directory": os.getenv("MIGRATION_OUTPUT_DIR", "./migration_results"),
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
    }
