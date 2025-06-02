import pytest

from arize_toolkit.exceptions import ArizeAPIException
from arize_toolkit.models import (
    BigQueryTableConfig,
    ClassificationSchemaInput,
    DatabricksTableConfig,
    EmbeddingFeatureInput,
    FileImportJobInput,
    MultiClassSchemaInput,
    RankSchemaInput,
    RegressionSchemaInput,
    SnowflakeTableConfig,
    TableImportJobInput,
)
from arize_toolkit.queries.data_import_queries import (
    CreateFileImportJobMutation,
    CreateTableImportJobMutation,
    DeleteFileImportJobMutation,
    DeleteTableImportJobMutation,
    GetAllTableImportJobsQuery,
    GetTableImportJobQuery,
    UpdateFileImportJobMutation,
    UpdateTableImportJobMutation,
)
from arize_toolkit.types import BlobStore, TableStore


@pytest.fixture
def mock_file_import_job():
    return {
        "id": "job123",
        "jobId": "job123",
        "jobStatus": "active",
        "totalFilesPendingCount": 5,
        "totalFilesSuccessCount": 0,
        "totalFilesFailedCount": 0,
    }


@pytest.fixture
def mock_classification_schema():
    return ClassificationSchemaInput(
        predictionLabel="prediction",
        actualLabel="actual",
        predictionScores="scores",
        actualScores="actual_scores",
        predictionId="id",
        timestamp="ts",
        featuresList=["feature1", "feature2"],
        embeddingFeatures=[
            EmbeddingFeatureInput(
                featureName="text_embedding",
                vectorCol="embedding_vector",
                rawDataCol="text",
                linkToDataCol="image_url",
            )
        ],
    )


@pytest.fixture
def mock_regression_schema():
    return RegressionSchemaInput(
        predictionScore="prediction",
        actualScore="actual",
        predictionId="id",
        timestamp="ts",
        featuresList=["feature1", "feature2"],
    )


@pytest.fixture
def mock_rank_schema():
    return RankSchemaInput(
        predictionGroupId="group_id",
        rank="rank",
        predictionScores="scores",
        relevanceScore="relevance",
        relevanceLabel="relevance_label",
        predictionId="id",
        timestamp="ts",
    )


@pytest.fixture
def mock_multiclass_schema():
    return MultiClassSchemaInput(
        predictionScores="scores",
        actualScores="actual_scores",
        thresholdScores="thresholds",
        predictionId="id",
        timestamp="ts",
    )


@pytest.fixture
def mock_table_import_job():
    return {
        "id": "job123",
        "jobId": "job123",
        "jobStatus": "active",
        "totalQueriesPendingCount": 5,
        "totalQueriesSuccessCount": 0,
        "totalQueriesFailedCount": 0,
        "createdAt": "2024-03-20T00:00:00Z",
        "modelName": "my-model",
        "modelId": "model123",
        "modelType": "score_categorical",
        "modelEnvironmentName": "production",
        "schema": {"predictionLabel": "prediction", "actualLabel": "actual"},
        "table": "my-table",
        "tableStore": "BigQuery",
        "projectId": "my-project",
        "dataset": "my-dataset",
    }


@pytest.fixture
def mock_bigquery_config():
    return BigQueryTableConfig(
        projectId="my-project",
        dataset="my-dataset",
        tableName="my-table",
    )


@pytest.fixture
def mock_snowflake_config():
    return SnowflakeTableConfig(
        accountID="my-account",
        schema="my-schema",
        database="my-database",
        tableName="my-table",
    )


@pytest.fixture
def mock_databricks_config():
    return DatabricksTableConfig(
        hostName="my-host",
        endpoint="my-endpoint",
        port="443",
        catalog="my-catalog",
        databricksSchema="my-schema",
        tableName="my-table",
    )


