from .sdk import SubsetsClient

from .models.common import (
    ChartType,
    ChartTags,
)
# Bar chart models
from .models.bar import (
    BarPattern,
    BarChartDatasetConfig,
    BarChartMetadata,
    BarChartData,
    BarChart
)

# Line chart models
from .models.line import (
    LineStyle,
    LineChartDatasetConfig,
    LineChartMetadata,
    LineChartData,
    LineChart
)

# Map chart models
from .models.map import (
    MapChartMetadata,
    MapChartData,
    MapChart
)

# Counter chart models
from .models.counter import (
    GradientStop,
    GradientDirection,
    BackgroundEffect,
    CounterChartMetadata,
    CounterChartData,
    CounterChart
)

# Scatterplot models
from .models.scatter import (
    ScatterplotMarkerStyle,
    ScatterplotDatasetConfig,
    ScatterplotChartMetadata,
    ScatterplotChartData,
    ScatterplotChart
)

# Table models
from .models.table import (
    ColumnConfig,
    TableChartMetadata,
    TableChartData,
    TableChart
)

# Misc utilities and types
from .models.misc import Color

# Time/Date types
from .models.time import (
    ISODateTime,
    ISODate,
    ISOWeek,
    Month,
    Quarter,
    Year,
    DateType
)

# Chart parsing and type unions
from .models.chart import (
    parse_chart,
    parse_chart_metadata,
    Chart,
    ChartData,
    ChartMetadata
)

# Update models
from .models.update import (
    BarChartMetadataUpdate,
    LineChartMetadataUpdate,
    MapChartMetadataUpdate,
    CounterChartMetadataUpdate,
    ScatterplotChartMetadataUpdate,
    TableChartMetadataUpdate,
    ChartUpdate
)


__version__ = "0.1.0"

__all__ = [
    # SDK
    "SubsetsClient",

    ## Common
    "ChartType",
    "ChartTags",
    
    # Bar Chart
    "BarPattern",
    "BarChartDatasetConfig",
    "BarChartAxisConfig",
    "BarChartYAxisConfig",
    "BarChartMetadata",
    "BarChartData",
    "BarChart",
    
    # Line Chart
    "LineStyle",
    "LineChartDatasetConfig",
    "LineChartAxisConfig",
    "LineChartYAxisConfig",
    "LineChartMetadata",
    "LineChartData",
    "LineChart",
    
    # Map Chart
    "MapChartMetadata",
    "MapChartData",
    "MapChart",
    
    # Counter Chart
    "GradientStop",
    "GradientDirection",
    "BackgroundEffect",
    "CounterChartMetadata",
    "CounterChartData",
    "CounterChart",
    
    # Scatterplot
    "ScatterplotMarkerStyle",
    "ScatterplotDatasetConfig",
    "ScatterplotAxisConfig",
    "ScatterplotChartMetadata",
    "ScatterplotChartData",
    "ScatterplotChart",
    
    # Table
    "ColumnConfig",
    "TableChartMetadata",
    "TableChartData",
    "TableChart",
    
    # Misc
    "Color",
    
    # Time/Date
    "ISODateTime",
    "ISODate",
    "ISOWeek",
    "Month",
    "Quarter",
    "Year",
    "DateType",
    
    "parse_chart",
    "parse_chart_metadata",
    "Chart",
    "ChartData",
    "ChartMetadata"
    
    # Updates
    "BarChartMetadataUpdate",
    "LineChartMetadataUpdate",
    "MapChartMetadataUpdate",
    "CounterChartMetadataUpdate",
    "ScatterplotChartMetadataUpdate",
    "TableChartMetadataUpdate",
    "ChartUpdate"
]