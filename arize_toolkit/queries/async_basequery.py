import asyncio
from typing import List, Optional, Tuple

from gql import Client as GraphQLClient
from gql import gql

from arize_toolkit.exceptions import ArizeAPIException
from arize_toolkit.queries.basequery import BaseResponse, BaseVariables


class AsyncExecutionMixin:
    """Mixin that provides async execution methods for GraphQL queries"""

    @classmethod
    async def _graphql_query(cls, client: GraphQLClient, **kwargs) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        try:
            query = gql(cls.graphql_query)
            variable_values = cls.Variables(**kwargs).to_dict(exclude_none=False)
            result = await client.execute_async(
                query,
                variable_values=variable_values,
            )
            if "errors" in result:
                cls.raise_exception(str(result["errors"]))
            return cls._parse_graphql_result(result)
        except ArizeAPIException as qe:
            raise qe
        except Exception as e:
            cls.raise_exception(str(e))

    @classmethod
    async def _graphql_mutation(cls, client: GraphQLClient, **kwargs) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        try:
            query = gql(cls.graphql_query)
            variable_values = cls.Variables(**kwargs).to_dict(exclude_none=True)
            result = await client.execute_async(
                query,
                variable_values={"input": variable_values},
            )
            if "errors" in result:
                cls.raise_exception(str(result["errors"]))
            return cls._parse_graphql_result(result)
        except ArizeAPIException as qe:
            raise qe
        except Exception as e:
            cls.raise_exception(str(e))

    @classmethod
    async def run_graphql_query(cls, client: GraphQLClient, **kwargs) -> BaseResponse:
        response, _, _ = await cls._graphql_query(client, **kwargs)
        return response[0]

    @classmethod
    async def run_graphql_query_to_list(cls, client: GraphQLClient, **kwargs) -> List[BaseResponse]:
        response, _, _ = await cls._graphql_query(client, **kwargs)
        return response

    @classmethod
    async def run_graphql_mutation(cls, client: GraphQLClient, **kwargs) -> BaseResponse:
        response, _, _ = await cls._graphql_mutation(client, **kwargs)
        return response[0]

    @classmethod
    async def iterate_over_pages(cls, client: GraphQLClient, sleep_time: int = 0, **kwargs) -> List[BaseResponse]:
        result = []
        cursorCount = 100
        currentPage, hasNextPage, endCursor = await cls._graphql_query(client, **kwargs)
        result.extend(currentPage)
        while hasNextPage and cursorCount > 0:
            currentPage, hasNextPage, endCursor = await cls._graphql_query(client, endCursor=endCursor, **kwargs)
            result.extend(currentPage)
            cursorCount -= 1
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
        return result


def make_async(sync_query_class):
    """
    Factory function that creates an async version of a sync query class.

    This allows us to reuse all the parsing logic, Variables, QueryResponse, etc.
    from the sync version while only changing the execution methods to be async.

    Args:
        sync_query_class: The sync query class to make async

    Returns:
        A new class that inherits from both the sync class and AsyncExecutionMixin

    Example:
        >>> from arize_toolkit.queries.model_queries import GetModelQuery
        >>> AsyncGetModelQuery = make_async(GetModelQuery)
        >>> # Now AsyncGetModelQuery has async execution but same parsing logic
    """

    class AsyncVersion(AsyncExecutionMixin, sync_query_class):
        pass

    # Set a meaningful name for the class
    AsyncVersion.__name__ = f"Async{sync_query_class.__name__}"
    AsyncVersion.__qualname__ = f"Async{sync_query_class.__qualname__}"

    return AsyncVersion


class AsyncBaseQuery(AsyncExecutionMixin):
    """Base class for all async queries"""

    graphql_query: str
    query_description: str

    class Variables(BaseVariables):
        """Validation for the query variables"""

        pass

    class QueryException(ArizeAPIException):
        """Exception for the query"""

        pass

    class QueryResponse(BaseResponse):
        """Response for the query"""

        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        # Default behavior for queries of objects by id
        if "node" in result and result["node"] is not None:
            result_node = result["node"]
            return [cls.QueryResponse(**result_node)], False, None
        else:
            cls.raise_exception("Object not found")

    @classmethod
    def raise_exception(cls, details: Optional[str] = None) -> None:
        raise cls.QueryException(details=details) from None
