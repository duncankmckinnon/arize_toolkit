from datetime import datetime
from typing import Dict, List, Optional

from pydantic import Field

from arize_toolkit.models.base_models import Dimension, Model, User

# Import common models that are used by dashboard models
from arize_toolkit.models.custom_metrics_models import CustomMetric
from arize_toolkit.models.space_models import Space
from arize_toolkit.types import DataQualityMetric, DimensionCategory, ModelEnvironment, ModelType, PerformanceMetric
from arize_toolkit.utils import GraphQLModel

## Dashboard GraphQL Models ##


class DashboardBasis(GraphQLModel):
    id: str = Field(description="The ID of the dashboard")
    name: Optional[str] = Field(default=None, description="The name of the dashboard")
    creator: Optional[User] = Field(default=None, description="The user who created the dashboard")
    createdAt: Optional[datetime] = Field(default=None, description="The datetime the dashboard was created")
    status: Optional[str] = Field(default=None, description="The status of the dashboard")


class WidgetBasis(GraphQLModel):
    """Base model for dashboard widgets with common fields"""

    id: str = Field(description="The ID of the widget")
    dashboardId: Optional[str] = Field(default=None, description="The dashboard ID of the widget")
    title: Optional[str] = Field(default=None, description="The title of the widget")
    gridPosition: Optional[List[int]] = Field(default=None, description="The grid position of the widget")
    creationStatus: Optional[str] = Field(default=None, description="The creation status of the widget")


# Supporting models for widgets
class WidgetModel(GraphQLModel):
    """A model on a dashboard widget"""

    id: Optional[str] = Field(default=None, description="The ID of the widget model")
    externalModelId: Optional[str] = Field(default=None, description="The external model ID")
    createdAt: Optional[datetime] = Field(default=None, description="When the model was created")
    modelType: Optional[ModelType] = Field(default=None, description="The type of the model")


class StatisticWidgetFilterItem(GraphQLModel):
    """Filter item for statistic widgets"""

    id: Optional[str] = Field(default=None, description="The ID of the filter item")
    filterType: Optional[str] = Field(default=None, description="The type of filter")
    operator: Optional[str] = Field(default=None, description="The comparison operator")
    dimension: Optional[Dimension] = Field(default=None, description="The dimension being filtered")
    dimensionValues: Optional[List[Dict]] = Field(default=None, description="The dimension values")
    binaryValues: Optional[List[str]] = Field(default=None, description="Binary values for filter")
    numericValues: Optional[List[str]] = Field(default=None, description="Numeric values for filter")
    categoricalValues: Optional[List[str]] = Field(default=None, description="Categorical values for filter")


class BarChartPlot(GraphQLModel):
    """A plot within a bar chart widget"""

    id: Optional[str] = Field(default=None, description="The ID of the plot")
    title: Optional[str] = Field(default=None, description="The title of the plot")
    position: Optional[int] = Field(default=None, description="The position of the plot")
    modelId: Optional[str] = Field(default=None, description="The model ID for the plot")
    modelVersionIds: Optional[List[str]] = Field(default=None, description="The model version IDs")
    model: Optional[WidgetModel] = Field(default=None, description="The widget model")
    modelEnvironmentName: Optional[ModelEnvironment] = Field(default=None, description="The model environment")
    modelVersionEnvironmentBatches: Optional[List[str]] = Field(default=None, description="Model version environment batches")
    dimensionCategory: Optional[DimensionCategory] = Field(default=None, description="The dimension category")
    aggregation: Optional[DataQualityMetric] = Field(default=None, description="The aggregation type")
    dimension: Optional[Dimension] = Field(default=None, description="The dimension")
    predictionValueClass: Optional[str] = Field(default=None, description="The prediction value class")
    rankingAtK: Optional[int] = Field(default=None, description="The ranking at K value")
    colors: Optional[List[str]] = Field(default=None, description="Colors for the plot")


class BarChartWidgetAxisConfig(GraphQLModel):
    """Axis configuration for bar chart widgets"""

    legend: Optional[str] = Field(default=None, description="The axis legend")


class BarChartWidgetConfig(GraphQLModel):
    """Configuration for bar chart widgets"""

    keys: Optional[List[str]] = Field(default=None, description="The keys for the chart")
    indexBy: Optional[str] = Field(default=None, description="The index by field")
    axisBottom: Optional[BarChartWidgetAxisConfig] = Field(default=None, description="Bottom axis configuration")
    axisLeft: Optional[BarChartWidgetAxisConfig] = Field(default=None, description="Left axis configuration")


