# arize_toolkit/extensions/migrations/migrator.py
import logging
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from arize_toolkit.extensions.migrations.exporters import AnnotationExporter, DatasetExporter, EvaluationExporter, PromptExporter, TraceExporter
from arize_toolkit.extensions.migrations.importers import AnnotationImporter, DatasetImporter, EvaluationImporter, PromptImporter, TraceImporter
from arize_toolkit.extensions.migrations.models import DataType, MigrationConfig, MigrationFilters, MigrationJob, MigrationResult, MigrationStatus, MigrationValidationReport
from arize_toolkit.extensions.migrations.utils import PhoenixClient, create_results_directory, save_migration_results

logger = logging.getLogger(__name__)


class PhoenixMigrator:
    """Main class for Phoenix to Arize data migration"""

    def __init__(
        self,
        phoenix_endpoint: str,
        arize_api_key: str,
        arize_space_id: str,
        developer_key: Optional[str] = None,
        config: Optional[MigrationConfig] = None,
    ):
        """
        Initialize Phoenix migrator

        Args:
            phoenix_endpoint: Phoenix server endpoint URL
            arize_api_key: Arize API key
            arize_space_id: Arize space ID
            developer_key: Optional Arize developer key
            config: Migration configuration
        """
        self.phoenix_endpoint = phoenix_endpoint.rstrip("/")
        self.arize_api_key = arize_api_key
        self.arize_space_id = arize_space_id
        self.developer_key = developer_key
        self.config = config or MigrationConfig()

        # Initialize clients
        self.phoenix_client = PhoenixClient(phoenix_endpoint)

        # Initialize exporters
        self.exporters = {
            DataType.datasets: DatasetExporter(self.phoenix_client),
            DataType.prompts: PromptExporter(self.phoenix_client),
            DataType.traces: TraceExporter(self.phoenix_client),
            DataType.annotations: AnnotationExporter(self.phoenix_client),
            DataType.evaluations: EvaluationExporter(self.phoenix_client),
        }

        # Initialize importers
        self.importers = {
            DataType.datasets: DatasetImporter(arize_api_key, arize_space_id, developer_key),
            DataType.prompts: PromptImporter(arize_api_key, arize_space_id, developer_key),
            DataType.traces: TraceImporter(arize_api_key, arize_space_id, developer_key),
            DataType.annotations: AnnotationImporter(arize_api_key, arize_space_id, developer_key),
            DataType.evaluations: EvaluationImporter(arize_api_key, arize_space_id, developer_key),
        }

        # Track active migration jobs
        self._active_jobs: Dict[str, MigrationJob] = {}

    def validate_migration_feasibility(self, project_name: str, data_types: Optional[List[DataType]] = None) -> MigrationValidationReport:
        """
        Validate if migration is feasible before starting

        Args:
            project_name: Phoenix project name
            data_types: Data types to validate (default: all)

        Returns:
            Validation report with feasibility assessment
        """
        logger.info(f"Validating migration feasibility for project: {project_name}")

        data_types = data_types or list(DataType)
        warnings = []
        blocking_issues = []
        recommendations = []
        estimated_records = {}

        # Check if Phoenix project exists
        try:
            project_exists = self.phoenix_client.project_exists(project_name)
            if not project_exists:
                blocking_issues.append(f"Project '{project_name}' does not exist in Phoenix")
        except Exception as e:
            blocking_issues.append(f"Cannot connect to Phoenix: {str(e)}")
            project_exists = False

        # Estimate record counts for each data type
        if project_exists:
            for data_type in data_types:
                try:
                    exporter = self.exporters[data_type]
                    count = exporter.estimate_record_count(project_name)
                    estimated_records[data_type.value] = count

                    if count > 10000:
                        warnings.append(f"Large {data_type.value} dataset ({count} records) - consider batch processing")
                    elif count == 0:
                        warnings.append(f"No {data_type.value} found in project")

                except Exception as e:
                    warnings.append(f"Could not estimate {data_type.value} count: {str(e)}")

        # Calculate estimated duration (rough estimate)
        total_records = sum(estimated_records.values())
        estimated_duration = total_records / 1000 * 2  # ~2 minutes per 1000 records

        # Generate recommendations
        if total_records > 50000:
            recommendations.append("Consider using smaller batch sizes for large datasets")
            recommendations.append("Run migration during off-peak hours")

        if any(count > 0 for count in estimated_records.values()):
            recommendations.append("Test migration with a subset of data first")

        return MigrationValidationReport(
            is_feasible=len(blocking_issues) == 0,
            project_exists=project_exists,
            estimated_records=estimated_records,
            estimated_duration=estimated_duration,
            warnings=warnings,
            blocking_issues=blocking_issues,
            recommendations=recommendations,
        )

    def migrate_project(
        self,
        project_name: str,
        data_types: Optional[List[DataType]] = None,
        filters: Optional[MigrationFilters] = None,
    ) -> MigrationJob:
        """
        Migrate a complete Phoenix project to Arize

        Args:
            project_name: Phoenix project name
            data_types: Data types to migrate (default: all)
            filters: Optional filters for selective migration

        Returns:
            Migration job instance
        """
        data_types = data_types or list(DataType)
        job_id = str(uuid.uuid4())

        # Create migration job
        job = MigrationJob(
            id=job_id,
            phoenix_endpoint=self.phoenix_endpoint,
            project_name=project_name,
            arize_space_id=self.arize_space_id,
            data_types=data_types,
            status=MigrationStatus.pending,
            created_at=datetime.now(),
            config={
                "batch_size": self.config.batch_size,
                "filters": filters.dict() if filters else None,
            },
        )

        self._active_jobs[job_id] = job

        # Start migration in background
        self._run_migration_async(job, filters)

        return job

    def _run_migration_async(self, job: MigrationJob, filters: Optional[MigrationFilters]) -> None:
        """Run migration asynchronously"""
        try:
            job.status = MigrationStatus.running
            results_dir = create_results_directory(self.config.output_directory, job.project_name)
            job.results_path = str(results_dir)

            # Run migration for each data type
            for data_type in job.data_types:
                try:
                    result = self._migrate_data_type(job.project_name, data_type, filters, results_dir)
                    job.results.append(result)
                    job.processed_records += result.success_count
                    job.failed_records += result.error_count

                except Exception as e:
                    error_result = MigrationResult(
                        data_type=data_type,
                        success_count=0,
                        error_count=1,
                        errors=[f"Migration failed: {str(e)}"],
                    )
                    job.results.append(error_result)
                    job.failed_records += 1
                    logger.error(f"Failed to migrate {data_type.value}: {e}")

            # Update job status
            if job.failed_records == 0:
                job.status = MigrationStatus.completed
            elif job.processed_records > 0:
                job.status = MigrationStatus.partial
            else:
                job.status = MigrationStatus.failed

            job.completed_at = datetime.now()

            # Save final results
            save_migration_results(job, results_dir)

        except Exception as e:
            job.status = MigrationStatus.failed
            job.completed_at = datetime.now()
            logger.error(f"Migration job {job.id} failed: {e}")

    def _migrate_data_type(
        self,
        project_name: str,
        data_type: DataType,
        filters: Optional[MigrationFilters],
        results_dir: Path,
    ) -> MigrationResult:
        """Migrate a specific data type"""
        logger.info(f"Starting migration of {data_type.value} for project {project_name}")
        start_time = time.time()

        try:
            # Export data from Phoenix
            exporter = self.exporters[data_type]
            export_file = exporter.export_data(project_name, results_dir, filters)

            if not export_file or not export_file.exists():
                return MigrationResult(
                    data_type=data_type,
                    success_count=0,
                    error_count=0,
                    errors=["No data found to export"],
                )

            # Import data to Arize
            importer = self.importers[data_type]
            import_result = importer.import_data(export_file, project_name)

            duration = time.time() - start_time

            return MigrationResult(
                data_type=data_type,
                success_count=import_result.get("success_count", 0),
                error_count=import_result.get("error_count", 0),
                skipped_count=import_result.get("skipped_count", 0),
                errors=import_result.get("errors", []),
                export_file=str(export_file),
                duration_seconds=duration,
            )

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Failed to migrate {data_type.value}: {e}")

            return MigrationResult(
                data_type=data_type,
                success_count=0,
                error_count=1,
                errors=[str(e)],
                duration_seconds=duration,
            )

    def get_migration_status(self, job_id: str) -> Optional[MigrationJob]:
        """Get status of migration job"""
        return self._active_jobs.get(job_id)

    def list_migration_jobs(self) -> List[MigrationJob]:
        """List all active migration jobs"""
        return list(self._active_jobs.values())

    def cancel_migration(self, job_id: str) -> bool:
        """Cancel a running migration job"""
        job = self._active_jobs.get(job_id)
        if job and job.status == MigrationStatus.running:
            job.status = MigrationStatus.failed
            job.completed_at = datetime.now()
            return True
        return False

    # Convenience methods for individual data types
    def migrate_datasets(self, project_name: str) -> MigrationResult:
        """Migrate datasets from Phoenix project"""
        job = self.migrate_project(project_name, [DataType.datasets])
        # Wait for completion (for synchronous use)
        while job.status == MigrationStatus.running:
            time.sleep(1)
        return job.results[0] if job.results else MigrationResult(data_type=DataType.datasets, success_count=0, error_count=1)

    def migrate_prompts(self, project_name: str) -> MigrationResult:
        """Migrate prompts from Phoenix project"""
        job = self.migrate_project(project_name, [DataType.prompts])
        while job.status == MigrationStatus.running:
            time.sleep(1)
        return job.results[0] if job.results else MigrationResult(data_type=DataType.prompts, success_count=0, error_count=1)

    def migrate_traces(self, project_name: str) -> MigrationResult:
        """Migrate traces from Phoenix project"""
        job = self.migrate_project(project_name, [DataType.traces])
        while job.status == MigrationStatus.running:
            time.sleep(1)
        return job.results[0] if job.results else MigrationResult(data_type=DataType.traces, success_count=0, error_count=1)

    def migrate_annotations(self, project_name: str) -> MigrationResult:
        """Migrate annotations from Phoenix project"""
        job = self.migrate_project(project_name, [DataType.annotations])
        while job.status == MigrationStatus.running:
            time.sleep(1)
        return job.results[0] if job.results else MigrationResult(data_type=DataType.annotations, success_count=0, error_count=1)

    def migrate_evaluations(self, project_name: str) -> MigrationResult:
        """Migrate evaluations from Phoenix project"""
        job = self.migrate_project(project_name, [DataType.evaluations])
        while job.status == MigrationStatus.running:
            time.sleep(1)
        return job.results[0] if job.results else MigrationResult(data_type=DataType.evaluations, success_count=0, error_count=1)
