# Integration Testing Guide

This guide explains how to set up and run integration tests for the Arize API client.

## Setup

### 1. Environment Variables

Create a `.env` file in the root directory with the following variables:

```bash
ARIZE_DEVELOPER_KEY=your_developer_key
ORGANIZATION_NAME=your_organization
SPACE_NAME=your_space_name
```

### 2. Prerequisites

Install required dependencies:

```bash
pip install python-dotenv
pip install arize-toolkit
```

## Running Tests

### Using the Shell Script

The simplest way to run integration tests is using the provided shell script:

```bash
sh bin/integration_test.sh
```

## Test Coverage

1. **Client Initialization**
   - Authenticates with API
   - Sets up organization and space context

```python
client = Client(
    organization=os.getenv("ORGANIZATION_NAME"),
    space=os.getenv("SPACE_NAME"),
    arize_developer_key=os.getenv("ARIZE_DEVELOPER_KEY"),
)
```

2. **Operations**

   The integration tests should verify the following functionality for each set of operations:

   - Get all objects
     -- For a list of objects, check that the response is a list

   - Select one of the objects listed and make sure the object can be retrieved by name and id
     -- You can often test both of these by getting the object by name, so long as the get_object function first gets the object's id.

   - Create an object
     -- Use the name of the object and some other unique identifier to create a new identical object

   - Update an object
     -- Use the created object and add or change an attribute

   - Delete an object
     -- Use the created object and delete it by name

```python
   # Get all monitors for a model
   monitors = client.get_all_monitors(model_name)
   
   # Get the name of the first monitor
   monitor_name = monitors[0].name

   # Get specific monitor details
   monitor = client.get_monitor(monitor_name)

   # create a new monitor name
   new_monitor_name = monitor_name + "_new"

   # Create a new monitor
   new_monitor_url = client.create_drift_monitor(new_monitor_name, ...)

   # Update the new monitor
   updated_monitor_url = client.update_monitor(new_monitor_name, ...)

   # Delete the new monitor
   monitor_deleted = client.delete_monitor(new_monitor_name)
```

## Test Structure

The integration tests follow this pattern:

1. Load environment configuration
1. Initialize client
1. Execute API operations
1. Verify responses

Example:

```python
def run_integration_tests():
    # Initialize client
    client = Client(
        organization=os.getenv("ORGANIZATION_NAME"),
        space=os.getenv("SPACE_NAME"),
        token=os.getenv("ARIZE_API_KEY"),
    )

    # Run tests
    try:
        models = client.get_all_models()
        print("Models found:", len(models))

        # Additional test cases...

    except Exception as e:
        print("Test failed:", str(e))
```

## Adding New Tests

To add new test cases:

1. Open `tests/integration_test/run.py`
1. Add new test scenarios within the `run_integration_tests()` function
1. Follow the existing error handling pattern

Example adding a new test:

```python
# Test monitor creation
try:
    monitor_id = client.create_performance_metric_monitor(
        model_name="my_model",
        metric="accuracy",
        name="Accuracy Monitor",
        operator="LESS_THAN",
        threshold=0.95,
    )
    print(f"Created monitor: {monitor_id}")
except Exception as e:
    print("Failed to create monitor:", str(e))
```

## Troubleshooting

Common issues and solutions:

1. **Authentication Errors**

   - Verify `ARIZE_API_KEY` is set correctly
   - Check API key permissions

1. **Resource Not Found**

   - Confirm organization and space names are correct
   - Verify model/monitor names exist

1. **Rate Limiting**

   - Add `sleep_time` parameter to client initialization
   - Reduce number of concurrent requests

## Best Practices

1. **Environment Management**

   - Use separate test environment
   - Never commit `.env` file (it should be excluded using .gitignore)
   - Document required environment variables

1. **Error Handling**

   - Catch and log specific exceptions
   - Provide meaningful error messages
   - Clean up test resources

1. **Test Data**

   - Use consistent test data
   - Clean up test artifacts
   - Document test prerequisites
