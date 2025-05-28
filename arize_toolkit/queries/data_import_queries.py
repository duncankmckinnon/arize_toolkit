from typing import List, Optional, Tuple

from arize_toolkit.models import FileImportJob, FileImportJobCheck, FileImportJobInput, TableImportJob, TableImportJobCheck, TableImportJobInput
from arize_toolkit.queries.basequery import ArizeAPIException, BaseQuery, BaseResponse, BaseVariables


class GetFileImportJobQuery(BaseQuery):
    """Query for getting a file import job status."""

    graphql_query = (
        """
    query GetFileImportJobStatus($spaceId: ID!, $jobId: String!) {
        node(id: $spaceId) {
            ... on Space {
                importJobs(search: $jobId, first: 1) {
                    edges {
                        node {
                            """
        + FileImportJob.to_graphql_fields()
        + """
                        }
                    }
                }
            }
        }
    }
    """
    )
    query_description = "Get a file import job"

    class Variables(BaseVariables):
        spaceId: str
        jobId: str

        class QueryException(ArizeAPIException):
            """Exception raised when file import job status check fails."""

        message: str = "Error getting file import job"

    class QueryResponse(FileImportJob):
        """Response from getting a file import job."""

        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        """Parse the GraphQL result into a FileImportJob response."""
        if "node" not in result:
            cls.raise_exception("No node found")

        if "importJobs" not in result["node"] or not result["node"]["importJobs"]["edges"]:
            cls.raise_exception("No import jobs found")

        job_data = result["node"]["importJobs"]["edges"][0]["node"]
        if not job_data:
            cls.raise_exception("No file import job data returned")

        return [cls.QueryResponse(**job_data)], False, None


class GetAllFileImportJobsQuery(BaseQuery):
    """Query for getting all file import jobs."""

    graphql_query = (
        """
    query GetAllFileImportJobs($spaceId: ID!, $endCursor: String) {
        node(id: $spaceId) {
            ... on Space {
                importJobs(first: 10, after: $endCursor) {
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                    edges {
                        node {
                            """
        + FileImportJobCheck.to_graphql_fields()
        + """
                        }
                    }
                }
            }
        }
    }
    """
    )
    query_description = "Get all file import jobs"

    class Variables(BaseVariables):
        """Input variables for getting all file import jobs."""

        spaceId: str

    class QueryException(ArizeAPIException):
        """Exception raised when getting all file import jobs fails."""

        message: str = "Error getting all file import jobs"

    class QueryResponse(FileImportJob):
        """Response from a file import job."""

        pass

    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        """Parse the GraphQL result into a FileImportJobCheck response."""
        if "node" not in result:
            cls.raise_exception("No node found")

        if "importJobs" not in result["node"] or not result["node"]["importJobs"]["edges"]:
            cls.raise_exception("No import jobs found")

        edges = result["node"]["importJobs"]["edges"]
        page_info = result["node"]["importJobs"]["pageInfo"]
        job_data = [cls.QueryResponse(**job["node"]) for job in edges]
        has_next_page = page_info["hasNextPage"]
        end_cursor = page_info["endCursor"]
        return job_data, has_next_page, end_cursor


class CreateFileImportJobMutation(BaseQuery):
    """Mutation for creating a file import job."""

    graphql_query = (
        """
    mutation CreateFileImportJob($input: CreateFileImportJobInput!) {
        createFileImportJob(input: $input) {
            fileImportJob { """
        + FileImportJobCheck.to_graphql_fields()
        + """
            }
        }
    }
    """
    )
    query_description = "Create a new file import job"

    class Variables(FileImportJobInput):
        """Input variables for creating a file import job."""

        pass

    class QueryException(ArizeAPIException):
        """Exception raised when file import job creation fails."""

        message: str = "Error creating file import job"

    class QueryResponse(FileImportJobCheck):
        """Response from creating a file import job."""

        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        """Parse the GraphQL result into a FileImportJob response."""
        if "createFileImportJob" not in result:
            cls.raise_exception("No file import job created")

        job_data = result["createFileImportJob"]["fileImportJob"]
        if not job_data:
            cls.raise_exception("No file import job data returned")

        return [cls.QueryResponse(**job_data)], False, None


