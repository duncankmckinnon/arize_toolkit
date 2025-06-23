import time
from pathlib import Path
from typing import Optional

import click

from arize_toolkit.client import ArizeClient
from arize_toolkit.migration.utils import create_migration_summary, setup_logging, validate_arize_connection, validate_phoenix_connection
from arize_toolkit.migrations.models import DataType, DateRange, MigrationConfig, MigrationFilters


@click.group()
def migrate():
    """Phoenix to Arize migration commands"""
    pass


@migrate.command()
@click.option(
    "--phoenix-endpoint",
    envvar="PHOENIX_ENDPOINT",
    required=True,
    help="Phoenix server endpoint (e.g., http://localhost:6006)",
)
@click.option("--arize-api-key", envvar="ARIZE_API_KEY", required=True, help="Arize API key")
@click.option("--arize-space-id", envvar="ARIZE_SPACE_ID", required=True, help="Arize space ID")
@click.option(
    "--developer-key",
    envvar="ARIZE_DEVELOPER_KEY",
    help="Arize developer key (optional)",
)
@click.option("--project-name", required=True, help="Phoenix project name to migrate")
@click.option(
    "--data-types",
    multiple=True,
    type=click.Choice(["datasets", "prompts", "traces", "annotations", "evaluations"]),
    help="Specific data types to migrate (default: all)",
)
@click.option("--batch-size", default=1000, help="Batch size for processing (default: 1000)")
@click.option(
    "--output-dir",
    default="./migration_results",
    help="Output directory for migration results",
)
@click.option("--max-records", type=int, help="Maximum records per data type to migrate")
@click.option("--start-date", help="Start date for filtering (YYYY-MM-DD)")
@click.option("--end-date", help="End date for filtering (YYYY-MM-DD)")
@click.option("--annotation-types", help="Comma-separated list of annotation types to include")
@click.option(
    "--validate-first",
    is_flag=True,
    help="Validate migration feasibility before starting",
)
@click.option(
    "--log-level",
    default="INFO",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    help="Log level (default: INFO)",
)
@click.option("--log-file", help="Log file path (optional)")
def project(
    phoenix_endpoint: str,
    arize_api_key: str,
    arize_space_id: str,
    developer_key: Optional[str],
    project_name: str,
    data_types: tuple,
    batch_size: int,
    output_dir: str,
    max_records: Optional[int],
    start_date: Optional[str],
    end_date: Optional[str],
    annotation_types: Optional[str],
    validate_first: bool,
    log_level: str,
    log_file: Optional[str],
):
    """Migrate a complete Phoenix project to Arize"""

    # Setup logging
    log_path = Path(log_file) if log_file else None
    setup_logging(log_level, log_path)

    click.echo("🚀 Starting migration of Phoenix project '{}' to Arize".format(project_name))

    # Validate connections
    click.echo("🔍 Validating connections...")

    phoenix_ok, phoenix_msg = validate_phoenix_connection(phoenix_endpoint)
    if not phoenix_ok:
        click.echo(click.style(f"❌ Phoenix connection failed: {phoenix_msg}", fg="red"))
        return
    click.echo(click.style(f"✅ Phoenix: {phoenix_msg}", fg="green"))

    arize_ok, arize_msg = validate_arize_connection(arize_api_key, arize_space_id)
    if not arize_ok:
        click.echo(click.style(f"❌ Arize connection failed: {arize_msg}", fg="red"))
        return
    click.echo(click.style(f"✅ Arize: {arize_msg}", fg="green"))

    # Create client
    client = ArizeClient(api_key=arize_api_key, space_id=arize_space_id, developer_key=developer_key)

    # Parse data types
    data_types_list = [DataType(dt) for dt in data_types] if data_types else None

    # Build filters
    filters = None
    if any([max_records, start_date, end_date, annotation_types]):
        date_range = None
        if start_date or end_date:
            date_range = DateRange(start=start_date, end=end_date)

        annotation_types_list = None
        if annotation_types:
            annotation_types_list = [t.strip() for t in annotation_types.split(",")]

        filters = MigrationFilters(
            max_records_per_type=max_records,
            date_range=date_range,
            annotation_types=annotation_types_list,
        )

    # Migration configuration
    config = MigrationConfig(batch_size=batch_size, output_directory=output_dir)

    # Validation step
    if validate_first:
        click.echo("🔍 Validating migration feasibility...")

        report = client.validate_phoenix_migration(
            phoenix_endpoint=phoenix_endpoint,
            project_name=project_name,
            data_types=data_types_list,
        )

        if not report.is_feasible:
            click.echo(click.style("❌ Migration validation failed:", fg="red"))
            for issue in report.blocking_issues:
                click.echo(f"  • {issue}")
            return

        # Show estimation
        click.echo(click.style("✅ Migration validation passed", fg="green"))
        if report.estimated_duration:
            click.echo(f"📊 Estimated duration: {report.estimated_duration:.1f} minutes")

        for data_type, count in report.estimated_records.items():
            click.echo(f"📊 {data_type}: {count:,} records")

        if report.warnings:
            click.echo(click.style("⚠️  Warnings:", fg="yellow"))
            for warning in report.warnings:
                click.echo(f"  • {warning}")

        if not click.confirm("🚀 Proceed with migration?"):
            click.echo("Migration cancelled")
            return

    # Start migration
    click.echo("🚀 Starting migration...")
    click.echo(f"📁 Results will be saved to: {output_dir}")

    try:
        job = client.migrate_from_phoenix(
            phoenix_endpoint=phoenix_endpoint,
            project_name=project_name,
            data_types=data_types_list,
            filters=filters,
            config=config,
        )

        click.echo(f"✅ Migration job created: {job.id}")
        click.echo(f"📊 Status: {job.status.value}")

        # Monitor progress
        with click.progressbar(length=100, label="Migration progress") as bar:
            last_progress = 0

            while job.status.value in ["pending", "running"]:
                time.sleep(2)
                job = client.get_migration_status(job.id)

                if job.total_records > 0:
                    progress = (job.processed_records / job.total_records) * 100
                    bar.update(progress - last_progress)
                    last_progress = progress

        # Show final results
        if job.status.value == "completed":
            click.echo(click.style("🎉 Migration completed successfully!", fg="green"))
        elif job.status.value == "partial":
            click.echo(click.style("⚠️  Migration completed with some errors", fg="yellow"))
        else:
            click.echo(click.style("❌ Migration failed", fg="red"))

        # Show summary
        summary = create_migration_summary(job)
        click.echo("\n📊 Migration Summary:")
        click.echo(f"  • Total records processed: {summary['total_records_processed']:,}")
        click.echo(f"  • Successful: {summary['successful_records']:,}")
        click.echo(f"  • Failed: {summary['failed_records']:,}")
        click.echo(f"  • Success rate: {summary['success_rate']:.1f}%")

        if summary["duration_minutes"]:
            click.echo(f"  • Duration: {summary['duration_minutes']:.1f} minutes")

        # Show results by data type
        for result in summary["results_by_type"]:
            click.echo(f"  • {result['data_type']}: {result['success_count']:,} successful, {result['error_count']:,} failed")

        if job.results_path:
            click.echo(f"\n📁 Detailed results saved to: {job.results_path}")

    except Exception as e:
        click.echo(click.style(f"❌ Migration failed: {str(e)}", fg="red"))
        raise click.ClickException(str(e))


