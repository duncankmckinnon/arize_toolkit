import pytest
from unittest.mock import patch
from arize_toolkit.client import Client
from arize_toolkit.queries.basequery import ArizeAPIException


@pytest.fixture
def mock_graphql_client():
    """Create a mock GraphQL client"""
    with patch("arize_toolkit.client.GraphQLClient") as mock_client:
        # Mock the initial org/space lookup response
        mock_client.return_value.execute.return_value = {
            "account": {
                "organizations": {
                    "edges": [
                        {
                            "node": {
                                "id": "test_org_id",
                                "spaces": {
                                    "edges": [{"node": {"id": "test_space_id"}}]
                                },
                            }
                        }
                    ]
                }
            }
        }
        yield mock_client


@pytest.fixture
def client(mock_graphql_client):
    """Create a test client with mocked GraphQL client"""
    return Client(
        organization="test_org", space="test_space", arize_developer_key="test_token"
    )


class TestClientInitialization:
    def test_client_initialization(self, mock_graphql_client):
        """Test client initialization with different parameters"""
        # Test with direct token
        client = Client(
            organization="test_org",
            space="test_space",
            arize_developer_key="test_token",
        )
        assert client.organization == "test_org"
        assert client.space == "test_space"
        assert client.org_id == "test_org_id"
        assert client.space_id == "test_space_id"

        # Test with environment variable
        with patch("os.getenv", return_value="env_token"):
            client = Client(organization="test_org", space="test_space")
            assert client.organization == "test_org"
            assert client.space == "test_space"
            assert client.org_id == "test_org_id"
            assert client.space_id == "test_space_id"


