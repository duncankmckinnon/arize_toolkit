import logging
import os
from datetime import datetime, timedelta, timezone
from time import sleep
from typing import Dict, List, Literal, Optional, Tuple, Union

from gql import Client as GraphQLClient
from gql.transport.requests import RequestsHTTPTransport
from pandas import DataFrame

from arize_toolkit.exceptions import ArizeAPIException
from arize_toolkit.model_managers import MonitorManager
from arize_toolkit.queries.custom_metric_queries import (
    CreateCustomMetricMutation,
    DeleteCustomMetricMutation,
    GetAllCustomMetricsByModelIdQuery,
    GetAllCustomMetricsQuery,
    GetCustomMetricByIDQuery,
    GetCustomMetricQuery,
    UpdateCustomMetricMutation,
)
from arize_toolkit.queries.language_models import (
    CreateAnnotationMutation,
    CreatePromptMutation,
    CreatePromptVersionMutation,
    DeletePromptMutation,
    GetAllPromptsQuery,
    GetAllPromptVersionsQuery,
    GetPromptByIDQuery,
    GetPromptQuery,
    UpdatePromptMutation,
)
from arize_toolkit.queries.model_queries import DeleteDataMutation, GetAllModelsQuery, GetModelByIDQuery, GetModelQuery, GetModelVolumeQuery, GetPerformanceMetricValuesQuery
from arize_toolkit.queries.monitor_queries import (
    CreateDataQualityMonitorMutation,
    CreateDriftMonitorMutation,
    CreatePerformanceMonitorMutation,
    DeleteMonitorMutation,
    GetAllModelMonitorsQuery,
    GetMonitorByIDQuery,
    GetMonitorQuery,
)
from arize_toolkit.queries.space_queries import OrgIDandSpaceIDQuery
from arize_toolkit.utils import FormattedPrompt, parse_datetime

logger = logging.getLogger("arize_toolkit")


