# Integration Testing Guide

This guide explains how to set up and run integration tests for the Arize API client.

## Setup

### 1. Select an Arize Organization and Space

For these integration tests, you will need to select an Arize organization and space. The space used for the tests should be separated from any sensitive use cases or production data that may also exist in the same account. Ideally, you should create Arize models and other resources in a separate space for testing, because this script will attempt to alter, delete and then recreate data resources in the chosen space, and it works best when:

- there is a good representation of all different types of resources in the space.
- it's easy to make synthetic resources for testing that won't be missed if they are deleted and fail to be recreated.
- new resources can be created easily to test new features without needing to setup entire use cases.

### 2. Environment Variables

Create a `.env` file in the root directory with the following variables:

```bash
ARIZE_DEVELOPER_KEY=your_developer_key
ORGANIZATION_NAME=your_organization
SPACE_NAME=your_space_name
```

### 3. Prerequisites

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

    # Model tests
    try:
        # Get ALL
        models = client.get_all_models()
        print("Models found:", len(models))

        # Get by name and id
        model_name = models[0].name
        model_id = models[0].id

        # Get by name
        model = client.get_model(model_name)
        print("Model found:", model)

        # Get by id
        model = client.get_model(model_id)
        print("Model found by id:", model)

        # Other tests...
    except Exception as e:
        print("Test failed:", str(e))

    # Monitor tests (uses model name)
    try:
        # get all monitors using the model name
        monitors = client.get_all_monitors(model_name)
        print("Monitors found:", len(monitors))

        # get monitor name and id
        ...

        # get monitor by name and id
        ...

        # update the monitor
        ...

        # delete the monitor
        ...

        # create the monitor again
        ...

    except Exception as e:
        print("Test failed:", str(e))

    # Pattern  continues for other resources...
```

## Adding New Tests

To add new test cases:

1. Open `tests/integration_test/run.py`
1. Add new test scenarios within the `run_integration_tests()` function
1. Use the existing test structure as a guide, with try/except blocks to catch errors and print the error message so the full integration test output can run all the way through
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

   - Verify `ARIZE_DEVELOPER_KEY` is set correctly
   - Make sure you use a space and organization that you have admin level permissions for

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
