from typing import Annotated, Union
from datetime import datetime
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema
import re

class ISODateTime(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: type | None, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(
                pattern=r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:[+-]\d{2}:\d{2}|Z)$'
            ),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(cls),
                core_schema.str_schema(
                    pattern=r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:[+-]\d{2}:\d{2}|Z)$'
                ),
            ]),
            serialization=core_schema.str_schema(),
        )

class ISODate(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: type | None, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(
                pattern=r'^\d{4}-\d{2}-\d{2}$'
            ),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(cls),
                core_schema.str_schema(
                    pattern=r'^\d{4}-\d{2}-\d{2}$'
                ),
            ]),
            serialization=core_schema.str_schema(),
        )

class ISOWeek(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: type | None, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(
                pattern=r'^\d{4}-W\d{2}$'
            ),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(cls),
                core_schema.str_schema(
                    pattern=r'^\d{4}-W\d{2}$'
                ),
            ]),
            serialization=core_schema.str_schema(),
        )

class Month(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: type | None, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(
                pattern=r'^\d{4}-\d{2}$'
            ),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(cls),
                core_schema.str_schema(
                    pattern=r'^\d{4}-\d{2}$'
                ),
            ]),
            serialization=core_schema.str_schema(),
        )

class Quarter(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: type | None, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(
                pattern=r'^\d{4}-Q[1-4]$'
            ),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(cls),
                core_schema.str_schema(
                    pattern=r'^\d{4}-Q[1-4]$'
                ),
            ]),
            serialization=core_schema.str_schema(),
        )

class Year(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: type | None, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(
                pattern=r'^\d{4}$'
            ),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(cls),
                core_schema.str_schema(
                    pattern=r'^\d{4}$'
                ),
            ]),
            serialization=core_schema.str_schema(),
        )

DateType = Union[ISODateTime, ISODate, ISOWeek, Month, Quarter, Year]