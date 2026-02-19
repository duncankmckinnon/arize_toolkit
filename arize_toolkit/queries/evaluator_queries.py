from typing import List, Optional, Tuple

from arize_toolkit.models.evaluator_models import CreateEvaluatorMutationInput, CreateEvaluatorVersionMutationInput, DeleteEvaluatorMutationInput, EditEvaluatorMutationInput, Evaluator
from arize_toolkit.queries.basequery import ArizeAPIException, BaseQuery, BaseResponse, BaseVariables


class GetEvaluatorsQuery(BaseQuery):
    graphql_query = (
        """
    query getEvaluators($space_id: ID!, $first: Int, $endCursor: String, $search: String, $name: String, $taskType: OnlineTaskType) {
        node(id: $space_id) {
            ... on Space {
                evaluators(first: $first, after: $endCursor, search: $search, name: $name, taskType: $taskType) {
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                    edges {
                        node {"""
        + Evaluator.to_graphql_fields()
        + """
                        }
                    }
                }
            }
        }
    }
    """
    )
    query_description = "Get evaluators for a space"

    class Variables(BaseVariables):
        space_id: str
        first: int = 50
        search: Optional[str] = None
        name: Optional[str] = None
        taskType: Optional[str] = None

    class QueryException(ArizeAPIException):
        message: str = "Error getting evaluators"

    class QueryResponse(Evaluator):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if "node" not in result or result["node"] is None:
            cls.raise_exception("Space not found")
        evaluators_data = result["node"].get("evaluators", {})
        pageInfo = evaluators_data.get("pageInfo", {})
        edges = evaluators_data.get("edges", [])
        evaluators = [cls.QueryResponse(**edge["node"]) for edge in edges if edge.get("node")]
        return evaluators, pageInfo.get("hasNextPage", False), pageInfo.get("endCursor")


class GetEvaluatorQuery(BaseQuery):
    graphql_query = (
        """
    query getEvaluator($eval_id: ID!) {
        node(id: $eval_id) {
            ... on Evaluator {"""
        + Evaluator.to_graphql_fields()
        + """
            }
        }
    }
    """
    )
    query_description = "Get an evaluator by id"

    class Variables(BaseVariables):
        eval_id: str

    class QueryException(ArizeAPIException):
        message: str = "Error getting evaluator by id"

    class QueryResponse(Evaluator):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if "node" not in result or result["node"] is None:
            cls.raise_exception("Evaluator not found")
        return [cls.QueryResponse(**result["node"])], False, None


class GetEvaluatorByNameQuery(BaseQuery):
    graphql_query = (
        """
    query getEvaluatorByName($space_id: ID!, $name: String!) {
        node(id: $space_id) {
            ... on Space {
                evaluators(first: 1, name: $name) {
                    edges {
                        node {"""
        + Evaluator.to_graphql_fields()
        + """
                        }
                    }
                }
            }
        }
    }
    """
    )
    query_description = "Get an evaluator by name"

    class Variables(BaseVariables):
        space_id: str
        name: str

    class QueryException(ArizeAPIException):
        message: str = "Error getting evaluator by name"

    class QueryResponse(Evaluator):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if "node" not in result or result["node"] is None:
            cls.raise_exception("Space not found")
        edges = result["node"].get("evaluators", {}).get("edges", [])
        if len(edges) == 0:
            cls.raise_exception("No evaluator found with the given name")
        return [cls.QueryResponse(**edges[0]["node"])], False, None


class CreateEvaluatorMutation(BaseQuery):
    graphql_query = (
        """
    mutation createEvaluator($input: CreateEvaluatorMutationInput!) {
        createEvaluator(input: $input) {
            evaluator {"""
        + Evaluator.to_graphql_fields()
        + """
            }
        }
    }
    """
    )
    query_description = "Create an evaluator (template or code)"

    class Variables(CreateEvaluatorMutationInput):
        pass

    class QueryException(ArizeAPIException):
        message: str = "Error in creating an evaluator"

    class QueryResponse(Evaluator):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if "createEvaluator" not in result:
            cls.raise_exception("No evaluator created")
        payload = result["createEvaluator"]
        if "evaluator" not in payload or payload["evaluator"] is None:
            cls.raise_exception("No evaluator returned in response")
        return [cls.QueryResponse(**payload["evaluator"])], False, None


class CreateEvaluatorVersionMutation(BaseQuery):
    graphql_query = (
        """
    mutation createEvaluatorVersion($input: CreateEvaluatorVersionMutationInput!) {
        createEvaluatorVersion(input: $input) {
            evaluator {"""
        + Evaluator.to_graphql_fields()
        + """
            }
        }
    }
    """
    )
    query_description = "Create a new version of an evaluator"

    class Variables(CreateEvaluatorVersionMutationInput):
        pass

    class QueryException(ArizeAPIException):
        message: str = "Error in creating an evaluator version"

    class QueryResponse(Evaluator):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if "createEvaluatorVersion" not in result:
            cls.raise_exception("No evaluator version created")
        payload = result["createEvaluatorVersion"]
        if "evaluator" not in payload or payload["evaluator"] is None:
            cls.raise_exception("No evaluator returned in response")
        return [cls.QueryResponse(**payload["evaluator"])], False, None


class EditEvaluatorMutation(BaseQuery):
    graphql_query = (
        """
    mutation editEvaluator($input: EditEvaluatorMutationInput!) {
        editEvaluator(input: $input) {
            evaluator {"""
        + Evaluator.to_graphql_fields()
        + """
            }
        }
    }
    """
    )
    query_description = "Edit an evaluator's metadata"

    class Variables(EditEvaluatorMutationInput):
        pass

    class QueryException(ArizeAPIException):
        message: str = "Error in editing an evaluator"

    class QueryResponse(Evaluator):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if "editEvaluator" not in result:
            cls.raise_exception("No evaluator edited")
        payload = result["editEvaluator"]
        if "evaluator" not in payload or payload["evaluator"] is None:
            cls.raise_exception("No evaluator returned in response")
        return [cls.QueryResponse(**payload["evaluator"])], False, None


class DeleteEvaluatorMutation(BaseQuery):
    graphql_query = """
    mutation deleteEvaluator($input: DeleteEvaluatorMutationInput!) {
        deleteEvaluator(input: $input) {
            success
        }
    }
    """
    query_description = "Delete an evaluator"

    class Variables(DeleteEvaluatorMutationInput):
        pass

    class QueryException(ArizeAPIException):
        message: str = "Error in deleting an evaluator"

    class QueryResponse(BaseResponse):
        success: bool

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if "deleteEvaluator" not in result:
            cls.raise_exception("No response from delete evaluator")
        payload = result["deleteEvaluator"]
        if not payload.get("success"):
            cls.raise_exception("Failed to delete evaluator")
        return [cls.QueryResponse(success=True)], False, None
