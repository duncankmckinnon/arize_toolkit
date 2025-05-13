# Integration Testing Guide

This guide explains how to set up and run integration tests for the Arize API client.

## Setup

### 1. Environment Variables

Create a `.env` file in the root directory with the following variables:

```bash
ARIZE_API_KEY=your_api_key
ORGANIZATION_NAME=your_organization
SPACE_NAME=your_space_name
```

### 2. Prerequisites

Install required dependencies:

```bash
pip install python-dotenv
pip install arize-api
```

## Running Tests

### Using the Shell Script

The simplest way to run integration tests is using the provided shell script:

```bash
./bin/integration_test.sh
```

### Running Tests Manually

You can also run the tests directly using Python:

```bash
python tests/integration_test/run.py
```

## Test Coverage

The integration tests verify the following functionality:

1. **Client Initialization**
   - Authenticates with API
   - Sets up organization and space context

2. **Model Operations**
   ```python
   # Get all models in the space
   models = client.get_all_models()
   
   # Get specific model details
   model = client.get_model(model_name)
   ```

3. **Monitor Operations**
   ```python
   # Get all monitors for a model
   monitors = client.get_all_monitors(model_id)
   
   # Get specific monitor details
   monitor = client.get_monitor(monitor_name)
   ```

## Test Structure

The integration tests follow this pattern:

1. Load environment configuration
2. Initialize client
3. Execute API operations
4. Verify responses

Example:
```python
def run_integration_tests():
    # Initialize client
    client = Client(
        organization=os.getenv("ORGANIZATION_NAME"),
        space=os.getenv("SPACE_NAME"),
        token=os.getenv("ARIZE_API_KEY")
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
2. Add new test scenarios within the `run_integration_tests()` function
3. Follow the existing error handling pattern

Example adding a new test:
```python
# Test monitor creation
try:
    monitor_id = client.create_performance_metric_monitor(
        model_name="my_model",
        metric="accuracy",
        name="Accuracy Monitor",
        operator="LESS_THAN",
        threshold=0.95
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

2. **Resource Not Found**
   - Confirm organization and space names are correct
   - Verify model/monitor names exist

3. **Rate Limiting**
   - Add `sleep_time` parameter to client initialization
   - Reduce number of concurrent requests

## Best Practices

1. **Environment Management**
   - Use separate test environment
   - Never commit `.env` file (it should be excluded using .gitignore)
   - Document required environment variables

2. **Error Handling**
   - Catch and log specific exceptions
   - Provide meaningful error messages
   - Clean up test resources

3. **Test Data**
   - Use consistent test data
   - Clean up test artifacts
   - Document test prerequisites
