from typing import List, Optional, Tuple

from arize_toolkit.models.dataset_models import Dataset, DatasetExample
from arize_toolkit.queries.basequery import ArizeAPIException, BaseQuery, BaseResponse, BaseVariables


class GetAllDatasetsQuery(BaseQuery):
    graphql_query = (
        """
    query getAllDatasets($spaceId: ID!, $endCursor: String) {
        node(id: $spaceId) {
            ... on Space {
                datasets(first: 50, after: $endCursor) {
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                    edges {
                        node { """
        + Dataset.to_graphql_fields()
        + """
                        }
                    }
                }
            }
        }
    }
    """
    )
    query_description = "List all datasets in a space"

    class Variables(BaseVariables):
        spaceId: str

    class QueryException(ArizeAPIException):
        message: str = "Error running query to list datasets"

    class QueryResponse(Dataset):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if "node" not in result or "datasets" not in result["node"] or "edges" not in result["node"]["datasets"]:
            return [], False, None
        edges = result["node"]["datasets"]["edges"]
        if not edges:
            return [], False, None
        page_info = result["node"]["datasets"]["pageInfo"]
        datasets = [cls.QueryResponse(**edge["node"]) for edge in edges]
        return (datasets, page_info["hasNextPage"], page_info["endCursor"])


class GetDatasetByIdQuery(BaseQuery):
    graphql_query = (
        """
    query getDatasetById($datasetId: ID!) {
        node(id: $datasetId) {
            ... on Dataset { """
        + Dataset.to_graphql_fields()
        + """
            }
        }
    }
    """
    )
    query_description = "Get a dataset by its ID"

    class Variables(BaseVariables):
        datasetId: str

    class QueryException(ArizeAPIException):
        message: str = "Error running query to retrieve dataset by ID"

    class QueryResponse(Dataset):
        pass


class GetDatasetByNameQuery(BaseQuery):
    graphql_query = (
        """
    query getDatasetByName($spaceId: ID!, $datasetName: String!) {
        node(id: $spaceId) {
            ... on Space {
                datasets(search: $datasetName, first: 1) {
                    edges {
                        node { """
        + Dataset.to_graphql_fields()
        + """
                        }
                    }
                }
            }
        }
    }
    """
    )
    query_description = "Get a dataset by name within a space"

    class Variables(BaseVariables):
        spaceId: str
        datasetName: str

    class QueryException(ArizeAPIException):
        message: str = "Error running query to retrieve dataset by name"

    class QueryResponse(Dataset):
        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if "node" not in result or "datasets" not in result["node"] or "edges" not in result["node"]["datasets"]:
            cls.raise_exception("No datasets found")
        edges = result["node"]["datasets"]["edges"]
        if len(edges) == 0:
            cls.raise_exception("No dataset found matching the given name")
        dataset = edges[0]["node"]
        return ([cls.QueryResponse(**dataset)], False, None)


class GetDatasetExamplesQuery(BaseQuery):
    graphql_query = """
    query getDatasetExamples($datasetId: ID!, $first: Int, $endCursor: String) {
        node(id: $datasetId) {
            ... on Dataset {
                latestDatasetVersion {
                    examples(first: $first, after: $endCursor) {
                        pageInfo {
                            hasNextPage
                            endCursor
                        }
                        edges {
                            node {
                                id
                                createdAt
                                updatedAt
                                columns {
                                    dimension {
                                        name
                                    }
                                    dimensionValue {
                                        ... on CategoricalDimensionValue { sv: value }
                                        ... on NumericDimensionValue { nv: value }
                                        ... on ListOfStringsDimensionValue { lv: value }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    """
    query_description = "Get examples from the latest version of a dataset"

    class Variables(BaseVariables):
        datasetId: str
        first: int = 50

    class QueryException(ArizeAPIException):
        message: str = "Error running query to retrieve dataset examples"

    class QueryResponse(DatasetExample):
        pass

    @classmethod
    def _extract_value(cls, dim_value: dict):
        """Extract the value from an aliased DimensionValueUnion response."""
        if dim_value is None:
            return None
        # Check each alias in order of likelihood
        for key in ("sv", "nv", "lv"):
            if key in dim_value:
                return dim_value[key]
        return None

    @classmethod
    def _parse_example(cls, example_node: dict) -> "GetDatasetExamplesQuery.QueryResponse":
        data = {}
        for col in example_node.get("columns", []):
            dim_name = col["dimension"]["name"]
            dim_value = col.get("dimensionValue")
            data[dim_name] = cls._extract_value(dim_value)
        return cls.QueryResponse(
            id=example_node["id"],
            createdAt=example_node.get("createdAt"),
            updatedAt=example_node.get("updatedAt"),
            data=data,
        )

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if "node" not in result or result["node"] is None:
            cls.raise_exception("Dataset not found")
        node = result["node"]
        version = node.get("latestDatasetVersion")
        if version is None:
            cls.raise_exception("No dataset version found")
        examples_conn = version.get("examples")
        if examples_conn is None:
            cls.raise_exception("No examples found")
        page_info = examples_conn["pageInfo"]
        examples = [cls._parse_example(edge["node"]) for edge in examples_conn.get("edges", [])]
        return (examples, page_info["hasNextPage"], page_info["endCursor"])
