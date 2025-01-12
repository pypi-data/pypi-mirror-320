from enum import Enum
from typing import List, Literal, Optional, Union, Any
from pydantic import BaseModel, Field, model_validator
from enum import Enum
from typing import Optional, Dict, Union, List, Literal, Any
from pydantic import GetCoreSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema, core_schema
from .common import BaseChartMetadata, BaseChartProperties, ChartType, Color, AxisConfig, NumericAxisConfig

class BarPattern(str, Enum):
    """Available patterns for bar fills"""
    SOLID = "solid"
    STRIPES = "stripes"
    DOTS = "dots"
    CROSSHATCH = "crosshatch"
    DIAGONAL = "diagonal"
    ZIGZAG = "zigzag"

class BarChartDatasetConfig(BaseModel):
    """Configuration for each dataset in the bar chart"""
    label: str = Field(..., min_length=1, max_length=100)
    color: Union[Color, List[Color]] = Field(default="#000000")
    pattern: Optional[BarPattern] = None

class BarChartMetadata(BaseChartMetadata):
    """Metadata specific to bar charts"""
    type: Literal[ChartType.BAR]
    dataset_configs: Optional[List[BarChartDatasetConfig]] = None
    x_axis: Optional[AxisConfig] = None
    y_axis: Optional[NumericAxisConfig] = None
    bar_width: float = Field(default=0.8, ge=0.1, le=1.0)
    stack_mode: Literal["none", "stack", "stack_100"] = Field(default="none")
    horizontal: bool = Field(default=False)
    rounded_corners: bool = Field(default=False)

class BarChartData(List[List[Any]]):
    """Bar chart data that can be used independently for updates"""
    
    def __init__(self, data: List[List[Any]], *, metadata_config_length: Optional[int] = None):
        # First validate, then initialize
        self.validate_data(data, metadata_config_length)
        super().__init__(data)
    
    @classmethod
    def validate_data(cls, data: List[List[Any]], metadata_config_length: Optional[int] = None) -> None:
        if not data:
            return
            
        if metadata_config_length is not None:
            expected_length = metadata_config_length + 1  # +1 for category
        else:
            expected_length = len(data[0]) if data else 0
        
        # Track categories for uniqueness
        categories = set()
        
        # Validate each row
        for i, row in enumerate(data):
            # Check row length
            # if len(row) != expected_length:
            #     raise ValueError(f"Row {i} has {len(row)} values, expected {expected_length}")
            
            # Validate category
            category = row[0]
            if not isinstance(category, str):
                raise ValueError(f"First element of row {i} must be a string category")
            
            if category in categories:
                raise ValueError(f"Duplicate category found: {category}")
            categories.add(category)

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
    
class BarChart(BaseChartProperties):
    """Bar chart model combining metadata and data"""
    metadata: BarChartMetadata
    data: BarChartData

    @model_validator(mode='after')
    def validate_metadata_data_match(self) -> 'BarChart':
        if not self.data:
            return self
            
        if self.metadata.dataset_configs is not None:
            expected_columns = len(self.metadata.dataset_configs) + 1  
            actual_columns = len(self.data[0])
            
            if actual_columns != expected_columns:
                raise ValueError(
                    f"Data has {actual_columns - 1} data columns but metadata has "
                    f"{expected_columns - 1} dataset configurations"
                )
        
        return self