class TestCreateFileImportJobMutation:
    def test_query_structure(self):
        """Test that the query structure is correct and includes all necessary fields."""
        query = CreateFileImportJobMutation.graphql_query
        assert "mutation CreateFileImportJob" in query
        assert "createFileImportJob(input: $input)" in query
        assert "fileImportJob" in query
        assert "id" in query
        assert "totalFilesPendingCount" in query
        assert "totalFilesSuccessCount" in query
        assert "totalFilesFailedCount" in query

    def test_create_file_import_job_classification_schema(self, gql_client, mock_classification_schema, mock_file_import_job):
        """Test creating a file import job with classification schema."""
        mock_response = {"createFileImportJob": {"fileImportJob": mock_file_import_job}}
        gql_client.execute.return_value = mock_response

        job_input = FileImportJobInput(
            blobStore=BlobStore.S3,
            prefix="path/to/files",
            bucketName="my-bucket",
            spaceId="space123",
            modelName="my-model",
            modelType="score_categorical",
            modelEnvironmentName="production",
            modelSchema=mock_classification_schema,
        )

        result = CreateFileImportJobMutation.run_graphql_mutation(gql_client, **job_input.model_dump())

        assert result.id == "job123"
        assert result.jobStatus == "active"
        assert result.totalFilesPendingCount == 5
        assert result.totalFilesSuccessCount == 0
        assert result.totalFilesFailedCount == 0

    def test_create_file_import_job_regression_schema(self, gql_client, mock_regression_schema, mock_file_import_job):
        """Test creating a file import job with regression schema."""
        mock_response = {"createFileImportJob": {"fileImportJob": mock_file_import_job}}
        gql_client.execute.return_value = mock_response

        job_input = FileImportJobInput(
            blobStore=BlobStore.S3,
            prefix="path/to/files",
            bucketName="my-bucket",
            spaceId="space123",
            modelName="my-model",
            modelType="numeric",
            modelEnvironmentName="production",
            modelSchema=mock_regression_schema,
        )

        result = CreateFileImportJobMutation.run_graphql_mutation(gql_client, **job_input.model_dump())

        assert result.id == "job123"
        assert result.jobStatus == "active"
        assert result.totalFilesPendingCount == 5
        assert result.totalFilesSuccessCount == 0
        assert result.totalFilesFailedCount == 0

    def test_create_file_import_job_rank_schema(self, gql_client, mock_rank_schema, mock_file_import_job):
        """Test creating a file import job with ranking schema."""
        mock_response = {"createFileImportJob": {"fileImportJob": mock_file_import_job}}
        gql_client.execute.return_value = mock_response

        job_input = FileImportJobInput(
            blobStore=BlobStore.S3,
            prefix="path/to/files",
            bucketName="my-bucket",
            spaceId="space123",
            modelName="my-model",
            modelType="ranking",
            modelEnvironmentName="production",
            modelSchema=mock_rank_schema,
        )

        result = CreateFileImportJobMutation.run_graphql_mutation(gql_client, **job_input.model_dump())

        assert result.id == "job123"
        assert result.totalFilesPendingCount == 5
        assert result.totalFilesSuccessCount == 0
        assert result.totalFilesFailedCount == 0

    def test_create_file_import_job_multiclass_schema(self, gql_client, mock_multiclass_schema, mock_file_import_job):
        """Test creating a file import job with multi-class schema."""
        mock_response = {"createFileImportJob": {"fileImportJob": mock_file_import_job}}
        gql_client.execute.return_value = mock_response

        job_input = FileImportJobInput(
            blobStore=BlobStore.S3,
            prefix="path/to/files",
            bucketName="my-bucket",
            spaceId="space123",
            modelName="my-model",
            modelType="multi_class",
            modelEnvironmentName="production",
            modelSchema=mock_multiclass_schema,
        )

        result = CreateFileImportJobMutation.run_graphql_mutation(gql_client, **job_input.model_dump())

        assert result.id == "job123"
        assert result.jobStatus == "active"
        assert result.totalFilesPendingCount == 5
        assert result.totalFilesSuccessCount == 0
        assert result.totalFilesFailedCount == 0

    def test_create_file_import_job_failure(self, gql_client, mock_classification_schema):
        """Test error handling when creating a file import job fails."""
        mock_response = {"createFileImportJob": None}
        gql_client.execute.return_value = mock_response

        job_input = FileImportJobInput(
            blobStore=BlobStore.S3,
            prefix="path/to/files",
            bucketName="my-bucket",
            spaceId="space123",
            modelName="my-model",
            modelType="score_categorical",
            modelEnvironmentName="production",
            modelSchema=mock_classification_schema,
        )

        with pytest.raises(ArizeAPIException, match="Error creating file import job"):
            CreateFileImportJobMutation.run_graphql_mutation(gql_client, **job_input.model_dump())

    @pytest.mark.parametrize(
        "input_data,expected_error",
        [
            (
                {
                    "blobStore": "S3",
                    "prefix": "path/to/files",
                    "bucketName": "my-bucket",
                    "spaceId": "space123",
                    "modelName": "my-model",
                    "modelType": "score_categorical",
                    "modelEnvironmentName": "production",
                },
                "schema",
            ),
            (
                {
                    "blobStore": "S3",
                    "prefix": "path/to/files",
                    "bucketName": "my-bucket",
                    "spaceId": "space123",
                    "modelName": "my-model",
                    "modelType": "blue",
                    "modelEnvironmentName": "production",
                    "modelSchema": {
                        "predictionScore": "prediction",
                        "actualScore": "actual",
                    },
                },
                "modelType",
            ),
            (
                {
                    "blobStore": "invalid",
                    "prefix": "path/to/files",
                    "bucketName": "my-bucket",
                    "spaceId": "space123",
                    "modelName": "my-model",
                    "modelType": "score_categorical",
                    "modelEnvironmentName": "production",
                    "modelSchema": {
                        "predictionLabel": "prediction",
                        "actualLabel": "actual",
                    },
                },
                "blobStore",
            ),
        ],
    )
    def test_file_import_job_input_validation(self, input_data, expected_error):
        """Test validation of file import job input."""
        with pytest.raises(Exception) as e:
            FileImportJobInput.model_validate(input_data)
        assert expected_error in str(e)


