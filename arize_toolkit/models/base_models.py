from datetime import datetime
from typing import List, Optional

from pydantic import Field, model_validator

from arize_toolkit.types import ComparisonOperator, DimensionCategory, DimensionDataType, FilterRowType, ModelType
from arize_toolkit.utils import GraphQLModel

## Common GraphQL Models ##


class User(GraphQLModel):
    id: str = Field(description="The ID of the user")
    name: Optional[str] = Field(default=None, description="The name of the user")
    email: Optional[str] = Field(default=None, description="The email of the user")


class Dimension(GraphQLModel):
    id: Optional[str] = Field(default=None)
    name: str
    dataType: Optional[DimensionDataType] = Field(default=None)
    category: Optional[DimensionCategory] = Field(default=None)


class DimensionValue(GraphQLModel):
    id: Optional[str] = Field(default=None)
    value: str


class DimensionFilterInput(GraphQLModel):
    dimensionType: FilterRowType
    operator: ComparisonOperator = Field(default=ComparisonOperator.equals)
    name: Optional[str] = Field(default=None)
    values: List[str] = Field(default=[])

    @model_validator(mode="after")
    def verify_values(self):
        if self.dimensionType == FilterRowType.featureLabel or self.dimensionType == FilterRowType.tagLabel:
            if self.name is None:
                raise ValueError("Name is required for feature label or tag label filter type")
        return self


## Model GraphQL Models ##


class Model(GraphQLModel):
    id: str
    name: str
    modelType: ModelType
    createdAt: datetime
    isDemoModel: bool