@migrate.command()
@click.option(
    "--phoenix-endpoint",
    envvar="PHOENIX_ENDPOINT",
    required=True,
    help="Phoenix server endpoint",
)
@click.option("--arize-api-key", envvar="ARIZE_API_KEY", required=True, help="Arize API key")
@click.option("--arize-space-id", envvar="ARIZE_SPACE_ID", required=True, help="Arize space ID")
@click.option("--project-name", required=True, help="Phoenix project name")
@click.option(
    "--data-types",
    multiple=True,
    type=click.Choice(["datasets", "prompts", "traces", "annotations", "evaluations"]),
    help="Data types to validate (default: all)",
)
def validate(
    phoenix_endpoint: str,
    arize_api_key: str,
    arize_space_id: str,
    project_name: str,
    data_types: tuple,
):
    """Validate migration feasibility without running migration"""

    click.echo("🔍 Validating migration for project '{}'...".format(project_name))

    # Validate connections first
    phoenix_ok, phoenix_msg = validate_phoenix_connection(phoenix_endpoint)
    if not phoenix_ok:
        click.echo(click.style(f"❌ Phoenix connection failed: {phoenix_msg}", fg="red"))
        return

    # Create client and validate
    client = ArizeClient(api_key=arize_api_key, space_id=arize_space_id)

    data_types_list = [DataType(dt) for dt in data_types] if data_types else None

    report = client.validate_phoenix_migration(
        phoenix_endpoint=phoenix_endpoint,
        project_name=project_name,
        data_types=data_types_list,
    )

    # Show results
    if report.is_feasible:
        click.echo(click.style("✅ Migration is feasible", fg="green"))
    else:
        click.echo(click.style("❌ Migration is not feasible", fg="red"))

    if not report.project_exists:
        click.echo(click.style(f"❌ Project '{project_name}' does not exist", fg="red"))

    # Show estimates
    click.echo("\n📊 Estimated Records:")
    total_records = 0
    for data_type, count in report.estimated_records.items():
        click.echo(f"  • {data_type}: {count:,}")
        total_records += count

    click.echo(f"  • Total: {total_records:,}")

    if report.estimated_duration:
        click.echo(f"\n⏱️  Estimated duration: {report.estimated_duration:.1f} minutes")

    # Show warnings
    if report.warnings:
        click.echo(click.style("\n⚠️  Warnings:", fg="yellow"))
        for warning in report.warnings:
            click.echo(f"  • {warning}")

    # Show blocking issues
    if report.blocking_issues:
        click.echo(click.style("\n❌ Blocking Issues:", fg="red"))
        for issue in report.blocking_issues:
            click.echo(f"  • {issue}")

    # Show recommendations
    if report.recommendations:
        click.echo(click.style("\n💡 Recommendations:", fg="blue"))
        for rec in report.recommendations:
            click.echo(f"  • {rec}")


