from pydantic import BaseModel, Field, GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema
from pydantic.json_schema import JsonSchemaValue
from typing import List, Literal, Union, Any, Optional
from .common import BaseChartMetadata, ChartType, ChartTags
from .misc import Color

class MapChartMetadata(BaseChartMetadata):
    type: Literal[ChartType.MAP]
    low_value_color: Color = None
    high_value_color: Color = None

class MapChartData(List[List[Any]]):
    """A 2D list type with map chart data validation"""
    
    def __init__(self, data: List[List[Any]], *, metadata_config_length: Optional[int] = None):
        self.validate_data(data, metadata_config_length)
        super().__init__(data)
    
    @classmethod
    def validate_data(cls, data: List[List[Any]], metadata_config_length: Optional[int] = None) -> None:
        if not data:
            return

        # Track country codes for uniqueness
        country_codes = set()
        
        # Validate each row
        for i, point in enumerate(data):
            # Check row length
            if len(point) != 2:
                raise ValueError(f"Point {i} has {len(point)} values, expected 2 (country_code, value)")
            
            # Validate country code
            country_code = point[0]
            if not isinstance(country_code, str):
                raise ValueError(f"Country code at point {i} must be a string")
            if not (len(country_code) == 2 and country_code.isalpha() and country_code.isupper()):
                raise ValueError(f"Country code '{country_code}' must be a 2-letter uppercase code")
            
            if country_code in country_codes:
                raise ValueError(f"Duplicate country code found: {country_code}")
            country_codes.add(country_code)

            # Validate value
            value = point[1]
            if not isinstance(value, (int, float)):
                raise ValueError(f"Value at point {i} must be a number, got {type(value)}")
    
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

class MapChart(BaseModel):
    metadata: MapChartMetadata
    data: MapChartData
    is_draft: bool = False
    tags: Optional[ChartTags] = None