class TestCreateTableImportJobMutation:
    def test_query_structure(self):
        """Test that the query structure is correct and includes all necessary fields."""
        query = CreateTableImportJobMutation.graphql_query
        assert "mutation CreateTableImportJob" in query
        assert "createTableImportJob(input: $input)" in query
        assert "tableImportJob" in query
        assert "id" in query
        assert "totalQueriesPendingCount" in query
        assert "totalQueriesSuccessCount" in query
        assert "totalQueriesFailedCount" in query

    def test_create_table_import_job_bigquery(
        self,
        gql_client,
        mock_classification_schema,
        mock_table_import_job,
        mock_bigquery_config,
    ):
        """Test creating a table import job with BigQuery configuration."""
        mock_response = {"createTableImportJob": {"tableImportJob": mock_table_import_job}}
        gql_client.execute.return_value = mock_response

        job_input = TableImportJobInput(
            tableStore=TableStore.BigQuery,
            bigQueryTableConfig=mock_bigquery_config,
            spaceId="space123",
            modelName="my-model",
            modelType="score_categorical",
            modelEnvironmentName="production",
            modelSchema=mock_classification_schema,
        )

        result = CreateTableImportJobMutation.run_graphql_mutation(gql_client, **job_input.model_dump())

        assert result.id == "job123"
        assert result.jobStatus == "active"
        assert result.totalQueriesPendingCount == 5
        assert result.totalQueriesSuccessCount == 0
        assert result.totalQueriesFailedCount == 0

    def test_create_table_import_job_snowflake(
        self,
        gql_client,
        mock_classification_schema,
        mock_table_import_job,
        mock_snowflake_config,
    ):
        """Test creating a table import job with Snowflake configuration."""
        mock_response = {"createTableImportJob": {"tableImportJob": mock_table_import_job}}
        gql_client.execute.return_value = mock_response

        job_input = TableImportJobInput(
            tableStore=TableStore.Snowflake,
            snowflakeTableConfig=mock_snowflake_config,
            spaceId="space123",
            modelName="my-model",
            modelType="score_categorical",
            modelEnvironmentName="production",
            modelSchema=mock_classification_schema,
        )

        result = CreateTableImportJobMutation.run_graphql_mutation(gql_client, **job_input.model_dump())

        assert result.id == "job123"
        assert result.jobStatus == "active"
        assert result.totalQueriesPendingCount == 5
        assert result.totalQueriesSuccessCount == 0
        assert result.totalQueriesFailedCount == 0

    def test_create_table_import_job_databricks(
        self,
        gql_client,
        mock_classification_schema,
        mock_table_import_job,
        mock_databricks_config,
    ):
        """Test creating a table import job with Databricks configuration."""
        mock_response = {"createTableImportJob": {"tableImportJob": mock_table_import_job}}
        gql_client.execute.return_value = mock_response

        job_input = TableImportJobInput(
            tableStore=TableStore.Databricks,
            databricksTableConfig=mock_databricks_config,
            spaceId="space123",
            modelName="my-model",
            modelType="score_categorical",
            modelEnvironmentName="production",
            modelSchema=mock_classification_schema,
        )

        result = CreateTableImportJobMutation.run_graphql_mutation(gql_client, **job_input.model_dump())

        assert result.id == "job123"
        assert result.jobStatus == "active"
        assert result.totalQueriesPendingCount == 5
        assert result.totalQueriesSuccessCount == 0
        assert result.totalQueriesFailedCount == 0

    def test_create_table_import_job_failure(self, gql_client, mock_classification_schema, mock_bigquery_config):
        """Test error handling when creating a table import job fails."""
        mock_response = {"createTableImportJob": None}
        gql_client.execute.return_value = mock_response

        job_input = TableImportJobInput(
            tableStore=TableStore.BigQuery,
            bigQueryTableConfig=mock_bigquery_config,
            spaceId="space123",
            modelName="my-model",
            modelType="score_categorical",
            modelEnvironmentName="production",
            modelSchema=mock_classification_schema,
        )

        with pytest.raises(ArizeAPIException, match="Error creating table import job"):
            CreateTableImportJobMutation.run_graphql_mutation(gql_client, **job_input.model_dump())

    @pytest.mark.parametrize(
        "input_data,expected_error",
        [
            (
                {
                    "tableStore": "BigQuery",
                    "spaceId": "space123",
                    "modelName": "my-model",
                    "modelType": "score_categorical",
                    "modelEnvironmentName": "production",
                    "modelSchema": {
                        "predictionLabel": "prediction",
                        "actualLabel": "actual",
                    },
                },
                "bigQueryTableConfig",
            ),
            (
                {
                    "tableStore": "Snowflake",
                    "spaceId": "space123",
                    "modelName": "my-model",
                    "modelType": "score_categorical",
                    "modelEnvironmentName": "production",
                    "modelSchema": {
                        "predictionLabel": "prediction",
                        "actualLabel": "actual",
                    },
                },
                "snowflakeTableConfig",
            ),
            (
                {
                    "tableStore": "Databricks",
                    "spaceId": "space123",
                    "modelName": "my-model",
                    "modelType": "score_categorical",
                    "modelEnvironmentName": "production",
                    "modelSchema": {
                        "predictionLabel": "prediction",
                        "actualLabel": "actual",
                    },
                },
                "databricksTableConfig",
            ),
            (
                {
                    "tableStore": "BigQuery",
                    "spaceId": "space123",
                    "modelName": "my-model",
                    "modelType": "score_categorical",
                    "modelEnvironmentName": "production",
                    "bigQueryTableConfig": {
                        "projectId": "my-project",
                        "dataset": "my-dataset",
                        "tableName": "my-table",
                    },
                },
                "schema",
            ),
        ],
    )
    def test_table_import_job_input_validation(self, input_data, expected_error):
        """Test input validation for table import job creation."""
        with pytest.raises(Exception) as e:
            TableImportJobInput.model_validate(input_data)
        assert expected_error in str(e)


