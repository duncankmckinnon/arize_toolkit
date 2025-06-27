from datetime import datetime

from arize_toolkit.models import (
    BarChartPlot,
    BarChartWidget,
    BarChartWidgetAxisConfig,
    BarChartWidgetConfig,
    BarChartWidgetData,
    BarChartWidgetDataKeysAndValuesObject,
    BarChartWidgetDataValueObjectType,
    CreateDashboardMutationInput,
    CreateLineChartWidgetMutationInput,
    CustomMetric,
    Dashboard,
    DashboardBasis,
    DashboardPerformanceSlice,
    Dimension,
    DimensionValue,
    ExperimentChartPlot,
    ExperimentChartWidget,
    LineChartPlot,
    LineChartPlotInput,
    LineChartWidget,
    LineChartWidgetAxisConfig,
    LineChartWidgetConfig,
    LineChartWidgetXScaleConfig,
    LineChartWidgetYScaleConfig,
    Model,
    Space,
    StatisticWidget,
    StatisticWidgetFilterItem,
    TextWidget,
    User,
    WidgetBasis,
    WidgetModel,
)
from arize_toolkit.types import DashboardStatus, DataQualityMetric, DimensionCategory, ModelEnvironment, ModelType, PerformanceMetric, TimeSeriesMetricCategory, WidgetCreationStatus


class TestDashboardBasis:
    """Test DashboardBasis model"""

    def test_init(self):
        """Test DashboardBasis initialization"""
        dashboard = DashboardBasis(
            id="dash_123",
            name="Test Dashboard",
            createdAt=datetime.now(),
            status=DashboardStatus.active,
        )
        assert dashboard.id == "dash_123"
        assert dashboard.name == "Test Dashboard"
        assert dashboard.status == DashboardStatus.active

    def test_optional_fields(self):
        """Test DashboardBasis with optional fields"""
        user = User(id="user_123", name="Test User")
        dashboard = DashboardBasis(
            id="dash_123",
            name="Test Dashboard",
            creator=user,
            createdAt=datetime.now(),
            status=DashboardStatus.inactive,
        )
        assert dashboard.creator.id == "user_123"
        assert dashboard.status == DashboardStatus.inactive

    def test_status_values(self):
        """Test DashboardBasis status field accepts valid values"""
        valid_statuses = [
            DashboardStatus.active,
            DashboardStatus.inactive,
            DashboardStatus.deleted,
            None,
        ]
        for status in valid_statuses:
            dashboard = DashboardBasis(
                id="dash_123",
                name="Test Dashboard",
                createdAt=datetime.now(),
                status=status,
            )
            assert dashboard.status == status


class TestWidgetBasis:
    """Test WidgetBasis model"""

    def test_init(self):
        """Test WidgetBasis initialization"""
        widget = WidgetBasis(
            id="widget_123",
            dashboardId="dash_123",
            title="Test Widget",
            gridPosition=[0, 0, 2, 2],
        )
        assert widget.id == "widget_123"
        assert widget.dashboardId == "dash_123"
        assert widget.title == "Test Widget"
        assert widget.gridPosition == [0, 0, 2, 2]

    def test_optional_fields(self):
        """Test WidgetBasis with optional fields"""
        widget = WidgetBasis(
            id="widget_123",
            dashboardId="dash_123",
            title="Test Widget",
            gridPosition=[0, 0, 2, 2],
            creationStatus=WidgetCreationStatus.created,
        )
        assert widget.creationStatus == WidgetCreationStatus.created


class TestStatisticWidget:
    """Test StatisticWidget model"""

    def test_init(self):
        """Test StatisticWidget initialization"""
        widget = StatisticWidget(
            id="stat_widget_123",
            dashboardId="dash_123",
            title="Statistics Widget",
            gridPosition=[0, 0, 2, 2],
            modelId="model_123",
            modelVersionIds=["v1", "v2"],
            dimensionCategory=DimensionCategory.featureLabel,
            modelEnvironmentName=ModelEnvironment.production,
        )
        assert widget.modelId == "model_123"
        assert widget.modelVersionIds == ["v1", "v2"]
        assert widget.dimensionCategory == DimensionCategory.featureLabel
        assert widget.modelEnvironmentName == ModelEnvironment.production

    def test_default_values(self):
        """Test StatisticWidget default values"""
        widget = StatisticWidget(
            id="stat_widget_123",
            dashboardId="dash_123",
            title="Statistics Widget",
            gridPosition=[0, 0, 2, 2],
            modelId="model_123",
            modelVersionIds=[],
        )
        assert widget.dimensionCategory is None
        assert widget.performanceMetric is None


