from wildcard_core.tool_registry.tools.utils.helpers import is_base64_urlsafe
import base64
from typing import Any, Dict, Union
from wildcard_core.tool_registry.tools.rest_api.types.api_types import (
    ObjectParameterSchema,
    PrimitiveParameterSchema,
    ArrayParameterSchema,
    ParameterSchema,
)

def validate_and_process_body_data(
    processed_kwargs: Dict[str, Any],
    body_schema: ParameterSchema,
    data: Dict[str, Any]
) -> None:
    """
    Recursively validates and processes the processed_kwargs based on the body_schema.
    Populates the data dictionary with validated and appropriately formatted values.

    Args:
        processed_kwargs (Dict[str, Any]): The input parameters to validate and process.
        body_schema (ParameterSchema): The schema defining the structure and types of the body.
        data (Dict[str, Any]): The dictionary to populate with validated data.

    Raises:
        ValueError: If validation fails or an unsupported schema type is encountered.
    """
    if isinstance(body_schema, PrimitiveParameterSchema):
        _validate_and_process_primitive(processed_kwargs, body_schema, data)
    elif isinstance(body_schema, ObjectParameterSchema):
        _validate_and_process_object(processed_kwargs, body_schema, data)
    elif isinstance(body_schema, ArrayParameterSchema):
        _validate_and_process_array(processed_kwargs, body_schema, data)
    else:
        raise ValueError("Unsupported body schema type.")

def _validate_and_process_primitive(
    processed_kwargs: Any,
    schema: PrimitiveParameterSchema,
    data: Dict[str, Any]
) -> None:
    """
    Validates and processes a primitive type.

    Args:
        processed_kwargs (Any): The value to validate and process.
        schema (PrimitiveParameterSchema): The primitive schema definition.
        data (Dict[str, Any]): The dictionary to populate with validated data.

    Raises:
        ValueError: If validation fails.
    """
    key = "value"  # Since it's a primitive, assign to a generic key
    _validate_primitive(key, processed_kwargs, schema.dict())
    
    value = processed_kwargs
    if schema.format == "byte":
        if not is_base64_urlsafe(value):
            value = base64.urlsafe_b64encode(value.encode('utf-8')).decode('utf-8')
    data[key] = value

def _validate_and_process_object(
    processed_kwargs: Dict[str, Any],
    schema: ObjectParameterSchema,
    data: Dict[str, Any]
) -> None:
    """
    Validates and processes an object type.
    """
    properties = schema.properties
    required_fields = schema.required or []

    for key, value in processed_kwargs.items():
        if key not in properties:
            raise ValueError(f"Unexpected field '{key}' in the request body.")

        field_schema = properties[key]
        field_data = {}
        validate_and_process_body_data(value, field_schema, field_data)
        data[key] = field_data.get("value", field_data)

    for field in required_fields:
        if field not in processed_kwargs:
            raise ValueError(f"Missing required field '{field}' in the request body.")

def _validate_and_process_array(
    processed_kwargs: Any,
    schema: ArrayParameterSchema,
    data: Dict[str, Any]
) -> None:
    """
    Validates and processes an array type.

    Args:
        processed_kwargs (Any): The array to validate and process.
        schema (ArrayParameterSchema): The array schema definition.
        data (Dict[str, Any]): The dictionary to populate with validated data.

    Raises:
        ValueError: If validation fails.
    """
    if not isinstance(processed_kwargs, list):
        raise ValueError(f"Expected array, got {type(processed_kwargs).__name__}")
    
    items_schema = schema.items
    data_key = "value"  # Assign processed array to a generic key
    data[data_key] = []

    for index, item in enumerate(processed_kwargs):
        item_data = {}
        validate_and_process_body_data(item, items_schema, item_data)
        data[data_key].append(item_data.get("value", item_data))

def _validate_primitive(key: str, value: Any, schema: Dict[str, Any]) -> None:
    """
    Validates a primitive value against its schema.

    Args:
        key (str): The name of the field being validated.
        value (Any): The value to validate.
        schema (Dict[str, Any]): The schema definition for the field.

    Raises:
        ValueError: If the value does not match the expected type.
    """
    expected_type = schema.get("type")
    type_mapping = {
        "string": str,
        "integer": int,
        "number": (int, float),
        "boolean": bool
    }

    if expected_type not in type_mapping:
        raise ValueError(f"Unsupported primitive type '{expected_type}' for field '{key}'.")

    if not isinstance(value, type_mapping[expected_type]):
        raise ValueError(
            f"Field '{key}' is expected to be of type '{expected_type}', but got '{type(value).__name__}'."
        )