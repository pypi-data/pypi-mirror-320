import unittest
from typing import List, Optional
from wildcard_core.tool_registry.tools.rest_api.types.api_types import (
    ParameterSchema,
    ParameterSchemaType,
    PrimitiveParameterSchema,
    ObjectParameterSchema,
    ArrayParameterSchema,
)
from wildcard_core.client.utils.parse_openapi import merge_allof_schemas

class TestSchemasMerge(unittest.TestCase):
    """Test cases for OpenAPI schema merging functionality."""

    def setUp(self):
        """Set up test schemas."""
        # Primitive schemas
        self.string_schema = PrimitiveParameterSchema(
            type=ParameterSchemaType.STRING,
            description="A string field",
            enum=["a", "b", "c"]
        )
        
        self.number_schema = PrimitiveParameterSchema(
            type=ParameterSchemaType.NUMBER,
            description="A number field",
            enum=[1, 2, 3]
        )
        
        self.boolean_schema = PrimitiveParameterSchema(
            type=ParameterSchemaType.BOOLEAN,
            description="A boolean field"
        )
        
        # Object schema
        self.object_schema = ObjectParameterSchema(
            type=ParameterSchemaType.OBJECT,
            properties={"key": self.string_schema},
            required=["key"],
            description="An object with a key"
        )
        
        # Array schema
        self.array_schema = ArrayParameterSchema(
            type=ParameterSchemaType.ARRAY,
            items=self.string_schema,
            description="An array of strings"
        )

    def test_merge_primitive_schemas(self):
        """Test merging primitive schemas with matching types."""
        schema1 = PrimitiveParameterSchema(
            type=ParameterSchemaType.STRING,
            enum=["a", "b", "c"],
            description="First schema"
        )
        schema2 = PrimitiveParameterSchema(
            type=ParameterSchemaType.STRING,
            enum=["b", "c", "d"],
            description="Second schema"
        )
        
        result = merge_allof_schemas([schema1, schema2])
        
        self.assertEqual(result.type, ParameterSchemaType.STRING)
        self.assertEqual(set(result.enum), {"b", "c"})
        self.assertIn("First schema", result.description)
        self.assertIn("Second schema", result.description)

    def test_merge_object_schemas(self):
        """Test merging object schemas."""
        schema1 = ObjectParameterSchema(
            type=ParameterSchemaType.OBJECT,
            properties={"name": self.string_schema},
            required=["name"]
        )
        schema2 = ObjectParameterSchema(
            type=ParameterSchemaType.OBJECT,
            properties={"age": self.number_schema},
            required=["age"]
        )
        
        result = merge_allof_schemas([schema1, schema2])
        
        self.assertEqual(result.type, ParameterSchemaType.OBJECT)
        self.assertIn("name", result.properties)
        self.assertIn("age", result.properties)
        self.assertEqual(set(result.required), {"name", "age"})

    def test_merge_array_schemas(self):
        """Test merging array schemas."""
        schema1 = ArrayParameterSchema(
            type=ParameterSchemaType.ARRAY,
            items=self.string_schema
        )
        schema2 = ArrayParameterSchema(
            type=ParameterSchemaType.ARRAY,
            items=self.string_schema
        )
        
        result = merge_allof_schemas([schema1, schema2])
        
        self.assertEqual(result.type, ParameterSchemaType.ARRAY)
        self.assertEqual(result.items.type, ParameterSchemaType.STRING)

    def test_merge_with_anyof(self):
        """Test merging schemas with anyOf conditions."""
        test_schemas = [
            self.string_schema,
            [self.number_schema, self.boolean_schema],
            self.object_schema
        ]
        
        result = merge_allof_schemas(test_schemas)
        
        # Should return a list of two schemas (one for each combination)
        self.assertIsInstance(result.schemas, list)
        self.assertEqual(len(result.schemas), 2)

    def test_complex_nested_merge(self):
        """Test merging complex nested schemas with multiple anyOf conditions."""
        test_schemas = [
            self.string_schema,
            [self.number_schema, self.boolean_schema],
            [self.object_schema, self.array_schema]
        ]
        
        result = merge_allof_schemas(test_schemas)
        
        # Should return a list of four schemas (all possible combinations)
        self.assertIsInstance(result.schemas, list)
        self.assertEqual(len(result.schemas), 4)

    def test_merge_conflicting_enums(self):
        """Test merging schemas with conflicting enum values."""
        schema1 = PrimitiveParameterSchema(
            type=ParameterSchemaType.STRING,
            enum=["a", "b"]
        )
        schema2 = PrimitiveParameterSchema(
            type=ParameterSchemaType.STRING,
            enum=["c", "d"]
        )
        
        with self.assertRaises(ValueError):
            merge_allof_schemas([schema1, schema2])

    def test_merge_different_types(self):
        """Test merging schemas of different types."""
        result = merge_allof_schemas([self.string_schema, self.number_schema])
        
        # Should return an AnyOf schema containing both types
        self.assertEqual(result.type, ParameterSchemaType.ANYOF)
        self.assertEqual(len(result.schemas), 2)
        self.assertEqual(result.schemas[0].type, ParameterSchemaType.STRING)
        self.assertEqual(result.schemas[1].type, ParameterSchemaType.NUMBER)

    def test_merge_nested_object_properties(self):
        """Test merging objects with nested properties."""
        nested_obj1 = ObjectParameterSchema(
            type=ParameterSchemaType.OBJECT,
            properties={
                "inner": ObjectParameterSchema(
                    type=ParameterSchemaType.OBJECT,
                    properties={"a": self.string_schema}
                )
            }
        )
        
        nested_obj2 = ObjectParameterSchema(
            type=ParameterSchemaType.OBJECT,
            properties={
                "inner": ObjectParameterSchema(
                    type=ParameterSchemaType.OBJECT,
                    properties={"b": self.number_schema}
                )
            }
        )
        
        result = merge_allof_schemas([nested_obj1, nested_obj2])
        
        self.assertEqual(result.type, ParameterSchemaType.OBJECT)
        self.assertIn("inner", result.properties)
        inner_props = result.properties["inner"].properties
        self.assertIn("a", inner_props)
        self.assertIn("b", inner_props)

    def test_empty_schema_list(self):
        """Test merging an empty list of schemas."""
        with self.assertRaises(ValueError):
            merge_allof_schemas([])

if __name__ == '__main__':
    unittest.main()