class TestLineChartWidget:
    """Test LineChartWidget model"""

    def test_init(self):
        """Test LineChartWidget initialization"""
        widget = LineChartWidget(
            id="line_widget_123",
            dashboardId="dash_123",
            title="Line Chart Widget",
            gridPosition=[0, 0, 4, 3],
            yMin=0.0,
            yMax=100.0,
            yAxisLabel="Performance %",
        )
        assert widget.yMin == 0.0
        assert widget.yMax == 100.0
        assert widget.yAxisLabel == "Performance %"

    def test_optional_fields(self):
        """Test LineChartWidget with optional fields as None"""
        widget = LineChartWidget(
            id="line_widget_123",
            dashboardId="dash_123",
            title="Line Chart Widget",
            gridPosition=[0, 0, 4, 3],
        )
        assert widget.yMin is None
        assert widget.yMax is None
        assert widget.yAxisLabel is None


class TestDashboard:
    """Test Dashboard model (extended)"""

    def test_init(self):
        """Test Dashboard initialization with connections"""
        space = Space(id="space_123", name="Test Space")
        model = Model(
            id="model_123",
            name="Test Model",
            modelType=ModelType.score_categorical,
            createdAt=datetime.now(),
            isDemoModel=False,
        )

        dashboard = Dashboard(
            id="dash_123",
            name="Extended Dashboard",
            createdAt=datetime.now(),
            status=DashboardStatus.active,
            space=space,
            models=[model],
        )
        assert dashboard.space.id == "space_123"
        assert len(dashboard.models) == 1
        assert dashboard.models[0].id == "model_123"

    def test_widget_connections(self):
        """Test Dashboard with widget connections"""
        stat_widget = StatisticWidget(
            id="stat_123",
            dashboardId="dash_123",
            title="Stat Widget",
            gridPosition=[0, 0, 2, 2],
            modelId="model_123",
            modelVersionIds=["v1"],
        )

        line_widget = LineChartWidget(
            id="line_123",
            dashboardId="dash_123",
            title="Line Widget",
            gridPosition=[2, 0, 2, 2],
            yAxisLabel="Accuracy",
        )

        dashboard = Dashboard(
            id="dash_123",
            name="Dashboard with Widgets",
            createdAt=datetime.now(),
            status=DashboardStatus.active,
            statisticWidgets=[stat_widget],
            lineChartWidgets=[line_widget],
        )

        assert len(dashboard.statisticWidgets) == 1
        assert dashboard.statisticWidgets[0].title == "Stat Widget"
        assert len(dashboard.lineChartWidgets) == 1
        assert dashboard.lineChartWidgets[0].yAxisLabel == "Accuracy"

    def test_empty_connections(self):
        """Test Dashboard with empty widget connections"""
        dashboard = Dashboard(
            id="dash_123",
            name="Empty Dashboard",
            createdAt=datetime.now(),
            status=DashboardStatus.active,
        )

        assert dashboard.models is None
        assert dashboard.statisticWidgets is None
        assert dashboard.lineChartWidgets is None


class TestWidgetModel:
    """Test WidgetModel model"""

    def test_init(self):
        """Test WidgetModel initialization"""
        widget_model = WidgetModel(
            id="widget_model_123",
            externalModelId="external_123",
            createdAt=datetime.now(),
            modelType=ModelType.score_categorical,
        )
        assert widget_model.id == "widget_model_123"
        assert widget_model.externalModelId == "external_123"
        assert widget_model.modelType == ModelType.score_categorical
        assert widget_model.createdAt is not None

    def test_optional_fields(self):
        """Test WidgetModel with optional fields"""
        widget_model = WidgetModel()
        assert widget_model.id is None
        assert widget_model.externalModelId is None
        assert widget_model.createdAt is None
        assert widget_model.modelType is None


class TestStatisticWidgetFilterItem:
    """Test StatisticWidgetFilterItem model"""

    def test_init(self):
        """Test StatisticWidgetFilterItem initialization"""
        dimension = Dimension(id="dim_123", name="test_dimension")
        dimension_value = DimensionValue(id="dv_123", value="test")

        filter_item = StatisticWidgetFilterItem(
            id="filter_123",
            filterType="feature",
            operator="equals",
            dimension=dimension,
            dimensionValues=[dimension_value],
            binaryValues=["true", "false"],
            numericValues=["1.0", "2.0"],
            categoricalValues=["cat1", "cat2"],
        )

        assert filter_item.id == "filter_123"
        assert filter_item.filterType == "feature"
        assert filter_item.operator == "equals"
        assert filter_item.dimension.name == "test_dimension"
        assert len(filter_item.dimensionValues) == 1
        assert filter_item.dimensionValues[0].value == "test"
        assert filter_item.binaryValues == ["true", "false"]

    def test_optional_fields(self):
        """Test StatisticWidgetFilterItem with optional fields"""
        filter_item = StatisticWidgetFilterItem()
        assert filter_item.id is None
        assert filter_item.filterType is None
        assert filter_item.operator is None
        assert filter_item.dimension is None


