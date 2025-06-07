from datetime import datetime
from typing import Optional

from pydantic import Field

from arize_toolkit.types import ModelEnvironment
from arize_toolkit.utils import GraphQLModel

## Custom Metric GraphQL Models ##


class CustomMetric(GraphQLModel):
    id: Optional[str] = Field(default=None)
    name: str
    createdAt: Optional[datetime] = Field(default=None)
    description: Optional[str] = Field(default=None)
    metric: str
    requiresPositiveClass: bool


class CustomMetricInput(GraphQLModel):
    modelId: str
    name: str
    description: str = Field(default="a custom metric")
    metric: str
    modelEnvironmentName: ModelEnvironment = Field(default=ModelEnvironment.production)