class TestGetTableImportJobQuery:
    def test_query_structure(self):
        """Test that the query structure is correct and includes all necessary fields."""
        query = GetTableImportJobQuery.graphql_query
        assert "query GetTableImportJobStatus" in query
        assert "tableJobs(search: $jobId, first: 1)" in query
        assert "id" in query
        assert "jobStatus" in query
        assert "totalQueriesPendingCount" in query
        assert "totalQueriesSuccessCount" in query
        assert "totalQueriesFailedCount" in query

    def test_get_table_import_job_success(self, gql_client, mock_table_import_job):
        """Test successful table import job retrieval."""
        mock_response = {"node": {"tableJobs": {"edges": [{"node": mock_table_import_job}]}}}
        gql_client.execute.return_value = mock_response

        result = GetTableImportJobQuery.run_graphql_query(
            gql_client,
            spaceId="space123",
            jobId="job123",
        )

        assert result.id == "job123"
        assert result.jobStatus == "active"
        assert result.totalQueriesPendingCount == 5
        assert result.totalQueriesSuccessCount == 0
        assert result.totalQueriesFailedCount == 0

    def test_get_table_import_job_not_found(self, gql_client):
        """Test handling of non-existent table import job."""
        mock_response = {"node": {"tableJobs": {"edges": []}}}
        gql_client.execute.return_value = mock_response

        with pytest.raises(
            GetTableImportJobQuery.QueryException,
            match="No table import jobs found",
        ):
            GetTableImportJobQuery.run_graphql_query(
                gql_client,
                spaceId="space123",
                jobId="non-existent",
            )


class TestGetAllTableImportJobsQuery:
    def test_query_structure(self):
        """Test that the query structure is correct and includes all necessary fields."""
        query = GetAllTableImportJobsQuery.graphql_query
        assert "query GetAllTableImportJobs" in query
        assert "tableJobs(first: 10, after: $endCursor)" in query
        assert "pageInfo" in query
        assert "hasNextPage" in query
        assert "endCursor" in query
        assert "edges" in query
        assert "node" in query

    def test_get_all_table_import_jobs_success(self, gql_client, mock_table_import_job):
        """Test successful retrieval of all table import jobs."""
        mock_response = {
            "node": {
                "tableJobs": {
                    "pageInfo": {
                        "hasNextPage": False,
                        "endCursor": None,
                    },
                    "edges": [{"node": mock_table_import_job}],
                }
            }
        }
        gql_client.execute.return_value = mock_response

        result = GetAllTableImportJobsQuery.iterate_over_pages(
            gql_client,
            spaceId="space123",
        )

        assert len(result) == 1
        assert result[0].id == "job123"
        assert result[0].jobStatus == "active"
        assert result[0].totalQueriesPendingCount == 5
        assert result[0].totalQueriesSuccessCount == 0
        assert result[0].totalQueriesFailedCount == 0

    def test_get_all_table_import_jobs_empty(self, gql_client):
        """Test handling of no table import jobs."""
        mock_response = {
            "node": {
                "tableJobs": {
                    "pageInfo": {
                        "hasNextPage": False,
                        "endCursor": None,
                    },
                    "edges": [],
                }
            }
        }
        gql_client.execute.return_value = mock_response

        with pytest.raises(
            GetAllTableImportJobsQuery.QueryException,
            match="No table import jobs found",
        ):
            GetAllTableImportJobsQuery.iterate_over_pages(
                gql_client,
                spaceId="space123",
            )

    def test_get_all_table_import_jobs_pagination(self, gql_client, mock_table_import_job):
        """Test pagination of table import jobs."""
        mock_responses = [
            {
                "node": {
                    "tableJobs": {
                        "pageInfo": {
                            "hasNextPage": True,
                            "endCursor": "cursor123",
                        },
                        "edges": [{"node": mock_table_import_job}],
                    }
                }
            },
            {
                "node": {
                    "tableJobs": {
                        "pageInfo": {
                            "hasNextPage": False,
                            "endCursor": None,
                        },
                        "edges": [{"node": mock_table_import_job}],
                    }
                }
            },
        ]
        gql_client.execute.side_effect = mock_responses

        result = GetAllTableImportJobsQuery.iterate_over_pages(
            gql_client,
            spaceId="space123",
        )

        assert len(result) == 2
        assert result[0].id == "job123"
        assert result[1].id == "job123"


