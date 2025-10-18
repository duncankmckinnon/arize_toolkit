"""
Example demonstrating the AsyncClient usage with the arize-toolkit.

This example shows how to use the AsyncClient to perform async operations
while reusing all the existing query logic from the sync client.
"""

import asyncio

from arize_toolkit import AsyncClient


async def main():
    """Example async client usage"""

    # Using context manager (recommended)
    async with AsyncClient(
        organization="your-org",
        space="your-space",
        # arize_developer_key="your-key"  # or set ARIZE_DEVELOPER_KEY env var
    ) as client:
        print(f"Connected to space: {client.space_url}")

        # Get all resources concurrently - this is the power of async!
        models, dashboards, monitors, prompts = await asyncio.gather(
            client.get_all_models(),
            client.get_all_dashboards(),
            client.get_all_monitors(),
            client.get_all_prompts(),
        )

        print(f"Found {len(models)} models")
        print(f"Found {len(dashboards)} dashboards")
        print(f"Found {len(monitors)} monitors")
        print(f"Found {len(prompts)} prompts")

        # Get specific resources by name
        if models:
            first_model = models[0]
            model_name = first_model["name"]

            # Get model details and its custom metrics concurrently
            model_details, custom_metrics = await asyncio.gather(client.get_model(model_name), client.get_all_custom_metrics(model_name))

            print(f"Model: {model_details['name']}")
            print(f"Custom metrics for {model_name}: {len(custom_metrics)}")
            print(f"Model URL: {client.model_url(first_model['id'])}")

        # Get monitors for a specific model
        if models and len(models) > 0:
            model_monitors = await client.get_all_monitors(models[0]["name"])
            print(f"Monitors for {models[0]['name']}: {len(model_monitors)}")

        # Demonstrate CRUD operations
        if models:
            model_name = models[0]["name"]

            # Create a custom metric
            try:
                metric_url = await client.create_custom_metric(model_name, "test_accuracy", "numeric", "Test accuracy metric")
                print(f"Created custom metric: {metric_url}")

                # Update the custom metric
                updated_metric = await client.update_custom_metric(
                    "test_accuracy",
                    model_name,
                    description="Updated test accuracy metric",
                )
                print(f"Updated metric: {updated_metric['name']}")

                # Delete the custom metric
                deleted = await client.delete_custom_metric("test_accuracy", model_name)
                print(f"Deleted custom metric: {deleted}")
            except Exception as e:
                print(f"Custom metric operations failed: {e}")

        # Demonstrate prompt operations
        try:
            # Create a prompt
            prompt_url = await client.create_prompt("test-prompt", "A test prompt for async client", ["test", "async"])
            print(f"Created prompt: {prompt_url}")

            # Update the prompt
            updated = await client.update_prompt("test-prompt", description="Updated test prompt description")
            print(f"Updated prompt: {updated}")

            # Delete the prompt
            deleted = await client.delete_prompt("test-prompt")
            print(f"Deleted prompt: {deleted}")
        except Exception as e:
            print(f"Prompt operations failed: {e}")


async def manual_session_management():
    """Example without context manager"""

    client = AsyncClient(
        organization="your-org",
        space="your-space",
    )

    try:
        await client.connect()
        models = await client.get_all_models()
        print(f"Found {len(models)} models")
    finally:
        await client.close()


if __name__ == "__main__":
    # Run the async example
    asyncio.run(main())

    # Or run the manual session management example
    # asyncio.run(manual_session_management())
