from typing import List, Optional, Union, Literal, Dict, Any, Annotated
from enum import Enum
from pydantic import BaseModel, Field

from wildcard_core.models import APIService

#
# Discriminator Model
#

class Discriminator(BaseModel):
    propertyName: str
    mapping: Optional[Dict[str, str]] = None

#
# Parameter and Response Models
#

class ParameterIn(str, Enum):
    QUERY = "query"
    HEADER = "header"
    PATH = "path"
    COOKIE = "cookie"
    BODY = "body"

class ParameterSchemaType(str, Enum):
    NULL = 'null'
    STRING = 'string'
    INTEGER = 'integer'
    NUMBER = 'number'
    FLOAT = 'float'
    BOOLEAN = 'boolean'
    ARRAY = 'array'
    OBJECT = 'object'
    CIRCULAR = 'circular'
    ALL_OF = 'allOf'
    ONE_OF = 'oneOf'
    ANY_OF = 'anyOf'
    
class ParameterSchemaRef(BaseModel):
    """A placeholder for a reference to another schema to handle circular references."""
    ref: str
    type: Literal[ParameterSchemaType.CIRCULAR]
    
PrimitiveTypes = Literal[
        ParameterSchemaType.NULL,
        ParameterSchemaType.STRING,
        ParameterSchemaType.INTEGER,
        ParameterSchemaType.FLOAT,
        ParameterSchemaType.BOOLEAN,
        ParameterSchemaType.NUMBER,
    ]

# Ensure this is updated if PrimitiveTypes is updated
# Use this for type checking in functions
PrimitiveTypesList = [
    ParameterSchemaType.NULL,
    ParameterSchemaType.STRING,
    ParameterSchemaType.INTEGER,
    ParameterSchemaType.FLOAT,
    ParameterSchemaType.BOOLEAN,
    ParameterSchemaType.NUMBER,
]

class PrimitiveParameterSchema(BaseModel):
    type: PrimitiveTypes
    format: Optional[str] = None
    description: Optional[str] = None
    example: Optional[Union[str, int, float, bool]] = None
    enum: Optional[List[Union[str, int, float, bool]]]
    required: Optional[bool] = False

class ArrayParameterSchema(BaseModel):
    type: Literal[ParameterSchemaType.ARRAY]
    items: 'ParameterSchema'
    description: Optional[str] = None
    example: Optional[List[Any]] = None

class ObjectParameterSchema(BaseModel):
    type: Literal[ParameterSchemaType.OBJECT]
    properties: Dict[str, Union['ParameterSchema', List['ParameterSchema']]]
    description: Optional[str] = None
    required: Optional[List[str]] = None
    example: Optional[Dict[str, Any]] = None
    discriminator: Optional[Discriminator] = None  # Added discriminator field

class AllOfParameterSchema(BaseModel):
    type: Literal[ParameterSchemaType.ALL_OF]
    allOf: List['ParameterSchema']
    description: Optional[str] = "I am an allOf schema. Merge all of my subschemas into a single schema and replace me with that schema."
    example: Optional[Any] = None
    examples: Optional[Dict[str, Any]] = None

class OneOfParameterSchema(BaseModel):
    type: Literal[ParameterSchemaType.ONE_OF]
    oneOf: List['ParameterSchema']
    description: Optional[str] = "I am a member of a oneOf schema. Choose one of me or my sibling subschemas and replace the oneOf schema with that schema. DO NOT KEEP THE ONEOF KEY."
    example: Optional[Any] = None
    examples: Optional[Dict[str, Any]] = None

class AnyOfParameterSchema(BaseModel):
    type: Literal[ParameterSchemaType.ANY_OF]
    anyOf: List['ParameterSchema']
    description: Optional[str] = "I am an anyOf schema. Choose from one or more of my subschemas and replace me with the chosen schemas."
    example: Optional[Any] = None
    examples: Optional[Dict[str, Any]] = None

ParameterSchema = Annotated[Union[
    PrimitiveParameterSchema,
    ArrayParameterSchema,
    ObjectParameterSchema,
    ParameterSchemaRef,
    AllOfParameterSchema,
    OneOfParameterSchema,
    AnyOfParameterSchema
], Field(discriminator='type')]

# Helper class to build ParameterSchema
class ParameterSchemaBuilder(BaseModel):
    schema_: ParameterSchema

class Parameter(BaseModel):
    description: Optional[str] = None
    in_: Annotated[ParameterIn, "Location of parameter"]
    name: str
    schema_: Union[ParameterSchema, List[ParameterSchema]]
    required: Optional[bool] = None

