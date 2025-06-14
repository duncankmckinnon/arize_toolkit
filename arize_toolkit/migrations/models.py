# arize_toolkit/migrations/models.py
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from arize_toolkit.types import InputValidationEnum


class DataType(InputValidationEnum):
    """Supported data types for Phoenix migration"""

    datasets = "datasets", "Datasets", "DATASETS"
    prompts = "prompts", "Prompts", "PROMPTS"
    traces = "traces", "Traces", "TRACES"
    annotations = "annotations", "Annotations", "ANNOTATIONS"
    evaluations = "evaluations", "Evaluations", "EVALUATIONS"


class MigrationStatus(InputValidationEnum):
    """Status of migration jobs"""

    pending = "pending", "Pending", "PENDING"
    running = "running", "Running", "RUNNING"
    completed = "completed", "Completed", "COMPLETED"
    failed = "failed", "Failed", "FAILED"
    partial = "partial", "Partial", "PARTIAL"


class ExportFormat(InputValidationEnum):
    """Export formats for Phoenix data"""

    json = "json", "JSON", "json_format"
    parquet = "parquet", "Parquet", "PARQUET"
    csv = "csv", "CSV", "csv_format"


class MigrationResult(BaseModel):
    """Result of migrating a specific data type"""

    data_type: DataType = Field(description="Type of data migrated")
    success_count: int = Field(description="Successfully migrated records")
    error_count: int = Field(description="Failed migration records")
    skipped_count: int = Field(default=0, description="Skipped records (duplicates)")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    export_file: Optional[str] = Field(default=None, description="Exported data file path")
    duration_seconds: Optional[float] = Field(default=None, description="Migration duration")


class MigrationJob(BaseModel):
    """Represents a Phoenix to Arize migration job"""

    id: str = Field(description="Unique migration job identifier")
    phoenix_endpoint: str = Field(description="Phoenix server endpoint")
    project_name: str = Field(description="Phoenix project name")
    arize_space_id: str = Field(description="Target Arize space ID")
    data_types: List[DataType] = Field(description="Data types being migrated")
    status: MigrationStatus = Field(description="Current migration status")
    created_at: datetime = Field(description="Migration start time")
    completed_at: Optional[datetime] = Field(default=None, description="Migration completion time")
    total_records: int = Field(default=0, description="Total records to migrate")
    processed_records: int = Field(default=0, description="Records processed so far")
    failed_records: int = Field(default=0, description="Records that failed migration")
    results: List[MigrationResult] = Field(default_factory=list, description="Results by data type")
    results_path: Optional[str] = Field(default=None, description="Path to detailed results")
    config: Dict[str, Any] = Field(default_factory=dict, description="Migration configuration")


class DateRange(BaseModel):
    """Date range for filtering migration data"""

    start: Optional[str] = Field(default=None, description="Start date (ISO format)")
    end: Optional[str] = Field(default=None, description="End date (ISO format)")


class MigrationFilters(BaseModel):
    """Filters for selective data migration"""

    date_range: Optional[DateRange] = Field(default=None, description="Date range filter")
    annotation_types: Optional[List[str]] = Field(default=None, description="Specific annotation types")
    trace_min_duration: Optional[float] = Field(default=None, description="Minimum trace duration (ms)")
    dataset_min_size: Optional[int] = Field(default=None, description="Minimum dataset size")
    include_evaluations: bool = Field(default=True, description="Include evaluation data")
    max_records_per_type: Optional[int] = Field(default=None, description="Limit records per data type")


class MigrationConfig(BaseModel):
    """Configuration for Phoenix migration"""

    batch_size: int = Field(default=1000, description="Batch size for processing")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    retry_delay: float = Field(default=1.0, description="Delay between retries (seconds)")
    export_format: ExportFormat = Field(default=ExportFormat.json, description="Export file format")
    output_directory: str = Field(default="./migration_results", description="Output directory")
    preserve_timestamps: bool = Field(default=True, description="Preserve original timestamps")
    validate_before_import: bool = Field(default=True, description="Validate data before import")
    skip_duplicates: bool = Field(default=True, description="Skip duplicate records")


class MigrationValidationReport(BaseModel):
    """Report on migration feasibility"""

    is_feasible: bool = Field(description="Whether migration is feasible")
    project_exists: bool = Field(description="Whether Phoenix project exists")
    estimated_records: Dict[str, int] = Field(default_factory=dict, description="Estimated records by type")
    estimated_duration: Optional[float] = Field(default=None, description="Estimated duration (minutes)")
    warnings: List[str] = Field(default_factory=list, description="Migration warnings")
    blocking_issues: List[str] = Field(default_factory=list, description="Issues preventing migration")
    recommendations: List[str] = Field(default_factory=list, description="Migration recommendations")


class TransformationRule(BaseModel):
    """Rule for transforming data during migration"""

    source_field: str = Field(description="Source field name")
    target_field: str = Field(description="Target field name")
    transformation_type: str = Field(description="Type of transformation")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Transformation parameters")


class TransformationConfig(BaseModel):
    """Configuration for data transformations"""

    dataset_transformations: List[TransformationRule] = Field(default_factory=list)
    prompt_transformations: List[TransformationRule] = Field(default_factory=list)
    trace_transformations: List[TransformationRule] = Field(default_factory=list)
    annotation_transformations: List[TransformationRule] = Field(default_factory=list)
    global_transformations: List[TransformationRule] = Field(default_factory=list)


class MigrationPipelineConfig(BaseModel):
    """Configuration for reusable migration pipeline"""

    name: str = Field(description="Pipeline name")
    description: Optional[str] = Field(default=None, description="Pipeline description")
    source_projects: List[str] = Field(description="Phoenix projects to migrate")
    data_types: List[DataType] = Field(description="Data types to include")
    filters: Optional[MigrationFilters] = Field(default=None, description="Migration filters")
    transformations: Optional[TransformationConfig] = Field(default=None, description="Data transformations")
    schedule: Optional[str] = Field(default=None, description="Cron schedule for automated runs")
    config: MigrationConfig = Field(default_factory=MigrationConfig, description="Migration configuration")


class MigrationPipeline(BaseModel):
    """Represents a reusable migration pipeline"""

    id: str = Field(description="Pipeline identifier")
    config: MigrationPipelineConfig = Field(description="Pipeline configuration")
    created_at: datetime = Field(description="Pipeline creation time")
    last_run: Optional[datetime] = Field(default=None, description="Last execution time")
    run_count: int = Field(default=0, description="Number of times executed")
    success_rate: float = Field(default=0.0, description="Success rate (0.0-1.0)")
    is_active: bool = Field(default=True, description="Whether pipeline is active")
