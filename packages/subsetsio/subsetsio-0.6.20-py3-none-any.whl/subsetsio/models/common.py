from enum import Enum
from typing import Optional, Dict, Union, List, Literal, Any
from pydantic import BaseModel, Field, HttpUrl
from pydantic import GetCoreSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema, core_schema
import re
import typing
from pydantic import BaseModel, Field
from pydantic import model_validator
import unicodedata

def validate_text(input_text: str, max_length: int, field_name: str, allow_newlines) -> str:
    """
    Validates text input for chart fields with reasonable Unicode support while maintaining security.
    
    Allows:
    - Common Unicode letters and numbers
    - Common punctuation and symbols
    - Mathematical symbols
    - Currency symbols
    - Diacritical marks
    - Common CJK characters
    
    Blocks:
    - Control characters
    - Private Use Areas
    - Unassigned code points
    - Potentially dangerous Unicode categories
    """
    if len(input_text) > max_length:
        raise ValueError(f"{field_name} exceeds the maximum allowed length of {max_length} characters.")
    
    if len(input_text.strip()) == 0:
        raise ValueError(f"{field_name} cannot be empty or just whitespace")
    
    # Block certain Unicode categories that could be used maliciously
    blocked_categories = {
        'Cc',  # Control
        'Cf',  # Format
        'Cs',  # Surrogate
        'Co',  # Private Use
        'Cn',  # Unassigned
    }
    
    # Additional blocked ranges (hex)
    blocked_ranges = [
        (0x2028, 0x2029),    # Line/paragraph separators
        (0x202A, 0x202E),    # Bidirectional formatting
        (0xFFF0, 0xFFFF),    # Specials
        (0xFFF9, 0xFFFB),    # Interlinear annotations
        (0xFEFF, 0xFEFF),    # Zero width no-break space
        (0x200B, 0x200F),    # Zero width spaces and direction marks
        (0x2060, 0x2064),    # Word joiner and invisible operators
    ]
    
    # Explicitly allow certain Unicode blocks that are useful for charts
    allowed_ranges = [
        (0x0020, 0x007E),    # Basic Latin
        (0x00A0, 0x00FF),    # Latin-1 Supplement (includes common symbols and diacritics)
        (0x0100, 0x017F),    # Latin Extended-A
        (0x0180, 0x024F),    # Latin Extended-B
        (0x0250, 0x02AF),    # IPA Extensions
        (0x02B0, 0x02FF),    # Spacing Modifier Letters (including ʻokina)
        (0x0300, 0x036F),    # Combining Diacritical Marks
        (0x0370, 0x03FF),    # Greek and Coptic
        (0x0400, 0x04FF),    # Cyrillic
        (0x0500, 0x052F),    # Cyrillic Supplement
        (0x0600, 0x06FF),    # Arabic
        (0x0900, 0x097F),    # Devanagari
        (0x0E00, 0x0E7F),    # Thai
        (0x1E00, 0x1EFF),    # Latin Extended Additional
        (0x2000, 0x206F),    # General Punctuation (excluding blocked items above)
        (0x2070, 0x209F),    # Superscripts and Subscripts
        (0x20A0, 0x20CF),    # Currency Symbols
        (0x2100, 0x214F),    # Letterlike Symbols
        (0x2150, 0x218F),    # Number Forms
        (0x2190, 0x21FF),    # Arrows
        (0x2200, 0x22FF),    # Mathematical Operators
        (0x2460, 0x24FF),    # Enclosed Alphanumerics
        (0x3000, 0x303F),    # CJK Symbols and Punctuation
        (0x3040, 0x309F),    # Hiragana
        (0x30A0, 0x30FF),    # Katakana
        (0x4E00, 0x9FFF),    # CJK Unified Ideographs (Common)
    ]
    
    if allow_newlines:
        allowed_ranges = [(0x000A, 0x000A), (0x000D, 0x000D)] + allowed_ranges

    for char in input_text:
        char_ord = ord(char)
        char_category = unicodedata.category(char)
        
        # Check if character is in blocked category
        if char_category in blocked_categories:
            raise ValueError(f"{field_name} contains invalid character: {char} (category {char_category})")
        
        # Check if character is in blocked range
        if any(start <= char_ord <= end for start, end in blocked_ranges):
            raise ValueError(f"{field_name} contains invalid character: {char}")
        
        # Check if character is in allowed range
        if not any(start <= char_ord <= end for start, end in allowed_ranges):
            raise ValueError(f"{field_name} contains invalid character: {char}")
            
    return input_text

class ChartType(str, Enum):
    """Types of supported charts"""
    BAR = "bar"
    LINE = "line"
    MAP = "map"
    COUNTER = "counter"
    SCATTERPLOT = "scatter"
    TABLE = "table"

class Color(str):
    """Validates hex colors with optional alpha"""
    
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: typing.Any,
        _handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("string required")
        
        if not re.match(r'^#[0-9a-fA-F]{6}([0-9a-fA-F]{2})?$', v):
            raise ValueError("invalid hex color format - must be #RRGGBB or #RRGGBBAA")
            
        return v