class TestModel:
    def test_get_model_by_id(self, client, mock_graphql_client):
        mock_graphql_client.return_value.execute.reset_mock()
        mock_graphql_client.return_value.execute.return_value = {
            "node": {
                "id": "test_model_id",
                "name": "test_model",
                "modelType": "score_categorical",
                "createdAt": "2021-01-01T00:00:00Z",
                "isDemoModel": False,
            }
        }
        result = client.get_model_by_id("test_model_id")
        assert result["id"] == "test_model_id"
        assert result["name"] == "test_model"
        assert result["modelType"] == "score_categorical"
        assert result["createdAt"] == "2021-01-01T00:00:00.000000Z"
        assert not result["isDemoModel"]

    def test_get_model(self, client, mock_graphql_client):
        mock_graphql_client.return_value.execute.reset_mock()
        mock_graphql_client.return_value.execute.return_value = {
            "node": {
                "models": {
                    "edges": [
                        {
                            "node": {
                                "id": "test_model_id",
                                "name": "test_model",
                                "modelType": "score_categorical",
                                "createdAt": "2021-01-01T00:00:00Z",
                                "isDemoModel": False,
                            }
                        }
                    ]
                }
            }
        }

        result = client.get_model("test_model")
        assert result["id"] == "test_model_id"
        assert result["name"] == "test_model"
        assert result["modelType"] == "score_categorical"
        assert result["createdAt"] == "2021-01-01T00:00:00.000000Z"
        assert not result["isDemoModel"]

        # Test model not found
        mock_graphql_client.return_value.execute.return_value = {
            "node": {"models": {"edges": []}}
        }

        with pytest.raises(ArizeAPIException) as exc_info:
            client.get_model("non_existent_model")
        assert "No model found" in str(exc_info.value)

    def test_get_all_models(self, client, mock_graphql_client):
        mock_graphql_client.return_value.execute.reset_mock()

        # Mock response with pagination
        mock_responses = [
            {
                "node": {
                    "models": {
                        "pageInfo": {"hasNextPage": True, "endCursor": "cursor1"},
                        "edges": [
                            {
                                "node": {
                                    "name": "model1",
                                    "id": "id1",
                                    "modelType": "numeric",
                                    "createdAt": "2021-01-01T00:00:00Z",
                                    "isDemoModel": False,
                                }
                            }
                        ],
                    }
                }
            },
            {
                "node": {
                    "models": {
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                        "edges": [
                            {
                                "node": {
                                    "name": "model2",
                                    "id": "id2",
                                    "modelType": "score_categorical",
                                    "createdAt": "2021-01-01T00:00:00Z",
                                    "isDemoModel": False,
                                }
                            }
                        ],
                    }
                }
            },
        ]

        mock_graphql_client.return_value.execute.side_effect = mock_responses

        results = client.get_all_models()
        assert len(results) == 2
        assert results[0]["id"] == "id1"
        assert results[1]["id"] == "id2"
        assert results[0]["modelType"] == "numeric"
        assert results[1]["modelType"] == "score_categorical"
        assert results[0]["createdAt"] == "2021-01-01T00:00:00.000000Z"
        assert results[1]["createdAt"] == "2021-01-01T00:00:00.000000Z"
        assert not results[0]["isDemoModel"]
        assert not results[1]["isDemoModel"]

    def test_get_model_volume(self, client, mock_graphql_client):
        mock_graphql_client.return_value.execute.reset_mock()
        mock_graphql_client.return_value.execute.side_effect = [
            {
                "node": {
                    "models": {
                        "pageInfo": {"hasNextPage": False, "endCursor": "cursor1"},
                        "edges": [
                            {
                                "node": {
                                    "name": "model1",
                                    "id": "id1",
                                    "modelType": "numeric",
                                    "createdAt": "2021-01-01T00:00:00Z",
                                    "isDemoModel": False,
                                }
                            }
                        ],
                    }
                }
            },
            {"node": {"modelPredictionVolume": {"totalVolume": 200}}},
        ]

        result = client.get_model_volume(model_name="test_model")
        assert mock_graphql_client.return_value.execute.call_count == 2
        assert result == 200

    def test_get_total_volume(self, client, mock_graphql_client):
        mock_graphql_client.return_value.execute.reset_mock()
        mock_graphql_client.return_value.execute.side_effect = [
            {
                "node": {
                    "models": {
                        "pageInfo": {"hasNextPage": False, "endCursor": "cursor1"},
                        "edges": [
                            {
                                "node": {
                                    "name": "model1",
                                    "id": "id1",
                                    "modelType": "numeric",
                                    "createdAt": "2021-01-01T00:00:00Z",
                                    "isDemoModel": False,
                                }
                            },
                            {
                                "node": {
                                    "name": "model2",
                                    "id": "id2",
                                    "modelType": "numeric",
                                    "createdAt": "2021-01-01T00:00:00Z",
                                    "isDemoModel": True,
                                }
                            },
                        ],
                    }
                }
            },
            {"node": {"modelPredictionVolume": {"totalVolume": 100}}},
            {"node": {"modelPredictionVolume": {"totalVolume": 200}}},
        ]

        total_volume, model_volumes = client.get_total_volume()
        assert total_volume == 300
        assert model_volumes["model1"] == 100
        assert model_volumes["model2"] == 200

    def test_delete_data_by_id(self, client, mock_graphql_client):
        mock_graphql_client.return_value.execute.reset_mock()
        mock_graphql_client.return_value.execute.return_value = {
            "deleteData": {"clientMutationId": None}
        }
        result = client.delete_data_by_id("test_model_id", "2021-01-01T00:00:00Z")
        assert result

    def test_delete_data(self, client, mock_graphql_client):
        mock_graphql_client.return_value.execute.reset_mock()
        mock_graphql_client.return_value.execute.side_effect = [
            {
                "node": {
                    "models": {
                        "pageInfo": {"hasNextPage": False, "endCursor": "cursor1"},
                        "edges": [
                            {
                                "node": {
                                    "name": "test_model",
                                    "id": "test_model_id",
                                    "modelType": "numeric",
                                    "createdAt": "2021-01-01T00:00:00Z",
                                    "isDemoModel": False,
                                }
                            }
                        ],
                    }
                }
            },
            {"deleteData": {"clientMutationId": None}},
        ]
        result = client.delete_data(
            "test_model", "2021-01-01", "2021-01-02", "preproduction"
        )
        assert result
        assert mock_graphql_client.return_value.execute.call_count == 2