class TestBarChartPlot:
    """Test BarChartPlot model"""

    def test_init(self):
        """Test BarChartPlot initialization"""
        widget_model = WidgetModel(id="widget_model_123")
        dimension = Dimension(id="dim_123", name="test_dim")

        plot = BarChartPlot(
            id="plot_123",
            title="Test Plot",
            position=1,
            modelId="model_123",
            modelVersionIds=["v1", "v2"],
            model=widget_model,
            modelEnvironmentName=ModelEnvironment.production,
            dimensionCategory=DimensionCategory.featureLabel,
            aggregation=DataQualityMetric.avg,
            dimension=dimension,
            colors=["#FF0000", "#00FF00"],
        )

        assert plot.id == "plot_123"
        assert plot.title == "Test Plot"
        assert plot.position == 1
        assert plot.modelId == "model_123"
        assert plot.modelVersionIds == ["v1", "v2"]
        assert plot.model.id == "widget_model_123"
        assert plot.colors == ["#FF0000", "#00FF00"]

    def test_optional_fields(self):
        """Test BarChartPlot with optional fields"""
        plot = BarChartPlot()
        assert plot.id is None
        assert plot.title is None
        assert plot.position is None
        assert plot.model is None


class TestBarChartWidgetAxisConfig:
    """Test BarChartWidgetAxisConfig model"""

    def test_init(self):
        """Test BarChartWidgetAxisConfig initialization"""
        config = BarChartWidgetAxisConfig(legend="Test Legend")
        assert config.legend == "Test Legend"

    def test_optional_fields(self):
        """Test BarChartWidgetAxisConfig with optional fields"""
        config = BarChartWidgetAxisConfig()
        assert config.legend is None


class TestBarChartWidgetConfig:
    """Test BarChartWidgetConfig model"""

    def test_init(self):
        """Test BarChartWidgetConfig initialization"""
        axis_bottom = BarChartWidgetAxisConfig(legend="Bottom Legend")
        axis_left = BarChartWidgetAxisConfig(legend="Left Legend")

        config = BarChartWidgetConfig(
            keys=["key1", "key2"],
            indexBy="index_field",
            axisBottom=axis_bottom,
            axisLeft=axis_left,
        )

        assert config.keys == ["key1", "key2"]
        assert config.indexBy == "index_field"
        assert config.axisBottom.legend == "Bottom Legend"
        assert config.axisLeft.legend == "Left Legend"

    def test_optional_fields(self):
        """Test BarChartWidgetConfig with optional fields"""
        config = BarChartWidgetConfig()
        assert config.keys is None
        assert config.indexBy is None
        assert config.axisBottom is None
        assert config.axisLeft is None


class TestLineChartPlot:
    """Test LineChartPlot model"""

    def test_init(self):
        """Test LineChartPlot initialization"""
        widget_model = WidgetModel(id="widget_model_123")
        dimension = Dimension(id="dim_123", name="test_dim")

        plot = LineChartPlot(
            id="plot_123",
            title="Line Plot",
            position=1,
            modelId="model_123",
            modelVersionIds=["v1", "v2"],
            modelEnvironmentName=ModelEnvironment.production,
            dimensionCategory=DimensionCategory.prediction,
            splitByEnabled=True,
            splitByDimension="split_dim",
            splitByDimensionCategory=DimensionCategory.featureLabel,
            splitByOverallMetricEnabled=False,
            cohorts=["cohort1", "cohort2"],
            colors=["#FF0000", "#00FF00"],
            dimension=dimension,
            model=widget_model,
        )

        assert plot.id == "plot_123"
        assert plot.title == "Line Plot"
        assert plot.splitByEnabled is True
        assert plot.splitByDimension == "split_dim"
        assert plot.cohorts == ["cohort1", "cohort2"]
        assert plot.model.id == "widget_model_123"

    def test_optional_fields(self):
        """Test LineChartPlot with optional fields"""
        plot = LineChartPlot()
        assert plot.id is None
        assert plot.splitByEnabled is None
        assert plot.cohorts is None
        assert plot.model is None


