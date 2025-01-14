from enum import Enum
from typing import List, Literal, Dict, Optional, Any
from pydantic import BaseModel, Field
from typing import Optional, Dict, Union, List, Literal, Any
from pydantic import GetCoreSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema, core_schema
from .common import BaseChartMetadata, BaseChartProperties, ChartType, NumericAxisConfig

class ScatterplotMarkerStyle(str, Enum):
    """Available marker styles for scatter points"""
    CIRCLE = "circle"
    SQUARE = "square"
    TRIANGLE = "triangle"

class ScatterplotDatasetConfig(BaseModel):
    """Configuration for each dataset in the scatter plot"""
    label: str = Field(..., min_length=1, max_length=100)
    marker_style: ScatterplotMarkerStyle = Field(default=ScatterplotMarkerStyle.CIRCLE)

class ScatterplotChartMetadata(BaseChartMetadata):
    """Metadata specific to scatter plots"""
    type: Literal[ChartType.SCATTERPLOT]
    dataset_configs: Optional[List[ScatterplotDatasetConfig]] = None
    x_axis: Optional[NumericAxisConfig] = None
    y_axis: Optional[NumericAxisConfig] = None
    correlation_coefficient_visible: bool = Field(default=False)

class ScatterplotChartData(List[List[Any]]):
    """A 2D list type with scatterplot data validation"""
    
    def __init__(self, data: List[List[Any]], *, metadata: Optional[ScatterplotChartMetadata] = None):
        self.validate_data(data)
        if metadata:
            self.validate_with_metadata(data, metadata)
        super().__init__(data)
    
    @classmethod
    def validate_data(cls, data: List[List[Any]]) -> None:
        if not data:
            return

        # Expected values per row: [label, x, y]
        expected_length = 3

        # Track points by label
        point_sets: Dict[str, int] = {}

        # Validate each row
        for i, row in enumerate(data):
            # Check row length
            if len(row) != expected_length:
                raise ValueError(f"Row {i} has {len(row)} values, expected {expected_length} (label, x, y)")
            
            # Validate label
            if not isinstance(row[0], str):
                raise ValueError(f"First element of row {i} must be a string label")
            
            # Track point for this label
            label = row[0]
            point_sets[label] = point_sets.get(label, 0) + 1

            # Validate x and y coordinates
            for j, value in enumerate(row[1:], 1):
                if value is not None and not isinstance(value, (int, float)):
                    raise ValueError(f"Value at row {i}, column {j} must be a number or None")

    @classmethod
    def validate_with_metadata(cls, data: List[List[Any]], metadata: ScatterplotChartMetadata) -> None:
        # Get configured dataset labels
        dataset_labels = {config.label for config in metadata.dataset_configs}

        # Get actual dataset labels from data
        data_labels = {row[0] for row in data}

        # Build error message for all validation issues
        errors = []
        
        # Check for missing datasets
        missing_datasets = dataset_labels - data_labels
        if missing_datasets:
            errors.append(f"Missing data points for datasets: {', '.join(missing_datasets)}")

        # Check for undefined datasets
        extra_datasets = data_labels - dataset_labels
        if extra_datasets:
            errors.append(f"Found data points for undefined datasets: {', '.join(extra_datasets)}")

        if errors:
            raise ValueError(". ".join(errors))

        # Validate log scale values
        for i, row in enumerate(data):
            if metadata.x_axis.log_scale and row[1] is not None:
                if row[1] <= 0:
                    errors.append(f"X values must be positive when using log scale (row {i})")
                    
            if metadata.y_axis.log_scale and row[2] is not None:
                if row[2] <= 0:
                    errors.append(f"Y values must be positive when using log scale (row {i})")

        if errors:
            raise ValueError(". ".join(errors))
    
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.list_schema(
                items_schema=core_schema.list_schema(
                    items_schema=core_schema.any_schema()
                )
            ),
            python_schema=core_schema.union_schema(
                choices=[
                    core_schema.is_instance_schema(cls),
                    core_schema.list_schema(
                        items_schema=core_schema.list_schema(
                            items_schema=core_schema.any_schema()
                        )
                    ),
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                function=lambda x: list(x),
                return_schema=core_schema.list_schema(
                    items_schema=core_schema.list_schema(
                        items_schema=core_schema.any_schema()
                    )
                ),
                when_used='json'
            )
        )
    
    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        _core_schema: CoreSchema,
        _handler: GetCoreSchemaHandler,
    ) -> JsonSchemaValue:
        return {
            "type": "array",
            "items": {
                "type": "array",
                "items": {"type": "any"}
            }
        }

class ScatterplotChart(BaseChartProperties):
    """Scatter plot model combining metadata and data"""
    metadata: ScatterplotChartMetadata
    data: ScatterplotChartData