class TestCustomMetrics:
    def test_get_all_custom_metrics(self, client, mock_graphql_client):
        mock_graphql_client.return_value.execute.reset_mock()

        metrics = [
            {
                "node": {
                    "id": f"custom_metric_id_{i}",
                    "name": f"custom_metric_{i}",
                    "description": f"Custom metric {i} description",
                    "createdAt": "2021-01-01T00:00:00Z",
                    "metric": "SELECT avg(column_name) FROM model",
                    "requiresPositiveClass": False,
                }
            }
            for i in range(1, 21)
        ]
        # Mock response for get_all_custom_metrics
        mock_custom_metrics_response = [
            {
                "node": {
                    "models": {
                        "edges": [
                            {
                                "node": {
                                    "customMetrics": {
                                        "pageInfo": {
                                            "hasNextPage": True,
                                            "endCursor": "cursor10",
                                        },
                                        "edges": metrics[0:10],
                                    }
                                }
                            }
                        ]
                    }
                }
            },
            {
                "node": {
                    "models": {
                        "edges": [
                            {
                                "node": {
                                    "customMetrics": {
                                        "pageInfo": {
                                            "hasNextPage": False,
                                            "endCursor": None,
                                        },
                                        "edges": metrics[10:20],
                                    }
                                }
                            }
                        ]
                    }
                }
            },
        ]

        mock_graphql_client.return_value.execute.side_effect = (
            mock_custom_metrics_response
        )

        results = client.get_all_custom_metrics(model_name="test_model")
        assert len(results) == 20
        assert results[0]["id"] == "custom_metric_id_1"
        assert results[0]["name"] == "custom_metric_1"
        assert results[0]["description"] == "Custom metric 1 description"
        assert results[0]["createdAt"] == "2021-01-01T00:00:00.000000Z"
        assert results[0]["metric"] == "SELECT avg(column_name) FROM model"
        assert results[-1]["id"] == "custom_metric_id_20"
        assert results[-1]["name"] == "custom_metric_20"
        assert results[-1]["description"] == "Custom metric 20 description"
        assert results[-1]["createdAt"] == "2021-01-01T00:00:00.000000Z"
        assert results[-1]["metric"] == "SELECT avg(column_name) FROM model"

    def test_copy_custom_metric(self, client, mock_graphql_client):
        mock_graphql_client.return_value.execute.reset_mock()
        mock_graphql_client.return_value.execute.side_effect = [
            {
                "node": {
                    "models": {
                        "edges": [
                            {
                                "node": {
                                    "customMetrics": {
                                        "edges": [
                                            {
                                                "node": {
                                                    "id": "custom_metric_id_1",
                                                    "name": "custom_metric_1",
                                                    "description": "Custom metric 1 description",
                                                    "createdAt": "2021-01-01T00:00:00Z",
                                                    "metric": "SELECT avg(column_name) FROM model",
                                                    "requiresPositiveClass": False,
                                                }
                                            }
                                        ]
                                    }
                                }
                            }
                        ]
                    }
                }
            },
            {
                "node": {
                    "models": {
                        "edges": [
                            {
                                "node": {
                                    "id": "test_model_id",
                                    "name": "test_model",
                                    "modelType": "score_categorical",
                                    "createdAt": "2021-01-01T00:00:00Z",
                                    "isDemoModel": False,
                                }
                            }
                        ]
                    }
                }
            },
            {"createCustomMetric": {"customMetric": {"id": "new_custom_metric_id"}}},
        ]

        new_metric_id = client.copy_custom_metric(
            current_model_name="test_model",
            current_metric_name="custom_metric_1",
            new_model_name="new_model",
        )
        assert new_metric_id == client.custom_metric_url(
            "test_model_id", "new_custom_metric_id"
        )
        assert mock_graphql_client.return_value.execute.call_count == 3