class TestDeleteFileImportJobMutation:
    def test_query_structure(self):
        """Test that the query structure is correct and includes all necessary fields."""
        query = DeleteFileImportJobMutation.graphql_query
        assert "mutation DeleteFileImportJob" in query
        assert "deleteFileImportJob(input: { jobId: $id })" in query
        assert "fileImportJob" in query
        assert "jobStatus" in query

    def test_delete_file_import_job_success(self, gql_client):
        """Test successful deletion of a file import job."""
        mock_response = {"deleteFileImportJob": {"fileImportJob": {"jobStatus": "deleted"}}}
        gql_client.execute.return_value = mock_response

        result = DeleteFileImportJobMutation.run_graphql_mutation(gql_client, id="job123")

        assert result.jobStatus == "deleted"

        # Verify the mutation was called with correct parameters
        gql_client.execute.assert_called_once()
        args, kwargs = gql_client.execute.call_args
        assert kwargs["variable_values"]["input"]["id"] == "job123"

    def test_delete_file_import_job_failure_no_response(self, gql_client):
        """Test error handling when delete mutation returns no response."""
        mock_response = {}
        gql_client.execute.return_value = mock_response

        with pytest.raises(
            DeleteFileImportJobMutation.QueryException,
            match="Error deleting file import job - No delete file import job response",
        ):
            DeleteFileImportJobMutation.run_graphql_mutation(gql_client, id="job123")

    def test_delete_file_import_job_failure_no_job_data(self, gql_client):
        """Test error handling when delete mutation returns no job data."""
        mock_response = {"deleteFileImportJob": {}}
        gql_client.execute.return_value = mock_response

        with pytest.raises(
            DeleteFileImportJobMutation.QueryException,
            match="Error deleting file import job - No file import job data returned",
        ):
            DeleteFileImportJobMutation.run_graphql_mutation(gql_client, id="job123")

    def test_delete_file_import_job_with_inactive_status(self, gql_client):
        """Test deletion returning inactive status."""
        mock_response = {"deleteFileImportJob": {"fileImportJob": {"jobStatus": "inactive"}}}
        gql_client.execute.return_value = mock_response

        result = DeleteFileImportJobMutation.run_graphql_mutation(gql_client, id="job123")

        assert result.jobStatus == "inactive"

    def test_delete_file_import_job_with_null_status(self, gql_client):
        """Test deletion returning null status."""
        mock_response = {"deleteFileImportJob": {"fileImportJob": {"jobStatus": None}}}
        gql_client.execute.return_value = mock_response

        result = DeleteFileImportJobMutation.run_graphql_mutation(gql_client, id="job123")

        assert result.jobStatus is None

    def test_delete_file_import_job_graphql_error(self, gql_client):
        """Test error handling when GraphQL returns errors."""
        gql_client.execute.side_effect = Exception("GraphQL error occurred")

        with pytest.raises(
            DeleteFileImportJobMutation.QueryException,
            match="Error deleting file import job - GraphQL error occurred",
        ):
            DeleteFileImportJobMutation.run_graphql_mutation(gql_client, id="job123")

    @pytest.mark.parametrize(
        "job_id,expected_error",
        [
            (1234, "Input should be a valid string"),
            (None, "Input should be a valid string"),
        ],
    )
    def test_delete_file_import_job_input_validation(self, job_id, expected_error):
        """Test validation of delete file import job input."""
        with pytest.raises(Exception) as e:
            DeleteFileImportJobMutation.Variables(id=job_id)
        assert expected_error.lower() in str(e.value).lower()


