from typing import List, Literal, Optional, Union, Any
from pydantic import BaseModel, Field, GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema
from pydantic.json_schema import JsonSchemaValue
from .common import BaseChartMetadata, ChartType, ChartTags

class ColumnConfig(BaseModel):
    label: str = Field(..., min_length=1, max_length=50)
    align: str = Field("left", pattern="^(left|center|right)$")
    width: Optional[int] = None
    format: Optional[str] = None

class TableChartMetadata(BaseChartMetadata):
    type: Literal[ChartType.TABLE]
    column_configs: List[ColumnConfig] = Field(
        ...,
        min_length=2,
        description="Configuration for each column in the data array"
    )
    striped: bool = Field(default=True)
    hoverable: bool = Field(default=True)
    page_size: Optional[int] = Field(default=10, ge=1)
    sortable: bool = Field(default=True)

class TableChartData(List[List[Any]]):
    """A 2D list type with table data validation"""
    
    def __init__(self, data: List[List[Any]], *, metadata: Optional[TableChartMetadata] = None):
        self.validate_data(data)
        if metadata:
            self.validate_with_metadata(data, metadata)
        super().__init__(data)
    
    @classmethod
    def validate_data(cls, data: List[List[Any]]) -> None:
        if not data:
            return

        # Check for consistent row lengths
        row_length = len(data[0])
        for i, row in enumerate(data):
            if len(row) != row_length:
                raise ValueError(f"Row {i} has {len(row)} values, expected {row_length} (must match first row)")

            # Validate value types
            for j, value in enumerate(row):
                if not isinstance(value, (str, int, float)):
                    raise ValueError(f"Value at row {i}, column {j} must be a string or number, got {type(value)}")

    @classmethod
    def validate_with_metadata(cls, data: List[List[Any]], metadata: TableChartMetadata) -> None:
        expected_columns = len(metadata.column_configs)
        actual_columns = len(data[0]) if data else 0

        if actual_columns != expected_columns:
            raise ValueError(
                f"Data has {actual_columns} columns but {expected_columns} column configs were provided"
            )
    
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

class TableChart(BaseModel):
    metadata: TableChartMetadata
    data: TableChartData
    is_draft: bool = False
    tags: Optional[ChartTags] = None

