from datetime import datetime, timezone

import pytest


class TestFileImportModels:
    def test_embedding_feature_input(self):
        """Test EmbeddingFeatureInput model."""
        from arize_toolkit.models import EmbeddingFeatureInput

        embedding = EmbeddingFeatureInput(
            featureName="text_embedding",
            vectorCol="embedding_vector",
            rawDataCol="text_content",
            linkToDataCol="image_url",
        )

        assert embedding.featureName == "text_embedding"
        assert embedding.vectorCol == "embedding_vector"
        assert embedding.rawDataCol == "text_content"
        assert embedding.linkToDataCol == "image_url"

    def test_classification_schema_input(self):
        """Test ClassificationSchemaInput model."""
        from arize_toolkit.models import (
            ClassificationSchemaInput,
            EmbeddingFeatureInput,
        )

        schema = ClassificationSchemaInput(
            predictionLabel="prediction",
            actualLabel="actual",
            predictionScores="pred_scores",
            predictionId="id",
            timestamp="ts",
            featuresList=["feature1", "feature2"],
            embeddingFeatures=[
                EmbeddingFeatureInput(
                    featureName="embedding",
                    vectorCol="vector",
                    rawDataCol="text",
                    linkToDataCol="url",
                )
            ],
        )

        assert schema.predictionLabel == "prediction"
        assert schema.actualLabel == "actual"
        assert schema.predictionScores == "pred_scores"
        assert schema.predictionId == "id"
        assert schema.timestamp == "ts"
        assert schema.featuresList == ["feature1", "feature2"]
        assert len(schema.embeddingFeatures) == 1

    def test_file_import_job_input(self):
        """Test FileImportJobInput model."""
        from arize_toolkit.models import FileImportJobInput, FullSchema
        from arize_toolkit.types import BlobStore, ModelEnvironment, ModelType

        job_input = FileImportJobInput(
            blobStore=BlobStore.S3,
            prefix="data/",
            bucketName="my-bucket",
            spaceId="space123",
            modelName="my-model",
            modelType=ModelType.score_categorical,
            modelEnvironmentName=ModelEnvironment.production,
            modelSchema=FullSchema(predictionLabel="prediction", actualLabel="actual"),
        )

        assert job_input.blobStore == BlobStore.S3
        assert job_input.prefix == "data/"
        assert job_input.bucketName == "my-bucket"
        assert job_input.spaceId == "space123"
        assert job_input.modelName == "my-model"
        assert job_input.modelType == ModelType.score_categorical
        assert job_input.modelEnvironmentName == ModelEnvironment.production
        assert job_input.modelSchema.predictionLabel == "prediction"
        assert job_input.dryRun is False  # Default value

    def test_file_import_job_input_serialization(self):
        """Test FileImportJobInput serialization with alias."""
        from arize_toolkit.models import FileImportJobInput, FullSchema
        from arize_toolkit.types import BlobStore, ModelEnvironment, ModelType

        job_input = FileImportJobInput(
            blobStore=BlobStore.S3,
            prefix="data/",
            bucketName="my-bucket",
            spaceId="space123",
            modelName="my-model",
            modelType=ModelType.score_categorical,
            modelEnvironmentName=ModelEnvironment.production,
            modelSchema=FullSchema(predictionLabel="prediction"),
        )

        data = job_input.model_dump(by_alias=True)
        assert "schema" in data  # Check alias is used
        assert "modelSchema" not in data


class TestTableImportModels:
    def test_bigquery_table_config(self):
        """Test BigQueryTableConfig model."""
        from arize_toolkit.models import BigQueryTableConfig

        config = BigQueryTableConfig(
            projectId="my-project", dataset="my-dataset", tableName="my-table"
        )

        assert config.projectId == "my-project"
        assert config.dataset == "my-dataset"
        assert config.tableName == "my-table"

    def test_snowflake_table_config(self):
        """Test SnowflakeTableConfig model with alias."""
        from arize_toolkit.models import SnowflakeTableConfig

        config = SnowflakeTableConfig(
            accountID="my-account",
            snowflakeSchema="my-schema",
            database="my-database",
            tableName="my-table",
        )

        assert config.accountID == "my-account"
        assert config.snowflakeSchema == "my-schema"
        assert config.database == "my-database"
        assert config.tableName == "my-table"

        # Test serialization with alias
        data = config.model_dump(by_alias=True)
        assert "schema" in data
        assert data["schema"] == "my-schema"
        assert "snowflakeSchema" not in data

    def test_table_import_job_input_validation(self):
        """Test TableImportJobInput validation."""
        from arize_toolkit.models import (
            BigQueryTableConfig,
            FullSchema,
            TableImportJobInput,
        )
        from arize_toolkit.types import ModelEnvironment, ModelType, TableStore

        # Valid case with BigQuery
        job_input = TableImportJobInput(
            tableStore=TableStore.BigQuery,
            bigQueryTableConfig=BigQueryTableConfig(
                projectId="project", dataset="dataset", tableName="table"
            ),
            spaceId="space123",
            modelName="model",
            modelType=ModelType.score_categorical,
            modelEnvironmentName=ModelEnvironment.production,
            modelSchema=FullSchema(predictionLabel="pred"),
        )

        assert job_input.tableStore == TableStore.BigQuery
        assert job_input.bigQueryTableConfig.projectId == "project"

    def test_table_import_job_input_validation_error(self):
        """Test TableImportJobInput validation error."""
        from arize_toolkit.models import FullSchema, TableImportJobInput
        from arize_toolkit.types import ModelEnvironment, ModelType, TableStore

        # Invalid case - missing required config
        with pytest.raises(
            ValueError, match="bigQueryTableConfig is required for BigQuery table store"
        ):
            TableImportJobInput(
                tableStore=TableStore.BigQuery,
                # Missing bigQueryTableConfig
                spaceId="space123",
                modelName="model",
                modelType=ModelType.score_categorical,
                modelEnvironmentName=ModelEnvironment.production,
                modelSchema=FullSchema(predictionLabel="pred"),
            )