class TestDeleteTableImportJobMutation:
    def test_query_structure(self):
        """Test that the query structure is correct and includes all necessary fields."""
        query = DeleteTableImportJobMutation.graphql_query
        assert "mutation DeleteTableImportJob" in query
        assert "deleteTableImportJob(input: { jobId: $id })" in query
        assert "tableImportJob" in query
        assert "jobStatus" in query

    def test_delete_table_import_job_success(self, gql_client):
        """Test successful deletion of a table import job."""
        mock_response = {"deleteTableImportJob": {"tableImportJob": {"jobStatus": "deleted"}}}
        gql_client.execute.return_value = mock_response

        result = DeleteTableImportJobMutation.run_graphql_mutation(gql_client, id="job123")

        assert result.jobStatus == "deleted"

        # Verify the mutation was called with correct parameters
        gql_client.execute.assert_called_once()
        args, kwargs = gql_client.execute.call_args
        assert kwargs["variable_values"]["input"]["id"] == "job123"

    def test_delete_table_import_job_failure_no_response(self, gql_client):
        """Test error handling when delete mutation returns no response."""
        mock_response = {}
        gql_client.execute.return_value = mock_response

        with pytest.raises(
            DeleteTableImportJobMutation.QueryException,
            match="Error deleting table import job - No delete table import job response",
        ):
            DeleteTableImportJobMutation.run_graphql_mutation(gql_client, id="job123")

    def test_delete_table_import_job_failure_no_job_data(self, gql_client):
        """Test error handling when delete mutation returns no job data."""
        mock_response = {"deleteTableImportJob": {}}
        gql_client.execute.return_value = mock_response

        with pytest.raises(
            DeleteTableImportJobMutation.QueryException,
            match="Error deleting table import job - No table import job data returned",
        ):
            DeleteTableImportJobMutation.run_graphql_mutation(gql_client, id="job123")

    def test_delete_table_import_job_with_inactive_status(self, gql_client):
        """Test deletion returning inactive status."""
        mock_response = {"deleteTableImportJob": {"tableImportJob": {"jobStatus": "inactive"}}}
        gql_client.execute.return_value = mock_response

        result = DeleteTableImportJobMutation.run_graphql_mutation(gql_client, id="job123")

        assert result.jobStatus == "inactive"

    def test_delete_table_import_job_with_null_status(self, gql_client):
        """Test deletion returning null status."""
        mock_response = {"deleteTableImportJob": {"tableImportJob": {"jobStatus": None}}}
        gql_client.execute.return_value = mock_response

        result = DeleteTableImportJobMutation.run_graphql_mutation(gql_client, id="job123")

        assert result.jobStatus is None

    def test_delete_file_import_job_graphql_error(self, gql_client):
        """Test error handling when GraphQL returns errors."""
        gql_client.execute.side_effect = Exception("GraphQL error occurred")

        with pytest.raises(
            DeleteFileImportJobMutation.QueryException,
            match="Error deleting file import job - GraphQL error occurred",
        ):
            DeleteFileImportJobMutation.run_graphql_mutation(gql_client, id="job123")

    @pytest.mark.parametrize(
        "job_id,expected_error",
        [
            (1234, "Input should be a valid string"),
            (None, "Input should be a valid string"),
        ],
    )
    def test_delete_file_import_job_input_validation(self, job_id, expected_error):
        """Test validation of delete file import job input."""
        with pytest.raises(Exception) as e:
            DeleteFileImportJobMutation.Variables(id=job_id)
        assert expected_error.lower() in str(e.value).lower()


