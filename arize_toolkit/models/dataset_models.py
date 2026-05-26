from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from arize_toolkit.models.base_models import BaseNode
from arize_toolkit.types import DatasetStatus, DatasetType
from arize_toolkit.utils import GraphQLModel


class Dataset(BaseNode):
    createdAt: Optional[datetime] = Field(default=None, description="The datetime the dataset was created")
    updatedAt: Optional[datetime] = Field(default=None, description="The datetime the dataset was last updated")
    datasetType: Optional[DatasetType] = Field(default=None, description="The type of the dataset")
    status: Optional[DatasetStatus] = Field(default=None, description="The status of the dataset")
    columns: Optional[List[str]] = Field(default=None, description="The column names in the dataset")
    experimentCount: Optional[int] = Field(default=None, description="The number of experiments using this dataset")


class DatasetExample(GraphQLModel):
    """A single example/row from a dataset version."""

    id: str = Field(description="The unique ID of the example")
    createdAt: Optional[datetime] = Field(default=None, description="When the example was created")
    updatedAt: Optional[datetime] = Field(default=None, description="When the example was last updated")
    data: Dict[str, Any] = Field(default_factory=dict, description="Column name to value mapping")
