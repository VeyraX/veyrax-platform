from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
from typing import Generic, TypeVar, Optional, Type
from pydantic_core import core_schema
from pydantic.json_schema import JsonSchemaValue


class FileReference(BaseModel):
    """Common file representation for OpenAI schemas"""
    file_name: str  # Original filename
    file_url: Optional[HttpUrl] = None  # File storage URL
    file_base64: Optional[str] = None  # Base64 content (optional for small files)
    content_type: str  # MIME type (e.g., "image/png", "application/pdf")
    size_bytes: Optional[int] = None  # File size in bytes



T = TypeVar("T", bound=str)  # Restrict type to strings

class DateStr(Generic[T]):
    """Generic DateStr wrapper that enforces a specific format and provides a valid Pydantic schema."""
    
    def __class_getitem__(cls, format: str) -> Type[str]:
        """Dynamically generate a validated string subclass with a Pydantic schema."""
        
        class _DateStr(str):
            """Inner class that validates and represents a date string."""
            
            @classmethod
            def __get_validators__(cls):
                yield cls.validate

            @classmethod
            def validate(cls, value: str) -> str:
                """Validates that the string follows the given date format."""
                if not isinstance(value, str):
                    raise TypeError(f"Expected a string, got {type(value).__name__}")
                
                try:
                    datetime.strptime(value, format)  # Validate format
                    return value
                except ValueError:
                    raise ValueError(f"Date must be in format '{format}', got: {value}")

            @classmethod
            def __get_pydantic_core_schema__(cls, source_type, handler) -> core_schema.CoreSchema:
                """Generate a valid Pydantic schema with description."""
                return core_schema.str_schema(metadata={"description": f"Date in format: {format}"})

            @classmethod
            def __get_pydantic_json_schema__(cls, core_schema: core_schema.CoreSchema, handler) -> JsonSchemaValue:
                """Ensure OpenAI schema includes the correct description."""
                json_schema = handler(core_schema)  # Get base JSON schema
                json_schema["description"] = f"Date in format: {format}"  # Inject description
                return json_schema

        return _DateStr  # ✅ Return a valid subclass of str

# # ✅ Now, you can use it directly in a Pydantic model!
# class MyModel(BaseModel):
#     date: DateStr["%Y-%m-%d"]  # ✅ Automatically validates and generates schema

# # 🔥 Test the model
# data = MyModel(date="2025-02-27")
# print(MyModel.model_json_schema())  

# import openai

# res = openai.pydantic_function_tool(MyModel)
# print(res)