class TestLineChartWidgetAxisConfig:
    """Test LineChartWidgetAxisConfig model"""

    def test_init(self):
        """Test LineChartWidgetAxisConfig initialization"""
        config = LineChartWidgetAxisConfig(legend="Axis Legend")
        assert config.legend == "Axis Legend"

    def test_optional_fields(self):
        """Test LineChartWidgetAxisConfig with optional fields"""
        config = LineChartWidgetAxisConfig()
        assert config.legend is None


class TestLineChartWidgetXScaleConfig:
    """Test LineChartWidgetXScaleConfig model"""

    def test_init(self):
        """Test LineChartWidgetXScaleConfig initialization"""
        config = LineChartWidgetXScaleConfig(max="100", min="0", scaleType="linear", format="%Y-%m-%d", precision="day")

        assert config.max == "100"
        assert config.min == "0"
        assert config.scaleType == "linear"
        assert config.format == "%Y-%m-%d"
        assert config.precision == "day"

    def test_optional_fields(self):
        """Test LineChartWidgetXScaleConfig with optional fields"""
        config = LineChartWidgetXScaleConfig()
        assert config.max is None
        assert config.min is None
        assert config.scaleType is None


class TestLineChartWidgetYScaleConfig:
    """Test LineChartWidgetYScaleConfig model"""

    def test_init(self):
        """Test LineChartWidgetYScaleConfig initialization"""
        config = LineChartWidgetYScaleConfig(max="100", min="0", scaleType="linear", stacked=True)

        assert config.max == "100"
        assert config.min == "0"
        assert config.scaleType == "linear"
        assert config.stacked is True

    def test_optional_fields(self):
        """Test LineChartWidgetYScaleConfig with optional fields"""
        config = LineChartWidgetYScaleConfig()
        assert config.max is None
        assert config.stacked is None


class TestLineChartWidgetConfig:
    """Test LineChartWidgetConfig model"""

    def test_init(self):
        """Test LineChartWidgetConfig initialization"""
        axis_bottom = LineChartWidgetAxisConfig(legend="X-Axis")
        axis_left = LineChartWidgetAxisConfig(legend="Y-Axis")
        x_scale = LineChartWidgetXScaleConfig(scaleType="time")
        y_scale = LineChartWidgetYScaleConfig(scaleType="linear", stacked=False)

        config = LineChartWidgetConfig(
            axisBottom=axis_bottom,
            axisLeft=axis_left,
            curve="linear",
            xScale=x_scale,
            yScale=y_scale,
        )

        assert config.axisBottom.legend == "X-Axis"
        assert config.axisLeft.legend == "Y-Axis"
        assert config.curve == "linear"
        assert config.xScale.scaleType == "time"
        assert config.yScale.stacked is False

    def test_optional_fields(self):
        """Test LineChartWidgetConfig with optional fields"""
        config = LineChartWidgetConfig()
        assert config.axisBottom is None
        assert config.curve is None
        assert config.xScale is None


class TestExperimentChartPlot:
    """Test ExperimentChartPlot model"""

    def test_init(self):
        """Test ExperimentChartPlot initialization"""
        plot = ExperimentChartPlot(
            id="exp_plot_123",
            title="Experiment Plot",
            position=1,
            datasetId="dataset_123",
            evaluationMetric="accuracy",
        )

        assert plot.id == "exp_plot_123"
        assert plot.title == "Experiment Plot"
        assert plot.position == 1
        assert plot.datasetId == "dataset_123"
        assert plot.evaluationMetric == "accuracy"

    def test_optional_fields(self):
        """Test ExperimentChartPlot with optional fields"""
        plot = ExperimentChartPlot()
        assert plot.id is None
        assert plot.title is None
        assert plot.datasetId is None


class TestEnhancedBarChartWidget:
    """Test enhanced BarChartWidget model"""

    def test_init(self):
        """Test BarChartWidget initialization with enhanced fields"""
        axis_config = BarChartWidgetAxisConfig(legend="Test Legend")
        widget_config = BarChartWidgetConfig(keys=["key1", "key2"], indexBy="index", axisBottom=axis_config)
        plot = BarChartPlot(id="plot_123", title="Plot 1")

        widget = BarChartWidget(
            id="bar_widget_123",
            dashboardId="dash_123",
            title="Enhanced Bar Chart",
            gridPosition=[0, 0, 2, 2],
            sortOrder="vol_desc",
            yMin=0.0,
            yMax=100.0,
            yAxisLabel="Performance",
            topN=10.0,
            isNormalized=True,
            binOption="custom",
            numBins=20,
            customBins=[0.0, 25.0, 50.0, 75.0, 100.0],
            quantiles=[0.25, 0.5, 0.75],
            performanceMetric=PerformanceMetric.accuracy,
            plots=[plot],
            config=widget_config,
        )

        assert widget.id == "bar_widget_123"
        assert widget.sortOrder == "vol_desc"
        assert widget.yMin == 0.0
        assert widget.topN == 10.0
        assert widget.isNormalized is True
        assert widget.numBins == 20
        assert len(widget.customBins) == 5
        assert len(widget.plots) == 1
        assert widget.config.keys == ["key1", "key2"]

    def test_optional_fields(self):
        """Test BarChartWidget with optional fields"""
        widget = BarChartWidget(id="bar_widget_123")
        assert widget.sortOrder is None
        assert widget.yMin is None
        assert widget.plots is None
        assert widget.config is None


