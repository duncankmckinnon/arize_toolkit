import os

from dotenv import load_dotenv

from arize_toolkit import Client
from arize_toolkit.model_managers import MonitorManager
from arize_toolkit.models import DataQualityMonitor, DriftMonitor, PerformanceMonitor

# Integration test for the Arize API
# This script runs on an Arize account with Developer Access
# Since it updates, creates, and deletes monitors, it should not be run in a production environment
# To run this script, you need to set the following environment variables in your .env file:
# ARIZE_DEVELOPER_KEY - The developer key for the Arize account
# ORGANIZATION_NAME - The name of the organization in Arize account
# SPACE_NAME - The name of the space in Arize account

# Load environment variables from .env file
load_dotenv()


def load_env_vars():
    arize_developer_key = os.getenv("ARIZE_DEVELOPER_KEY")
    if not arize_developer_key:
        raise ValueError("ARIZE_DEVELOPER_KEY must be set in the .env file")

    organization = os.getenv("ORGANIZATION_NAME")
    if not organization:
        raise ValueError("ORGANIZATION_NAME must be set in the .env file")

    space = os.getenv("SPACE_NAME")
    if not space:
        raise ValueError("SPACE_NAME must be set in the .env file")

    return arize_developer_key, organization, space


def run_integration_tests():
    # Retrieve environment variables
    arize_developer_key, organization, space = load_env_vars()
    model_name = None
    # Initialize the client
    client = Client(
        organization=organization,
        space=space,
        arize_developer_key=arize_developer_key,
        sleep_time=5,
    )

    # Run client queries
    try:
        print("Running get_all_models query...")
        models = client.get_all_models()
        print("Models:", models)

        # Example: Run get_model query for a specific model
        if models:
            model_names = [model["name"] for model in models]
            model_name = model_names.pop()  # Get the first model name
            print(f"Running get_model query for model: {model_name}...")
            model = client.get_model(model_name=model_name)
            print(f"Model ID for {model_name}: {model['id']}")

            # Get model volume
            print(f"Running get_model_volume query for model: {model_name}...")
            model_volume = client.get_model_volume(model_name=model_name)
            print(f"Model Volume for {model_name}: {model_volume}")

            # Get total volume
            print("Running get_total_volume query...")
            # total_volume, model_volumes = client.get_total_volume()
            # print(f"Total Volume: {total_volume}")
            # print(f"Model Volumes: {model_volumes}")
            print("Running get_performance_metric_over_time query...")
            try:
                performance_metric_over_time = client.get_performance_metric_over_time(
                    metric="predictionAverage",
                    environment="production",
                    model_name=model_name,
                    start_time="2025-01-01",
                )
                print(f"Performance Metric Over Time: {performance_metric_over_time}")
            except Exception as e:
                print(f"Performance Metric Over Time Error: {e}")

        if model["id"]:
            print("Running get_all_monitors query...")
            monitors = client.get_all_monitors(model_id=model["id"])
            print("Monitors:", monitors)
            if not monitors:
                print("No monitors found for model:", model_name)
                for nm in model_names:
                    print("Running get_all_monitors query...")
                    model = client.get_model(model_name=nm)
                    print(f"Model ID for {nm}: {model['id']}")
                    monitors = client.get_all_monitors(model_id=model["id"])
                    if monitors:
                        model_name = nm
                        print(f"Monitors found for model {model_name}:", monitors)
                        break
                    else:
                        print("No monitors found for model:", nm)

        prompts = client.get_all_prompts()
        print("Prompts:", prompts)
        if prompts:
            prompt_name = prompts.pop(0)["name"]
            print(f"Running get_prompt query for prompt: {prompt_name}...")
            prompt = client.get_prompt(prompt_name=prompt_name)
            print(f"Prompt ID for {prompt_name}: {prompt['id']}")
            prompt_versions = client.get_all_prompt_versions(prompt_name=prompt_name)
            print("Prompt Versions:", [pv["id"] for pv in prompt_versions])

        if monitors:
            monitor_name = monitors.pop(0)["name"]  # Get the first monitor name
            print(f"Running get_monitor query for monitor: {monitor_name}...")
            monitor = client.get_monitor(model_name=model_name, monitor_name=monitor_name)
            print(f"Monitor ID for {monitor_name}: {monitor['id']}")
            print(f"Monitor Category for {monitor_name}: {monitor.get('monitorCategory')}")

            if monitor:
                monitor_creator = MonitorManager.extract_monitor_type_from_dict(
                    space_id=client.space_id,
                    model_name=model_name,
                    monitor=monitor,
                )
                print(f"Monitor Creator: {monitor_creator.to_dict(exclude_none=True)}")
                old_id = client.delete_monitor_by_id(monitor_id=monitor["id"])
                print(f"Deleted monitor with ID: {old_id}")
                if isinstance(monitor_creator, PerformanceMonitor):
                    performance_monitor = client.create_performance_monitor(
                        name=monitor_creator.name,
                        model_name=model_name,
                        performance_metric=monitor_creator.performanceMetric,
                        model_environment_name=monitor_creator.modelEnvironmentName,
                        operator=monitor_creator.operator,
                        notes=monitor_creator.notes,
                        scheduled_runtime_cadence_seconds=monitor_creator.scheduledRuntimeCadenceSeconds,
                        scheduled_runtime_days_of_week=monitor_creator.scheduledRuntimeDaysOfWeek,
                        threshold=monitor_creator.threshold,
                        threshold_mode=monitor_creator.thresholdMode,
                        std_dev_multiplier=(monitor_creator.dynamicAutoThreshold.stdDevMultiplier if monitor_creator.dynamicAutoThreshold else None),
                    )
                    print(f"Performance Monitor: {performance_monitor}")
                elif isinstance(monitor_creator, DataQualityMonitor):
                    data_quality_monitor = client.create_data_quality_monitor(
                        name=monitor_creator.name,
                        model_name=model_name,
                        data_quality_metric=monitor_creator.dataQualityMetric,
                        dimension_name=monitor_creator.dimensionName,
                        dimension_category=monitor_creator.dimensionCategory,
                        notes=monitor_creator.notes,
                        model_environment_name=monitor_creator.modelEnvironmentName,
                        threshold=monitor_creator.threshold,
                        threshold_mode=monitor_creator.thresholdMode,
                        std_dev_multiplier=(monitor_creator.dynamicAutoThreshold.stdDevMultiplier if monitor_creator.dynamicAutoThreshold else None),
                    )
                    print(f"Data Quality Monitor: {data_quality_monitor}")
                elif isinstance(monitor_creator, DriftMonitor):
                    drift_monitor = client.create_drift_monitor(
                        name=monitor_creator.name,
                        model_name=model_name,
                        drift_metric=monitor_creator.driftMetric,
                        dimension_name=monitor_creator.dimensionName,
                        dimension_category=monitor_creator.dimensionCategory,
                        notes=monitor_creator.notes,
                        threshold=monitor_creator.threshold,
                        threshold_mode=monitor_creator.thresholdMode,
                        std_dev_multiplier=(monitor_creator.dynamicAutoThreshold.stdDevMultiplier if monitor_creator.dynamicAutoThreshold else None),
                    )
                    print(f"Drift Monitor: {drift_monitor}")
        # Add more client queries as needed
    except Exception as e:
        print("An error occurred during integration tests:", e)


if __name__ == "__main__":
    run_integration_tests()