class TestSchemaInputModels:
    def test_regression_schema_input(self):
        """Test RegressionSchemaInput model."""
        from arize_toolkit.models import RegressionSchemaInput

        schema = RegressionSchemaInput(
            predictionScore="pred_score",
            actualScore="actual_score",
            predictionId="id",
            timestamp="ts",
            featuresList=["f1", "f2"],
            version="v1.0",
        )

        assert schema.predictionScore == "pred_score"
        assert schema.actualScore == "actual_score"
        assert schema.predictionId == "id"
        assert schema.timestamp == "ts"
        assert len(schema.featuresList) == 2
        assert schema.version == "v1.0"

    def test_rank_schema_input(self):
        """Test RankSchemaInput model."""
        from arize_toolkit.models import RankSchemaInput

        schema = RankSchemaInput(
            predictionGroupId="group_id",
            rank="rank_col",
            predictionScores="scores",
            relevanceScore="relevance",
            relevanceLabel="rel_label",
        )

        assert schema.predictionGroupId == "group_id"
        assert schema.rank == "rank_col"
        assert schema.predictionScores == "scores"
        assert schema.relevanceScore == "relevance"
        assert schema.relevanceLabel == "rel_label"

    def test_multiclass_schema_input(self):
        """Test MultiClassSchemaInput model."""
        from arize_toolkit.models import MultiClassSchemaInput

        schema = MultiClassSchemaInput(
            predictionScores="pred_scores",
            actualScores="actual_scores",
            thresholdScores="thresholds",
            tags="tag_",
            tagsList=["tag_1", "tag_2"],
        )

        assert schema.predictionScores == "pred_scores"
        assert schema.actualScores == "actual_scores"
        assert schema.thresholdScores == "thresholds"
        assert schema.tags == "tag_"
        assert len(schema.tagsList) == 2

    def test_object_detection_schema_input(self):
        """Test ObjectDetectionSchemaInput model."""
        from arize_toolkit.models import (
            ObjectDetectionInput,
            ObjectDetectionSchemaInput,
        )

        pred_detection = ObjectDetectionInput(
            boundingBoxesCoordinatesColumnName="pred_coords",
            boundingBoxesCategoriesColumnName="pred_categories",
            boundingBoxesScoresColumnName="pred_scores",
        )

        actual_detection = ObjectDetectionInput(
            boundingBoxesCoordinatesColumnName="actual_coords",
            boundingBoxesCategoriesColumnName="actual_categories",
        )

        schema = ObjectDetectionSchemaInput(
            predictionObjectDetection=pred_detection,
            actualObjectDetection=actual_detection,
        )

        assert (
            schema.predictionObjectDetection.boundingBoxesCoordinatesColumnName
            == "pred_coords"
        )
        assert (
            schema.predictionObjectDetection.boundingBoxesScoresColumnName
            == "pred_scores"
        )
        assert schema.actualObjectDetection.boundingBoxesScoresColumnName is None

    def test_full_schema_flexibility(self):
        """Test FullSchema model with mixed fields."""
        from arize_toolkit.models import FullSchema, ObjectDetectionInput

        # Test that FullSchema can be used with different model types
        # Classification fields
        schema1 = FullSchema(predictionLabel="pred", actualLabel="actual")
        assert schema1.predictionLabel == "pred"
        assert schema1.predictionScore is None  # Regression field

        # Regression fields
        schema2 = FullSchema(predictionScore="score", actualScore="actual_score")
        assert schema2.predictionScore == "score"
        assert schema2.predictionLabel is None  # Classification field

        # Mixed fields
        schema3 = FullSchema(
            predictionLabel="class",
            predictionScore="score",
            rank="rank_col",
            predictionObjectDetection=ObjectDetectionInput(
                boundingBoxesCoordinatesColumnName="coords",
                boundingBoxesCategoriesColumnName="categories",
            ),
        )
        assert schema3.predictionLabel == "class"
        assert schema3.predictionScore == "score"
        assert schema3.rank == "rank_col"
        assert schema3.predictionObjectDetection is not None