class ResponseContent(BaseModel):
    description: str
    content: Dict[str, Any]  # Can be refined based on specific content types

class Response(BaseModel):
    status_code: str
    description: str
    content: Optional[Dict[str, ResponseContent]] = None

class RequestBody(BaseModel):
    description: Optional[str] = None
    content: Dict[str, Any]  # Similar to ResponseContent, maps content types to schemas
    required: Optional[bool] = None

#
# Security Models
#

class SecuritySchemeType(str, Enum):
    API_KEY = "apiKey"
    HTTP = "http"
    OAUTH2 = "oauth2"
    OPENID_CONNECT = "openIdConnect"

class SecuritySchemeBase(BaseModel):
    type: SecuritySchemeType
    description: Optional[str] = None

    class Config:
        extra = 'forbid'
        use_enum_values = True

# API Key Security Scheme
class ApiKeySecurityScheme(SecuritySchemeBase):
    type: Literal[SecuritySchemeType.API_KEY]
    name: str
    in_: ParameterIn = Field(..., alias='in')

# HTTP Security Scheme
class HttpSecurityScheme(SecuritySchemeBase):
    type: Literal[SecuritySchemeType.HTTP]
    scheme: str
    bearerFormat: Optional[str] = None

# OAuth2 Flow Models
class AuthorizationCodeFlow(BaseModel):
    authorizationUrl: str
    tokenUrl: str
    scopes: Dict[str, str]

class ImplicitFlow(BaseModel):
    authorizationUrl: str
    scopes: Dict[str, str]

class PasswordFlow(BaseModel):
    tokenUrl: str
    scopes: Dict[str, str]

class ClientCredentialsFlow(BaseModel):
    tokenUrl: str
    scopes: Dict[str, str]

class OAuth2Flows(BaseModel):
    authorizationCode: Optional[AuthorizationCodeFlow] = None
    implicit: Optional[ImplicitFlow] = None
    password: Optional[PasswordFlow] = None
    clientCredentials: Optional[ClientCredentialsFlow] = None

class OAuth2SecurityScheme(SecuritySchemeBase):
    type: Literal[SecuritySchemeType.OAUTH2]
    flows: OAuth2Flows

# OpenID Connect Security Scheme
class OpenIdConnectSecurityScheme(SecuritySchemeBase):
    type: Literal[SecuritySchemeType.OPENID_CONNECT]
    openIdConnectUrl: str

# Security Scheme Union and Helper Classes
SecuritySchemeUnion = Annotated[
    Union[
        ApiKeySecurityScheme,
        HttpSecurityScheme, 
        OAuth2SecurityScheme,
        OpenIdConnectSecurityScheme
    ],
    Field(discriminator='type')
]

class SecuritySchemeBuilder(BaseModel):
    scheme: SecuritySchemeUnion

class SecurityRequirement(BaseModel):
    # The name keys should correspond to the names of the security schemes defined in SecuritySchemes
    # The list of scopes depends on the security scheme type
    requirements: Dict[str, List[str]]  # Adjusted for simplicity

#
# API Documentation Models
#

class Server(BaseModel):
    url: str
    description: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None  # Can be structured further if needed

class ExternalDocumentation(BaseModel):
    description: Optional[str] = None
    url: str

class APIInfo(BaseModel):
    title: str
    version: str
    description: Optional[str] = None
    termsOfService: Optional[str] = None
    contact: Optional[Dict[str, Any]] = None  # Can be structured further
    license: Optional[Dict[str, Any]] = None  # Can be structured further

class APITag(BaseModel):
    name: str
    description: Optional[str] = None
    externalDocs: Optional[ExternalDocumentation] = None

#
# Core API Schema Models
#
    
class EndpointSchema(BaseModel):
    endpoint_id: str
    path: str
    method: Literal["get", "post", "put", "delete", "patch", "options", "head"]
    description: Optional[str] = None
    parameters: Optional[List[Parameter]] = None
    requestBody: Optional[RequestBody] = None
    responses: Optional[Dict[str, Response]] = None  # Changed to List for consistency
    security: Optional[List[SecurityRequirement]] = None

class APISchema(BaseModel):
    id: APIService
    name: str
    description: Optional[str] = None
    base_url: Optional[str] = None
    endpoints: Optional[List[EndpointSchema]] = None
    version: Optional[str] = None
    securitySchemes: Optional[Dict[str, SecuritySchemeUnion]] = None
    tags: Optional[List[APITag]] = None
    servers: Optional[List[Server]] = None
    info: Optional[APIInfo] = None
    externalDocs: Optional[ExternalDocumentation] = None