@migrate.command()
@click.option("--job-id", required=True, help="Migration job ID")
@click.option("--arize-api-key", envvar="ARIZE_API_KEY", required=True, help="Arize API key")
@click.option("--arize-space-id", envvar="ARIZE_SPACE_ID", required=True, help="Arize space ID")
def status(job_id: str, arize_api_key: str, arize_space_id: str):
    """Check migration job status"""

    client = ArizeClient(api_key=arize_api_key, space_id=arize_space_id)
    job = client.get_migration_status(job_id)

    if not job:
        click.echo(click.style(f"❌ Migration job {job_id} not found", fg="red"))
        return

    click.echo("📊 Migration Job Status: {}".format(job_id))
    click.echo(f"  • Project: {job.project_name}")
    click.echo(f"  • Status: {job.status.value}")
    click.echo(f"  • Created: {job.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

    if job.completed_at:
        duration = (job.completed_at - job.created_at).total_seconds() / 60
        click.echo(f"  • Completed: {job.completed_at}")
        click.echo(f"  • Duration: {duration:.1f} minutes")

    if job.total_records > 0:
        progress = (job.processed_records / job.total_records) * 100
        click.echo(f"  • Progress: {job.processed_records:,}/{job.total_records:,} ({progress:.1f}%)")

    if job.failed_records > 0:
        click.echo(f"  • Failed records: {job.failed_records:,}")

    # Show results by data type
    if job.results:
        click.echo("\n📊 Results by Data Type:")
        for result in job.results:
            click.echo(f"  • {result.data_type.value}: {result.success_count:,} success, {result.error_count:,} failed")
            if result.errors:
                for error in result.errors[:3]:  # Show first 3 errors
                    click.echo(f"    ⚠️  {error}")
                if len(result.errors) > 3:
                    click.echo(f"    ... and {len(result.errors) - 3} more errors")


@migrate.command()
@click.option("--arize-api-key", envvar="ARIZE_API_KEY", required=True, help="Arize API key")
@click.option("--arize-space-id", envvar="ARIZE_SPACE_ID", required=True, help="Arize space ID")
def jobs(arize_api_key: str, arize_space_id: str):
    """List all migration jobs"""

    client = ArizeClient(api_key=arize_api_key, space_id=arize_space_id)
    jobs = client.list_migration_jobs()

    if not jobs:
        click.echo("📭 No migration jobs found")
        return

    click.echo(f"📊 Found {len(jobs)} migration job(s):")

    for job in sorted(jobs, key=lambda j: j.created_at, reverse=True):
        status_color = {
            "completed": "green",
            "running": "blue",
            "pending": "yellow",
            "failed": "red",
            "partial": "yellow",
        }.get(job.status.value, "white")

        click.echo(f"  • {job.id[:8]}... - {job.project_name}")
        click.echo("    Status: " + click.style(job.status.value, fg=status_color))
        click.echo("    Created: {}".format(job.created_at.strftime("%Y-%m-%d %H:%M:%S")))

        if job.total_records > 0:
            progress = (job.processed_records / job.total_records) * 100
            click.echo(f"    Progress: {progress:.1f}% ({job.processed_records:,}/{job.total_records:,})")


if __name__ == "__main__":
    migrate()