class TestMonitors:
    def test_get_all_monitors(self, client, mock_graphql_client):
        mock_graphql_client.return_value.execute.reset_mock()
        # Mock response for get_all_monitors with all required fields
        mock_monitors_response = {
            "node": {
                "monitors": {
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                    "edges": [
                        {
                            "node": {
                                "id": "monitor1",
                                "name": "performance_monitor",
                                "monitorCategory": "performance",
                                "createdDate": "2024-03-20T10:00:00Z",
                                "evaluationIntervalSeconds": 3600,
                                "evaluatedAt": "2024-03-20T11:00:00Z",
                                "creator": None,
                                "notes": None,
                                "contacts": None,
                                "dimensionCategory": "prediction",
                                "status": "cleared",
                                "isTriggered": False,
                                "isManaged": True,
                                "threshold": 0.95,
                                "thresholdMode": "single",
                                "threshold2": None,
                                "notificationsEnabled": True,
                                "updatedAt": "2024-03-20T11:00:00Z",
                                "downtimeStart": None,
                                "downtimeDurationHrs": None,
                                "downtimeFrequencyDays": None,
                                "scheduledRuntimeEnabled": False,
                                "scheduledRuntimeCadenceSeconds": None,
                                "scheduledRuntimeDaysOfWeek": None,
                                "latestComputedValue": None,
                                "performanceMetric": "accuracy",
                                "customMetric": None,
                                "operator": "lessThan",
                                "operator2": None,
                                "stdDevMultiplier": None,
                                "stdDevMultiplier2": None,
                                "dynamicAutoThresholdEnabled": None,
                                "driftMetric": None,
                                "dataQualityMetric": None,
                                "topKPercentileValue": None,
                                "positiveClassValue": None,
                                "metricAtRankingKValue": None,
                                "primaryMetricWindow": None,
                            }
                        },
                        {
                            "node": {
                                "id": "monitor2",
                                "name": "drift_monitor",
                                "monitorCategory": "drift",
                                "createdDate": "2024-03-20T10:00:00Z",
                                "evaluationIntervalSeconds": 3600,
                                "evaluatedAt": "2024-03-20T11:00:00Z",
                                "creator": None,
                                "notes": None,
                                "contacts": None,
                                "dimensionCategory": None,
                                "status": "triggered",
                                "isTriggered": True,
                                "isManaged": True,
                                "threshold": 0.1,
                                "thresholdMode": "single",
                                "threshold2": None,
                                "notificationsEnabled": True,
                                "updatedAt": "2024-03-20T11:00:00Z",
                                "downtimeStart": None,
                                "downtimeDurationHrs": None,
                                "downtimeFrequencyDays": None,
                                "scheduledRuntimeEnabled": False,
                                "scheduledRuntimeCadenceSeconds": None,
                                "scheduledRuntimeDaysOfWeek": None,
                                "latestComputedValue": None,
                                "performanceMetric": "accuracy",
                                "customMetric": None,
                                "operator": "lessThan",
                                "operator2": None,
                                "stdDevMultiplier": None,
                                "stdDevMultiplier2": None,
                                "dynamicAutoThresholdEnabled": None,
                                "driftMetric": None,
                                "dataQualityMetric": None,
                                "topKPercentileValue": None,
                                "positiveClassValue": None,
                                "metricAtRankingKValue": None,
                                "primaryMetricWindow": None,
                            }
                        },
                    ],
                }
            }
        }

        # Test with model_id
        mock_graphql_client.return_value.execute.return_value = mock_monitors_response
        results = client.get_all_monitors(model_id="test_model_id")
        assert len(results) == 2
        assert results[0]["name"] == "performance_monitor"
        assert results[0]["status"] == "cleared"
        assert results[0]["dimensionCategory"] == "prediction"

    @pytest.mark.parametrize(
        "input",
        [
            {
                "model_name": "test_model",
                "performance_metric": "accuracy",
                "name": "Accuracy Monitor",
                "operator": "lessThan",  # Changed from "less_than" to "lessThan"
                "threshold": 0.95,
                "model_environment_name": "production",
            },
            {
                "model_name": "test_model",
                "performance_metric": "accuracy",
                "name": "Accuracy Monitor",
                "operator": "lessThan",  # Changed from "less_than" to "lessThan"
                "threshold": 0.95,
                "notes": "Test monitor",
                "prediction_class_value": "positive",
                "email_addresses": ["test@example.com"],
                "model_environment_name": "production",
            },
        ],
    )
    def test_create_performance_monitor(self, client, mock_graphql_client, input):
        mock_graphql_client.return_value.execute.reset_mock()

        mock_response = {
            "createPerformanceMonitor": {
                "monitor": {"id": "new_monitor_id"},
            }
        }

        mock_graphql_client.return_value.execute.return_value = mock_response

        # Test with minimal required parameters using correct operator value
        monitor_url = client.create_performance_monitor(**input)
        assert monitor_url == client.monitor_url("new_monitor_id")

    @pytest.mark.parametrize(
        "input",
        [
            {
                "model_name": "test_model",
                "name": "Drift Monitor",
                "drift_metric": "psi",
                "dimension_category": "prediction",
            },
            {
                "model_name": "test_model",
                "name": "Drift Monitor",
                "drift_metric": "psi",
                "dimension_category": "prediction",
                "dimension_name": "feature_1",
                "notes": "Test monitor",
                "operator": "lessThan",
                "threshold": 0.95,
                "std_dev_multiplier": 2.0,
                "downtime_start": None,
                "downtime_duration_hrs": None,
                "downtime_frequency_days": None,
                "scheduled_runtime_enabled": False,
                "scheduled_runtime_cadence_seconds": None,
                "scheduled_runtime_days_of_week": None,
                "evaluation_window_length_seconds": 259200,
                "delay_seconds": 0,
                "threshold_mode": "single",
                "operator2": None,
                "std_dev_multiplier2": None,
            },
        ],
    )
    def test_create_drift_monitor(self, client, mock_graphql_client, input):
        mock_graphql_client.return_value.execute.reset_mock()

        mock_response = {
            "createDriftMonitor": {
                "monitor": {"id": "new_monitor_id"},
            }
        }
        mock_graphql_client.return_value.execute.return_value = mock_response

        monitor_url = client.create_drift_monitor(**input)
        assert monitor_url == client.monitor_url("new_monitor_id")

    @pytest.mark.parametrize(
        "input",
        [
            {
                "model_name": "test_model",
                "name": "Data Quality Monitor",
                "data_quality_metric": "average",
                "dimension_category": "prediction",
                "model_environment_name": "production",
            },
            {
                "model_name": "test_model",
                "name": "Data Quality Monitor",
                "data_quality_metric": "average",
                "model_environment_name": "production",
                "dimension_category": "prediction",
                "dimension_name": "feature_1",
                "notes": "Test monitor",
                "operator": "lessThan",
                "threshold": 0.95,
                "std_dev_multiplier": 2.0,
                "downtime_start": None,
                "downtime_duration_hrs": None,
                "downtime_frequency_days": None,
                "scheduled_runtime_enabled": False,
                "scheduled_runtime_cadence_seconds": None,
                "scheduled_runtime_days_of_week": None,
                "evaluation_window_length_seconds": 259200,
                "delay_seconds": 0,
                "threshold_mode": "single",
                "operator2": None,
                "std_dev_multiplier2": None,
            },
        ],
    )
    def test_create_data_quality_monitor(self, client, mock_graphql_client, input):
        mock_graphql_client.return_value.execute.reset_mock()

        mock_response = {
            "createDataQualityMonitor": {
                "monitor": {"id": "new_monitor_id"},
            }
        }
        mock_graphql_client.return_value.execute.return_value = mock_response

        # Test with minimal required parameters
        monitor_url = client.create_data_quality_monitor(**input)
        assert monitor_url == client.monitor_url("new_monitor_id")

    @pytest.mark.parametrize(
        "input, expected_error",
        [
            (
                {
                    "model_name": "test_model",
                    "name": "Performance Monitor",
                    "performance_metric": "nothing",
                    "operator": "lessThan",
                    "threshold": 0.95,
                    "model_environment_name": "production",
                },
                "performanceMetric",
            ),
            (
                {
                    "model_name": "test_model",
                    "name": "Performance Monitor",
                    "performance_metric": "accuracy",
                    "operator": "invalid_operator",
                    "threshold": 0.95,
                    "model_environment_name": "production",
                },
                "operator",
            ),
        ],
    )
    def test_create_performance_monitor_validation(
        self, client, mock_graphql_client, input, expected_error
    ):
        """Test creating a performance metric monitor with invalid parameters"""

        # Reset mock for this test
        mock_graphql_client.return_value.execute.reset_mock()

        with pytest.raises(Exception) as exc_info:
            client.create_performance_monitor(**input)
        assert expected_error in str(exc_info.value)