class TestEnhancedStatisticWidget:
    """Test enhanced StatisticWidget model"""

    def test_init_with_enhanced_fields(self):
        """Test StatisticWidget initialization with enhanced fields"""
        dimension = Dimension(id="dim_123", name="test_dim")
        widget_model = WidgetModel(id="widget_model_123")
        custom_metric = CustomMetric(
            id="metric_123",
            name="Custom Metric",
            metric="test_metric",
            requiresPositiveClass=False,
        )
        filter_item = StatisticWidgetFilterItem(id="filter_123", filterType="feature")

        widget = StatisticWidget(
            id="stat_widget_123",
            dashboardId="dash_123",
            title="Enhanced Statistic Widget",
            gridPosition=[0, 0, 2, 2],
            modelId="model_123",
            modelVersionIds=["v1", "v2"],
            dimensionCategory=DimensionCategory.featureLabel,
            performanceMetric=PerformanceMetric.accuracy,
            timeSeriesMetricType=TimeSeriesMetricCategory.modelDataMetric,
            filters=[filter_item],
            dimension=dimension,
            model=widget_model,
            customMetric=custom_metric,
        )

        assert widget.timeSeriesMetricType == TimeSeriesMetricCategory.modelDataMetric
        assert len(widget.filters) == 1
        assert widget.filters[0].id == "filter_123"
        assert widget.dimension.name == "test_dim"
        assert widget.model.id == "widget_model_123"
        assert widget.customMetric.name == "Custom Metric"

    def test_enhanced_optional_fields(self):
        """Test StatisticWidget enhanced optional fields"""
        widget = StatisticWidget(id="stat_widget_123")
        assert widget.filters is None
        assert widget.dimension is None
        assert widget.model is None
        assert widget.customMetric is None


class TestEnhancedLineChartWidget:
    """Test enhanced LineChartWidget model"""

    def test_init_with_enhanced_fields(self):
        """Test LineChartWidget initialization with enhanced fields"""
        axis_config = LineChartWidgetAxisConfig(legend="Time")
        widget_config = LineChartWidgetConfig(axisBottom=axis_config, curve="smooth")
        plot = LineChartPlot(id="plot_123", title="Line Plot")

        widget = LineChartWidget(
            id="line_widget_123",
            dashboardId="dash_123",
            title="Enhanced Line Chart",
            gridPosition=[0, 0, 4, 3],
            yMin=0.0,
            yMax=100.0,
            yAxisLabel="Accuracy %",
            timeSeriesMetricType="evaluation",
            config=widget_config,
            plots=[plot],
        )

        assert widget.timeSeriesMetricType == "evaluation"
        assert widget.config.axisBottom.legend == "Time"
        assert widget.config.curve == "smooth"
        assert len(widget.plots) == 1
        assert widget.plots[0].title == "Line Plot"

    def test_enhanced_optional_fields(self):
        """Test LineChartWidget enhanced optional fields"""
        widget = LineChartWidget(id="line_widget_123")
        assert widget.timeSeriesMetricType is None
        assert widget.config is None
        assert widget.plots is None


class TestExperimentChartWidget:
    """Test ExperimentChartWidget model"""

    def test_init(self):
        """Test ExperimentChartWidget initialization"""
        plot1 = ExperimentChartPlot(id="plot_1", title="Plot 1", datasetId="dataset_1")
        plot2 = ExperimentChartPlot(id="plot_2", title="Plot 2", datasetId="dataset_2")

        widget = ExperimentChartWidget(
            id="exp_widget_123",
            dashboardId="dash_123",
            title="Experiment Chart Widget",
            gridPosition=[0, 0, 3, 3],
            plots=[plot1, plot2],
        )

        assert widget.id == "exp_widget_123"
        assert widget.title == "Experiment Chart Widget"
        assert len(widget.plots) == 2
        assert widget.plots[0].title == "Plot 1"
        assert widget.plots[1].datasetId == "dataset_2"

    def test_optional_fields(self):
        """Test ExperimentChartWidget with optional fields"""
        widget = ExperimentChartWidget(id="exp_widget_123")
        assert widget.plots is None