class LineChartPlot(GraphQLModel):
    """A plot within a line chart widget"""

    id: Optional[str] = Field(default=None, description="The ID of the plot")
    title: Optional[str] = Field(default=None, description="The title of the plot")
    position: Optional[int] = Field(default=None, description="The position of the plot")
    modelId: Optional[str] = Field(default=None, description="The model ID for the plot")
    modelVersionIds: Optional[List[str]] = Field(default=None, description="The model version IDs")
    modelEnvironmentName: Optional[ModelEnvironment] = Field(default=None, description="The model environment")
    modelVersionEnvironmentBatches: Optional[List[str]] = Field(default=None, description="Model version environment batches")
    dimensionCategory: Optional[DimensionCategory] = Field(default=None, description="The dimension category")
    splitByEnabled: Optional[bool] = Field(default=None, description="Whether split by is enabled")
    splitByDimension: Optional[str] = Field(default=None, description="The split by dimension")
    splitByDimensionCategory: Optional[DimensionCategory] = Field(default=None, description="The split by dimension category")
    splitByOverallMetricEnabled: Optional[bool] = Field(default=None, description="Whether split by overall metric is enabled")
    cohorts: Optional[List[str]] = Field(default=None, description="Cohorts for the plot")
    colors: Optional[List[str]] = Field(default=None, description="Colors for the plot")
    dimension: Optional[Dimension] = Field(default=None, description="The dimension")
    predictionValueClass: Optional[str] = Field(default=None, description="The prediction value class")
    rankingAtK: Optional[int] = Field(default=None, description="The ranking at K value")
    model: Optional[WidgetModel] = Field(default=None, description="The widget model")


class LineChartWidgetAxisConfig(GraphQLModel):
    """Axis configuration for line chart widgets"""

    legend: Optional[str] = Field(default=None, description="The axis legend")


class LineChartWidgetXScaleConfig(GraphQLModel):
    """X-axis scale configuration for line chart widgets"""

    max: Optional[str] = Field(default=None, description="Maximum value")
    min: Optional[str] = Field(default=None, description="Minimum value")
    scaleType: Optional[str] = Field(default=None, description="Scale type")
    format: Optional[str] = Field(default=None, description="Format string")
    precision: Optional[str] = Field(default=None, description="Precision type")


class LineChartWidgetYScaleConfig(GraphQLModel):
    """Y-axis scale configuration for line chart widgets"""

    max: Optional[str] = Field(default=None, description="Maximum value")
    min: Optional[str] = Field(default=None, description="Minimum value")
    scaleType: Optional[str] = Field(default=None, description="Scale type")
    stacked: Optional[bool] = Field(default=None, description="Whether the chart is stacked")


class LineChartWidgetConfig(GraphQLModel):
    """Configuration for line chart widgets"""

    axisBottom: Optional[LineChartWidgetAxisConfig] = Field(default=None, description="Bottom axis configuration")
    axisLeft: Optional[LineChartWidgetAxisConfig] = Field(default=None, description="Left axis configuration")
    curve: Optional[str] = Field(default=None, description="Curve type")
    xScale: Optional[LineChartWidgetXScaleConfig] = Field(default=None, description="X-axis scale configuration")
    yScale: Optional[LineChartWidgetYScaleConfig] = Field(default=None, description="Y-axis scale configuration")


class ExperimentChartPlot(GraphQLModel):
    """A plot within an experiment chart widget"""

    id: Optional[str] = Field(default=None, description="The ID of the plot")
    title: Optional[str] = Field(default=None, description="The title of the plot")
    position: Optional[int] = Field(default=None, description="The position of the plot")
    datasetId: Optional[str] = Field(default=None, description="The dataset ID")
    evaluationMetric: Optional[str] = Field(default=None, description="The evaluation metric")


