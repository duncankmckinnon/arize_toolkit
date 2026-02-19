import os

from dotenv import load_dotenv

from arize_toolkit import Client
from arize_toolkit.model_managers import MonitorManager
from arize_toolkit.models import DataQualityMonitor, DriftMonitor, PerformanceMonitor

# Integration test for the Arize API
# This script runs on an Arize account with Developer Access
# Since it updates, creates, and deletes monitors, it should not be run in a production environment
#
# Tests include:
# - Model operations (get_all_models, get_model, get_model_volume, get_performance_metric_over_time)
# - Monitor operations (get_all_monitors, get_monitor, create/delete monitors)
# - Prompt operations (get_all_prompts, get_prompt, get_all_prompt_versions)
# - Dashboard operations (get_all_dashboards, get_dashboard, get_dashboard_by_id, get_dashboard_url)
#
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
            try:
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
            except Exception as e:
                print(f"Monitors Error: {e}")
        try:
            prompts = client.get_all_prompts()
            print("Prompts:", prompts)
            if prompts:
                prompt_name = prompts.pop(0)["name"]
                print(f"Running get_prompt query for prompt: {prompt_name}...")
                prompt = client.get_prompt(prompt_name=prompt_name)
                print(f"Prompt ID for {prompt_name}: {prompt['id']}")
                prompt_versions = client.get_all_prompt_versions(
                    prompt_name=prompt_name
                )
                print("Prompt Versions:", [pv["id"] for pv in prompt_versions])
        except Exception as e:
            print(f"Prompts Error: {e}")

        # Dashboard integration tests
        print("Running dashboard integration tests...")
        try:
            # Test 1: Retrieve all dashboards
            print("Running get_all_dashboards query...")
            dashboards = client.get_all_dashboards()
            print(f"Found {len(dashboards)} dashboards")
            for dashboard in dashboards:
                print(f"  Dashboard: {dashboard['name']} (ID: {dashboard['id']})")

            # Test 2: For a specific dashboard retrieve the detailed set of widgets
            if dashboards:
                dashboard_name = dashboards[0]["name"]
                dashboard_id = dashboards[0]["id"]

                print(f"Running get_dashboard query for dashboard: {dashboard_name}...")
                detailed_dashboard = client.get_dashboard(dashboard_name)

                # Print widget counts and details
                widget_counts = {
                    "statisticWidgets": len(
                        detailed_dashboard.get("statisticWidgets", [])
                    ),
                    "lineChartWidgets": len(
                        detailed_dashboard.get("lineChartWidgets", [])
                    ),
                    "experimentChartWidgets": len(
                        detailed_dashboard.get("experimentChartWidgets", [])
                    ),
                    "driftLineChartWidgets": len(
                        detailed_dashboard.get("driftLineChartWidgets", [])
                    ),
                    "monitorLineChartWidgets": len(
                        detailed_dashboard.get("monitorLineChartWidgets", [])
                    ),
                    "textWidgets": len(detailed_dashboard.get("textWidgets", [])),
                    "barChartWidgets": len(
                        detailed_dashboard.get("barChartWidgets", [])
                    ),
                }

                print(f"Dashboard '{dashboard_name}' widget counts:")
                for widget_type, count in widget_counts.items():
                    print(f"  {widget_type}: {count}")

                # Print model information
                models_in_dashboard = detailed_dashboard.get("models", [])
                print(f"  Models referenced: {len(models_in_dashboard)}")
                for model in models_in_dashboard:
                    print(
                        f"    Model: {model.get('name', 'Unknown')} (ID: {model.get('id', 'Unknown')})"
                    )

                # Print some sample widget details if available
                if detailed_dashboard.get("statisticWidgets"):
                    print("  Sample statistic widgets:")
                    for widget in detailed_dashboard["statisticWidgets"][
                        :3
                    ]:  # Show first 3
                        print(f"    Widget: {widget.get('title', 'Untitled')}")
                        print(f"      Metric: {widget.get('performanceMetric', 'N/A')}")
                        print(
                            f"      Environment: {widget.get('modelEnvironmentName', 'N/A')}"
                        )

                # Test 3: Retrieve the URL for the dashboard
                print(
                    f"Running get_dashboard_url query for dashboard: {dashboard_name}..."
                )
                dashboard_url = client.get_dashboard_url(dashboard_name)
                print(f"Dashboard URL: {dashboard_url}")

                # Also test the dashboard_url property method
                direct_url = client.dashboard_url(dashboard_id)
                print(f"Direct dashboard URL: {direct_url}")

                # Test get_dashboard_by_id as well
                print(
                    f"Running get_dashboard_by_id query for dashboard ID: {dashboard_id}..."
                )
                dashboard_by_id = client.get_dashboard_by_id(dashboard_id)
                print(f"Dashboard by ID name: {dashboard_by_id['name']}")

            else:
                print("No dashboards found in the space")

        except Exception as e:
            print(f"Dashboard integration tests error: {e}")

        if monitors:
            monitor_name = monitors.pop(0)["name"]  # Get the first monitor name
            print(f"Running get_monitor query for monitor: {monitor_name}...")
            monitor = client.get_monitor(
                model_name=model_name, monitor_name=monitor_name
            )
            print(f"Monitor ID for {monitor_name}: {monitor['id']}")
            print(
                f"Monitor Category for {monitor_name}: {monitor.get('monitorCategory')}"
            )
            try:
                print(
                    f"Running get_monitor_metric_values query for monitor: {monitor_name}..."
                )
                monitor_metric_values = client.get_monitor_metric_values(
                    model_name=model_name,
                    monitor_name=monitor_name,
                    start_date="2024-01-01",
                    end_date="2025-01-01",
                    to_dataframe=True,
                )
                print(f"Monitor Metric Values: {monitor_metric_values}")
                print(
                    f"Running get_latest_monitor_value query for monitor: {monitor_name}..."
                )
                latest_monitor_value = client.get_latest_monitor_value(
                    model_name=model_name,
                    monitor_name=monitor_name,
                )
                print(f"Latest Monitor Value: {latest_monitor_value}")
            except Exception as e:
                print(f"Monitor Metric Values Error: {e}")

            if monitor:
                monitor_creator = MonitorManager.extract_monitor_type_from_dict(
                    space_id=client.space_id,
                    model_name=model_name,
                    monitor=monitor,
                )
                print(f"Monitor Creator: {monitor_creator.to_dict(exclude_none=True)}")
                old_id = client.delete_monitor_by_id(monitor_id=monitor["id"])
                print(f"Deleted monitor with ID: {old_id}")
                email_addresses = [
                    email.emailAddress
                    for email in monitor_creator.contacts
                    if email.notificationChannelType == "email"
                ]
                integration_key_ids = [
                    integration_key.integrationKeyId
                    for integration_key in monitor_creator.contacts
                    if integration_key.notificationChannelType == "integration"
                ]
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
                        email_addresses=email_addresses,
                        integration_key_ids=integration_key_ids,
                        std_dev_multiplier=(
                            monitor_creator.dynamicAutoThreshold.stdDevMultiplier
                            if monitor_creator.dynamicAutoThreshold
                            else None
                        ),
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
                        email_addresses=email_addresses,
                        integration_key_ids=integration_key_ids,
                        std_dev_multiplier=(
                            monitor_creator.dynamicAutoThreshold.stdDevMultiplier
                            if monitor_creator.dynamicAutoThreshold
                            else None
                        ),
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
                        email_addresses=email_addresses,
                        integration_key_ids=integration_key_ids,
                        std_dev_multiplier=(
                            monitor_creator.dynamicAutoThreshold.stdDevMultiplier
                            if monitor_creator.dynamicAutoThreshold
                            else None
                        ),
                    )
                    print(f"Drift Monitor: {drift_monitor}")

        get_all_spaces = client.get_all_spaces()
        space_names = [space["name"] for space in get_all_spaces]
        if "integration_test_space" not in space_names:
            print(f"All Spaces: {get_all_spaces}")
            create_space = client.create_new_space(name="integration_test_space")
            print(f"Created Space: {create_space}")
            create_space_admin_api_key = client.create_space_admin_api_key(
                name="integration_test_space_admin_api_key"
            )
            print(
                f"Created Space Admin API Key - ID: {create_space_admin_api_key['id']}"
            )

        # Add more client queries as needed
    except Exception as e:
        print("An error occurred during integration tests:", e)


if __name__ == "__main__":
    run_integration_tests()