class TestTextWidget:
    """Test TextWidget model"""

    def test_init(self):
        """Test TextWidget initialization"""
        widget = TextWidget(
            id="text_widget_123",
            dashboardId="dash_123",
            title="Text Widget",
            gridPosition=[0, 0, 2, 1],
            content="This is some text content for the widget.",
        )

        assert widget.id == "text_widget_123"
        assert widget.title == "Text Widget"
        assert widget.content == "This is some text content for the widget."

    def test_optional_fields(self):
        """Test TextWidget with optional fields"""
        widget = TextWidget(id="text_widget_123")
        assert widget.content is None


class TestBarChartWidgetData:
    """Test BarChartWidgetData model"""

    def test_init(self):
        """Test BarChartWidgetData initialization"""
        keys_and_values = [
            BarChartWidgetDataKeysAndValuesObject(
                k="prediction_class",
                v="0.85",
                vType=BarChartWidgetDataValueObjectType.number,
            ),
            BarChartWidgetDataKeysAndValuesObject(k="accuracy", v="85%", vType=BarChartWidgetDataValueObjectType.string),
        ]

        data = BarChartWidgetData(
            keysAndValues=keys_and_values,
            performanceImpactValue=0.92,
            evalMetricMin=0.0,
            evalMetricMax=1.0,
        )

        assert len(data.keysAndValues) == 2
        assert data.keysAndValues[0].k == "prediction_class"
        assert data.keysAndValues[1].v == "85%"
        assert data.performanceImpactValue == 0.92
        assert data.evalMetricMin == 0.0
        assert data.evalMetricMax == 1.0

    def test_required_fields_only(self):
        """Test BarChartWidgetData with only required fields"""
        keys_and_values = [BarChartWidgetDataKeysAndValuesObject(k="feature_name", vType=BarChartWidgetDataValueObjectType.string)]

        data = BarChartWidgetData(keysAndValues=keys_and_values)

        assert len(data.keysAndValues) == 1
        assert data.keysAndValues[0].k == "feature_name"
        assert data.performanceImpactValue is None
        assert data.evalMetricMin is None
        assert data.evalMetricMax is None

    def test_optional_fields(self):
        """Test BarChartWidgetData with partial optional fields"""
        keys_and_values = [
            BarChartWidgetDataKeysAndValuesObject(
                k="range_bucket",
                v="0.65 to 0.89823",
                vType=BarChartWidgetDataValueObjectType.range,
            )
        ]

        data = BarChartWidgetData(keysAndValues=keys_and_values, performanceImpactValue=0.75)

        assert len(data.keysAndValues) == 1
        assert data.keysAndValues[0].vType == BarChartWidgetDataValueObjectType.range
        assert data.performanceImpactValue == 0.75
        assert data.evalMetricMin is None
        assert data.evalMetricMax is None


class TestBarChartWidgetDataKeysAndValuesObject:
    """Test BarChartWidgetDataKeysAndValuesObject model"""

    def test_init(self):
        """Test BarChartWidgetDataKeysAndValuesObject initialization"""
        data_object = BarChartWidgetDataKeysAndValuesObject(
            k="prediction_class",
            v="0.85",
            vType=BarChartWidgetDataValueObjectType.number,
            secondaryValue="85%",
            secondaryValueType=BarChartWidgetDataValueObjectType.string,
            secondaryValueColorIndex=3,
            plotKey="Accuracy by Class",
        )

        assert data_object.k == "prediction_class"
        assert data_object.v == "0.85"
        assert data_object.vType == BarChartWidgetDataValueObjectType.number
        assert data_object.secondaryValue == "85%"
        assert data_object.secondaryValueType == BarChartWidgetDataValueObjectType.string
        assert data_object.secondaryValueColorIndex == 3
        assert data_object.plotKey == "Accuracy by Class"

    def test_required_fields_only(self):
        """Test BarChartWidgetDataKeysAndValuesObject with only required fields"""
        data_object = BarChartWidgetDataKeysAndValuesObject(k="feature_name", vType=BarChartWidgetDataValueObjectType.string)

        assert data_object.k == "feature_name"
        assert data_object.v is None
        assert data_object.vType == BarChartWidgetDataValueObjectType.string
        assert data_object.secondaryValue is None
        assert data_object.secondaryValueType is None
        assert data_object.secondaryValueColorIndex is None
        assert data_object.plotKey is None

    def test_optional_fields(self):
        """Test BarChartWidgetDataKeysAndValuesObject with partial optional fields"""
        data_object = BarChartWidgetDataKeysAndValuesObject(
            k="range_value",
            v="0.65 to 0.89823",
            vType=BarChartWidgetDataValueObjectType.range,
            plotKey="Score Distribution",
        )

        assert data_object.k == "range_value"
        assert data_object.v == "0.65 to 0.89823"
        assert data_object.vType == BarChartWidgetDataValueObjectType.range
        assert data_object.plotKey == "Score Distribution"
        assert data_object.secondaryValue is None
        assert data_object.secondaryValueColorIndex is None