class Client:
    """Client for the Arize API

    Args:
        - `organization` (str): The Arize organization name
        - `space` (str): The Arize space name
        - `arize_developer_key` (Optional[str]): The API key. This can be copied from the space settings page in Arize.
        - `arize_app_url` (Optional[str]): The URL of the Arize API (default for SaaS is https://app.arize.com). For on-prem deployments, this will need to be set to the URL of Arize app.
        - `sleep_time` (Optional[int]): The number of seconds to sleep between API requests (may be needed if rate limiting is an issue)
    (Note: ARIZE_DEVELOPER_KEY environment variable can be set instead of passing in `arize_developer_key`)

    Properties:
        space (str): The Arize space name
        organization (str): The Arize organization name
        org_id (str): The Arize organization ID
        space_id (str): The Arize space ID
        sleep_time (int): The sleep time between API requests
        arize_app_url (str): The URL of the Arize API
        space_url (str): The URL of the current space

    """

    org_id: str
    space_id: str

    def __init__(
        self,
        organization: str,
        space: str,
        arize_developer_key: Optional[str] = None,
        arize_app_url: str = "https://app.arize.com",
        sleep_time: int = 0,
    ):
        self.organization = organization
        self.space = space
        self.sleep_time = sleep_time
        self.arize_app_url = arize_app_url
        arize_developer_key = arize_developer_key or os.getenv("ARIZE_DEVELOPER_KEY")
        self._graphql_client = GraphQLClient(
            transport=RequestsHTTPTransport(
                url=f"{self.arize_app_url}/graphql",
                headers={"x-api-key": arize_developer_key},
            )
        )
        self._set_org_and_space_id()

    def _set_org_and_space_id(self) -> None:
        results = OrgIDandSpaceIDQuery.run_graphql_query(self._graphql_client, organization=self.organization, space=self.space)
        self.org_id = results.organization_id
        self.space_id = results.space_id

    def set_sleep_time(self, sleep_time: int) -> "Client":
        """Updates the sleep time between API requests.

        Args:
            sleep_time (int): The number of seconds to sleep between API requests

        Returns:
            Client: The updated client

        """
        self.sleep_time = sleep_time
        return self

    def switch_space(self, space: str, organization: Optional[str] = None) -> str:
        """Switches the space for the client. Can also switch to a space in a different organization.

        Args:
            space (str): The space to switch to
            organization (Optional[str]): The organization to switch to (defaults to the current organization)

        Returns:
            str: The URL of the new space

        """
        space = space
        organization = organization or self.organization
        result = OrgIDandSpaceIDQuery.run_graphql_query(self._graphql_client, organization=organization, space=space)
        if self.space_id != result.space_id:
            self.org_id = result.organization_id
            self.space_id = result.space_id
            self.organization = organization
            self.space = space
        return self.space_url

    @property
    def space_url(self) -> str:
        return f"{self.arize_app_url}/organizations/{self.org_id}/spaces/{self.space_id}"

    def model_url(self, model_id: str) -> str:
        return f"{self.space_url}/models/{model_id}"

    def custom_metric_url(self, model_id: str, custom_metric_id: str) -> str:
        return f"{self.model_url(model_id)}/custom_metrics/{custom_metric_id}"

    def monitor_url(self, monitor_id: str) -> str:
        return f"{self.space_url}/monitors/{monitor_id}"

    def prompt_url(self, prompt_id: str) -> str:
        return f"{self.space_url}/prompt-hub/{prompt_id}"

    def prompt_version_url(self, prompt_id: str, prompt_version_id: str) -> str:
        return f"{self.prompt_url(prompt_id)}?version={prompt_version_id}"

    def get_all_models(self) -> List[dict]:
        """Retrieves all models in the current space.

        Returns:
            List[dict]: A list of model dictionaries, each containing:
            - id (str): Unique identifier for the model
            - name (str): Name of the model
            - modelType (ModelType): Type of the model (e.g. numeric, categorical)
            - createdAt (datetime): When the model was created
            - isDemoModel (bool): Whether this is a demo model

        Raises:
            ArizeAPIException: If there is an error retrieving models from the API

        """
        results = GetAllModelsQuery.iterate_over_pages(self._graphql_client, space_id=self.space_id, sleep_time=self.sleep_time)
        return [result.to_dict() for result in results]

    def get_model_by_id(self, model_id: str) -> dict:
        """Retrieves a specific model by ID.

        Args:
            model_id (str): The ID of the model to retrieve

        Returns:
            dict: A dictionary containing model information:
            - id (str): Unique identifier for the model
            - name (str): Name of the model
            - modelType (ModelType): Type of the model
            - createdAt (datetime): When the model was created
            - isDemoModel (bool): Whether this is a demo model

        Raises:
            ArizeAPIException: If the model is not found or there is an API error

        """
        results = GetModelByIDQuery.run_graphql_query(self._graphql_client, model_id=model_id, space_id=self.space_id)
        return results.to_dict()

    def get_model(self, model_name: str) -> dict:
        """Retrieves a specific model by name from the current space.

        Args:
            model_name (str): The name of the model to retrieve

        Returns:
            dict: A dictionary containing model information:
            - id (str): Unique identifier for the model
            - name (str): Name of the model
            - modelType (ModelType): Type of the model
            - createdAt (datetime): When the model was created
            - isDemoModel (bool): Whether this is a demo model

        Raises:
            ArizeAPIException: If the model is not found or there is an API error

        """
        results = GetModelQuery.run_graphql_query(self._graphql_client, model_name=model_name, space_id=self.space_id)
        return results.to_dict()

    def get_model_url(self, model_name: str) -> str:
        """Retrieves the path to a specific model by name from the current space.

        Args:
            model_name (str): The name of the model to retrieve

        Returns:
            str: The path to the model

        """
        model = GetModelQuery.run_graphql_query(self._graphql_client, model_name=model_name, space_id=self.space_id)
        return self.model_url(model.id)

    def get_model_volume_by_id(
        self,
        model_id: str,
        start_time: Optional[Union[datetime, str]] = None,
        end_time: Optional[Union[datetime, str]] = None,
    ) -> dict:
        """Retrieves prediction volume statistics for a specific model by ID.

        If start_time and end_time are not provided, the default is the previous 30 days.

        Args:
            model_id (str): The ID of the model to get volume for
            start_time (Optional[datetime | str]): Start time for volume calculation.
            end_time (Optional[datetime | str]): End time for volume calculation.

        Returns:
            int: The total number of predictions in the time period

        Raises:
            ArizeAPIException: If the model is not found or there is an API error

        """
        if start_time:
            start_time = parse_datetime(start_time)
        if end_time:
            end_time = parse_datetime(end_time)
        results = GetModelVolumeQuery.run_graphql_query(
            self._graphql_client,
            model_id=model_id,
            start_time=start_time,
            end_time=end_time,
        )
        return results.totalVolume

    def get_model_volume(
        self,
        model_name: str,
        start_time: Optional[Union[datetime, str]] = None,
        end_time: Optional[Union[datetime, str]] = None,
    ) -> dict:
        """Retrieves prediction volume statistics for a specific model.
        If start_time and end_time are not provided, the default is the previous 30 days.

        Args:
            model_name (str): The name of the model to get volume for
            start_time (Optional[datetime | str]): Start time for volume calculation.
                If None, uses the earliest available data.
            end_time (Optional[datetime | str]): End time for volume calculation.
                If None, uses the latest available data.

        Returns:
            int: The total number of predictions in the time period

        Raises:
            ArizeAPIException: If the model is not found or there is an API error

        """
        model = GetModelQuery.run_graphql_query(
            self._graphql_client,
            model_name=model_name,
            space_id=self.space_id,
        )
        return self.get_model_volume_by_id(model_id=model.id, start_time=start_time, end_time=end_time)

    def get_total_volume(
        self,
        start_time: Optional[Union[datetime, str]] = None,
        end_time: Optional[Union[datetime, str]] = None,
    ) -> Tuple[int, Dict[str, int]]:
        """Retrieves prediction volume statistics for all models in the space.
        If start_time and end_time are not provided, the default is the previous 30 days.

        Args:
            start_time (Optional[datetime | str]): Start time for volume calculation.
            end_time (Optional[datetime | str]): End time for volume calculation.

        Returns:
            Tuple[int, Dict[str, int]]: A tuple containing:
            - int: The total number of predictions in the time period
            - Dict[str, int]: A dictionary mapping model names to their prediction volumes

        Raises:
            ArizeAPIException: If the space is not found or there is an API error

        """
        if start_time:
            start_time = parse_datetime(start_time)
        if end_time:
            end_time = parse_datetime(end_time)
        models = GetAllModelsQuery.iterate_over_pages(
            self._graphql_client,
            space_id=self.space_id,
            sleep_time=self.sleep_time,
        )
        total_volume = 0
        model_volumes = {}

        for model in models:
            sleep(self.sleep_time)
            model_id = model.id
            model_name = model.name
            model_volume = self.get_model_volume_by_id(model_id, start_time, end_time)
            total_volume += model_volume
            model_volumes[model_name] = model_volume

        return total_volume, model_volumes

    def delete_data_by_id(
        self,
        model_id: str,
        start_time: Union[datetime, str],
        end_time: Optional[Union[datetime, str]] = None,
        environment: Literal["PRODUCTION", "PREPRODUCTION"] = "PRODUCTION",
    ) -> bool:
        """Deletes data from a model for a given time range and environment.

        Args:
            model_id (str): The ID of the model to delete data from
            start_time (datetime | str): The start time of the time range to delete data from
            end_time (Optional[datetime | str]): The end time of the time range to delete data from (defaults to now)
            environment (Literal["PRODUCTION", "PREPRODUCTION"]): The environment to delete data from (defaults to PRODUCTION)

        Returns:
            bool: True if the data was deleted successfully, False otherwise

        Raises:
            ArizeAPIException: If the model is not found or there is an API error

        """
        if start_time:
            start_time = parse_datetime(start_time)
        if end_time:
            end_time = parse_datetime(end_time)
        variables = {
            "modelId": model_id,
            "startTime": start_time,
            "environment": environment.upper(),
        }
        if end_time and end_time > start_time:
            variables["endTime"] = end_time

        result = DeleteDataMutation.run_graphql_mutation(
            self._graphql_client,
            **variables,
        )
        return result.success

    def delete_data(
        self,
        model_name: str,
        start_time: Union[datetime, str],
        end_time: Optional[Union[datetime, str]] = None,
        environment: Literal["PRODUCTION", "PREPRODUCTION"] = "PRODUCTION",
    ) -> bool:
        """Deletes data from a model for a given time range and environment.

        Args:
            model_name (str): The name of the model to delete data from
            start_time (datetime | str): The start time of the time range to delete data from
            end_time (Optional[datetime | str]): The end time of the time range to delete data from (defaults to now)
            environment (Literal["PRODUCTION", "PREPRODUCTION"]): The environment to delete data from (defaults to PRODUCTION)

        Returns:
            bool: True if the data was deleted successfully, False otherwise

        Raises:
            ArizeAPIException: If the model is not found or there is an API error

        """
        model = GetModelQuery.run_graphql_query(
            self._graphql_client,
            model_name=model_name,
            space_id=self.space_id,
        )
        return self.delete_data_by_id(model.id, start_time, end_time, environment)

    def get_performance_metric_over_time(
        self,
        metric: str,
        environment: str,
        model_id: Optional[str] = None,
        model_name: Optional[str] = None,
        granularity: str = "month",
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        to_dataframe: bool = True,
    ) -> Union[List[dict], DataFrame]:
        """Get the performance metric over time for a model.

        Args:
            metric (str): The name of the metric to get the performance metric over time for (e.g. "accuracy", "f_1", "precision", "recall", "auc_roc", ...)
            environment (str): The environment to get the performance metric over time for (options are "production", "staging", "development", "tracing")
            model_id (Optional[str]): The ID of the model to get the performance metric over time for (either model_id or model_name must be provided)
            model_name (Optional[str]): The name of the model to get the performance metric over time for (either model_id or model_name must be provided)
            granularity (Optional[str]): The granularity of the performance metric over time (options are "hour", "day", "week", "month", default is "month")
            start_time (Optional[datetime | str]): The start time of the performance metric over time (defaults to 30 days ago)
            end_time (Optional[datetime | str]): The end time of the performance metric over time (defaults to now)
            to_dataframe (bool): Whether to return the performance metrics as list of dictionaries or a pandas DataFrame with columns "metricDisplayDate" and "metricValue" (default is True)

        Returns:
            Union[List[dict], DataFrame]: A list of dictionaries containing the performance metric over time for each data window or
            a pandas DataFrame with columns "metricDisplayDate" and "metricValue"

        """
        if not model_id and not model_name:
            raise ValueError("Either model_id or model_name must be provided")
        if not model_id:
            model = GetModelQuery.run_graphql_query(
                self._graphql_client,
                model_name=model_name,
                space_id=self.space_id,
            )
            model_id = model.id
        if start_time:
            start_time = parse_datetime(start_time)
        else:
            # default to 30 days ago
            start_time = datetime.now(tz=timezone.utc) - timedelta(days=30)
        if end_time:
            end_time = parse_datetime(end_time)
        else:
            # default to now
            end_time = datetime.now(tz=timezone.utc)

        if start_time > end_time:
            # verify start_time is before end_time
            raise ValueError("start_time must be before end_time")

        results = GetPerformanceMetricValuesQuery.run_graphql_query_to_list(
            self._graphql_client,
            modelId=model_id,
            metric=metric,
            environment=environment,
            granularity=granularity,
            startDate=start_time,
            endDate=end_time,
        )
        list_of_results = [result.to_dict() for result in results]
        if to_dataframe and len(list_of_results) > 0:
            return DataFrame.from_records(list_of_results)
        return list_of_results

    def create_annotation(
        self,
        name: str,
        updated_by: str,
        record_id: str,
        annotation_type: Literal["label", "score"],
        model_id: Optional[str] = None,
        model_name: Optional[str] = None,
        label: Optional[str] = None,
        score: Optional[float] = None,
        note: Optional[str] = None,
        model_environment: Optional[str] = None,
        start_time: Optional[Union[datetime, str]] = None,
    ) -> bool:
        """Creates an annotation on a record for a model.

        Args:
            name (str): The name of the annotation
            updated_by (str): The user who updated the annotation
            record_id (str): The ID of the record to annotate
            annotation_type (Literal["label", "score"]): The type of annotation
            model_id (Optional[str]): The ID of the model to annotate (either model_id or model_name must be provided)
            model_name (Optional[str]): The name of the model to annotate (either model_id or model_name must be provided)
            label (Optional[str]): The label of the annotation (required if annotation_type is "label")
            score (Optional[float]): The score of the annotation (required if annotation_type is "score")
            note (Optional[str]): A note to accompany the annotation
            model_environment (Optional[str]): The environment of the model (options are "production", "staging", "development", "tracing", defaults to "tracing")
            start_time (Optional[datetime | str]): The start time of the annotation (defaults to now)

        Returns:
            bool: True if the annotation was created successfully, False otherwise

        Raises:
            ValueError: If neither model_id nor model_name is provided or annotation_type does not match annotation given
            ArizeAPIException: If the model is not found or there is an API error

        """
        if not model_id and not model_name:
            raise ValueError("Either model_id or model_name must be provided")
        if not model_id:
            model = GetModelQuery.run_graphql_query(
                self._graphql_client,
                model_name=model_name,
                space_id=self.space_id,
            )
            model_id = model.id
        inputs = {
            "modelId": model_id,
            "recordId": record_id,
            "annotations": [
                {
                    "name": name,
                    "updatedBy": updated_by,
                    "label": label,
                    "score": score,
                    "annotationType": annotation_type,
                }
            ],
        }
        if start_time:
            inputs["startTime"] = parse_datetime(start_time)
        if note:
            inputs["note"] = {"text": note}
        if model_environment:
            inputs["modelEnvironment"] = model_environment
        result = CreateAnnotationMutation.run_graphql_mutation(
            self._graphql_client,
            **inputs,
        )
        return result.success

    def get_all_prompts(self) -> List[dict]:
        """Retrieves all prompts in the space.

        Returns:
            List[dict]: A list of prompt dictionaries, each containing:
            - id (str): The ID of the prompt
            - name (str): The name of the prompt
            - description (str): The description of the prompt
            - tags (List[str]): The tags of the prompt
            - commitMessage (str): The commit message of the prompt
            - createdBy (dict): The user who created the prompt
            - messages (List[dict]): The messages of the prompt
            - inputVariableFormat (str): The input variable format of the prompt
            - toolChoice (str): The tool choice of the prompt
            - toolCalls (List[dict]): The tool calls of the prompt
            - llmParameters (dict): The LLM parameters of the prompt
            - createdAt (datetime): The date and time the prompt was created
            - updatedAt (datetime): The date and time the prompt was last updated
            - provider (str): The provider of the prompt
            - modelName (str): The model name of the prompt

        Raises:
            ArizeAPIException: If the prompt is not found or there is an API error

        """
        results = GetAllPromptsQuery.iterate_over_pages(
            self._graphql_client,
            sleep_time=self.sleep_time,
            space_id=self.space_id,
        )
        return [result.to_dict() for result in results]

    def get_prompt_by_id(self, prompt_id: str) -> dict:
        """Retrieves a prompt by ID.

        Args:
            prompt_id (str): The ID of the prompt to retrieve

        Returns:
            dict: A dictionary containing the prompt information
            - id (str): The ID of the prompt
            - name (str): The name of the prompt
            - description (str): The description of the prompt
            - tags (List[str]): The tags of the prompt
            - commitMessage (str): The commit message of the prompt
            - createdBy (dict): The user who created the prompt
            - messages (List[dict]): The messages of the prompt
            - inputVariableFormat (str): The input variable format of the prompt
            - toolChoice (str): The tool choice of the prompt
            - toolCalls (List[dict]): The tool calls of the prompt
            - llmParameters (dict): The LLM parameters of the prompt
            - createdAt (datetime): The date and time the prompt was created
            - updatedAt (datetime): The date and time the prompt was last updated
            - provider (str): The provider of the prompt
            - modelName (str): The model name of the prompt


        Raises:
            ArizeAPIException: If the prompt is not found or there is an API error

        """
        result = GetPromptByIDQuery.run_graphql_query(
            self._graphql_client,
            prompt_id=prompt_id,
        )
        return result.to_dict()

    def get_prompt(self, prompt_name: str) -> dict:
        """Retrieves a prompt by name.

        Args:
            prompt_name (str): The name of the prompt to retrieve

        Returns:
            dict: A dictionary containing the prompt information
            - id (str): The ID of the prompt
            - name (str): The name of the prompt
            - description (str): The description of the prompt
            - tags (List[str]): The tags of the prompt
            - commitMessage (str): The commit message of the prompt
            - createdBy (dict): The user who created the prompt
            - messages (List[dict]): The messages of the prompt
            - inputVariableFormat (str): The input variable format of the prompt
            - toolChoice (str): The tool choice of the prompt
            - toolCalls (List[dict]): The tool calls of the prompt
            - llmParameters (dict): The LLM parameters of the prompt
            - createdAt (datetime): The date and time the prompt was created
            - updatedAt (datetime): The date and time the prompt was last updated
            - provider (str): The provider of the prompt
            - modelName (str): The model name of the prompt

        Raises:
            ArizeAPIException: If the prompt is not found or there is an API error

        """
        result = GetPromptQuery.run_graphql_query(
            self._graphql_client,
            prompt_name=prompt_name,
            space_id=self.space_id,
        )
        return result.to_dict()

    def get_formatted_prompt(self, prompt_name: str, **variables) -> FormattedPrompt:
        """Retrieves a formatted prompt by name.

        Args:
            prompt_name (str): The name of the prompt to retrieve
            **variables (dict): The variables to format the prompt with

        Returns:
            FormattedPrompt: The formatted prompt

        Raises:
            ArizeAPIException: If the prompt is not found or there is an API error

        """
        prompt = GetPromptQuery.run_graphql_query(
            self._graphql_client,
            prompt_name=prompt_name,
            space_id=self.space_id,
        )
        return prompt.format(**variables)

    def get_all_prompt_versions(self, prompt_name: str) -> List[dict]:
        """Retrieves all prompt versions for a prompt.

        Args:
            prompt_name (str): The name of the prompt to retrieve

        Returns:
            List[dict]: A list of prompt version dictionaries, each containing:
            - id (str): The ID of the prompt version
            - commitMessage (str): The commit message of the prompt version
            - provider (str): The provider of the prompt version
            - modelName (str): The model name of the prompt version
            - messages (List[dict]): The messages of the prompt version
            - inputVariableFormat (str): The input variable format of the prompt version
            - toolChoice (str): The tool choice of the prompt version
            - toolCalls (List[dict]): The tool calls of the prompt version
            - llmParameters (dict): The LLM parameters of the prompt version
            - createdBy (dict): The user who created the prompt version
            - createdAt (datetime): The date and time the prompt version was created

        Raises:
            ArizeAPIException: If the prompt is not found or there is an API error

        """
        results = GetAllPromptVersionsQuery.iterate_over_pages(
            self._graphql_client,
            sleep_time=self.sleep_time,
            space_id=self.space_id,
            prompt_name=prompt_name,
        )
        return [result.to_dict() for result in results]

    def create_prompt(
        self,
        name: str,
        messages: List[dict],
        commit_message: Optional[str] = "created prompt",
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        input_variable_format: Optional[str] = None,
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
        tools: Optional[List[dict]] = None,
        tool_choice: Optional[dict] = None,
        invocation_params: Optional[dict] = None,
        provider_params: Optional[dict] = None,
    ) -> bool:
        """Create a new prompt or prompt version.

        Args:
            name (str): The name of the prompt
            commit_message (Optional[str]): The commit message of the prompt (default: "created prompt")
            messages (List[dict]): The messages of the prompt
            description (Optional[str]): The description of the prompt
            tags (Optional[List[str]]): The tags of the prompt
            input_variable_format (Optional[str]): The input variable format of the prompt ("f_string", "mustache", "none")
            provider (Optional[str]): The provider of the llm model to use for the prompt ("openAI", "awsBedrock", "azureOpenAI", "vertexAI", "custom") (default: "openAI")
            model_name (Optional[str]): The name of the llm model to use for the prompt (e.g. "gpt-4o-mini")
            tools (Optional[List[dict]]): The tools of the prompt (example below)
            tool_choice (Optional[dict]): The tool choice of the prompt (example below)
            invocation_params (Optional[dict]): The invocation parameters of the prompt (example below)
            provider_params (Optional[dict]): The provider parameters of the prompt (example below)

        Format of the messages:
        ```python
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "{question} {context}"},
        ]
        ```
        ## Using tools:
        Format of the tools:
        ```python
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get the weather in a given location",
                    "parameters": {"location": "San Francisco"}
                }
            },
            ...
        ]
        ```
        or using tool choice:
        ```python
        tool_choice = {
            "choice": "required",
            "tool": {
                    "type": "function",
                    "function": {
                        "name": "get_weather",
                        "description": "Get the weather in a given location",
                        "parameters": {
                            "location": "San Francisco"
                        }
                    }
                }
            }
        }
        ```

        ## Using invocation and provider parameters:
        Format of the Invocation Parameters:
        ```python
        invocation_params = {
            "temperature": 0.5,
            "top_p": 1.0,
            "top_k": 100,
            "stop": ["stop_sequence_1", "stop_sequence_2"],
            "max_tokens": 100,
            "max_completion_tokens": 100,
            "presence_penalty": 0.0,
            "frequency_penalty": 0.0,
        }
        ```

        Format of the Provider Parameters:
        ```python
        provider_params = {
            "azureParams": {
                "azureDeploymentName": "deployment_name",
                "azureOpenAIEndpoint": "endpoint",
                "azureOpenAIVersion": "version"
            },
            "customProviderParams": {
                "customModelEndpoint": {
                    "baseUrl": "...",
                    "modelName": "...",
                    "compatibleFormat": "azureopenai"
                }
            }
        }
        ```

        Returns:
            str: The url of the created prompt or prompt version

        Raises:
            ArizeAPIException: If the prompt is not found or there is an API error

        """
        if tools or tool_choice:
            invocation_params = invocation_params or {}
            if tool_choice:
                invocation_params["toolConfig"] = {"toolChoice": tool_choice}
            else:
                invocation_params["toolConfig"] = {"tools": tools}
        prompt_id = None
        variables = {
            "spaceId": self.space_id,
            "commitMessage": commit_message,
            "messages": messages,
        }
        try:
            prompt = self.get_prompt(name)
            prompt_id = prompt["id"]
            variables["promptId"] = prompt_id
            variables["provider"] = provider or prompt["provider"]
            variables["model"] = model_name or prompt["modelName"]
            variables["inputVariableFormat"] = input_variable_format or prompt["inputVariableFormat"]
            if provider_params:
                variables["providerParams"] = provider_params
            if invocation_params and prompt["toolCalls"]:
                if "toolConfig" in invocation_params:
                    variables["invocationParams"] = invocation_params
                else:
                    variables["invocationParams"] = {"toolConfig": prompt["toolCalls"]}
            elif prompt["toolCalls"]:
                variables["invocationParams"] = {"toolConfig": prompt["toolCalls"]}
            elif invocation_params:
                variables["invocationParams"] = invocation_params
        except ArizeAPIException:
            for key, value in {
                "name": name,
                "description": description,
                "tags": tags,
                "provider": provider,
                "model": model_name,
                "inputVariableFormat": input_variable_format,
                "invocationParams": invocation_params,
                "providerParams": provider_params,
            }.items():
                if value:
                    variables[key] = value
        if prompt_id:
            result = CreatePromptVersionMutation.run_graphql_mutation(
                self._graphql_client,
                **variables,
            )
            prompt_version_id = result.to_dict()["id"]
            return self.prompt_version_url(prompt_id, prompt_version_id)
        else:
            result = CreatePromptMutation.run_graphql_mutation(
                self._graphql_client,
                **variables,
            )
            return self.prompt_url(result.to_dict()["id"])

    def update_prompt_by_id(
        self,
        prompt_id: str,
        updated_name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> bool:
        """Update the tags, description, or name of a top-levelprompt.

        Args:
            prompt_id (str): The ID of the prompt to update
            updated_name (Optional[str]): The updated name of the prompt
            description (Optional[str]): The updated description of the prompt
            tags (Optional[List[str]]): The updated tags of the prompt

        Returns:
            bool: True if the prompt was updated, False otherwise


        Raises:
            ArizeAPIException: If the prompt is not found or there is an API error

        """
        if not updated_name and not description and not tags:
            raise ValueError("At least one of updated_name, description, or tags must be provided to update a prompt")
        if not updated_name:
            updated_name = self.get_prompt_by_id(prompt_id)["name"]

        result = UpdatePromptMutation.run_graphql_mutation(
            self._graphql_client,
            space_id=self.space_id,
            prompt_id=prompt_id,
            name=updated_name,
            description=description,
            tags=tags,
        )
        return result.to_dict()

    def update_prompt(
        self,
        prompt_name: str,
        updated_name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> bool:
        """Update the name, description, or tags of a top-level prompt.

        Args:
            prompt_name (str): The name of the prompt to update
            updated_name (Optional[str]): The updated name of the prompt
            description (Optional[str]): The updated description of the prompt
            tags (Optional[List[str]]): The updated tags of the prompt

        Returns:
            bool: True if the prompt was updated, False otherwise

        Raises:
            ArizeAPIException: If the prompt is not found or there is an API error

        """
        if not updated_name and not description and not tags:
            raise ValueError("At least one of updated_name, description, or tags must be provided to update a prompt")

        prompt_id = self.get_prompt(prompt_name)["id"]
        name = updated_name if updated_name else prompt_name
        return self.update_prompt_by_id(prompt_id, name=name, description=description, tags=tags)

    def delete_prompt_by_id(self, prompt_id: str) -> bool:
        """Deletes a prompt.

        Args:
            prompt_id (str): The ID of the prompt to delete

        Returns:
            bool: True if the prompt was deleted, False otherwise

        Raises:
            ArizeAPIException: If the prompt is not found or there is an API error

        """
        result = DeletePromptMutation.run_graphql_mutation(
            self._graphql_client,
            prompt_id=prompt_id,
            space_id=self.space_id,
        )
        return result.success

    def delete_prompt(self, prompt_name: str) -> bool:
        """Deletes a prompt.

        Args:
            prompt_name (str): The name of the prompt to delete

        Returns:
            bool: True if the prompt was deleted, False otherwise

        Raises:
            ArizeAPIException: If the prompt is not found or there is an API error

        """
        prompt_id = self.get_prompt(prompt_name)["id"]
        return self.delete_prompt_by_id(prompt_id)

    def get_all_custom_metrics(self, model_name: Optional[str] = None) -> Union[List[dict], Dict[str, List[dict]]]:
        """Retrieves all custom metrics for all models in the space.
        If model_name is provided, retrieves custom metrics for the specified model.
        Otherwise, retrieves custom metrics for all models in the space by model name.

        Args:
            model_name (Optional[str]): Name of the model to get metrics for.
                If None, retrieves metrics for all models.

        Returns:
            Union[List[dict], Dict[str, List[dict]]]: A list of custom metric dictionaries,
            or a dictionary of model name to list of custom metric dictionaries.

            Each custom metric dictionary contains:
            - id (str): Unique identifier for the metric
            - name (str): Name of the metric
            - description (str): Description of what the metric measures
            - metric (str): The metric expression/formula
            - createdAt (datetime): When the metric was created
            - requiresPositiveClass (bool): Whether metric requires positive class label

        Example:
            If model_name is None, returns a dictionary of model name to list of custom metric dictionaries for all models in the space:
            ```python
            {
                "model1": [custom_metric_dict1, custom_metric_dict2],
                "model2": [custom_metric_dict3, custom_metric_dict4],
            }
            ```
            If model_name "model1" is provided, returns a list of custom metric dictionaries:
            ```python
            [custom_metric_dict1, custom_metric_dict2]
            ```

        Raises:
            ArizeAPIException: If there is an API error

        """
        if model_name:
            return self.get_all_custom_metrics_for_model(model_name=model_name)
        else:
            models = GetAllModelsQuery.run_graphql_query(
                self._graphql_client,
                space_id=self.space_id,
            )
            results = {}
            for model in models:
                if model.id:
                    try:
                        results[model.name] = self.get_all_custom_metrics_for_model(model_id=model.id)
                    except ArizeAPIException as e:
                        logger.warning(f"Error getting custom metrics for model {model.name}: {e}")
            return results

    def get_all_custom_metrics_for_model(self, model_name: Optional[str] = None, model_id: Optional[str] = None) -> List[dict]:
        """Retrieves all custom metrics for a specific model. Model must be specified by either model_name or model_id.

        Args:
            model_name (Optional[str]): Name of the model to get metrics for.
            model_id (Optional[str]): ID of the model to get metrics for.

        Returns:
            List[dict]: A list of custom metric dictionaries, each containing:
            - id (str): Unique identifier for the metric
            - name (str): Name of the metric
            - description (str): Description of what the metric measures
            - metric (str): The metric expression/formula
            - createdAt (datetime): When the metric was created
            - requiresPositiveClass (bool): Whether metric requires positive class label

        Raises:
            ValueError: If neither model_name nor model_id is provided
            ArizeAPIException: If the model is not found or there is an API error

        """
        if not model_name and not model_id:
            raise ValueError("Either model_name or model_id must be provided")
        if model_id:
            results = GetAllCustomMetricsByModelIdQuery.iterate_over_pages(
                self._graphql_client,
                sleep_time=self.sleep_time,
                model_id=model_id,
            )
        else:
            results = GetAllCustomMetricsQuery.iterate_over_pages(
                self._graphql_client,
                sleep_time=self.sleep_time,
                space_id=self.space_id,
                model_name=model_name,
            )
        return [result.to_dict() for result in results]

    def get_custom_metric_by_id(self, custom_metric_id: str) -> dict:
        """Retrieve a specific custom metric by ID.

        Args:
            custom_metric_id (str): The ID of the custom metric to retrieve

        Returns:
            dict: A dictionary containing metric information:
            - id (str): Unique identifier for the metric
            - name (str): Name of the metric
            - description (str): Description of what the metric measures
            - metric (str): The metric expression/formula (e.g. "select avg(prediction) from model")
            - createdAt (datetime): When the metric was created
            - requiresPositiveClass (bool): Whether metric requires positive class label

        Raises:
            ArizeAPIException: If the custom metric is not found or there is an API error

        """
        results = GetCustomMetricByIDQuery.run_graphql_query(
            self._graphql_client,
            custom_metric_id=custom_metric_id,
        )
        return results.to_dict()

    def get_custom_metric(self, model_name: str, metric_name: str) -> dict:
        """Retrieve a specific custom metric for a model by name.

        Args:
            model_name (str): The name of the model to get the metric for
            metric_name (str): The name of the metric to get

        Returns:
            dict: A dictionary containing metric information:
            - id (str): Unique identifier for the metric
            - name (str): Name of the metric
            - description (str): Description of what the metric measures
            - metric (str): The metric expression/formula (e.g. "select avg(prediction) from model")
            - createdAt (datetime): When the metric was created
            - requiresPositiveClass (bool): Whether metric requires positive class label

        Raises:
            ArizeAPIException: If the model is not found or there is an API error

        """
        results = GetCustomMetricQuery.run_graphql_query(
            self._graphql_client,
            space_id=self.space_id,
            model_name=model_name,
            metric_name=metric_name,
        )
        return results.to_dict()

    def get_custom_metric_url(self, model_name: str, metric_name: str) -> str:
        """Retrieves the path to a specific custom metric of a model from the current space.

        Args:
            model_name (str): The name of the model to retrieve the custom metric for
            metric_name (str): The name of the custom metric to retrieve

        Returns:
            str: The path to the custom metric

        Raises:
            ArizeAPIException: If the model or custom metric is not found or there is an API error

        """
        model = GetModelQuery.run_graphql_query(self._graphql_client, model_name=model_name, space_id=self.space_id)
        custom_metric = GetCustomMetricQuery.run_graphql_query(
            self._graphql_client,
            space_id=self.space_id,
            model_name=model_name,
            metric_name=metric_name,
        )
        return self.custom_metric_url(model.id, custom_metric.id)

    def create_custom_metric(
        self,
        metric: str,
        metric_name: str,
        model_id: Optional[str] = None,
        model_name: Optional[str] = None,
        metric_description: Optional[str] = None,
        metric_environment: Optional[str] = None,
    ) -> str:
        """Creates a new custom metric for a model.

        Args:
            metric (str): The metric expression/formula (e.g. "select avg(prediction) from model")
            metric_name (str): Name for the new metric
            model_id (Optional[str]): ID of the model to create metric for.
                Either model_id or model_name must be provided.
            model_name (Optional[str]): Name of the model to create metric for.
                Used to look up model_id if not provided.
            metric_description (Optional[str]): Description of what the metric measures
            metric_environment (Optional[str]): Environment name for the metric.
                Valid values are: "production", "staging", "development"
                Defaults to "production" if not specified.

        Returns:
            str: The path to the newly created custom metric

        Raises:
            ValueError: If neither model_id nor model_name is provided
            ArizeAPIException: If metric creation fails or there is an API error

        """
        if not model_id:
            if not model_name:
                raise ValueError("Either model_id or model_name must be provided")
            model = GetModelQuery.run_graphql_query(
                self._graphql_client,
                model_name=model_name,
                space_id=self.space_id,
            )
            model_id = model.id
        inputs = {
            "metric": metric,
            "modelId": model_id,
            "name": metric_name,
        }
        if metric_description:
            inputs["description"] = metric_description
        if metric_environment:
            inputs["modelEnvironmentName"] = metric_environment
        results = CreateCustomMetricMutation.run_graphql_mutation(
            self._graphql_client,
            **inputs,
        )
        return self.custom_metric_url(model_id, results.metric_id)

    def delete_custom_metric_by_id(self, custom_metric_id: str, model_id: str) -> bool:
        """Deletes a custom metric by ID.

        Args:
            custom_metric_id (str): ID of the custom metric to delete
            model_id (str): ID of the model to delete the custom metric for

        Returns:
            bool: True if the custom metric was deleted, False otherwise

        Raises:
            ArizeAPIException: If the custom metric is not found or there is an API error

        """
        results = DeleteCustomMetricMutation.run_graphql_mutation(
            self._graphql_client,
            customMetricId=custom_metric_id,
            modelId=model_id,
        )
        return results.model_id == model_id

    def delete_custom_metric(self, model_name: str, metric_name: str) -> bool:
        """Deletes a custom metric by name.

        Args:
            model_name (str): Name of the model to delete the custom metric for
            metric_name (str): Name of the custom metric to delete

        Returns:
            bool: True if the custom metric was deleted, False otherwise

        Raises:
            ArizeAPIException: If the custom metric is not found or there is an API error

        """
        model = GetModelQuery.run_graphql_query(
            self._graphql_client,
            model_name=model_name,
            space_id=self.space_id,
        )
        metric = GetCustomMetricQuery.run_graphql_query(
            self._graphql_client,
            space_id=self.space_id,
            model_name=model_name,
            metric_name=metric_name,
        )
        return self.delete_custom_metric_by_id(metric.id, model.id)

    def update_custom_metric_by_id(
        self,
        custom_metric_id: str,
        model_id: str,
        name: Optional[str] = None,
        metric: Optional[str] = None,
        description: Optional[str] = None,
        environment: Optional[str] = None,
    ) -> str:
        """Updates a custom metric by ID.

        Args:
            custom_metric_id (str): ID of the custom metric to update
            model_id (str): ID of the model to update the custom metric for
            name (Optional[str]): Name of the custom metric (if updating name)
            metric (Optional[str]): The metric expression/formula (e.g. "select avg(prediction) from model") (if updating metric)
            description (Optional[str]): Description of what the metric measures (if updating description)
            environment (Optional[str]): Environment name for the metric. (if updating environment)
                Valid values are: "production", "staging", "development"
                Defaults to "production" if not specified.

        Returns:
            dict: A dictionary containing the updated custom metric information:
            - id (str): Unique identifier for the metric
            - name (str): Name of the metric
            - description (str): Description of what the metric measures
            - metric (str): The metric expression/formula (e.g. "select avg(prediction) from model")
            - requiresPositiveClass (bool): Whether metric requires positive class label

        Raises:
            ArizeAPIException: If the custom metric is not found or there is an API error

        """
        custom_metric = self.get_custom_metric_by_id(custom_metric_id)
        inputs = {
            "customMetricId": custom_metric_id,
            "modelId": model_id,
            "name": name or custom_metric["name"],
            "metric": metric or custom_metric["metric"],
            "description": description or custom_metric["description"],
            "modelEnvironmentName": environment or custom_metric["modelEnvironmentName"],
        }
        results = UpdateCustomMetricMutation.run_graphql_mutation(
            self._graphql_client,
            **inputs,
        )
        return results.to_dict()

    def update_custom_metric(
        self,
        custom_metric_name: str,
        model_name: str,
        name: Optional[str] = None,
        metric: Optional[str] = None,
        description: Optional[str] = None,
        environment: Optional[str] = None,
    ) -> str:
        """Updates a custom metric.

        Args:
            custom_metric_name (str): Current name of the custom metric to update
            model_name (str): Name of the model to update the custom metric for
            name (Optional[str]): New name of the custom metric (if updating name)
            metric (Optional[str]): The metric expression/formula (e.g. "select avg(prediction) from model") (if updating metric)
            description (Optional[str]): Description of what the metric measures (if updating description)
            environment (Optional[str]): Environment name for the metric. (if updating environment)
                Valid values are: "production", "staging", "development"
                Defaults to "production" if not specified.

        Returns:
            dict: A dictionary containing the updated custom metric information:
            - id (str): Unique identifier for the metric
            - name (str): Name of the metric
            - description (str): Description of what the metric measures
            - metric (str): The metric expression/formula (e.g. "select avg(prediction) from model")
            - requiresPositiveClass (bool): Whether metric requires positive class label

        Raises:
            ArizeAPIException: If the custom metric is not found or there is an API error

        """
        model = GetModelQuery.run_graphql_query(
            self._graphql_client,
            model_name=model_name,
            space_id=self.space_id,
        )
        custom_metric = GetCustomMetricQuery.run_graphql_query(
            self._graphql_client,
            space_id=self.space_id,
            model_name=model_name,
            metric_name=custom_metric_name,
        )
        inputs = {
            "customMetricId": custom_metric.id,
            "modelId": model.id,
            "name": name or custom_metric_name,
            "customMetric": metric or custom_metric.metric,
            "modelEnvironmentName": environment or custom_metric.modelEnvironmentName,
            "description": description or custom_metric.description,
        }
        results = UpdateCustomMetricMutation.run_graphql_mutation(
            self._graphql_client,
            **inputs,
        )
        return results.to_dict()

    def copy_custom_metric(
        self,
        current_metric_name: str,
        current_model_name: str,
        new_model_name: Optional[str] = None,
        new_model_id: Optional[str] = None,
        new_metric_name: Optional[str] = None,
        new_metric_description: Optional[str] = None,
        new_model_environment: Optional[str] = "production",
    ) -> str:
        """Copies a custom metric from one model to another.

        Args:
            custom_metric_name (str): Name of the custom metric to copy
            current_model_name (str): Name of the model to copy the custom metric from
            new_model_name (Optional[str]): Name of the model to copy the custom metric to (must provide either new_model_name or new_model_id)
            new_model_id (Optional[str]): ID of the model to copy the custom metric to (must provide either new_model_name or new_model_id)
            new_metric_name (Optional[str]): Name of the new custom metric (default copies current metric name)
            new_metric_description (Optional[str]): Description of the new custom metric (default copies current metric description)
            new_model_environment (Optional[str]): Environment of the new custom metric (default is "production" options are "production", "staging", "development")

        Returns:
            str: The path to the newly created custom metric

        Raises:
            ArizeAPIException: If the custom metric is not found or there is an API error

        """
        custom_metric = GetCustomMetricQuery.run_graphql_query(
            self._graphql_client,
            space_id=self.space_id,
            model_name=current_model_name,
            metric_name=current_metric_name,
        )
        return self.create_custom_metric(
            metric=custom_metric.metric,
            metric_name=new_metric_name or current_metric_name,
            model_name=new_model_name,
            model_id=new_model_id,
            metric_description=new_metric_description or custom_metric.description,
            metric_environment=new_model_environment,
        )

    def get_all_monitors(self, model_id: str = None, model_name: str = None, monitor_category: str = None) -> List[dict]:
        """Retrieves all monitors for a specific model.

        Args:
            model_id (Optional[str]): ID of the model to get monitors for.
                Either model_id or model_name must be provided.
            model_name (Optional[str]): Name of the model to get monitors for.
                Used to look up model_id if not provided.
            monitor_category (Optional[str]): Filter monitors by category.
                Valid values are: "drift", "dataQuality", "performance"
                If None, returns monitors of all categories.

        Returns:
            List[dict]: A list of monitor dictionaries, each containing:
            - id (str): Unique identifier for the monitor
            - name (str): Name of the monitor
            - monitorCategory (str): Category of the monitor ("performance", "drift", "dataQuality")
            - status (str): Current status ("triggered", "cleared", "noData")
            - isTriggered (bool): Whether the monitor is currently triggered
            - threshold (float): Alert threshold value
            - operator (str): Comparison operator for the threshold (e.g. "greaterThan", "lessThan")

            Additional fields depend on the monitor category.

        Raises:
            ValueError: If neither model_id nor model_name is provided
            ArizeAPIException: If the model is not found or there is an API error

        """
        if not model_id:
            if not model_name:
                raise ValueError("Either model_id or model_name must be provided")
            model = self.get_model(model_name)
            model_id = model["id"]
        results = GetAllModelMonitorsQuery.iterate_over_pages(
            self._graphql_client,
            sleep_time=self.sleep_time,
            model_id=model_id,
            monitor_category=monitor_category,
        )
        return [result.to_dict() for result in results]

    def get_monitor(self, model_name: str, monitor_name: str) -> dict:
        """Retrieves a specific monitor by name and model name.

        Args:
            model_name (str): Name of the model to get the monitor for
            monitor_name (str): Name of the monitor to get

        Returns:
            dict: A dictionary containing monitor information:
            - id (str): Unique identifier for the monitor
            - name (str): Name of the monitor
            - monitorCategory (str): Category of the monitor ("performance", "drift", "dataQuality")
            - status (str): Current status ("triggered", "cleared", "noData")
            - isTriggered (bool): Whether the monitor is currently triggered
            - threshold (float): Alert threshold value
            - operator (str): Comparison operator for the threshold (e.g. "greaterThan", "lessThan")

            Additional fields depend on the monitor category.

        Raises:
            ArizeAPIException: If the monitor is not found or there is an API error

        """
        result = GetMonitorQuery.run_graphql_query(
            self._graphql_client,
            model_name=model_name,
            monitor_name=monitor_name,
            space_id=self.space_id,
        )
        return result.to_dict()

    def get_monitor_by_id(self, monitor_id: str) -> dict:
        """Retrieves a specific monitor by ID.

        Args:
            monitor_id (str): ID of the monitor to get

        Returns:
            dict: A dictionary containing monitor information:
            - id (str): Unique identifier for the monitor
            - name (str): Name of the monitor
            - monitorCategory (str): Category of the monitor ("performance", "drift", "dataQuality")
            - status (str): Current status ("triggered", "cleared", "noData")
            - isTriggered (bool): Whether the monitor is currently triggered
            - threshold (float): Alert threshold value
            - operator (str): Comparison operator for the threshold (e.g. "greaterThan", "lessThan")

            Additional fields depend on the monitor category.

        Raises:
            ArizeAPIException: If the monitor is not found or there is an API error

        """
        results = GetMonitorByIDQuery.run_graphql_query(
            self._graphql_client,
            monitor_id=monitor_id,
        )
        return results.to_dict()

    def get_monitor_url(self, monitor_name: str, model_name: str) -> str:
        """Retrieves the path to a specific monitor by name and model name.

        Args:
            monitor_name (str): Name of the monitor to get
            model_name (str): Name of the model to get the monitor for

        Returns:
            str: The path to the monitor

        Raises:
            ArizeAPIException: If the monitor is not found or there is an API error

        """
        monitor = GetMonitorQuery.run_graphql_query(
            self._graphql_client,
            model_name=model_name,
            monitor_name=monitor_name,
            space_id=self.space_id,
        )
        return self.monitor_url(monitor.id)

    def create_performance_monitor(
        self,
        name: str,
        model_name: str,
        model_environment_name: str,
        operator: str = "greaterThan",
        performance_metric: Optional[str] = None,
        custom_metric_id: Optional[str] = None,
        notes: Optional[str] = None,
        threshold: Optional[float] = None,
        std_dev_multiplier: Optional[float] = 2.0,
        prediction_class_value: Optional[str] = None,
        positive_class_value: Optional[str] = None,
        downtime_start: Optional[Union[datetime, str]] = None,
        downtime_duration_hrs: Optional[int] = None,
        downtime_frequency_days: Optional[int] = None,
        scheduled_runtime_enabled: Optional[bool] = False,
        scheduled_runtime_cadence_seconds: Optional[int] = None,
        scheduled_runtime_days_of_week: Optional[List[int]] = None,
        evaluation_window_length_seconds: Optional[int] = 259200,
        delay_seconds: Optional[int] = 0,
        threshold_mode: Optional[str] = "single",
        threshold2: Optional[float] = None,
        operator2: Optional[str] = None,
        std_dev_multiplier2: Optional[float] = None,
        email_addresses: Optional[Union[str, List[str]]] = None,
        integration_key_ids: Optional[Union[str, List[str]]] = None,
    ) -> str:
        """Creates a new performance metric monitor for a model.

        Args:
            name (str): Name of the monitor
            model_name (str): Name of the model to monitor
            model_environment_name (str): Environment name for the model (options are "tracing", "production", "validation", or "training")
            operator (str): Comparison operator for the threshold (e.g. "greaterThan", "lessThan")
            performance_metric (Optional[str]): Name of the performance metric to monitor (e.g. "accuracy", "auc") - either performance_metric or custom_metric_id must be provided
            custom_metric_id (Optional[str]): ID of the custom metric to monitor - either performance_metric or custom_metric_id must be provided
            notes (Optional[str]): Notes for the monitor
            threshold (Optional[float]): Alert threshold value (e.g. 0.95)
            std_dev_multiplier (Optional[float]): Standard deviation multiplier for the threshold (e.g. 2.0)
            prediction_class_value (Optional[str]): Value of the prediction class to monitor
            positive_class_value (Optional[str]): Value of the positive class to monitor
            downtime_start (Optional[datetime | str]): Start time for downtime
            downtime_duration_hrs (Optional[int]): Duration of downtime in hours
            downtime_frequency_days (Optional[int]): Frequency of downtime in days
            scheduled_runtime_enabled (Optional[bool]): Whether the monitor is scheduled to run
            scheduled_runtime_cadence_seconds (Optional[int]): Cadence of scheduled runtime in seconds
            scheduled_runtime_days_of_week (Optional[List[int]]): Days of the week to run the monitor
            evaluation_window_length_seconds (Optional[int]): Length of the evaluation window in seconds - default is 259200 (1 day)
            delay_seconds (Optional[int]): Delay in seconds before the monitor is evaluated - default is 0
            threshold_mode (Optional[str]): Mode for the threshold (options are "single" for one threshold or "double" for two thresholds) - default is "single"
            threshold2 (Optional[float]): Second threshold value (only used if threshold_mode is "double")
            operator2 (Optional[str]): Comparison operator for the second threshold (e.g. "greaterThan", "lessThan" only used if threshold_mode is "double")
            std_dev_multiplier2 (Optional[float]): Standard deviation multiplier for the second threshold (only used if threshold_mode is "double")
            email_addresses (Optional[Union[str, List[str]]]): Email address(es) to notify when the monitor is triggered
            integration_key_ids (Optional[Union[str, List[str]]]): ID(s) of integration key(s) to notify when the monitor is triggered

        Returns:
            str: The path to the newly created performance metric monitor

        Raises:
            ArizeAPIException: If monitor creation fails or there is an API error

        """
        if performance_metric is None and custom_metric_id is None:
            raise ValueError("Either performance_metric or custom_metric_id must be provided")
        contacts = []
        if email_addresses:
            if isinstance(email_addresses, str):
                email_addresses = [email_addresses]
            contacts.extend([{"notificationChannelType": "email", "emailAddress": email_address} for email_address in email_addresses])
        if integration_key_ids:
            if isinstance(integration_key_ids, str):
                integration_key_ids = [integration_key_ids]
            contacts.extend(
                [
                    {
                        "notificationChannelType": "integration",
                        "integrationKeyId": integration_key_id,
                    }
                    for integration_key_id in integration_key_ids
                ]
            )
        results = CreatePerformanceMonitorMutation.run_graphql_mutation(
            self._graphql_client,
            **{
                "spaceId": self.space_id,
                "modelName": model_name,
                "name": name,
                "notes": notes,
                "performanceMetric": performance_metric,
                "customMetricId": custom_metric_id,
                "operator": operator,
                "threshold": threshold,
                "dynamicAutoThreshold": ({"stdDevMultiplier": std_dev_multiplier} if not threshold else None),
                "contacts": contacts,
                "downtimeStart": (parse_datetime(downtime_start) if downtime_start else None),
                "downtimeDurationHrs": downtime_duration_hrs,
                "downtimeFrequencyDays": downtime_frequency_days,
                "scheduledRuntimeEnabled": scheduled_runtime_enabled,
                "scheduledRuntimeCadenceSeconds": scheduled_runtime_cadence_seconds,
                "scheduledRuntimeDaysOfWeek": scheduled_runtime_days_of_week,
                "evaluationWindowLengthSeconds": evaluation_window_length_seconds,
                "delaySeconds": delay_seconds,
                "thresholdMode": threshold_mode,
                "threshold2": threshold2,
                "operator2": operator2,
                "stdDevMultiplier2": std_dev_multiplier2 if not threshold2 else None,
                "modelEnvironmentName": model_environment_name,
                "predictionClassValue": prediction_class_value,
                "positiveClassValue": positive_class_value,
            },
        )
        return self.monitor_url(results.monitor_id)

    def create_drift_monitor(
        self,
        name: str,
        model_name: str,
        drift_metric: str = "psi",
        dimension_category: str = "prediction",
        operator: str = "greaterThan",
        dimension_name: Optional[str] = None,
        notes: Optional[str] = None,
        threshold: Optional[float] = None,
        std_dev_multiplier: Optional[float] = 2.0,
        downtime_start: Optional[datetime] = None,
        downtime_duration_hrs: Optional[int] = None,
        downtime_frequency_days: Optional[int] = None,
        scheduled_runtime_enabled: Optional[bool] = False,
        scheduled_runtime_cadence_seconds: Optional[int] = None,
        scheduled_runtime_days_of_week: Optional[List[int]] = None,
        evaluation_window_length_seconds: Optional[int] = 259200,
        delay_seconds: Optional[int] = 0,
        threshold_mode: Optional[str] = "single",
        threshold2: Optional[float] = None,
        operator2: Optional[str] = None,
        std_dev_multiplier2: Optional[float] = 2.0,
        email_addresses: Optional[Union[str, List[str]]] = None,
        integration_key_ids: Optional[Union[str, List[str]]] = None,
    ) -> str:
        """Creates a new drift monitor for a model.

        Args:
            name (str): Name of the monitor
            model_name (str): Name of the model to monitor
            drift_metric (str): Metric to use for drift detection (options are "psi", "js", "kl", "ks", or for embeddings "euclideanDistance" or "cosineSimilarity") - default is "psi"
            dimension_category (str): Category of the dimension to monitor (e.g. "prediction", "featureLabel", etc.) - default is "prediction"
            operator (str): Comparison operator for the threshold (e.g. "greaterThan", "lessThan") - default is "greaterThan"
            dimension_name (Optional[str]): Name of the dimension to monitor (not applicable for prediction drift)
            notes (Optional[str]): Notes for the monitor
            threshold (Optional[float]): Alert threshold value
            std_dev_multiplier (Optional[float]): Standard deviation multiplier for the threshold (default is 2.0 if a threshold is not provided)
            downtime_start (Optional[datetime | str]): Start time for downtime
            downtime_duration_hrs (Optional[int]): Duration of downtime in hours
            downtime_frequency_days (Optional[int]): Frequency of downtime in days
            scheduled_runtime_enabled (Optional[bool]): Whether the monitor is scheduled to run
            scheduled_runtime_cadence_seconds (Optional[int]): Cadence of scheduled runtime in seconds
            scheduled_runtime_days_of_week (Optional[List[int]]): Days of the week to run the monitor
            evaluation_window_length_seconds (Optional[int]): Length of the evaluation window in seconds - default is 259200 (1 day)
            delay_seconds (Optional[int]): Delay in seconds before the monitor is evaluated - default is 0
            threshold_mode (Optional[str]): Mode for the threshold (options are "single" for one threshold or "double" for two thresholds) - default is "single"
            threshold2 (Optional[float]): Second threshold value (only used if threshold_mode is "double")
            operator2 (Optional[str]): Comparison operator for the second threshold (e.g. "greaterThan", "lessThan" only used if threshold_mode is "double")
            std_dev_multiplier2 (Optional[float]): Standard deviation multiplier for the second threshold (default is 2.0 if threshold_mode is "double" and a threshold2 is not provided)
            email_addresses (Optional[List[str]]): Email addresses to notify when the monitor is triggered

        Returns:
            str: The path to the newly created drift monitor

        Raises:
            ArizeAPIException: If monitor creation fails or there is an API error

        """
        contacts = []
        if email_addresses:
            if isinstance(email_addresses, str):
                email_addresses = [email_addresses]
            contacts.extend([{"notificationChannelType": "email", "emailAddress": email_address} for email_address in email_addresses])
        if integration_key_ids:
            if isinstance(integration_key_ids, str):
                integration_key_ids = [integration_key_ids]
            contacts.extend(
                [
                    {
                        "notificationChannelType": "integration",
                        "integrationKeyId": integration_key_id,
                    }
                    for integration_key_id in integration_key_ids
                ]
            )
        results = CreateDriftMonitorMutation.run_graphql_mutation(
            self._graphql_client,
            **{
                "spaceId": self.space_id,
                "modelName": model_name,
                "name": name,
                "dimensionCategory": dimension_category,
                "dimensionName": dimension_name,
                "notes": notes,
                "driftMetric": drift_metric,
                "operator": operator,
                "threshold": threshold,
                "dynamicAutoThreshold": ({"stdDevMultiplier": std_dev_multiplier} if not threshold else None),
                "contacts": contacts,
                "downtimeStart": (parse_datetime(downtime_start) if downtime_start else None),
                "downtimeDurationHrs": downtime_duration_hrs,
                "downtimeFrequencyDays": downtime_frequency_days,
                "scheduledRuntimeEnabled": scheduled_runtime_enabled,
                "scheduledRuntimeCadenceSeconds": scheduled_runtime_cadence_seconds,
                "scheduledRuntimeDaysOfWeek": scheduled_runtime_days_of_week,
                "evaluationWindowLengthSeconds": evaluation_window_length_seconds,
                "delaySeconds": delay_seconds,
                "thresholdMode": threshold_mode,
                "threshold2": threshold2,
                "operator2": operator2,
                "stdDevMultiplier2": std_dev_multiplier2 if not threshold2 else None,
            },
        )
        return self.monitor_url(results.monitor_id)

    def create_data_quality_monitor(
        self,
        name: str,
        model_name: str,
        data_quality_metric: str,
        model_environment_name: str,
        dimension_category: str = "prediction",
        operator: str = "greaterThan",
        dimension_name: Optional[str] = None,
        notes: Optional[str] = None,
        threshold: Optional[float] = None,
        std_dev_multiplier: Optional[float] = 2.0,
        downtime_start: Optional[Union[datetime, str]] = None,
        downtime_duration_hrs: Optional[int] = None,
        downtime_frequency_days: Optional[int] = None,
        scheduled_runtime_enabled: Optional[bool] = False,
        scheduled_runtime_cadence_seconds: Optional[int] = None,
        scheduled_runtime_days_of_week: Optional[List[int]] = None,
        evaluation_window_length_seconds: Optional[int] = 259200,
        delay_seconds: Optional[int] = 0,
        threshold_mode: Optional[str] = "single",
        operator2: Optional[str] = None,
        threshold2: Optional[float] = None,
        std_dev_multiplier2: Optional[float] = 2.0,
        email_addresses: Optional[Union[str, List[str]]] = None,
        integration_key_ids: Optional[Union[str, List[str]]] = None,
    ) -> str:
        """Creates a new data quality monitor for a model.

        Args:
            name (str): Name of the monitor
            model_name (str): Name of the model to monitor
            data_quality_metric (str): Metric to use for data quality detection (e.g. "percentEmpty", "cardinality", "avg", etc.)
            model_environment_name (str): Environment name for the model (options are "tracing", "production", "validation", or "training")
            dimension_category (str): Category of the dimension to monitor (e.g. "prediction", "featureLabel", etc.) - default is "prediction"
            operator (str): Comparison operator for the threshold (e.g. "greaterThan", "lessThan") - default is "greaterThan"
            dimension_name (Optional[str]): Name of the dimension to monitor (not applicable for predictions)
            notes (Optional[str]): Notes for the monitor
            threshold (Optional[float]): Alert threshold value
            std_dev_multiplier (Optional[float]): Standard deviation multiplier for the threshold (default is 2.0 if a threshold is not provided)
            downtime_start (Optional[datetime | str]): Start time for downtime
            downtime_duration_hrs (Optional[int]): Duration of downtime in hours
            downtime_frequency_days (Optional[int]): Frequency of downtime in days
            scheduled_runtime_enabled (Optional[bool]): Whether the monitor is scheduled to run
            scheduled_runtime_cadence_seconds (Optional[int]): Cadence of scheduled runtime in seconds
            scheduled_runtime_days_of_week (Optional[List[int]]): Days of the week to run the monitor
            evaluation_window_length_seconds (Optional[int]): Length of the evaluation window in seconds - default is 259200 (1 day)
            delay_seconds (Optional[int]): Delay in seconds before the monitor is evaluated - default is 0
            threshold_mode (Optional[str]): Mode for the threshold (options are "single" for one threshold or "double" for two thresholds) - default is "single"
            operator2 (Optional[str]): Comparison operator for the second threshold (e.g. "greaterThan", "lessThan" only used if threshold_mode is "double")
            threshold2 (Optional[float]): Alert threshold value for the second threshold (only used if threshold_mode is "double")
            std_dev_multiplier2 (Optional[float]): Standard deviation multiplier for the second threshold (default is 2.0 if threshold_mode is "double" and a threshold2 is not provided)
            email_addresses (Optional[Union[str, List[str]]]): Email address(es) to notify when the monitor is triggered
            integration_key_ids (Optional[Union[str, List[str]]]): ID(s) of integration key(s) to notify when the monitor is triggered

        Returns:
            str: The path to the newly created data quality monitor

        Raises:
            ArizeAPIException: If monitor creation fails or there is an API error

        """
        contacts = []
        if email_addresses:
            if isinstance(email_addresses, str):
                email_addresses = [email_addresses]
            contacts.extend([{"notificationChannelType": "email", "emailAddress": email_address} for email_address in email_addresses])
        if integration_key_ids:
            if isinstance(integration_key_ids, str):
                integration_key_ids = [integration_key_ids]
            contacts.extend(
                [
                    {
                        "notificationChannelType": "integration",
                        "integrationKeyId": integration_key_id,
                    }
                    for integration_key_id in integration_key_ids
                ]
            )
        results = CreateDataQualityMonitorMutation.run_graphql_mutation(
            self._graphql_client,
            **{
                "spaceId": self.space_id,
                "modelName": model_name,
                "name": name,
                "dataQualityMetric": data_quality_metric,
                "dimensionCategory": dimension_category,
                "dimensionName": dimension_name,
                "notes": notes,
                "operator": operator,
                "threshold": threshold,
                "dynamicAutoThreshold": ({"stdDevMultiplier": std_dev_multiplier} if not threshold else None),
                "contacts": contacts,
                "downtimeStart": (parse_datetime(downtime_start) if downtime_start else None),
                "downtimeDurationHrs": downtime_duration_hrs,
                "downtimeFrequencyDays": downtime_frequency_days,
                "scheduledRuntimeEnabled": scheduled_runtime_enabled,
                "scheduledRuntimeCadenceSeconds": scheduled_runtime_cadence_seconds,
                "scheduledRuntimeDaysOfWeek": scheduled_runtime_days_of_week,
                "evaluationWindowLengthSeconds": evaluation_window_length_seconds,
                "delaySeconds": delay_seconds,
                "thresholdMode": threshold_mode,
                "operator2": operator2,
                "threshold2": threshold2,
                "stdDevMultiplier2": std_dev_multiplier2 if not threshold2 else None,
                "modelEnvironmentName": model_environment_name,
            },
        )
        return self.monitor_url(results.monitor_id)

    def delete_monitor_by_id(self, monitor_id: str) -> bool:
        """Deletes a monitor by its ID.

        Args:
            monitor_id (str): ID of the monitor to delete

        Returns:
            bool: `True` if the monitor was deleted, `False` otherwise

        Raises:
            ArizeAPIException: If monitor deletion fails or there is an API error

        """
        results = DeleteMonitorMutation.run_graphql_mutation(self._graphql_client, monitorId=monitor_id)
        return results.monitor_id == monitor_id

    def delete_monitor(
        self,
        monitor_name: str,
        model_name: str,
    ) -> bool:
        """Deletes a monitor using its name and the name of the model it belongs to.

        Args:
            monitor_name (str): Name of the monitor to delete
            model_name (str): Name of the model to delete the monitor from

        Returns:
            bool: `True` if the monitor was deleted, `False` otherwise

        Raises:
            ArizeAPIException: If monitor deletion fails or there is an API error

        """
        monitor = GetMonitorQuery.run_graphql_query(
            self._graphql_client,
            model_name=model_name,
            monitor_name=monitor_name,
            space_id=self.space_id,
        )
        return self.delete_monitor_by_id(monitor_id=monitor.id)

    def copy_monitor(
        self,
        current_monitor_name: str,
        current_model_name: str,
        new_monitor_name: Optional[str] = None,
        new_model_name: Optional[str] = None,
        new_space_id: Optional[str] = None,
        **kwargs,
    ):
        """Copies a monitor from one model to another.

        Args:
            current_monitor_name (str): Name of the monitor to copy
            current_model_name (str): Name of the model to copy the monitor from
            new_model_name (Optional[str]): Name of the model to copy the monitor to (default is current model name)
            new_monitor_name (Optional[str]): Name of the new monitor (default copies current monitor name)
            new_space_id (Optional[str]): ID of the space to copy the monitor to (default is current space)
            **kwargs: Additional keyword arguments to pass to the create_monitor function to update new monitor fields

        Returns:
            str: The path to the newly created monitor

        Raises:
            ArizeAPIException: If monitor creation fails or there is an API error

        """
        current_monitor = GetMonitorQuery.run_graphql_query(
            self._graphql_client,
            model_name=current_model_name,
            monitor_name=current_monitor_name,
            space_id=self.space_id,
        )
        monitor_type = MonitorManager.extract_monitor_type(
            space_id=new_space_id or self.space_id,
            model_name=new_model_name or current_model_name,
            monitor=current_monitor,
        )
        if new_monitor_name:
            kwargs["name"] = new_monitor_name
        if kwargs:
            monitor_fields = monitor_type.to_dict()
            for key, value in kwargs.items():
                if value is not None and key in monitor_fields:
                    monitor_fields[key] = value
            monitor_type = MonitorManager.extract_monitor_type_from_dict(
                space_id=new_space_id or self.space_id,
                model_name=new_model_name or current_model_name,
                monitor=monitor_fields,
            )
        monitor_query = {
            "performance": CreatePerformanceMonitorMutation,
            "data_quality": CreateDataQualityMonitorMutation,
            "drift": CreateDriftMonitorMutation,
        }.get(current_monitor.monitorCategory.name)
        new_monitor = monitor_query.run_graphql_mutation(
            self._graphql_client,
            **monitor_type.to_dict(),
        )
        return self.monitor_url(new_monitor.monitor_id)
