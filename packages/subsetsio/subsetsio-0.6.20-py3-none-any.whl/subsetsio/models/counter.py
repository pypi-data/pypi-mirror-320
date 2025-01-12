from pydantic import BaseModel, Field, GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema
from pydantic.json_schema import JsonSchemaValue
from typing import List, Literal, Optional, Any
from .common import BaseChartMetadata, ChartType, ChartTags
from .misc import Color
from enum import Enum

class GradientStop(BaseModel):
    color: Color
    position: float = Field(ge=0, le=1, description="Position of the color stop (0-1)")
    opacity: float = Field(default=1.0, ge=0, le=1)

class GradientDirection(str, Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    DIAGONAL = "diagonal"
    RADIAL = "radial"

class BackgroundEffect(BaseModel):
    gradient_stops: List[GradientStop] = Field(min_length=2, max_length=4)
    direction: GradientDirection = Field(default=GradientDirection.VERTICAL)
    blur_radius: float = Field(default=0, ge=0, le=100, description="Blur effect radius in pixels")

class CounterChartMetadata(BaseChartMetadata):
    type: Literal[ChartType.COUNTER]
    text_color: Color = Field(default="#000000")
    background_color: Color = Field(default="#FFFFFF")
    background_effect: Optional[BackgroundEffect] = None
    prefix: Optional[str] = None
    postfix: Optional[str] = None
    value_color: Color = Field(default="#000000")
    prefix_color: Color = Field(default="#000000")
    postfix_color: Color = Field(default="#000000")

    @classmethod
    def validate_affix(cls, v):
        if v is not None and len(v.strip()) == 0:
            raise ValueError("Prefix/postfix cannot be empty or just whitespace")
        return v

class CounterChartData(float):
    """A float type with counter chart data validation"""
    
    def __new__(cls, value):
        # First validate, then create
        cls.validate_data(value)
        return float.__new__(cls, value)
    
    @classmethod
    def validate_data(cls, value) -> None:
        if not isinstance(value, (int, float, str)):
            raise ValueError("Value must be a number or numeric string")
        
        try:
            float_value = float(value)
        except ValueError:
            raise ValueError("Could not convert value to float")
        
        if not isinstance(float_value, float):
            raise ValueError("Value must be convertible to float")
    
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.float_schema(),
            python_schema=core_schema.union_schema(
                choices=[
                    core_schema.is_instance_schema(cls),
                    core_schema.float_schema(),
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                function=lambda x: float(x),
                return_schema=core_schema.float_schema(),
                when_used='json'
            )
        )
    
    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        _core_schema: CoreSchema,
        _handler: GetCoreSchemaHandler,
    ) -> JsonSchemaValue:
        return {"type": "number"}

class CounterChart(BaseModel):
    metadata: CounterChartMetadata
    data: CounterChartData
    is_draft: bool = False
    tags: Optional[ChartTags] = None

