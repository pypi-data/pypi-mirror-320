from typing import List, Union, Optional, Any
from pydantic import BaseModel
from wildcard_core.tool_registry.tools.rest_api.types import ParameterSchema, ParameterSchemaRef, ParameterSchemaType, PrimitiveParameterSchema, ObjectParameterSchema, ArrayParameterSchema
from wildcard_core.tool_registry.tools.rest_api.types.api_types import PrimitiveTypesList

def merge_allof_schemas(
    schemas: List[Union['ParameterSchema', List['ParameterSchema']]]
) -> Union['ParameterSchema', List['ParameterSchema']]:
    """
    Merge schemas from allOf, handling nested oneOf/anyOf arrays.
    
    The logic treats:
    - Outer list elements as AND conditions (all must be satisfied)
    - Inner list elements (from oneOf/anyOf) as OR conditions (any can be satisfied)
    
    Examples:
    [A, B, C] -> Single merged schema combining all constraints
    [A, [B, C], D] -> [ABD, ACD] (distributing the OR condition)
    [A, [B, C], [D, E]] -> [ABD, ABE, ACD, ACE] (distributing both OR conditions)
    """
    # Start with an empty "combination set"
    result_combinations = [[]]

    for schema_or_array in schemas:
        if isinstance(schema_or_array, list):
            # Handle OR condition (oneOf/anyOf)
            new_combinations = []
            for existing_combo in result_combinations:
                for option in schema_or_array:
                    new_combinations.append(existing_combo + [option])
            result_combinations = new_combinations
        else:
            # Handle AND condition (single schema)
            # IMPORTANT: create new lists rather than mutating in place
            result_combinations = [combo + [schema_or_array] for combo in result_combinations]
    
    # Now merge each combination into a single schema
    merged_results = []
    for combination in result_combinations:
        merged = merge_schema_list(combination)
        merged_results.append(merged)
    
    # If there's only one result, return it directly, otherwise return the list
    return merged_results[0] if len(merged_results) == 1 else merged_results

def merge_schema_list(schemas: List['ParameterSchema']) -> 'ParameterSchema':
    """
    Merge a list of schemas into a single schema, handling different types appropriately.
    """
    if not schemas:
        raise ValueError("Cannot merge empty schema list")
    
    # Start with the first schema as base
    result = schemas[0]
    
    # Merge each subsequent schema
    for schema in schemas[1:]:
        result = merge_two_schemas(result, schema)
    
    return result

def merge_two_schemas(schema1: 'ParameterSchema', schema2: 'ParameterSchema') -> 'ParameterSchema':
    """
    Merge two schemas, handling different type combinations appropriately.
    """
    # Handle circular references
    if isinstance(schema1, ParameterSchemaRef) or isinstance(schema2, ParameterSchemaRef):
        return schema1 if isinstance(schema1, ParameterSchemaRef) else schema2

    # If both are objects, merge their properties
    if schema1.type == ParameterSchemaType.OBJECT and schema2.type == ParameterSchemaType.OBJECT:
        return merge_object_schemas(schema1, schema2)
    
    # If both are arrays, merge their item definitions
    if schema1.type == ParameterSchemaType.ARRAY and schema2.type == ParameterSchemaType.ARRAY:
        return merge_array_schemas(schema1, schema2)
    
    # If both are primitives of the same type, merge their constraints
    if schema1.type == schema2.type and schema1.type in PrimitiveTypesList:
        return merge_primitive_schemas(schema1, schema2)
    
    # Handle type mismatches by creating an anyOf schema
    return [schema1, schema2]

def merge_object_schemas(schema1: ObjectParameterSchema, schema2: ObjectParameterSchema) -> ObjectParameterSchema:
    """Merge two object schemas."""
    merged_properties = {**schema1.properties}
    
    for key, prop2 in schema2.properties.items():
        if key in merged_properties:
            merged_prop = merge_two_schemas(merged_properties[key], prop2)
            if isinstance(merged_prop, list):
                # If property merge resulted in anyOf, store it appropriately
                merged_properties[key] = merged_prop[0]  # Take first option as default
            else:
                merged_properties[key] = merged_prop
        else:
            merged_properties[key] = prop2
    
    return ObjectParameterSchema(
        type=ParameterSchemaType.OBJECT,
        properties=merged_properties,
        required=list(set(schema1.required + schema2.required)),
        description=merge_descriptions(schema1.description, schema2.description),
        example=schema2.example or schema1.example,
        discriminator=schema2.discriminator or schema1.discriminator
    )

def merge_array_schemas(schema1: ArrayParameterSchema, schema2: ArrayParameterSchema) -> ArrayParameterSchema:
    """Merge two array schemas."""
    merged_items = (
        merge_two_schemas(schema1.items, schema2.items)
        if schema1.items and schema2.items
        else schema2.items or schema1.items
    )
    
    # If items merged into anyOf, handle appropriately
    if isinstance(merged_items, list):
        merged_items = merged_items[0]  # Take first option as default
    
    return ArrayParameterSchema(
        type=ParameterSchemaType.ARRAY,
        items=merged_items,
        description=merge_descriptions(schema1.description, schema2.description),
        example=schema2.example or schema1.example
    )

def merge_primitive_schemas(schema1: PrimitiveParameterSchema, schema2: PrimitiveParameterSchema) -> PrimitiveParameterSchema:
    """Merge two primitive schemas."""
    return PrimitiveParameterSchema(
        type=schema1.type,
        description=merge_descriptions(schema1.description, schema2.description),
        format=schema2.format or schema1.format,
        example=schema2.example or schema1.example,
        enum=merge_enums(schema1.enum, schema2.enum),
        required=schema1.required or schema2.required
    )

def merge_descriptions(desc1: Optional[str], desc2: Optional[str]) -> Optional[str]:
    """Merge two descriptions."""
    if desc1 and desc2:
        return f"{desc1}\n{desc2}"
    return desc2 or desc1

def merge_enums(enum1: Optional[List[Any]], enum2: Optional[List[Any]]) -> Optional[List[Any]]:
    """Merge enum values, taking intersection if both exist."""
    if enum1 and enum2:
        return list(set(enum1) & set(enum2))
    return enum2 or enum1