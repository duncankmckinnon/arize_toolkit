import logging
import os
from datetime import datetime
from typing import Dict, List, Literal, Optional, Tuple, Union

from gql import Client as GraphQLClient
from gql.transport.aiohttp import AIOHTTPTransport

from arize_toolkit.client import Client
from arize_toolkit.exceptions import ArizeAPIException

logger = logging.getLogger("arize_toolkit")


class AsyncClient(Client):
    """Async Client for the Arize API

    Args:
        - `organization` (str): The Arize organization name
        - `space` (str): The Arize space name
        - `arize_developer_key` (Optional[str]): The API key. This can be copied from the space settings page in Arize.
        - `arize_app_url` (Optional[str]): The URL of the Arize API (default for SaaS is https://app.arize.com). For on-prem deployments, this will need to be set to the URL of Arize app.
        - `sleep_time` (Optional[int]): The number of seconds to sleep between API requests (may be needed if rate limiting is an issue)
    (Note: ARIZE_DEVELOPER_KEY environment variable can be set instead of passing in `arize_developer_key`)
        - `headers` (Optional[Dict[str, str]]): Additional headers to send with the request (e.g. for proxy authentication)
        - `verify` (bool): Whether to verify the SSL certificate of the Arize API (defaults to True)

    Properties:
        space (str): The Arize space name
        organization (str): The Arize organization name
        org_id (str): The Arize organization ID
        space_id (str): The Arize space ID
        sleep_time (int): The sleep time between API requests
        arize_app_url (str): The URL of the Arize API
        space_url (str): The URL of the current space

    Usage:
        >>> async with AsyncClient(organization="my-org", space="my-space") as client:
        ...     models = await client.get_all_models()
        ...     print(f"Found {len(models)} models")

    Or without context manager:
        >>> client = AsyncClient(organization="my-org", space="my-space")
        >>> await client.connect()
        >>> try:
        ...     models = await client.get_all_models()
        ...     print(f"Found {len(models)} models")
        ... finally:
        ...     await client.close()
    """

    org_id: str
    space_id: str

    def __init__(
        self,
        organization: Optional[str] = None,
        space: Optional[str] = None,
        arize_developer_key: Optional[str] = None,
        arize_app_url: str = "https://app.arize.com",
        sleep_time: int = 0,
        headers: Optional[Dict[str, str]] = None,
        verify: bool = True,
    ):
        self.organization = organization
        self.space = space
        self.sleep_time = sleep_time
        self.arize_app_url = arize_app_url
        arize_developer_key = arize_developer_key or os.getenv("ARIZE_DEVELOPER_KEY")
        transport_headers = {
            "x-api-key": arize_developer_key,
            **(headers or {}),
        }
        verify = bool(verify)

        # Create async transport
        self._transport = AIOHTTPTransport(
            url=f"{self.arize_app_url}/graphql",
            headers=transport_headers,
            ssl=verify,
        )
        self._graphql_client = GraphQLClient(transport=self._transport)
        self._session_started = False

    async def __aenter__(self) -> "AsyncClient":
        """Async context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit"""
        await self.close()

    async def connect(self) -> None:
        """Initialize the async client session and set organization/space IDs"""
        if not self._session_started:
            # Start the session for the transport
            await self._transport.__aenter__()
            self._session_started = True

            # Set org and space IDs
            await self._set_org_and_space_id()

    async def close(self) -> None:
        """Close the async client session"""
        if self._session_started:
            await self._transport.__aexit__(None, None, None)
            self._session_started = False

    async def _set_org_and_space_id(self) -> None:
        """Set organization and space IDs using async queries"""
        from arize_toolkit.queries.space_queries import AsyncGetAllOrganizationsQuery, AsyncGetAllSpacesQuery, AsyncOrgIDandSpaceIDQuery

        if not self.organization:
            organizations = await AsyncGetAllOrganizationsQuery.iterate_over_pages(self._graphql_client, sleep_time=self.sleep_time)
            if len(organizations) > 0:
                self.organization = organizations[0].name
                self.org_id = organizations[0].id
            else:
                raise ValueError("no organizations in the account")

        if not self.space:
            spaces = await AsyncGetAllSpacesQuery.iterate_over_pages(
                self._graphql_client,
                organization_id=self.org_id,
                sleep_time=self.sleep_time,
            )
            if len(spaces) > 0:
                self.space = spaces[0].name
                self.space_id = spaces[0].id
            else:
                raise ValueError("no spaces in the organization")
        else:
            results = await AsyncOrgIDandSpaceIDQuery.run_graphql_query(self._graphql_client, organization=self.organization, space=self.space)
            self.org_id = results.organization_id
            self.space_id = results.space_id

        logger.info(f"Using organization: {self.organization} and space: {self.space}")

    async def get_all_models(self) -> List[dict]:
        """Retrieves all models in the current space.

        Returns:
            List[dict]: A list of model dictionaries, each containing:
            - id (str): Unique identifier
            - name (str): Model name
            - modelType (str): Type of model
            - createdAt (datetime): Creation timestamp

        Raises:
            ArizeAPIException: If retrieval fails or there is an API error

        Example:
            >>> async with AsyncClient() as client:
            ...     models = await client.get_all_models()
            ...     print(f"Found {len(models)} models")
        """
        from arize_toolkit.queries.model_queries import AsyncGetAllModelsQuery

        results = await AsyncGetAllModelsQuery.iterate_over_pages(
            self._graphql_client,
            space_id=self.space_id,
            sleep_time=self.sleep_time,
        )
        return [result.to_dict() for result in results]

    async def get_model(self, model_name: str) -> dict:
        """Retrieves a model by name.

        Args:
            model_name (str): Name of the model to retrieve

        Returns:
            dict: A dictionary containing model information:
            - id (str): Unique identifier
            - name (str): Model name
            - modelType (str): Type of model
            - createdAt (datetime): Creation timestamp

        Raises:
            ValueError: If model_name is empty or None
            ArizeAPIException: If model not found or API error occurs

        Example:
            >>> async with AsyncClient() as client:
            ...     model = await client.get_model("my-model")
            ...     print(f"Model ID: {model['id']}")
        """
        if not model_name:
            raise ValueError("model_name is required")

        from arize_toolkit.queries.model_queries import AsyncGetModelQuery

        try:
            result = await AsyncGetModelQuery.run_graphql_query(
                self._graphql_client,
                space_id=self.space_id,
                model_name=model_name,
            )
        except ArizeAPIException as e:
            if "not found" in str(e).lower():
                raise ArizeAPIException(f"Model '{model_name}' not found in space")
            raise

        return result.to_dict()

    async def get_model_by_id(self, model_id: str) -> dict:
        """Retrieves a model by ID.

        Args:
            model_id (str): ID of the model to retrieve

        Returns:
            dict: A dictionary containing model information:
            - id (str): Unique identifier
            - name (str): Model name
            - modelType (str): Type of model
            - createdAt (datetime): Creation timestamp

        Raises:
            ValueError: If model_id is empty or None
            ArizeAPIException: If model not found or API error occurs

        Example:
            >>> async with AsyncClient() as client:
            ...     model = await client.get_model_by_id("model_123")
            ...     print(f"Model name: {model['name']}")
        """
        if not model_id:
            raise ValueError("model_id is required")

        from arize_toolkit.queries.model_queries import AsyncGetModelByIDQuery

        result = await AsyncGetModelByIDQuery.run_graphql_query(
            self._graphql_client,
            model_id=model_id,
        )
        return result.to_dict()

    # Organization and Space methods
    async def get_all_organizations(self) -> List[dict]:
        """Retrieves all organizations in the current account.

        Returns:
            List[dict]: A list of organization dictionaries, each containing:
            - id (str): Unique identifier for the organization
            - name (str): Name of the organization
            - createdAt (datetime): When the organization was created
            - description (str): Description of the organization

        Raises:
            ArizeAPIException: If there is an error retrieving organizations from the API
        """
        from arize_toolkit.queries.space_queries import AsyncGetAllOrganizationsQuery

        results = await AsyncGetAllOrganizationsQuery.iterate_over_pages(
            self._graphql_client,
            sleep_time=self.sleep_time,
        )
        return [result.to_dict() for result in results]

    async def get_all_spaces(self) -> List[dict]:
        """Retrieves all spaces in the current organization.

        Returns:
            List[dict]: A list of space dictionaries, each containing:
            - id (str): Unique identifier for the space
            - name (str): Name of the space
            - createdAt (datetime): When the space was created
            - description (str): Description of the space
            - private (bool): Whether the space is private

        Raises:
            ArizeAPIException: If there is an error retrieving organizations from the API
        """
        from arize_toolkit.queries.space_queries import AsyncGetAllSpacesQuery

        results = await AsyncGetAllSpacesQuery.iterate_over_pages(
            self._graphql_client,
            organization_id=self.org_id,
            sleep_time=self.sleep_time,
        )
        return [result.to_dict() for result in results]

    # Dashboard methods
    async def get_all_dashboards(self) -> List[dict]:
        """Retrieves all dashboards in the current space.

        Returns:
            List[dict]: A list of dashboard dictionaries, each containing:
            - id (str): Unique identifier
            - name (str): Dashboard name
            - createdAt (datetime): Creation timestamp
            - creator (dict): Creator information

        Raises:
            ArizeAPIException: If retrieval fails or there is an API error

        Example:
            >>> async with AsyncClient() as client:
            ...     dashboards = await client.get_all_dashboards()
            ...     print(f"Found {len(dashboards)} dashboards")
        """
        from arize_toolkit.queries.dashboard_queries import AsyncGetAllDashboardsQuery

        results = await AsyncGetAllDashboardsQuery.iterate_over_pages(
            self._graphql_client,
            spaceId=self.space_id,
            sleep_time=self.sleep_time,
        )
        return [result.to_dict() for result in results]

    async def get_dashboard(self, dashboard_name: str) -> dict:
        """Retrieves complete information about a dashboard by its name.

        Args:
            dashboard_name (str): Name of the dashboard to retrieve

        Returns:
            dict: A dictionary representing the dashboard with complete information

        Raises:
            ValueError: If dashboard_name is empty or None
            ArizeAPIException: If dashboard not found or API error occurs

        Example:
            >>> async with AsyncClient() as client:
            ...     dashboard = await client.get_dashboard("my-dashboard")
            ...     print(f"Dashboard ID: {dashboard['id']}")
        """
        if not dashboard_name:
            raise ValueError("dashboard_name is required")

        from arize_toolkit.queries.dashboard_queries import AsyncGetDashboardQuery

        try:
            result = await AsyncGetDashboardQuery.run_graphql_query(
                self._graphql_client,
                spaceId=self.space_id,
                dashboardName=dashboard_name,
            )
            return await self.get_dashboard_by_id(result.id)
        except ArizeAPIException as e:
            if "not found" in str(e).lower():
                raise ArizeAPIException(f"Dashboard '{dashboard_name}' not found in space")
            raise

    async def get_dashboard_by_id(self, dashboard_id: str) -> dict:
        """Retrieves complete information about a dashboard by its ID.

        Args:
            dashboard_id (str): ID of the dashboard to retrieve

        Returns:
            dict: A dictionary representing the dashboard with complete information

        Raises:
            ValueError: If dashboard_id is empty or None
            ArizeAPIException: If dashboard not found or API error occurs

        Example:
            >>> async with AsyncClient() as client:
            ...     dashboard = await client.get_dashboard_by_id("dashboard_123")
            ...     print(f"Dashboard name: {dashboard['name']}")
        """
        if not dashboard_id:
            raise ValueError("dashboard_id is required")

        # This is a complex method that requires multiple queries
        # For now, delegate to the sync version - in a full implementation
        # we'd make all the sub-queries async too
        return super().get_dashboard_by_id(dashboard_id)

    # Monitor methods
    async def get_all_monitors(self, model_id: str = None, model_name: str = None, monitor_category: str = None) -> List[dict]:
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
            - operator (str): Comparison operator for the threshold

        Raises:
            ValueError: If neither model_id nor model_name is provided
            ArizeAPIException: If the model is not found or there is an API error

        Example:
            >>> async with AsyncClient() as client:
            ...     monitors = await client.get_all_monitors(model_name="my-model")
            ...     performance_monitors = await client.get_all_monitors(model_id="model_123", monitor_category="performance")
        """
        if not model_id:
            if not model_name:
                raise ValueError("Either model_id or model_name must be provided")
            model = await self.get_model(model_name)
            model_id = model["id"]

        from arize_toolkit.queries.monitor_queries import AsyncGetAllModelMonitorsQuery

        results = await AsyncGetAllModelMonitorsQuery.iterate_over_pages(
            self._graphql_client,
            space_id=self.space_id,
            model_id=model_id,
            monitor_category=monitor_category,
            sleep_time=self.sleep_time,
        )
        return [result.to_dict() for result in results]

    async def get_monitor(self, monitor_name: str) -> dict:
        """Retrieves a monitor by name.

        Args:
            monitor_name (str): Name of the monitor to retrieve

        Returns:
            dict: A dictionary containing monitor information

        Raises:
            ValueError: If monitor_name is empty or None
            ArizeAPIException: If monitor not found or API error occurs

        Example:
            >>> async with AsyncClient() as client:
            ...     monitor = await client.get_monitor("my-monitor")
            ...     print(f"Monitor ID: {monitor['id']}")
        """
        if not monitor_name:
            raise ValueError("monitor_name is required")

        from arize_toolkit.queries.monitor_queries import AsyncGetMonitorQuery

        try:
            result = await AsyncGetMonitorQuery.run_graphql_query(
                self._graphql_client,
                space_id=self.space_id,
                monitor_name=monitor_name,
            )
        except ArizeAPIException as e:
            if "not found" in str(e).lower():
                raise ArizeAPIException(f"Monitor '{monitor_name}' not found in space")
            raise

        return result.to_dict()

    async def get_monitor_by_id(self, monitor_id: str) -> dict:
        """Retrieves a monitor by ID.

        Args:
            monitor_id (str): ID of the monitor to retrieve

        Returns:
            dict: A dictionary containing monitor information

        Raises:
            ValueError: If monitor_id is empty or None
            ArizeAPIException: If monitor not found or API error occurs

        Example:
            >>> async with AsyncClient() as client:
            ...     monitor = await client.get_monitor_by_id("monitor_123")
            ...     print(f"Monitor name: {monitor['name']}")
        """
        if not monitor_id:
            raise ValueError("monitor_id is required")

        from arize_toolkit.queries.monitor_queries import AsyncGetMonitorByIDQuery

        result = await AsyncGetMonitorByIDQuery.run_graphql_query(
            self._graphql_client,
            monitor_id=monitor_id,
        )
        return result.to_dict()

    # Custom Metrics methods
    async def get_all_custom_metrics(self, model_name: Optional[str] = None) -> List[dict]:
        """Retrieves all custom metrics, optionally filtered by model.

        Args:
            model_name (Optional[str]): If provided, only return custom metrics for this model

        Returns:
            List[dict]: A list of custom metric dictionaries

        Raises:
            ArizeAPIException: If retrieval fails or there is an API error

        Example:
            >>> async with AsyncClient() as client:
            ...     metrics = await client.get_all_custom_metrics()
            ...     model_metrics = await client.get_all_custom_metrics("my-model")
        """
        if model_name:
            from arize_toolkit.queries.custom_metric_queries import AsyncGetAllCustomMetricsByModelIdQuery

            model = await self.get_model(model_name)
            results = await AsyncGetAllCustomMetricsByModelIdQuery.iterate_over_pages(
                self._graphql_client,
                model_id=model["id"],
                sleep_time=self.sleep_time,
            )
        else:
            from arize_toolkit.queries.custom_metric_queries import AsyncGetAllCustomMetricsQuery

            results = await AsyncGetAllCustomMetricsQuery.iterate_over_pages(
                self._graphql_client,
                space_id=self.space_id,
                sleep_time=self.sleep_time,
            )

        return [result.to_dict() for result in results]

    async def get_custom_metric(self, model_name: str, metric_name: str) -> dict:
        """Retrieve a specific custom metric for a model by name.

        Args:
            model_name (str): The name of the model to get the metric for
            metric_name (str): The name of the metric to get

        Returns:
            dict: A dictionary containing metric information:
            - id (str): Unique identifier for the metric
            - name (str): Name of the metric
            - description (str): Description of what the metric measures
            - metric (str): The metric expression/formula
            - createdAt (datetime): When the metric was created
            - requiresPositiveClass (bool): Whether metric requires positive class label

        Raises:
            ValueError: If required parameters are empty or None
            ArizeAPIException: If custom metric not found or API error occurs

        Example:
            >>> async with AsyncClient() as client:
            ...     metric = await client.get_custom_metric("my-model", "accuracy")
            ...     print(f"Metric ID: {metric['id']}")
        """
        if not model_name:
            raise ValueError("model_name is required")
        if not metric_name:
            raise ValueError("metric_name is required")

        from arize_toolkit.queries.custom_metric_queries import AsyncGetCustomMetricQuery

        try:
            result = await AsyncGetCustomMetricQuery.run_graphql_query(
                self._graphql_client,
                space_id=self.space_id,
                model_name=model_name,
                metric_name=metric_name,
            )
        except ArizeAPIException as e:
            if "not found" in str(e).lower():
                raise ArizeAPIException(f"Custom metric '{metric_name}' not found for model '{model_name}'")
            raise

        return result.to_dict()

    # Prompt methods (LLM Utils)
    async def get_all_prompts(self) -> List[dict]:
        """Retrieves all prompts in the current space.

        Returns:
            List[dict]: A list of prompt dictionaries

        Raises:
            ArizeAPIException: If retrieval fails or there is an API error

        Example:
            >>> async with AsyncClient() as client:
            ...     prompts = await client.get_all_prompts()
            ...     print(f"Found {len(prompts)} prompts")
        """
        from arize_toolkit.queries.llm_utils_queries import AsyncGetAllPromptsQuery

        results = await AsyncGetAllPromptsQuery.iterate_over_pages(
            self._graphql_client,
            space_id=self.space_id,
            sleep_time=self.sleep_time,
        )
        return [result.to_dict() for result in results]

    async def get_prompt(self, prompt_name: str) -> dict:
        """Retrieves a prompt by name.

        Args:
            prompt_name (str): Name of the prompt to retrieve

        Returns:
            dict: A dictionary containing prompt information

        Raises:
            ValueError: If prompt_name is empty or None
            ArizeAPIException: If prompt not found or API error occurs

        Example:
            >>> async with AsyncClient() as client:
            ...     prompt = await client.get_prompt("my-prompt")
            ...     print(f"Prompt ID: {prompt['id']}")
        """
        if not prompt_name:
            raise ValueError("prompt_name is required")

        from arize_toolkit.queries.llm_utils_queries import AsyncGetPromptQuery

        try:
            result = await AsyncGetPromptQuery.run_graphql_query(
                self._graphql_client,
                space_id=self.space_id,
                prompt_name=prompt_name,
            )
        except ArizeAPIException as e:
            if "not found" in str(e).lower():
                raise ArizeAPIException(f"Prompt '{prompt_name}' not found in space")
            raise

        return result.to_dict()

    async def get_prompt_by_id(self, prompt_id: str) -> dict:
        """Retrieves a prompt by ID.

        Args:
            prompt_id (str): ID of the prompt to retrieve

        Returns:
            dict: A dictionary containing prompt information

        Raises:
            ValueError: If prompt_id is empty or None
            ArizeAPIException: If prompt not found or API error occurs

        Example:
            >>> async with AsyncClient() as client:
            ...     prompt = await client.get_prompt_by_id("prompt_123")
            ...     print(f"Prompt name: {prompt['name']}")
        """
        if not prompt_id:
            raise ValueError("prompt_id is required")

        from arize_toolkit.queries.llm_utils_queries import AsyncGetPromptByIDQuery

        result = await AsyncGetPromptByIDQuery.run_graphql_query(
            self._graphql_client,
            prompt_id=prompt_id,
        )
        return result.to_dict()

    # Model data methods
    async def get_model_volume_by_id(
        self,
        model_id: str,
        start_time: Optional[Union[datetime, str]] = None,
        end_time: Optional[Union[datetime, str]] = None,
    ) -> dict:
        """Retrieves prediction volume statistics for a specific model by ID.

        Args:
            model_id (str): The ID of the model to get volume for
            start_time (Optional[datetime | str]): Start time for volume calculation
            end_time (Optional[datetime | str]): End time for volume calculation

        Returns:
            int: The total number of predictions in the time period

        Raises:
            ValueError: If model_id is empty or None
            ArizeAPIException: If model not found or API error occurs

        Example:
            >>> async with AsyncClient() as client:
            ...     volume = await client.get_model_volume_by_id("model_123")
            ...     print(f"Total predictions: {volume}")
        """
        if not model_id:
            raise ValueError("model_id is required")

        from arize_toolkit.queries.model_queries import AsyncGetModelVolumeQuery
        from arize_toolkit.utils import parse_datetime

        if start_time:
            start_time = parse_datetime(start_time)
        if end_time:
            end_time = parse_datetime(end_time)

        result = await AsyncGetModelVolumeQuery.run_graphql_query(
            self._graphql_client,
            model_id=model_id,
            start_time=start_time,
            end_time=end_time,
        )
        return result.totalVolume

    async def get_model_volume(
        self,
        model_name: str,
        start_time: Optional[Union[datetime, str]] = None,
        end_time: Optional[Union[datetime, str]] = None,
    ) -> dict:
        """Retrieves prediction volume statistics for a specific model.

        Args:
            model_name (str): The name of the model to get volume for
            start_time (Optional[datetime | str]): Start time for volume calculation
            end_time (Optional[datetime | str]): End time for volume calculation

        Returns:
            int: The total number of predictions in the time period

        Raises:
            ValueError: If model_name is empty or None
            ArizeAPIException: If model not found or API error occurs

        Example:
            >>> async with AsyncClient() as client:
            ...     volume = await client.get_model_volume("my-model")
            ...     print(f"Total predictions: {volume}")
        """
        if not model_name:
            raise ValueError("model_name is required")

        model = await self.get_model(model_name)
        return await self.get_model_volume_by_id(model_id=model["id"], start_time=start_time, end_time=end_time)

    async def get_total_volume(
        self,
        start_time: Optional[Union[datetime, str]] = None,
        end_time: Optional[Union[datetime, str]] = None,
    ) -> Tuple[int, Dict[str, int]]:
        """Retrieves prediction volume statistics for all models in the space.

        Args:
            start_time (Optional[datetime | str]): Start time for volume calculation
            end_time (Optional[datetime | str]): End time for volume calculation

        Returns:
            Tuple[int, Dict[str, int]]: A tuple containing:
            - int: The total number of predictions in the time period
            - Dict[str, int]: A dictionary mapping model names to their prediction volumes

        Raises:
            ArizeAPIException: If the space is not found or there is an API error

        Example:
            >>> async with AsyncClient() as client:
            ...     total, volumes = await client.get_total_volume()
            ...     print(f"Total volume: {total}")
            ...     for model_name, volume in volumes.items():
            ...         print(f"{model_name}: {volume}")
        """
        import asyncio

        from arize_toolkit.utils import parse_datetime

        if start_time:
            start_time = parse_datetime(start_time)
        if end_time:
            end_time = parse_datetime(end_time)

        # Get all models first
        models = await self.get_all_models()

        total_volume = 0
        model_volumes = {}

        # Get volumes for all models concurrently - this is the async advantage!
        volume_tasks = []
        model_names = []

        for model in models:
            model_id = model["id"]
            model_name = model["name"]
            model_names.append(model_name)

            # Create async task for getting volume
            task = self.get_model_volume_by_id(model_id, start_time, end_time)
            volume_tasks.append(task)

        # Wait for all volume queries to complete concurrently
        if self.sleep_time > 0:
            # If sleep_time is set, add delays between batches
            volumes = []
            for task in volume_tasks:
                volume = await task
                volumes.append(volume)
                if self.sleep_time > 0:
                    await asyncio.sleep(self.sleep_time)
        else:
            # Run all concurrently without delays
            volumes = await asyncio.gather(*volume_tasks)

        # Aggregate results
        for model_name, volume in zip(model_names, volumes):
            total_volume += volume
            model_volumes[model_name] = volume

        return total_volume, model_volumes

    async def delete_data_by_id(
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
            end_time (Optional[datetime | str]): The end time of the time range to delete data from
            environment (Literal["PRODUCTION", "PREPRODUCTION"]): The environment to delete data from

        Returns:
            bool: True if the data was deleted successfully, False otherwise

        Raises:
            ValueError: If required parameters are missing
            ArizeAPIException: If model not found or API error occurs

        Example:
            >>> async with AsyncClient() as client:
            ...     success = await client.delete_data_by_id("model_123", "2023-01-01")
            ...     print(f"Data deleted: {success}")
        """
        if not model_id:
            raise ValueError("model_id is required")
        if not start_time:
            raise ValueError("start_time is required")

        from arize_toolkit.queries.model_queries import AsyncDeleteDataMutation
        from arize_toolkit.utils import parse_datetime

        if start_time:
            start_time = parse_datetime(start_time).date()
        if end_time:
            end_time = parse_datetime(end_time).date()

        variables = {
            "modelId": model_id,
            "startDate": start_time,
            "environment": environment.upper(),
        }
        if end_time and end_time > start_time:
            variables["endDate"] = end_time

        result = await AsyncDeleteDataMutation.run_graphql_mutation(
            self._graphql_client,
            **variables,
        )
        return result.success

    async def delete_data(
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
            end_time (Optional[datetime | str]): The end time of the time range to delete data from
            environment (Literal["PRODUCTION", "PREPRODUCTION"]): The environment to delete data from

        Returns:
            bool: True if the data was deleted successfully, False otherwise

        Raises:
            ValueError: If required parameters are missing
            ArizeAPIException: If model not found or API error occurs

        Example:
            >>> async with AsyncClient() as client:
            ...     success = await client.delete_data("my-model", "2023-01-01")
            ...     print(f"Data deleted: {success}")
        """
        if not model_name:
            raise ValueError("model_name is required")

        model = await self.get_model(model_name)
        return await self.delete_data_by_id(model["id"], start_time, end_time, environment)

    # Custom Metrics CRUD methods
    async def create_custom_metric(
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

        Example:
            >>> async with AsyncClient() as client:
            ...     url = await client.create_custom_metric(
            ...         "SELECT AVG(prediction) FROM model",
            ...         "avg_prediction",
            ...         model_name="my-model"
            ...     )
            ...     print(f"Created custom metric: {url}")
        """
        if not model_id:
            if not model_name:
                raise ValueError("Either model_id or model_name must be provided")
            model = await self.get_model(model_name)
            model_id = model["id"]

        from arize_toolkit.queries.custom_metric_queries import AsyncCreateCustomMetricMutation

        inputs = {
            "metric": metric,
            "modelId": model_id,
            "name": metric_name,
        }
        if metric_description:
            inputs["description"] = metric_description
        if metric_environment:
            inputs["modelEnvironmentName"] = metric_environment

        result = await AsyncCreateCustomMetricMutation.run_graphql_mutation(
            self._graphql_client,
            **inputs,
        )
        return self.custom_metric_url(model_id, result.metric_id)

    async def delete_custom_metric_by_id(self, custom_metric_id: str, model_id: str) -> bool:
        """Deletes a custom metric by ID.

        Args:
            custom_metric_id (str): ID of the custom metric to delete
            model_id (str): ID of the model to delete the custom metric for

        Returns:
            bool: True if the custom metric was deleted, False otherwise

        Raises:
            ValueError: If required parameters are missing
            ArizeAPIException: If the custom metric is not found or there is an API error

        Example:
            >>> async with AsyncClient() as client:
            ...     success = await client.delete_custom_metric_by_id("metric_123", "model_456")
            ...     print(f"Deleted: {success}")
        """
        if not custom_metric_id:
            raise ValueError("custom_metric_id is required")
        if not model_id:
            raise ValueError("model_id is required")

        from arize_toolkit.queries.custom_metric_queries import AsyncDeleteCustomMetricMutation

        result = await AsyncDeleteCustomMetricMutation.run_graphql_mutation(
            self._graphql_client,
            customMetricId=custom_metric_id,
            modelId=model_id,
        )
        return result.model_id == model_id

    async def delete_custom_metric(self, model_name: str, metric_name: str) -> bool:
        """Deletes a custom metric by name.

        Args:
            model_name (str): Name of the model to delete the custom metric for
            metric_name (str): Name of the custom metric to delete

        Returns:
            bool: True if the custom metric was deleted, False otherwise

        Raises:
            ValueError: If required parameters are missing
            ArizeAPIException: If the custom metric is not found or there is an API error

        Example:
            >>> async with AsyncClient() as client:
            ...     success = await client.delete_custom_metric("my-model", "accuracy")
            ...     print(f"Deleted: {success}")
        """
        if not model_name:
            raise ValueError("model_name is required")
        if not metric_name:
            raise ValueError("metric_name is required")

        model = await self.get_model(model_name)
        metric = await self.get_custom_metric(model_name, metric_name)
        return await self.delete_custom_metric_by_id(metric["id"], model["id"])

    # Prompt CRUD methods
    async def create_prompt(
        self,
        name: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        """Creates a new prompt.

        Args:
            name (str): Name of the prompt
            description (Optional[str]): Description of the prompt
            tags (Optional[List[str]]): Tags for the prompt

        Returns:
            str: URL to the newly created prompt

        Raises:
            ValueError: If required parameters are missing
            ArizeAPIException: If creation fails or API error occurs

        Example:
            >>> async with AsyncClient() as client:
            ...     url = await client.create_prompt("my-prompt", "A test prompt")
            ...     print(f"Created prompt: {url}")
        """
        if not name:
            raise ValueError("name is required")

        from arize_toolkit.queries.llm_utils_queries import AsyncCreatePromptMutation

        result = await AsyncCreatePromptMutation.run_graphql_mutation(
            self._graphql_client,
            spaceId=self.space_id,
            name=name,
            description=description,
            tags=tags or [],
        )
        return self.prompt_url(result.id)

    async def update_prompt_by_id(
        self,
        prompt_id: str,
        updated_name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> bool:
        """Updates a prompt by ID.

        Args:
            prompt_id (str): ID of the prompt to update
            updated_name (Optional[str]): Updated name for the prompt
            description (Optional[str]): Updated description for the prompt
            tags (Optional[List[str]]): Updated tags for the prompt

        Returns:
            bool: True if the prompt was updated successfully

        Raises:
            ValueError: If required parameters are missing
            ArizeAPIException: If update fails or API error occurs

        Example:
            >>> async with AsyncClient() as client:
            ...     success = await client.update_prompt_by_id("prompt_123", description="Updated description")
            ...     print(f"Updated: {success}")
        """
        if not prompt_id:
            raise ValueError("prompt_id is required")

        from arize_toolkit.queries.llm_utils_queries import AsyncUpdatePromptMutation

        result = await AsyncUpdatePromptMutation.run_graphql_mutation(
            self._graphql_client,
            promptId=prompt_id,
            name=updated_name,
            description=description,
            tags=tags,
        )
        return result.success

    async def update_prompt(
        self,
        prompt_name: str,
        updated_name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> bool:
        """Updates a prompt by name.

        Args:
            prompt_name (str): Name of the prompt to update
            updated_name (Optional[str]): Updated name for the prompt
            description (Optional[str]): Updated description for the prompt
            tags (Optional[List[str]]): Updated tags for the prompt

        Returns:
            bool: True if the prompt was updated successfully

        Raises:
            ValueError: If required parameters are missing
            ArizeAPIException: If update fails or API error occurs

        Example:
            >>> async with AsyncClient() as client:
            ...     success = await client.update_prompt("my-prompt", description="Updated description")
            ...     print(f"Updated: {success}")
        """
        if not prompt_name:
            raise ValueError("prompt_name is required")
        if not updated_name and not description and not tags:
            raise ValueError("At least one of updated_name, description, or tags must be provided")

        prompt = await self.get_prompt(prompt_name)
        name = updated_name if updated_name else prompt_name
        return await self.update_prompt_by_id(prompt["id"], updated_name=name, description=description, tags=tags)

    async def delete_prompt_by_id(self, prompt_id: str) -> bool:
        """Deletes a prompt by ID.

        Args:
            prompt_id (str): ID of the prompt to delete

        Returns:
            bool: True if the prompt was deleted successfully

        Raises:
            ValueError: If prompt_id is empty or None
            ArizeAPIException: If deletion fails or API error occurs

        Example:
            >>> async with AsyncClient() as client:
            ...     success = await client.delete_prompt_by_id("prompt_123")
            ...     print(f"Deleted: {success}")
        """
        if not prompt_id:
            raise ValueError("prompt_id is required")

        from arize_toolkit.queries.llm_utils_queries import AsyncDeletePromptMutation

        result = await AsyncDeletePromptMutation.run_graphql_mutation(
            self._graphql_client,
            promptId=prompt_id,
            spaceId=self.space_id,
        )
        return result.success

    async def delete_prompt(self, prompt_name: str) -> bool:
        """Deletes a prompt by name.

        Args:
            prompt_name (str): Name of the prompt to delete

        Returns:
            bool: True if the prompt was deleted successfully

        Raises:
            ValueError: If prompt_name is empty or None
            ArizeAPIException: If deletion fails or API error occurs

        Example:
            >>> async with AsyncClient() as client:
            ...     success = await client.delete_prompt("my-prompt")
            ...     print(f"Deleted: {success}")
        """
        if not prompt_name:
            raise ValueError("prompt_name is required")

        prompt = await self.get_prompt(prompt_name)
        return await self.delete_prompt_by_id(prompt["id"])

    # Space management methods
    async def create_new_space(self, name: str, private: bool = True, set_as_active: bool = True) -> str:
        """Creates a new space in the current organization.

        Args:
            name (str): Name for the new space
            private (bool): Whether the space should be private (default: True)
            set_as_active (bool): Whether to set the new space as active (default: True)

        Returns:
            str: The unique identifier (ID) of the newly created space

        Raises:
            ValueError: If name is empty or None
            ArizeAPIException: If creation fails or API error occurs

        Example:
            >>> async with AsyncClient() as client:
            ...     space_id = await client.create_new_space("my-new-space")
            ...     print(f"Created space: {space_id}")
        """
        if not name:
            raise ValueError("name is required")

        from arize_toolkit.queries.space_queries import AsyncCreateNewSpaceMutation

        result = await AsyncCreateNewSpaceMutation.run_graphql_mutation(
            self._graphql_client,
            accountOrganizationId=self.org_id,
            name=name,
            private=private,
        )
        if set_as_active:
            # Note: switch_space is a sync method, would need async version
            super().switch_space(organization=self.organization, space=name)
        return result.id

    async def create_space_admin_api_key(self, name: str) -> dict:
        """Creates an admin API key for a specific space.

        Args:
            name (str): Name for the API key

        Returns:
            dict: A dictionary containing:
            - apiKey (str): The generated API key
            - expiresAt (datetime, optional): When the key expires
            - id (str): Unique identifier for the key

        Raises:
            ValueError: If name is empty or None
            ArizeAPIException: If creation fails or API error occurs

        Example:
            >>> async with AsyncClient() as client:
            ...     api_key = await client.create_space_admin_api_key("my-api-key")
            ...     print(f"API Key: {api_key['apiKey']}")
        """
        if not name:
            raise ValueError("name is required")

        from arize_toolkit.queries.space_queries import AsyncCreateSpaceAdminApiKeyMutation

        result = await AsyncCreateSpaceAdminApiKeyMutation.run_graphql_mutation(
            self._graphql_client,
            name=name,
            spaceId=self.space_id,
        )
        return result.to_dict()