# Enhanced Widget Models
class StatisticWidget(WidgetBasis):
    """A statistic widget on a dashboard"""

    modelId: Optional[str] = Field(default=None, description="The model ID on the widget")
    modelVersionIds: Optional[List[str]] = Field(default=None, description="The model version IDs on the widget")
    dimensionCategory: Optional[DimensionCategory] = Field(default=None, description="The dimension category of the widget")
    performanceMetric: Optional[PerformanceMetric] = Field(default=None, description="The performance metric function of the widget")
    aggregation: Optional[DataQualityMetric] = Field(default=None, description="The data quality metric type of the widget")
    predictionValueClass: Optional[str] = Field(default=None, description="The class of the classification model on the widget")
    rankingAtK: Optional[int] = Field(default=None, description="The @K value for the performance metric")
    modelEnvironmentName: Optional[ModelEnvironment] = Field(default=None, description="The model environment of the widget")
    modelVersionEnvironmentBatches: Optional[List[str]] = Field(default=None, description="The batch ids on the widget")
    timeSeriesMetricType: Optional[str] = Field(default=None, description="The type of timeseries metric on the widget")
    filters: Optional[List[StatisticWidgetFilterItem]] = Field(default=None, description="Filters applied to the widget")
    dimension: Optional[Dimension] = Field(default=None, description="The dimension")
    model: Optional[WidgetModel] = Field(default=None, description="The widget model")
    customMetric: Optional[CustomMetric] = Field(default=None, description="Custom metric if used")


class BarChartWidget(WidgetBasis):
    """A bar chart widget on a dashboard"""

    sortOrder: Optional[str] = Field(default=None, description="Sort order for the bars")
    yMin: Optional[float] = Field(default=None, description="Minimum Y-axis value")
    yMax: Optional[float] = Field(default=None, description="Maximum Y-axis value")
    yAxisLabel: Optional[str] = Field(default=None, description="Y-axis label")
    topN: Optional[float] = Field(default=None, description="Top N value")
    isNormalized: Optional[bool] = Field(default=None, description="Whether the chart is normalized")
    binOption: Optional[str] = Field(default=None, description="Bin option")
    numBins: Optional[int] = Field(default=None, description="Number of bins")
    customBins: Optional[List[float]] = Field(default=None, description="Custom bin values")
    quantiles: Optional[List[float]] = Field(default=None, description="Quantile values")
    performanceMetric: Optional[PerformanceMetric] = Field(default=None, description="Performance metric")
    plots: Optional[List[BarChartPlot]] = Field(default=None, description="Plots in the bar chart")
    config: Optional[BarChartWidgetConfig] = Field(default=None, description="Widget configuration")


class LineChartWidget(WidgetBasis):
    """A line chart widget on a dashboard"""

    yMin: Optional[float] = Field(default=None, description="The minimum domain on the y-axis")
    yMax: Optional[float] = Field(default=None, description="The maximum domain on the y-axis")
    yAxisLabel: Optional[str] = Field(default=None, description="The label for the y-axis")
    timeSeriesMetricType: Optional[str] = Field(default=None, description="The type of timeseries metric on the widget")
    config: Optional[LineChartWidgetConfig] = Field(default=None, description="Widget configuration")
    plots: Optional[List[LineChartPlot]] = Field(default=None, description="Plots in the line chart")


class ExperimentChartWidget(WidgetBasis):
    """An experiment chart widget on a dashboard"""

    plots: Optional[List[ExperimentChartPlot]] = Field(default=None, description="Plots in the experiment chart")


class TextWidget(WidgetBasis):
    """A text widget on a dashboard"""

    content: Optional[str] = Field(default=None, description="The content of the text widget")


class Dashboard(DashboardBasis):
    """Extended dashboard model with all connections"""

    space: Optional[Space] = Field(default=None, description="The space that the dashboard belongs to")
    models: Optional[List[Model]] = Field(default=None, description="A list of unique models referenced in this dashboard")
    statisticWidgets: Optional[List[StatisticWidget]] = Field(default=None, description="The statistic widgets on the dashboard")
    barChartWidgets: Optional[List[BarChartWidget]] = Field(default=None, description="The bar chart widgets on the dashboard")
    lineChartWidgets: Optional[List[LineChartWidget]] = Field(default=None, description="The line chart widgets on the dashboard")
    experimentChartWidgets: Optional[List[ExperimentChartWidget]] = Field(default=None, description="The experiment chart widgets on the dashboard")
    driftLineChartWidgets: Optional[List[LineChartWidget]] = Field(default=None, description="The drift line chart widgets on the dashboard")
    monitorLineChartWidgets: Optional[List[LineChartWidget]] = Field(default=None, description="The monitor line chart widgets on the dashboard")
    textWidgets: Optional[List[TextWidget]] = Field(default=None, description="The text widgets on the dashboard")