class GetTableImportJobQuery(BaseQuery):
    """Query for getting a table import job status."""

    graphql_query = (
        """
    query GetTableImportJobStatus($spaceId: ID!, $jobId: String!) {
        node(id: $spaceId) {
            ... on Space {
                tableJobs(search: $jobId, first: 1) {
                    edges {
                        node {
                            """
        + TableImportJob.to_graphql_fields()
        + """
                        }
                    }
                }
            }
        }
    }
    """
    )
    query_description = "Get a table import job"

    class Variables(BaseVariables):
        """Input variables for getting a table import job."""

        spaceId: str
        jobId: str

    class QueryException(ArizeAPIException):
        """Exception raised when table import job status check fails."""

        message: str = "Error getting table import job"

    class QueryResponse(TableImportJob):
        """Response from getting a table import job."""

        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        """Parse the GraphQL result into a TableImportJob response."""
        if "node" not in result:
            cls.raise_exception("No node found")

        if "tableJobs" not in result["node"] or not result["node"]["tableJobs"]["edges"]:
            cls.raise_exception("No table import jobs found")

        job_data = result["node"]["tableJobs"]["edges"][0]["node"]
        if not job_data:
            cls.raise_exception("No table import job data returned")

        return [cls.QueryResponse(**job_data)], False, None


class GetAllTableImportJobsQuery(BaseQuery):
    """Query for getting all table import jobs."""

    graphql_query = (
        """
    query GetAllTableImportJobs($spaceId: ID!, $endCursor: String) {
        node(id: $spaceId) {
            ... on Space {
                tableJobs(first: 10, after: $endCursor) {
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                    edges {
                        node {
                            """
        + TableImportJob.to_graphql_fields()
        + """
                        }
                    }
                }
            }
        }
    }
    """
    )
    query_description = "Get all table import jobs"

    class Variables(BaseVariables):
        """Input variables for getting all table import jobs."""

        spaceId: str

    class QueryException(ArizeAPIException):
        """Exception raised when getting all table import jobs fails."""

        message: str = "Error getting all table import jobs"

    class QueryResponse(TableImportJob):
        """Response from getting all table import jobs."""

        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        """Parse the GraphQL result into a TableImportJobCheck response."""
        if "node" not in result:
            cls.raise_exception("No node found")

        if "tableJobs" not in result["node"] or not result["node"]["tableJobs"]["edges"]:
            cls.raise_exception("No table import jobs found")

        edges = result["node"]["tableJobs"]["edges"]
        page_info = result["node"]["tableJobs"]["pageInfo"]
        job_data = [cls.QueryResponse(**job["node"]) for job in edges]
        has_next_page = page_info["hasNextPage"]
        end_cursor = page_info["endCursor"]
        return job_data, has_next_page, end_cursor


class CreateTableImportJobMutation(BaseQuery):
    """Mutation for creating a table import job."""

    graphql_query = (
        """
    mutation CreateTableImportJob($input: CreateTableImportJobInput!) {
        createTableImportJob(input: $input) {
            tableImportJob { """
        + TableImportJobCheck.to_graphql_fields()
        + """
            }
        }
    }
    """
    )
    query_description = "Create a new table import job"

    class Variables(TableImportJobInput):
        """Input variables for creating a table import job."""

        pass

    class QueryException(ArizeAPIException):
        """Exception raised when table import job creation fails."""

        message: str = "Error creating table import job"

    class QueryResponse(TableImportJobCheck):
        """Response from creating a table import job."""

        pass

    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        """Parse the GraphQL result into a TableImportJobCheck response."""
        if "createTableImportJob" not in result:
            cls.raise_exception("No table import job created")
        import_job = result["createTableImportJob"]

        if "tableImportJob" not in import_job:
            cls.raise_exception("No table import job data returned")

        job_data = import_job["tableImportJob"]

        return [cls.QueryResponse(**job_data)], False, None