class TestUpdateFileImportJobMutation:
    def test_query_structure(self):
        """Test that the query structure is correct and includes all necessary fields."""
        query = UpdateFileImportJobMutation.graphql_query
        assert "mutation UpdateFileImportJob" in query
        assert "updateFileImportJob(" in query
        assert "fileImportJob" in query
        assert "$modelSchema: FileImportSchemaInputType!" in query
        assert "id" in query
        assert "jobId" in query
        assert "jobStatus" in query
        assert "totalFilesFailedCount" in query
        assert "totalFilesSuccessCount" in query
        assert "totalFilesPendingCount" in query

    def test_update_file_import_job_all_params(self, gql_client, mock_classification_schema):
        """Test successful update with all parameters."""
        mock_response = {
            "updateFileImportJob": {
                "fileImportJob": {
                    "id": "job123",
                    "jobId": "job123",
                    "jobStatus": "active",
                    "totalFilesFailedCount": 2,
                    "totalFilesSuccessCount": 8,
                    "totalFilesPendingCount": 0,
                }
            }
        }
        gql_client.execute.return_value = mock_response

        result = UpdateFileImportJobMutation.run_graphql_mutation(
            gql_client,
            jobId="job123",
            jobStatus="active",
            modelSchema=mock_classification_schema,
        )

        assert result.id == "job123"
        assert result.jobStatus == "active"
        assert result.totalFilesFailedCount == 2
        assert result.totalFilesSuccessCount == 8
        assert result.totalFilesPendingCount == 0

        # Verify the mutation was called with correct parameters
        gql_client.execute.assert_called_once()
        args, kwargs = gql_client.execute.call_args
        input_data = kwargs["variable_values"]["input"]
        assert input_data["jobId"] == "job123"
        assert input_data["jobStatus"] == "active"
        assert "modelSchema" in input_data

    def test_update_file_import_job_minimal_params(self, gql_client, mock_regression_schema):
        """Test successful update with only required parameters."""
        mock_response = {
            "updateFileImportJob": {
                "fileImportJob": {
                    "id": "job456",
                    "jobId": "job456",
                    "jobStatus": "inactive",
                    "totalFilesFailedCount": 0,
                    "totalFilesSuccessCount": 100,
                    "totalFilesPendingCount": 0,
                }
            }
        }
        gql_client.execute.return_value = mock_response

        result = UpdateFileImportJobMutation.run_graphql_mutation(
            gql_client,
            jobId="job456",
            modelSchema=mock_regression_schema,
        )

        assert result.id == "job456"
        assert result.jobStatus == "inactive"
        assert result.totalFilesSuccessCount == 100

    def test_update_file_import_job_status_change(self, gql_client, mock_multiclass_schema):
        """Test updating job status from active to inactive."""
        mock_response = {
            "updateFileImportJob": {
                "fileImportJob": {
                    "id": "job789",
                    "jobId": "job789",
                    "jobStatus": "inactive",
                    "totalFilesFailedCount": 0,
                    "totalFilesSuccessCount": 50,
                    "totalFilesPendingCount": 0,
                }
            }
        }
        gql_client.execute.return_value = mock_response

        result = UpdateFileImportJobMutation.run_graphql_mutation(
            gql_client,
            jobId="job789",
            jobStatus="inactive",
            modelSchema=mock_multiclass_schema,
        )

        assert result.jobStatus == "inactive"

    def test_update_file_import_job_failure_no_response(self, gql_client, mock_classification_schema):
        """Test error handling when update mutation returns no response."""
        mock_response = {}
        gql_client.execute.return_value = mock_response

        with pytest.raises(
            UpdateFileImportJobMutation.QueryException,
            match="Error updating file import job - No update file import job response",
        ):
            UpdateFileImportJobMutation.run_graphql_mutation(
                gql_client,
                jobId="job123",
                modelSchema=mock_classification_schema,
            )

    def test_update_file_import_job_failure_no_job_data(self, gql_client, mock_classification_schema):
        """Test error handling when update mutation returns no job data."""
        mock_response = {"updateFileImportJob": {}}
        gql_client.execute.return_value = mock_response

        with pytest.raises(
            UpdateFileImportJobMutation.QueryException,
            match="Error updating file import job - No file import job data returned",
        ):
            UpdateFileImportJobMutation.run_graphql_mutation(
                gql_client,
                jobId="job123",
                modelSchema=mock_classification_schema,
            )

    def test_update_file_import_job_graphql_error(self, gql_client, mock_classification_schema):
        """Test error handling when GraphQL returns errors."""
        gql_client.execute.side_effect = Exception("GraphQL error occurred")

        with pytest.raises(
            UpdateFileImportJobMutation.QueryException,
            match="Error updating file import job - GraphQL error occurred",
        ):
            UpdateFileImportJobMutation.run_graphql_mutation(
                gql_client,
                jobId="job123",
                modelSchema=mock_classification_schema,
            )

    @pytest.mark.parametrize(
        "input_data,expected_error",
        [
            ({"modelSchema": {}}, "jobId"),
            ({"jobId": None, "modelSchema": {}}, "Input should be a valid string"),
            ({"jobId": 123, "modelSchema": {}}, "Input should be a valid string"),
            ({"jobId": "job123"}, "modelSchema"),
        ],
    )
    def test_update_file_import_job_input_validation(self, input_data, expected_error):
        """Test validation of update file import job input."""
        with pytest.raises(Exception) as e:
            UpdateFileImportJobMutation.Variables(**input_data)
        assert expected_error.lower() in str(e.value).lower()


