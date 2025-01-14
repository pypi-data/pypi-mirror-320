from enum import Enum
from typing import List, Literal, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Literal, Optional, Union, Any
from pydantic import BaseModel, Field, model_validator
from enum import Enum
from typing import Optional, Dict, Union, List, Literal, Any
from pydantic import GetCoreSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema, core_schema
from .common import BaseChartMetadata, BaseChartProperties, ChartType, Color, AxisConfig, NumericAxisConfig


class LineStyle(str, Enum):
    """Available line styles for the chart"""
    SOLID = "solid"
    DASHED = "dashed"
    DOTTED = "dotted"

class LineChartDatasetConfig(BaseModel):
    """Configuration for each dataset in the line chart"""
    label: str = Field(..., min_length=1, max_length=100)
    line_style: LineStyle = Field(default=LineStyle.SOLID)
    color: Color = Field(default="#000000")
    point_size: int = Field(default=4, ge=2, le=10)


class LineChartMetadata(BaseChartMetadata):
    """Metadata specific to line charts"""
    type: Literal[ChartType.LINE]
    dataset_configs: Optional[List[LineChartDatasetConfig]] = None
    x_axis: Optional[AxisConfig] = None
    y_axis: Optional[NumericAxisConfig] = None
    connect_null_points: bool = Field(default=False)
    interpolation: Literal["linear", "smooth"] = Field(default="linear")
    stacked: bool = Field(default=False)

class LineChartData(List[List[Any]]):
    """A 2D list type with line chart data validation"""

    def __init__(self, data: List[List[Any]], *, metadata_config_length: Optional[int] = None):
        self.validate_data(data, metadata_config_length)
        super().__init__(data)
    
    @classmethod
    def validate_data(cls, data: List[List[Any]], metadata_config_length: Optional[int] = None) -> None:
        if not data:
            return
            
        # Determine expected length
        expected_datasets = metadata_config_length if metadata_config_length is not None else 1
        expected_length = expected_datasets + 1  # +1 for date
        
        # Track dates for ordering
        prev_date = None
        
        # Validate each row
        for i, row in enumerate(data):
            # Check row length
            if len(row) != expected_length:
                raise ValueError(f"Row {i} has {len(row)} values, expected {expected_length}")
            
            # Validate date
            date = row[0]
            # if not isinstance(date, (str, DateType)):
            #     raise ValueError(f"First element of row {i} must be a date")
            
            # Check date ordering
            if prev_date is not None and date < prev_date:
                raise ValueError(f"Dates must be in ascending order, found {date} after {prev_date}")
            prev_date = date

            # Validate values
            for j, value in enumerate(row[1:], 1):
                if value is not None and not isinstance(value, (int, float)):
                    raise ValueError(f"Value at row {i}, column {j} must be a number or None")
    
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

class LineChart(BaseChartProperties):
    """Line chart model combining metadata and data"""
    metadata: LineChartMetadata
    data: LineChartData