class TestLanguageModel:
    def test_create_annotation(self, client, mock_graphql_client):
        mock_graphql_client.return_value.execute.reset_mock()

        mock_response = {
            "updateAnnotations": {
                "clientMutationId": None,
            },
        }
        mock_graphql_client.return_value.execute.return_value = mock_response

        annotation_result = client.create_annotation(
            name="test",
            label="test",
            updated_by="test",
            annotation_type="label",
            model_id="test_model_id",
            record_id="test_record_id",
            model_environment="tracing",
            note="test",
            start_time="2024-01-01T00:00:00Z",
        )
        assert annotation_result is True

    def test_get_all_prompts(self, client, mock_graphql_client):
        mock_graphql_client.return_value.execute.reset_mock()

        mock_response = [
            {
                "node": {
                    "prompts": {
                        "pageInfo": {"hasNextPage": True, "endCursor": "1234"},
                        "edges": [
                            {
                                "node": {
                                    "id": "prompt_id",
                                    "name": "test_prompt",
                                    "description": "test_description",
                                    "tags": ["test_tag"],
                                    "commitMessage": "test_commit_message",
                                    "inputVariableFormat": "f_string",
                                    "toolCalls": [
                                        {
                                            "id": "tool_call_id",
                                            "name": "test_tool_name",
                                            "description": "test_tool_description",
                                            "parameters": "test_tool_parameters",
                                            "function": {
                                                "name": "test_function_name",
                                                "description": "test_function_description",
                                            },
                                        }
                                    ],
                                    "llmParameters": {"temperature": 0.5},
                                    "provider": "openai",
                                    "modelName": "gpt-3.5-turbo",
                                    "createdAt": "2024-01-01T00:00:00Z",
                                    "updatedAt": "2024-01-01T00:00:00Z",
                                    "messages": [
                                        {
                                            "id": "message_id",
                                            "role": "user",
                                            "content": "test_content",
                                        }
                                    ],
                                }
                            }
                        ],
                    }
                }
            },
            {
                "node": {
                    "prompts": {
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                        "edges": [
                            {
                                "node": {
                                    "id": "prompt_id_2",
                                    "name": "test_prompt_2",
                                    "description": "test_description_2",
                                    "tags": ["test_tag_2"],
                                    "commitMessage": "test_commit_message_2",
                                    "inputVariableFormat": "f_string",
                                    "toolCalls": [
                                        {
                                            "id": "tool_call_id_2",
                                            "name": "test_tool_name_2",
                                            "description": "test_tool_description_2",
                                            "parameters": "test_tool_parameters_2",
                                        }
                                    ],
                                    "llmParameters": {"temperature": 0.5},
                                    "provider": "openai",
                                    "modelName": "gpt-3.5-turbo",
                                    "createdAt": "2024-01-01T00:00:00Z",
                                    "updatedAt": "2024-01-01T00:00:00Z",
                                    "messages": [
                                        {
                                            "id": "message_id",
                                            "role": "user",
                                            "content": "test_content",
                                        }
                                    ],
                                }
                            }
                        ],
                    }
                }
            },
        ]
        mock_graphql_client.return_value.execute.side_effect = mock_response

        prompts = client.get_all_prompts()
        assert len(prompts) == 2
        assert prompts[0]["id"] == "prompt_id"
        assert prompts[1]["id"] == "prompt_id_2"
        assert prompts[0]["name"] == "test_prompt"
        assert prompts[1]["name"] == "test_prompt_2"
        assert prompts[0]["description"] == "test_description"
        assert prompts[1]["description"] == "test_description_2"
        assert prompts[0]["tags"] == ["test_tag"]
        assert prompts[1]["tags"] == ["test_tag_2"]
        assert prompts[0]["commitMessage"] == "test_commit_message"
        assert prompts[1]["commitMessage"] == "test_commit_message_2"
        assert prompts[0]["inputVariableFormat"] == "F_STRING"
        assert prompts[1]["inputVariableFormat"] == "F_STRING"

    def test_get_prompt_by_id(self, client, mock_graphql_client):
        mock_graphql_client.return_value.execute.reset_mock()

        mock_response = {
            "node": {
                "id": "prompt_id",
                "name": "test_prompt",
                "description": "test_description",
                "tags": ["test_tag"],
                "commitMessage": "test_commit_message",
                "inputVariableFormat": "f_string",
                "toolCalls": [
                    {
                        "id": "tool_call_id",
                        "name": "test_tool_name",
                        "description": "test_tool_description",
                        "parameters": "test_tool_parameters",
                        "function": {
                            "name": "test_function_name",
                            "description": "test_function_description",
                        },
                    }
                ],
                "llmParameters": {"temperature": 0.5},
                "provider": "openai",
                "modelName": "gpt-3.5-turbo",
                "createdAt": "2024-01-01T00:00:00Z",
                "updatedAt": "2024-01-01T00:00:00Z",
                "messages": [
                    {
                        "id": "message_id",
                        "role": "user",
                        "content": "test_content",
                    }
                ],
            }
        }
        mock_graphql_client.return_value.execute.return_value = mock_response

        prompt_result = client.get_prompt_by_id("prompt_id")
        assert prompt_result["id"] == "prompt_id"
        assert prompt_result["name"] == "test_prompt"
        assert prompt_result["description"] == "test_description"
        assert prompt_result["tags"] == ["test_tag"]
        assert prompt_result["commitMessage"] == "test_commit_message"
        assert prompt_result["inputVariableFormat"] == "F_STRING"
        assert prompt_result["toolCalls"] == [
            {
                "id": "tool_call_id",
                "name": "test_tool_name",
                "description": "test_tool_description",
                "parameters": "test_tool_parameters",
                "function": {
                    "name": "test_function_name",
                    "description": "test_function_description",
                },
            }
        ]
        assert prompt_result["llmParameters"] == {"temperature": 0.5}
        assert prompt_result["provider"] == "openAI"
        assert prompt_result["modelName"] == "GPT_3_5_TURBO"
        assert prompt_result["createdAt"] == "2024-01-01T00:00:00.000000Z"
        assert prompt_result["updatedAt"] == "2024-01-01T00:00:00.000000Z"
        assert prompt_result["messages"] == [
            {
                "id": "message_id",
                "role": "user",
                "content": "test_content",
            }
        ]

    def test_get_prompt(self, client, mock_graphql_client):
        mock_graphql_client.return_value.execute.reset_mock()

        mock_responses = {
            "node": {
                "prompts": {
                    "edges": [
                        {
                            "node": {
                                "id": "prompt_id",
                                "name": "test_prompt",
                                "description": "test_description",
                                "tags": ["test_tag"],
                                "commitMessage": "test_commit_message",
                                "inputVariableFormat": "f_string",
                                "toolCalls": [
                                    {
                                        "id": "tool_call_id",
                                        "name": "test_tool_name",
                                    }
                                ],
                                "llmParameters": {"temperature": 0.5},
                                "provider": "openai",
                                "modelName": "gpt-3.5-turbo",
                                "createdAt": "2024-01-01T00:00:00Z",
                                "updatedAt": "2024-01-01T00:00:00Z",
                                "messages": [
                                    {
                                        "id": "message_id",
                                        "role": "user",
                                        "content": "test_content",
                                    }
                                ],
                            }
                        }
                    ]
                }
            }
        }
        mock_graphql_client.return_value.execute.return_value = mock_responses

        prompt_result = client.get_prompt("test_prompt")
        assert prompt_result["id"] == "prompt_id"
        assert prompt_result["name"] == "test_prompt"
        assert prompt_result["description"] == "test_description"
        assert prompt_result["tags"] == ["test_tag"]
        assert prompt_result["commitMessage"] == "test_commit_message"
        assert prompt_result["inputVariableFormat"] == "F_STRING"
        assert prompt_result["toolCalls"] == [
            {
                "id": "tool_call_id",
                "name": "test_tool_name",
            }
        ]
        assert prompt_result["llmParameters"] == {"temperature": 0.5}
        assert prompt_result["provider"] == "openAI"
        assert prompt_result["modelName"] == "GPT_3_5_TURBO"
        assert prompt_result["createdAt"] == "2024-01-01T00:00:00.000000Z"
        assert prompt_result["updatedAt"] == "2024-01-01T00:00:00.000000Z"
        assert prompt_result["messages"] == [
            {
                "id": "message_id",
                "role": "user",
                "content": "test_content",
            }
        ]

    def test_get_formatted_prompt(self, client, mock_graphql_client):
        mock_graphql_client.return_value.execute.reset_mock()

        mock_response = {
            "node": {
                "prompts": {
                    "edges": [
                        {
                            "node": {
                                "id": "prompt_id",
                                "name": "test_prompt",
                                "description": "test_description",
                                "tags": ["test_tag"],
                                "commitMessage": "test_commit_message",
                                "inputVariableFormat": "f_string",
                                "toolCalls": [
                                    {
                                        "id": "tool_call_id",
                                        "name": "test_tool_name",
                                    }
                                ],
                                "llmParameters": {"temperature": 0.5},
                                "provider": "openai",
                                "modelName": "gpt-3.5-turbo",
                                "createdAt": "2024-01-01T00:00:00Z",
                                "updatedAt": "2024-01-01T00:00:00Z",
                                "messages": [
                                    {
                                        "id": "message_id",
                                        "role": "user",
                                        "content": "Hello, {variable_1} - i am {variable_2}",
                                    }
                                ],
                            }
                        }
                    ]
                }
            }
        }
        mock_graphql_client.return_value.execute.return_value = mock_response

        formatted_prompt = client.get_formatted_prompt(
            "prompt_id", variable_1="John", variable_2="a software engineer"
        )
        assert formatted_prompt.messages == [
            {
                "id": "message_id",
                "role": "user",
                "content": "Hello, John - i am a software engineer",
            }
        ]

    @pytest.mark.parametrize(
        "input,get_prompt_output,create_prompt_output, id, version_id",
        [
            (
                {
                    "name": "test_prompt_1",
                    "description": "test_description_1",
                    "tags": ["test_tag_1"],
                    "commit_message": "test_commit_message_1",
                    "messages": [
                        {
                            "role": "user",
                            "content": "Hello, {variable_1} - i am {variable_2}",
                        }
                    ],
                    "input_variable_format": "f_string",
                    "provider": "openai",
                },
                {
                    "node": {
                        "prompts": {
                            "edges": [
                                {
                                    "node": {
                                        "id": "prompt_id",
                                        "name": "test_prompt",
                                        "description": "test_description",
                                        "tags": ["test_tag"],
                                        "commitMessage": "test_commit_message",
                                        "inputVariableFormat": "f_string",
                                        "toolCalls": [
                                            {
                                                "id": "tool_call_id",
                                                "name": "test_tool_name",
                                            }
                                        ],
                                        "llmParameters": {"temperature": 0.5},
                                        "provider": "openai",
                                        "modelName": "gpt-3.5-turbo",
                                        "createdAt": "2024-01-01T00:00:00Z",
                                        "updatedAt": "2024-01-01T00:00:00Z",
                                        "messages": [
                                            {
                                                "id": "message_id",
                                                "role": "user",
                                                "content": "test_content",
                                            }
                                        ],
                                    }
                                }
                            ]
                        }
                    }
                },
                {
                    "createPromptVersion": {
                        "promptVersion": {
                            "id": "prompt_version_id",
                            "name": "test_prompt",
                            "description": "test_description",
                            "tags": ["test_tag"],
                            "commitMessage": "test_commit_message",
                            "inputVariableFormat": "f_string",
                            "provider": "openai",
                            "modelName": "gpt-3.5-turbo",
                            "createdAt": "2024-01-01T00:00:00Z",
                            "updatedAt": "2024-01-01T00:00:00Z",
                            "messages": [
                                {
                                    "id": "message_id",
                                    "role": "user",
                                    "content": "Hello, {variable_1} - i am {variable_2}",
                                }
                            ],
                            "toolCalls": [
                                {
                                    "id": "tool_call_id",
                                    "name": "test_tool_name",
                                }
                            ],
                            "llmParameters": {
                                "temperature": 0.5,
                            },
                        }
                    }
                },
                "prompt_id",
                "prompt_version_id",
            ),
            (
                {
                    "name": "test_prompt_2",
                    "description": "test_description_2",
                    "tags": ["test_tag_2"],
                    "commit_message": "test_commit_message_2",
                    "input_variable_format": "f_string",
                    "messages": [
                        {
                            "role": "user",
                            "content": "Hello, {variable_1} - i am {variable_2}",
                        }
                    ],
                    "tool_choice": {
                        "choice": "required",
                        "tool": {
                            "type": "function",
                            "function": {"name": "test_function_name"},
                        },
                    },
                    "invocation_params": {
                        "temperature": 0.5,
                        "top_p": 1.0,
                        "stop": ["stop_sequence_1", "stop_sequence_2"],
                        "max_tokens": 100,
                        "max_completion_tokens": 100,
                        "presence_penalty": 0.0,
                    },
                    "provider": "openai",
                },
                {"node": {"prompts": {"edges": []}}},
                {
                    "createPrompt": {
                        "prompt": {
                            "id": "prompt_id_2",
                            "name": "test_prompt_2",
                            "description": "test_description_2",
                            "tags": ["test_tag_2"],
                            "commitMessage": "test_commit_message_2",
                            "inputVariableFormat": "f_string",
                            "provider": "openai",
                            "modelName": "gpt-3.5-turbo",
                            "createdAt": "2024-01-01T00:00:00Z",
                            "updatedAt": "2024-01-01T00:00:00Z",
                            "messages": [
                                {
                                    "id": "message_id",
                                    "role": "user",
                                    "content": "Hello, {variable_1} - i am {variable_2}",
                                }
                            ],
                            "toolCalls": [
                                {
                                    "type": "function",
                                    "function": {"name": "test_function_name"},
                                }
                            ],
                            "llmParameters": {
                                "temperature": 0.5,
                                "top_p": 1.0,
                                "stop": ["stop_sequence_1", "stop_sequence_2"],
                                "max_tokens": 100,
                                "max_completion_tokens": 100,
                            },
                        }
                    }
                },
                "prompt_id_2",
                None,
            ),
        ],
    )
    def test_create_prompt(
        self,
        client,
        mock_graphql_client,
        input,
        get_prompt_output,
        create_prompt_output,
        id,
        version_id,
    ):
        mock_graphql_client.return_value.execute.reset_mock()
        client.space_id = "234567890"
        client.org_id = "1234567890"
        mock_graphql_client.return_value.execute.side_effect = [
            get_prompt_output,
            create_prompt_output,
        ]
        result = client.create_prompt(**input)
        expected_url = f"https://app.arize.com/organizations/{client.org_id}/spaces/{client.space_id}/prompt-hub/{id}"
        if version_id:
            assert result == f"{expected_url}?version={version_id}"
        else:
            assert result == expected_url