class TestUpdateTableImportJobMutation:
    def test_query_structure(self):
        """Test that the query structure is correct and includes all necessary fields."""
        query = UpdateTableImportJobMutation.graphql_query
        assert "mutation UpdateTableImportJob" in query
        assert "updateTableImportJob(" in query
        assert "tableImportJob" in query
        assert "$modelSchema: TableImportSchemaInputType!" in query
        assert "tableIngestionParameters" in query
        assert "refreshIntervalMinutes" in query
        assert "queryWindowSizeHours" in query
        assert "id" in query
        assert "jobId" in query
        assert "jobStatus" in query
        assert "totalQueriesFailedCount" in query
        assert "totalQueriesSuccessCount" in query
        assert "totalQueriesPendingCount" in query

    def test_update_table_import_job_all_params(self, gql_client, mock_classification_schema):
        """Test successful update with all parameters including ingestion params."""
        mock_response = {
            "updateTableImportJob": {
                "tableImportJob": {
                    "id": "job123",
                    "jobId": "job123",
                    "jobStatus": "active",
                    "totalQueriesFailedCount": 1,
                    "totalQueriesSuccessCount": 9,
                    "totalQueriesPendingCount": 0,
                }
            }
        }
        gql_client.execute.return_value = mock_response

        result = UpdateTableImportJobMutation.run_graphql_mutation(
            gql_client,
            jobId="job123",
            jobStatus="active",
            modelVersion="v2",
            modelSchema=mock_classification_schema,
            refreshInterval=60,
            queryWindowSize=24,
        )

        assert result.id == "job123"
        assert result.jobStatus == "active"
        assert result.totalQueriesFailedCount == 1
        assert result.totalQueriesSuccessCount == 9
        assert result.totalQueriesPendingCount == 0

        # Verify the mutation was called with correct parameters
        gql_client.execute.assert_called_once()
        args, kwargs = gql_client.execute.call_args
        input_data = kwargs["variable_values"]["input"]
        assert input_data["jobId"] == "job123"
        assert input_data["jobStatus"] == "active"
        assert input_data["modelVersion"] == "v2"
        assert input_data["refreshInterval"] == 60
        assert input_data["queryWindowSize"] == 24
        assert "modelSchema" in input_data

    def test_update_table_import_job_minimal_params(self, gql_client, mock_regression_schema):
        """Test successful update with only required parameters."""
        mock_response = {
            "updateTableImportJob": {
                "tableImportJob": {
                    "id": "job456",
                    "jobId": "job456",
                    "jobStatus": "active",
                    "totalQueriesFailedCount": 0,
                    "totalQueriesSuccessCount": 200,
                    "totalQueriesPendingCount": 0,
                }
            }
        }
        gql_client.execute.return_value = mock_response

        result = UpdateTableImportJobMutation.run_graphql_mutation(
            gql_client,
            jobId="job456",
            modelSchema=mock_regression_schema,
        )

        assert result.id == "job456"
        assert result.jobStatus == "active"
        assert result.totalQueriesSuccessCount == 200

    def test_update_table_import_job_with_ingestion_params(self, gql_client, mock_rank_schema):
        """Test updating table import job with ingestion parameters only."""
        mock_response = {
            "updateTableImportJob": {
                "tableImportJob": {
                    "id": "job789",
                    "jobId": "job789",
                    "jobStatus": "active",
                    "totalQueriesFailedCount": 0,
                    "totalQueriesSuccessCount": 150,
                    "totalQueriesPendingCount": 10,
                }
            }
        }
        gql_client.execute.return_value = mock_response

        result = UpdateTableImportJobMutation.run_graphql_mutation(
            gql_client,
            jobId="job789",
            modelSchema=mock_rank_schema,
            refreshInterval=30,
            queryWindowSize=48,
        )

        assert result.id == "job789"
        assert result.totalQueriesPendingCount == 10

    def test_update_table_import_job_status_change(self, gql_client, mock_classification_schema):
        """Test updating job status from active to inactive."""
        mock_response = {
            "updateTableImportJob": {
                "tableImportJob": {
                    "id": "job999",
                    "jobId": "job999",
                    "jobStatus": "inactive",
                    "totalQueriesFailedCount": 0,
                    "totalQueriesSuccessCount": 1000,
                    "totalQueriesPendingCount": 0,
                }
            }
        }
        gql_client.execute.return_value = mock_response

        result = UpdateTableImportJobMutation.run_graphql_mutation(
            gql_client,
            jobId="job999",
            jobStatus="inactive",
            modelSchema=mock_classification_schema,
        )

        assert result.jobStatus == "inactive"
        assert result.totalQueriesSuccessCount == 1000

    def test_update_table_import_job_failure_no_response(self, gql_client, mock_classification_schema):
        """Test error handling when update mutation returns no response."""
        mock_response = {}
        gql_client.execute.return_value = mock_response

        with pytest.raises(
            UpdateTableImportJobMutation.QueryException,
            match="Error updating table import job - No update table import job response",
        ):
            UpdateTableImportJobMutation.run_graphql_mutation(
                gql_client,
                jobId="job123",
                modelSchema=mock_classification_schema,
            )

    def test_update_table_import_job_failure_no_job_data(self, gql_client, mock_classification_schema):
        """Test error handling when update mutation returns no job data."""
        mock_response = {"updateTableImportJob": {}}
        gql_client.execute.return_value = mock_response

        with pytest.raises(
            UpdateTableImportJobMutation.QueryException,
            match="Error updating table import job - No table import job data returned",
        ):
            UpdateTableImportJobMutation.run_graphql_mutation(
                gql_client,
                jobId="job123",
                modelSchema=mock_classification_schema,
            )

    def test_update_table_import_job_graphql_error(self, gql_client, mock_classification_schema):
        """Test error handling when GraphQL returns errors."""
        gql_client.execute.side_effect = Exception("GraphQL error occurred")

        with pytest.raises(
            UpdateTableImportJobMutation.QueryException,
            match="Error updating table import job - GraphQL error occurred",
        ):
            UpdateTableImportJobMutation.run_graphql_mutation(
                gql_client,
                jobId="job123",
                modelSchema=mock_classification_schema,
            )

    @pytest.mark.parametrize(
        "input_data,expected_error",
        [
            ({"modelSchema": {}}, "jobId"),
            ({"jobId": None, "modelSchema": {}}, "Input should be a valid string"),
            ({"jobId": 123, "modelSchema": {}}, "Input should be a valid string"),
            ({"jobId": "job123"}, "modelSchema"),
            (
                {"jobId": "job123", "modelSchema": {}, "refreshInterval": "sixty"},
                "Input should be a valid integer",
            ),
            (
                {"jobId": "job123", "modelSchema": {}, "queryWindowSize": "24hrs"},
                "Input should be a valid integer",
            ),
        ],
    )
    def test_update_table_import_job_input_validation(self, input_data, expected_error):
        """Test validation of update table import job input."""
        with pytest.raises(Exception) as e:
            UpdateTableImportJobMutation.Variables(**input_data)
        assert expected_error.lower() in str(e.value).lower()