class TestBarChartWidgetDataValueObjectType:
    """Test BarChartWidgetDataValueObjectType enum"""

    def test_enum_values(self):
        """Test BarChartWidgetDataValueObjectType enum values"""
        # Test all enum values exist
        assert BarChartWidgetDataValueObjectType.number.name == "number"
        assert BarChartWidgetDataValueObjectType.string.name == "string"
        assert BarChartWidgetDataValueObjectType.range.name == "range"
        assert BarChartWidgetDataValueObjectType.total.name == "total"

    def test_enum_usage(self):
        """Test using the enum in model creation"""
        data_object = BarChartWidgetDataKeysAndValuesObject(k="test_key", vType=BarChartWidgetDataValueObjectType.number)
        assert data_object.vType == BarChartWidgetDataValueObjectType.number

        # Test with different enum value
        data_object2 = BarChartWidgetDataKeysAndValuesObject(k="another_key", vType=BarChartWidgetDataValueObjectType.range)
        assert data_object2.vType == BarChartWidgetDataValueObjectType.range


class TestDashboardPerformanceSlice:
    """Test DashboardPerformanceSlice model"""

    def test_init(self):
        """Test DashboardPerformanceSlice initialization"""
        bar_widget = BarChartWidget(id="bar_widget_123", title="Performance Chart")

        keys_and_values = [BarChartWidgetDataKeysAndValuesObject(k="accuracy", v="92.5", vType=BarChartWidgetDataValueObjectType.number)]
        bar_data = BarChartWidgetData(keysAndValues=keys_and_values, performanceImpactValue=0.925)

        performance_slice = DashboardPerformanceSlice(
            id="slice_123",
            evalMetricMin=0.0,
            evalMetricMax=1.0,
            performanceMetric=PerformanceMetric.accuracy,
            metricValue="92.5%",
            metricValueType=BarChartWidgetDataValueObjectType.string,
            metricValueColorIndex=2,
            metricValueKey="Bank of America",
            metricValueKeyType=BarChartWidgetDataValueObjectType.string,
            widget=bar_widget,
            barChartBarNode=bar_data,
        )

        assert performance_slice.id == "slice_123"
        assert performance_slice.evalMetricMin == 0.0
        assert performance_slice.evalMetricMax == 1.0
        assert performance_slice.performanceMetric == PerformanceMetric.accuracy
        assert performance_slice.metricValue == "92.5%"
        assert performance_slice.metricValueType == BarChartWidgetDataValueObjectType.string
        assert performance_slice.metricValueColorIndex == 2
        assert performance_slice.metricValueKey == "Bank of America"
        assert performance_slice.metricValueKeyType == BarChartWidgetDataValueObjectType.string
        assert performance_slice.widget.id == "bar_widget_123"
        assert performance_slice.barChartBarNode.performanceImpactValue == 0.925

    def test_required_id_only(self):
        """Test DashboardPerformanceSlice with only required id field"""
        performance_slice = DashboardPerformanceSlice(id="slice_456")

        assert performance_slice.id == "slice_456"
        assert performance_slice.evalMetricMin is None
        assert performance_slice.evalMetricMax is None
        assert performance_slice.performanceMetric is None
        assert performance_slice.metricValue is None
        assert performance_slice.widget is None
        assert performance_slice.barChartBarNode is None

    def test_optional_fields(self):
        """Test DashboardPerformanceSlice with partial optional fields"""
        performance_slice = DashboardPerformanceSlice(
            id="slice_789",
            evalMetricMin=0.2,
            performanceMetric=PerformanceMetric.precision,
            metricValueColorIndex=5,
        )

        assert performance_slice.id == "slice_789"
        assert performance_slice.evalMetricMin == 0.2
        assert performance_slice.evalMetricMax is None
        assert performance_slice.performanceMetric == PerformanceMetric.precision
        assert performance_slice.metricValueColorIndex == 5
        assert performance_slice.metricValueKey is None

    def test_dashboard_performance_slice_initialization(self):
        """Test DashboardPerformanceSlice initialization"""
        slice_data = {
            "id": "slice1",
            "evalMetricMin": 0.0,
            "evalMetricMax": 1.0,
            "performanceMetric": "accuracy",
            "metricValue": "0.85",
            "metricValueType": "number",
            "metricValueColorIndex": 1,
            "metricValueKey": "class_a",
            "metricValueKeyType": "string",
        }
        dashboard_slice = DashboardPerformanceSlice(**slice_data)
        assert dashboard_slice.id == "slice1"
        assert dashboard_slice.evalMetricMin == 0.0
        assert dashboard_slice.evalMetricMax == 1.0
        assert dashboard_slice.performanceMetric == PerformanceMetric.accuracy
        assert dashboard_slice.metricValue == "0.85"