class TestImportJobModels:
    def test_file_import_job_check(self):
        """Test FileImportJobCheck model."""
        from arize_toolkit.models import FileImportJobCheck

        check = FileImportJobCheck(
            id="job123",
            jobId="job123",
            jobStatus="active",
            totalFilesPendingCount=10,
            totalFilesSuccessCount=5,
            totalFilesFailedCount=1,
        )

        assert check.id == "job123"
        assert check.jobId == "job123"
        assert check.jobStatus == "active"
        assert check.totalFilesPendingCount == 10
        assert check.totalFilesSuccessCount == 5
        assert check.totalFilesFailedCount == 1

    def test_file_import_job(self):
        """Test FileImportJob model."""
        from arize_toolkit.models import FileImportJob, FullSchema
        from arize_toolkit.types import BlobStore, ModelEnvironment, ModelType

        created_time = datetime(2024, 1, 1, tzinfo=timezone.utc)

        job = FileImportJob(
            id="job123",
            jobId="job123",
            jobStatus="active",
            totalFilesPendingCount=10,
            totalFilesSuccessCount=5,
            totalFilesFailedCount=1,
            createdAt=created_time,
            modelName="my-model",
            modelId="model123",
            modelVersion="v1.0",
            modelType=ModelType.score_categorical,
            modelEnvironmentName=ModelEnvironment.production,
            modelSchema=FullSchema(predictionLabel="pred"),
            batchId="batch123",
            blobStore=BlobStore.S3,
            bucketName="my-bucket",
            prefix="data/",
        )

        assert job.id == "job123"
        assert job.createdAt == created_time
        assert job.modelName == "my-model"
        assert job.modelVersion == "v1.0"
        assert job.batchId == "batch123"
        assert job.blobStore == BlobStore.S3
        assert job.bucketName == "my-bucket"
        assert job.prefix == "data/"

    def test_table_import_job_check(self):
        """Test TableImportJobCheck model."""
        from arize_toolkit.models import TableImportJobCheck

        check = TableImportJobCheck(
            id="job456",
            jobId="job456",
            jobStatus="inactive",
            totalQueriesSuccessCount=100,
            totalQueriesFailedCount=2,
            totalQueriesPendingCount=0,
        )

        assert check.id == "job456"
        assert check.jobStatus == "inactive"
        assert check.totalQueriesSuccessCount == 100
        assert check.totalQueriesFailedCount == 2
        assert check.totalQueriesPendingCount == 0

    def test_table_import_job(self):
        """Test TableImportJob model."""
        from arize_toolkit.models import (
            FullSchema,
            TableImportJob,
            TableIngestionParameters,
        )
        from arize_toolkit.types import ModelEnvironment, ModelType, TableStore

        created_time = datetime(2024, 1, 1, tzinfo=timezone.utc)

        job = TableImportJob(
            id="job789",
            jobStatus="active",
            jobId="job789",
            createdAt=created_time,
            modelName="table-model",
            modelId="model789",
            modelType=ModelType.numeric,
            modelEnvironmentName=ModelEnvironment.validation,
            modelSchema=FullSchema(predictionScore="score"),
            table="my_table",
            tableStore=TableStore.BigQuery,
            projectId="my-project",
            dataset="my-dataset",
            totalQueriesSuccessCount=50,
            totalQueriesFailedCount=0,
            totalQueriesPendingCount=10,
            tableIngestionParameters=TableIngestionParameters(
                refreshIntervalSeconds=3600, queryWindowSizeSeconds=86400
            ),
        )

        assert job.id == "job789"
        assert job.table == "my_table"
        assert job.tableStore == TableStore.BigQuery
        assert job.projectId == "my-project"
        assert job.dataset == "my-dataset"
        assert job.tableIngestionParameters.refreshIntervalSeconds == 3600
        assert job.tableIngestionParameters.queryWindowSizeSeconds == 86400

    def test_azure_storage_identifier_input(self):
        """Test AzureStorageIdentifierInput model."""
        from arize_toolkit.models import AzureStorageIdentifierInput

        azure_id = AzureStorageIdentifierInput(
            tenantId="tenant123", storageAccountName="mystorageaccount"
        )

        assert azure_id.tenantId == "tenant123"
        assert azure_id.storageAccountName == "mystorageaccount"

    def test_databricks_table_config(self):
        """Test DatabricksTableConfig model."""
        from arize_toolkit.models import DatabricksTableConfig

        config = DatabricksTableConfig(
            hostName="my-databricks.cloud.databricks.com",
            endpoint="/sql/1.0/endpoints/123",
            port="443",
            token="dapi123",
            azureResourceId="resource123",
            azureTenantId="tenant456",
            catalog="my_catalog",
            databricksSchema="my_schema",
            tableName="my_table",
        )

        assert config.hostName == "my-databricks.cloud.databricks.com"
        assert config.endpoint == "/sql/1.0/endpoints/123"
        assert config.port == "443"
        assert config.token == "dapi123"
        assert config.azureResourceId == "resource123"
        assert config.azureTenantId == "tenant456"
        assert config.catalog == "my_catalog"
        assert config.databricksSchema == "my_schema"
        assert config.tableName == "my_table"