class Source(BaseModel):
    """Metadata about the data source"""
    name: str = Field(..., min_length=1, max_length=100)
    data_provider_url: HttpUrl
    integration_url: Optional[HttpUrl] = None
    license: Optional[str] = Field(None, min_length=1, max_length=100)
    
    def model_dump(self, **kwargs) -> Dict[str, Any]:
        dump = super().model_dump(**kwargs)
        dump['data_provider_url'] = str(dump['data_provider_url'])
        if dump.get('integration_url'):
            dump['integration_url'] = str(dump['integration_url'])
        return dump
    
    model_config = {
        'extra': 'forbid'
    }

class ChartTags(Dict[str, Union[str, List[str]]]):
    """Tags for charts with validation rules"""
    
    def __init__(self, tags: Dict[str, Union[str, List[str]]]):
        self.validate_tags(tags)
        super().__init__(tags)
    
    @classmethod
    def validate_tags(cls, tags: Dict[str, Any]) -> None:
        if len(tags) > 10:
            raise ValueError("Maximum of 10 tags allowed")

        key_pattern = re.compile(r'^[a-z0-9][a-z0-9-]*[a-z0-9]$')
        
        for key, value in tags.items():
            # Key validation
            if not 1 <= len(key) <= 32:
                raise ValueError(f"Tag key '{key}' must be between 1 and 32 characters")
            
            if not key_pattern.match(key):
                raise ValueError(f"Tag key '{key}' must be lowercase alphanumeric with hyphens, cannot start/end with hyphen")

            # Value validation
            values = [value] if isinstance(value, str) else value
            
            if not isinstance(values, (str, list)):
                raise ValueError(f"Tag value must be string or list of strings")

            for val in values:
                if not isinstance(val, str):
                    raise ValueError(f"Tag value must be string, got {type(val)}")
                
                if not 1 <= len(val) <= 64:
                    raise ValueError(f"Tag value '{val}' must be between 1 and 64 characters")
                
                if not all(c.isprintable() for c in val):
                    raise ValueError(f"Tag value '{val}' contains invalid characters")
    
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.dict_schema(
                keys_schema=core_schema.str_schema(),
                values_schema=core_schema.union_schema([
                    core_schema.str_schema(),
                    core_schema.list_schema(core_schema.str_schema())
                ])
            ),
            python_schema=core_schema.union_schema(
                choices=[
                    core_schema.is_instance_schema(cls),
                    core_schema.dict_schema(
                        keys_schema=core_schema.str_schema(),
                        values_schema=core_schema.union_schema([
                            core_schema.str_schema(),
                            core_schema.list_schema(core_schema.str_schema())
                        ])
                    ),
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                function=lambda x: dict(x),
                return_schema=core_schema.dict_schema(
                    keys_schema=core_schema.str_schema(),
                    values_schema=core_schema.union_schema([
                        core_schema.str_schema(),
                        core_schema.list_schema(core_schema.str_schema())
                    ])
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
            "type": "object",
            "maxProperties": 10,
            "propertyNames": {
                "type": "string",
                "pattern": "^[a-z0-9][a-z0-9-]*[a-z0-9]$",
                "minLength": 3,
                "maxLength": 32
            },
            "additionalProperties": {
                "oneOf": [
                    {"type": "string", "maxLength": 64},
                    {
                        "type": "array",
                        "items": {"type": "string", "maxLength": 64},
                        "uniqueItems": True
                    }
                ]
            }
        }

class BaseChartMetadata(BaseModel):
    model_config = {
        'extra': 'forbid'
    }

    type: ChartType
    title: str = Field(..., min_length=8, max_length=140)
    subtitle: Optional[str] = Field(None, min_length=3, max_length=140)
    description: Optional[str] = Field(None, min_length=8, max_length=2000)
    icon: Optional[HttpUrl] = None

    @model_validator(mode='before')
    def validate_fields(cls, values):
        if 'title' in values and values['title'] is not None:
            values['title'] = validate_text(values['title'], 140, 'title', allow_newlines=False)
        
        if 'description' in values and values['description'] is not None:
            values['description'] = validate_text(values['description'], 2000, 'description', allow_newlines=True)
            
        if 'subtitle' in values and values['subtitle'] is not None:
            values['subtitle'] = validate_text(values['subtitle'], 140, 'subtitle', allow_newlines=False)
            
        return values

class AxisConfig(BaseModel):
    """Base configuration for chart axes"""
    label: Optional[str] = Field(..., min_length=1, max_length=100)
    show_grid: bool = Field(default=True)
    show_line: bool = Field(default=True)

class NumericAxisConfig(AxisConfig):
    """Configuration for numeric axes with scale options"""
    min: Optional[float] = None
    max: Optional[float] = None  
    log_scale: bool = Field(default=False)

class BaseChartProperties(BaseModel):
    """Base properties shared by all charts"""
    metadata: BaseChartMetadata
    data: Any 
    is_draft: bool = Field(default=False)
    tags: Optional[ChartTags] = None
    source: Optional[Source] = None
    
    model_config = {
        'extra': 'forbid'
    }