class TestDashboardMutationInputModels:
    def test_create_dashboard_mutation_input(self):
        """Test CreateDashboardMutationInput initialization"""
        input_data = {
            "name": "Test Dashboard",
            "spaceId": "space123",
            "clientMutationId": "mutation123",
        }
        mutation_input = CreateDashboardMutationInput(**input_data)
        assert mutation_input.name == "Test Dashboard"
        assert mutation_input.spaceId == "space123"
        assert mutation_input.clientMutationId == "mutation123"

    def test_create_dashboard_mutation_input_minimal(self):
        """Test CreateDashboardMutationInput with minimal fields"""
        input_data = {"name": "Test Dashboard", "spaceId": "space123"}
        mutation_input = CreateDashboardMutationInput(**input_data)
        assert mutation_input.name == "Test Dashboard"
        assert mutation_input.spaceId == "space123"
        assert mutation_input.clientMutationId is None

    def test_line_chart_plot_input(self):
        """Test LineChartPlotInput initialization"""
        plot_data = {
            "modelId": "model123",
            "modelVersionIds": ["v1", "v2"],
            "modelEnvironmentName": ModelEnvironment.production,
            "title": "Model Volume",
            "position": 0,
        }
        plot_input = LineChartPlotInput(**plot_data)
        assert plot_input.modelId == "model123"
        assert plot_input.modelVersionIds == ["v1", "v2"]
        assert plot_input.modelEnvironmentName == ModelEnvironment.production
        assert plot_input.title == "Model Volume"
        assert plot_input.position == 0

    def test_line_chart_plot_input_minimal(self):
        """Test LineChartPlotInput with minimal fields"""
        plot_data = {"modelId": "model123"}
        plot_input = LineChartPlotInput(**plot_data)
        assert plot_input.modelId == "model123"
        assert plot_input.modelVersionIds is None
        assert plot_input.modelEnvironmentName is None
        assert plot_input.title is None
        assert plot_input.position is None

    def test_create_line_chart_widget_mutation_input(self):
        """Test CreateLineChartWidgetMutationInput initialization"""
        plots = [
            {"modelId": "model123", "title": "Model A Volume", "position": 0},
            {"modelId": "model456", "title": "Model B Volume", "position": 1},
        ]
        input_data = {
            "title": "Model Volumes",
            "dashboardId": "dashboard123",
            "timeSeriesMetricType": "modelDataMetric",
            "plots": [LineChartPlotInput(**plot) for plot in plots],
            "gridPosition": [0, 0, 6, 4],
            "clientMutationId": "mutation123",
        }
        mutation_input = CreateLineChartWidgetMutationInput(**input_data)
        assert mutation_input.title == "Model Volumes"
        assert mutation_input.dashboardId == "dashboard123"
        assert mutation_input.timeSeriesMetricType == "modelDataMetric"
        assert len(mutation_input.plots) == 2
        assert mutation_input.plots[0].modelId == "model123"
        assert mutation_input.plots[1].modelId == "model456"
        assert mutation_input.gridPosition == [0, 0, 6, 4]
        assert mutation_input.clientMutationId == "mutation123"

    def test_create_line_chart_widget_mutation_input_minimal(self):
        """Test CreateLineChartWidgetMutationInput with minimal fields"""
        plots = [{"modelId": "model123"}]
        input_data = {
            "title": "Model Volume",
            "dashboardId": "dashboard123",
            "plots": [LineChartPlotInput(**plot) for plot in plots],
        }
        mutation_input = CreateLineChartWidgetMutationInput(**input_data)
        assert mutation_input.title == "Model Volume"
        assert mutation_input.dashboardId == "dashboard123"
        assert mutation_input.timeSeriesMetricType == "modelDataMetric"  # default value
        assert len(mutation_input.plots) == 1
        assert mutation_input.gridPosition is None
        assert mutation_input.clientMutationId is None
