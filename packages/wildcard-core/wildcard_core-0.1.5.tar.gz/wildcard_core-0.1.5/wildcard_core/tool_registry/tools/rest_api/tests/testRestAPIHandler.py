import unittest
import requests
from unittest.mock import patch, Mock
from wildcard_core.tool_registry.tools.rest_api.RestAPIHandler import RestAPIHandler
from wildcard_core.tool_registry.tools.rest_api.types import APISchema, ParameterIn, AuthType

class TestRestAPIHandler(unittest.TestCase):
    def setUp(self):
        # Base schema with no authentication
        self.base_schema = APISchema(
            api_id='baseAction',
            api_name='Base Action',
            endpoint_id='base_endpoint',
            path='/base-endpoint',
            method='get',
            description='Base action description',
            parameters=[
                {
                    'in_': ParameterIn.QUERY,
                    'name': 'query_param',
                    'schema': {'type': 'string'},
                    'required': False,
                    'description': 'A query parameter'
                }
            ],
            responses={
                '200': {
                    'description': 'Successful response',
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'object',
                                'properties': {
                                    'success': {'type': 'boolean'}
                                }
                            }
                        }
                    }
                }
            },
            base_url='https://api.example.com',
            security=[],  # No security by default
            securitySchemes={}
        )
        
        # Authentication configurations
        self.auth_none = None

        self.auth_basic = {
            'type': AuthType.BASIC,
            'credentials': 'base64encodedcredentials'
        }
        
        self.auth_bearer = {
            'type': AuthType.BEARER,
            'token': 'test_bearer_token'
        }
        
        self.auth_api_key_header = {
            'type': AuthType.API_KEY,
            'key_value': 'test_api_key_header',
            'name': 'X-API-KEY',
            'in_': 'header'
        }
        
        self.auth_api_key_query = {
            'type': AuthType.API_KEY,
            'key_value': 'test_api_key_query',
            'name': 'api_key',
            'in_': 'query'
        }

        # HTTP methods to test
        self.methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']

    # Helper method to create schemas with different auth types and methods
    def create_schema(self, method: str, path: str, auth_scheme: str = 'none') -> APISchema:
        security = []
        security_schemes = {}
        if auth_scheme == 'basic':
            security = [{'basic_scheme': []}]
            security_schemes = {
                'basic_scheme': {
                    'type': AuthType.BASIC,
                    'scheme': 'basic'
                }
            }
        elif auth_scheme == 'bearer':
            security = [{'bearer_scheme': []}]
            security_schemes = {
                'bearer_scheme': {
                    'type': AuthType.BEARER,
                    'scheme': 'bearer',
                    'bearerFormat': 'JWT'
                }
            }
        elif auth_scheme == 'api_key_header':
            security = [{'api_key_scheme': []}]
            security_schemes = {
                'api_key_scheme': {
                    'type': AuthType.API_KEY,
                    'name': 'X-API-KEY',
                    'in_': 'header'
                }
            }
        elif auth_scheme == 'api_key_query':
            security = [{'api_key_scheme_query': []}]
            security_schemes = {
                'api_key_scheme_query': {
                    'type': AuthType.API_KEY,
                    'name': 'api_key',
                    'in_': 'query'
                }
            }

        return APISchema(
            api_id=f'{path.strip("/")}Action',
            api_name=f'{path.strip("/").capitalize()} Action',
            endpoint_id=f'{path.strip("/")}Endpoint',
            path=path,
            method=method.lower(),
            description=f'{method.upper()} {path} description',
            parameters=[
                {
                    'in_': ParameterIn.QUERY,
                    'name': 'query_param',
                    'schema': {'type': 'string'},
                    'required': False,
                    'description': 'A query parameter'
                },
                {
                    'in_': ParameterIn.BODY,
                    'name': 'body_param',
                    'schema': {'type': 'string'},
                    'required': False,
                    'description': 'A body parameter'
                },
                {
                    'in_': ParameterIn.HEADER,
                    'name': 'header_param',
                    'schema': {'type': 'string'},
                    'required': False,
                    'description': 'A header parameter'
                }
            ],
            responses={
                '200': {
                    'description': 'Successful response',
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'object',
                                'properties': {
                                    'success': {'type': 'boolean'}
                                }
                            }
                        }
                    }
                },
                '201': {
                    'description': 'Created',
                    'content': {
                        'application/json': {
                            'schema': {
                                'type': 'object',
                                'properties': {
                                    'created': {'type': 'boolean'}
                                }
                            }
                        }
                    }
                },
                '204': {
                    'description': 'No Content',
                    'content': {}
                }
            },
            base_url='https://api.example.com',
            security=security,
            securitySchemes=security_schemes
        )

    # Test cases for different HTTP methods and authentication types

    @patch('wildcard_core.tool_registry.tools.rest_api.RestAPIHandler.requests.request')
    async def test_execute_get_none_auth(self, mock_request):
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {'success': True}
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        # Create schema for GET with no auth
        schema = self.create_schema(method='GET', path='/get-endpoint', auth_scheme='none')

        handler = RestAPIHandler(
            name='GetHandlerNoAuth',
            action_id='get_handler_no_auth',
            schema=schema,
            description='GET handler with no authentication',
            base_url='https://api.example.com',
            auth=self.auth_none
        )

        # Execute
        response = await handler.execute(query_param='value1')

        # Assert
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], 'get')
        self.assertEqual(kwargs['url'], 'https://api.example.com/get-endpoint')
        self.assertEqual(kwargs['params'], {'query_param': 'value1'})
        self.assertEqual(kwargs['json'], {})
        self.assertNotIn('Authorization', kwargs['headers'])
        self.assertEqual(response, {'success': True})

    @patch('wildcard_core.tool_registry.tools.rest_api.RestAPIHandler.requests.request')
    async def test_execute_get_basic_auth(self, mock_request):
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {'success': True}
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        # Create schema for GET with Basic auth
        schema = self.create_schema(method='GET', path='/get-basic', auth_scheme='basic')

        handler = RestAPIHandler(
            name='GetHandlerBasicAuth',
            action_id='get_handler_basic_auth',
            schema=schema,
            description='GET handler with Basic authentication',
            base_url='https://api.example.com',
            auth=self.auth_basic
        )

        # Execute
        response = await handler.execute(query_param='value1')

        # Assert
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], 'get')
        self.assertEqual(kwargs['url'], 'https://api.example.com/get-basic')
        self.assertEqual(kwargs['params'], {'query_param': 'value1'})
        self.assertEqual(kwargs['json'], {})
        self.assertIn('Authorization', kwargs['headers'])
        self.assertEqual(kwargs['headers']['Authorization'], 'Basic base64encodedcredentials')
        self.assertEqual(response, {'success': True})

    @patch('wildcard_core.tool_registry.tools.rest_api.RestAPIHandler.requests.request')
    async def test_execute_get_bearer_auth_api_key_header(self, mock_request):
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {'success': True}
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        # Create schema for GET with Bearer auth
        schema = self.create_schema(method='GET', path='/get-bearer', auth_scheme='bearer')

        handler = RestAPIHandler(
            name='GetHandlerBearerAuth',
            action_id='get_handler_bearer_auth',
            schema=schema,
            description='GET handler with Bearer authentication',
            base_url='https://api.example.com',
            auth=self.auth_bearer
        )

        # Execute
        response = await handler.execute(query_param='value1')

        # Assert
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], 'get')
        self.assertEqual(kwargs['url'], 'https://api.example.com/get-bearer')
        self.assertEqual(kwargs['params'], {'query_param': 'value1'})
        self.assertEqual(kwargs['json'], {})
        self.assertIn('Authorization', kwargs['headers'])
        self.assertEqual(kwargs['headers']['Authorization'], 'Bearer test_bearer_token')
        self.assertEqual(response, {'success': True})

    @patch('wildcard_core.tool_registry.tools.rest_api.RestAPIHandler.requests.request')
    async def test_execute_get_api_key_header_auth(self, mock_request):
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {'success': True}
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        # Create schema for GET with API Key in header
        schema = self.create_schema(method='GET', path='/get-api-key-header', auth_scheme='api_key_header')

        handler = RestAPIHandler(
            name='GetHandlerAPIKeyHeader',
            action_id='get_handler_api_key_header',
            schema=schema,
            description='GET handler with API Key in header',
            base_url='https://api.example.com',
            auth=self.auth_api_key_header
        )

        # Execute
        response = await handler.execute(query_param='value1')

        # Assert
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], 'get')
        self.assertEqual(kwargs['url'], 'https://api.example.com/get-api-key-header')
        self.assertEqual(kwargs['params'], {'query_param': 'value1'})
        self.assertEqual(kwargs['json'], {})
        self.assertIn('X-API-KEY', kwargs['headers'])
        self.assertEqual(kwargs['headers']['X-API-KEY'], 'test_api_key_header')
        self.assertEqual(response, {'success': True})

    @patch('wildcard_core.tool_registry.tools.rest_api.RestAPIHandler.requests.request')
    async def test_execute_get_api_key_query_auth(self, mock_request):
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {'success': True}
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        # Create schema for GET with API Key in query
        schema = self.create_schema(method='GET', path='/get-api-key-query', auth_scheme='api_key_query')

        handler = RestAPIHandler(
            name='GetHandlerAPIKeyQuery',
            action_id='get_handler_api_key_query',
            schema=schema,
            description='GET handler with API Key in query parameters',
            base_url='https://api.example.com',
            auth=self.auth_api_key_query
        )

        # Execute
        response = await handler.execute(query_param='value1')

        # Assert
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], 'get')
        self.assertEqual(kwargs['url'], 'https://api.example.com/get-api-key-query')
        expected_params = {
            'query_param': 'value1',
            'api_key': 'test_api_key_query'
        }
        self.assertEqual(kwargs['params'], expected_params)
        self.assertEqual(kwargs['json'], {})
        self.assertNotIn('Authorization', kwargs['headers'])
        self.assertEqual(response, {'success': True})

    @patch('wildcard_core.tool_registry.tools.rest_api.RestAPIHandler.requests.request')
    async def test_execute_post_basic_auth(self, mock_request):
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {'created': True}
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        # Create schema for POST with Basic auth
        schema = self.create_schema(method='POST', path='/post-basic', auth_scheme='basic')

        handler = RestAPIHandler(
            name='PostHandlerBasicAuth',
            action_id='post_handler_basic_auth',
            schema=schema,
            description='POST handler with Basic authentication',
            base_url='https://api.example.com',
            auth=self.auth_basic
        )

        # Execute
        response = await handler.execute(body_param='value2')

        # Assert
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], 'post')
        self.assertEqual(kwargs['url'], 'https://api.example.com/post-basic')
        self.assertEqual(kwargs['params'], {})
        self.assertEqual(kwargs['json'], {'body_param': 'value2'})
        self.assertIn('Authorization', kwargs['headers'])
        self.assertEqual(kwargs['headers']['Authorization'], 'Basic base64encodedcredentials')
        self.assertEqual(response, {'created': True})

    @patch('wildcard_core.tool_registry.tools.rest_api.RestAPIHandler.requests.request')
    async def test_execute_post_bearer_auth(self, mock_request):
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {'created': True}
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        # Create schema for POST with Bearer auth
        schema = self.create_schema(method='POST', path='/post-bearer', auth_scheme='bearer')

        handler = RestAPIHandler(
            name='PostHandlerBearerAuth',
            action_id='post_handler_bearer_auth',
            schema=schema,
            description='POST handler with Bearer authentication',
            base_url='https://api.example.com',
            auth=self.auth_bearer
        )

        # Execute
        response = await handler.execute(body_param='value2')

        # Assert
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], 'post')
        self.assertEqual(kwargs['url'], 'https://api.example.com/post-bearer')
        self.assertEqual(kwargs['params'], {})
        self.assertEqual(kwargs['json'], {'body_param': 'value2'})
        self.assertIn('Authorization', kwargs['headers'])
        self.assertEqual(kwargs['headers']['Authorization'], 'Bearer test_bearer_token')
        self.assertEqual(response, {'created': True})

    @patch('wildcard_core.tool_registry.tools.rest_api.RestAPIHandler.requests.request')
    async def test_execute_put_none_auth(self, mock_request):
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {'updated': True}
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        # Create schema for PUT with no auth
        schema = self.create_schema(method='PUT', path='/put-endpoint', auth_scheme='none')

        handler = RestAPIHandler(
            name='PutHandlerNoAuth',
            action_id='put_handler_no_auth',
            schema=schema,
            description='PUT handler with no authentication',
            base_url='https://api.example.com',
            auth=self.auth_none
        )

        # Execute
        response = await handler.execute(body_param='value2')

        # Assert
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], 'put')
        self.assertEqual(kwargs['url'], 'https://api.example.com/put-endpoint')
        self.assertEqual(kwargs['params'], {})
        self.assertEqual(kwargs['json'], {'body_param': 'value2'})
        self.assertNotIn('Authorization', kwargs['headers'])
        self.assertEqual(response, {'updated': True})

    @patch('wildcard_core.tool_registry.tools.rest_api.RestAPIHandler.requests.request')
    async def test_execute_patch_api_key_header_auth(self, mock_request):
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {'patched': True}
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        # Create schema for PATCH with API Key in header
        schema = self.create_schema(method='PATCH', path='/patch-api-key-header', auth_scheme='api_key_header')

        handler = RestAPIHandler(
            name='PatchHandlerAPIKeyHeader',
            action_id='patch_handler_api_key_header',
            schema=schema,
            description='PATCH handler with API Key in header',
            base_url='https://api.example.com',
            auth=self.auth_api_key_header
        )

        # Execute
        response = await handler.execute(body_param='value2')

        # Assert
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], 'patch')
        self.assertEqual(kwargs['url'], 'https://api.example.com/patch-api-key-header')
        self.assertEqual(kwargs['params'], {})
        self.assertEqual(kwargs['json'], {'body_param': 'value2'})
        self.assertIn('X-API-KEY', kwargs['headers'])
        self.assertEqual(kwargs['headers']['X-API-KEY'], 'test_api_key_header')
        self.assertEqual(response, {'patched': True})

    @patch('wildcard_core.tool_registry.tools.rest_api.RestAPIHandler.requests.request')
    async def test_execute_patch_api_key_query_auth(self, mock_request):
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {'patched': True}
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        # Create schema for PATCH with API Key in query
        schema = self.create_schema(method='PATCH', path='/patch-api-key-query', auth_scheme='api_key_query')

        handler = RestAPIHandler(
            name='PatchHandlerAPIKeyQuery',
            action_id='patch_handler_api_key_query',
            schema=schema,
            description='PATCH handler with API Key in query parameters',
            base_url='https://api.example.com',
            auth=self.auth_api_key_query
        )

        # Execute with both body_param and query_param
        response = await handler.execute(body_param='value2', query_param='value1')

        # Assert
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], 'patch')
        self.assertEqual(kwargs['url'], 'https://api.example.com/patch-api-key-query')
        expected_params = {
            'query_param': 'value1',
            'api_key': 'test_api_key_query'
        }
        self.assertEqual(kwargs['params'], expected_params)
        self.assertEqual(kwargs['json'], {'body_param': 'value2'})
        self.assertNotIn('Authorization', kwargs['headers'])
        self.assertEqual(response, {'patched': True})

    @patch('wildcard_core.tool_registry.tools.rest_api.RestAPIHandler.requests.request')
    async def test_execute_all_methods_with_none_auth(self, mock_request):
        for method in self.methods:
            with self.subTest(method=method):
                # Setup mock response
                mock_response = Mock()
                expected_response = {'status': f'{method} success'}
                mock_response.json.return_value = expected_response
                mock_response.raise_for_status = Mock()
                mock_request.return_value = mock_response

                # Create schema for each method with no auth
                schema = self.create_schema(method=method, path=f'/{method.lower()}-endpoint', auth_scheme='none')

                handler = RestAPIHandler(
                    name=f'{method}HandlerNoAuth',
                    action_id=f'{method.lower()}_handler_no_auth',
                    schema=schema,
                    description=f'{method.upper()} handler with no authentication',
                    base_url='https://api.example.com',
                    auth=self.auth_none
                )

                # Execute
                if method in ['POST', 'PUT', 'PATCH', 'DELETE']:
                    response = await handler.execute(body_param='value2')
                else:
                    response = await handler.execute(query_param='value1')

                # Assert
                mock_request.assert_called_once()
                args, kwargs = mock_request.call_args
                self.assertEqual(args[0], method.lower())
                self.assertEqual(kwargs['url'], f'https://api.example.com/{method.lower()}-endpoint')
                if method in ['POST', 'PUT', 'PATCH', 'DELETE']:
                    self.assertEqual(kwargs['params'], {})
                    self.assertEqual(kwargs['json'], {'body_param': 'value2'})
                else:
                    self.assertEqual(kwargs['params'], {'query_param': 'value1'})
                    self.assertEqual(kwargs['json'], {})
                self.assertNotIn('Authorization', kwargs['headers'])
                self.assertEqual(response, expected_response)
                mock_request.reset_mock()

    @patch('wildcard_core.tool_registry.tools.rest_api.RestAPIHandler.requests.request')
    async def test_execute_all_methods_with_bearer_auth(self, mock_request):
        for method in self.methods:
            with self.subTest(method=method):
                # Setup mock response
                mock_response = Mock()
                expected_response = {'status': f'{method} success'}
                mock_response.json.return_value = expected_response
                mock_response.raise_for_status = Mock()
                mock_request.return_value = mock_response

                # Create schema for each method with Bearer auth
                schema = self.create_schema(method=method, path=f'/{method.lower()}-bearer', auth_scheme='bearer')

                handler = RestAPIHandler(
                    name=f'{method}HandlerBearerAuth',
                    action_id=f'{method.lower()}_handler_bearer_auth',
                    schema=schema,
                    description=f'{method.upper()} handler with Bearer authentication',
                    base_url='https://api.example.com',
                    auth=self.auth_bearer
                )

                # Execute
                if method in ['POST', 'PUT', 'PATCH', 'DELETE']:
                    response = await handler.execute(body_param='value2')
                else:
                    response = await handler.execute(query_param='value1')

                # Assert
                mock_request.assert_called_once()
                args, kwargs = mock_request.call_args
                self.assertEqual(args[0], method.lower())
                self.assertEqual(kwargs['url'], f'https://api.example.com/{method.lower()}-bearer')
                if method in ['POST', 'PUT', 'PATCH', 'DELETE']:
                    self.assertEqual(kwargs['params'], {})
                    self.assertEqual(kwargs['json'], {'body_param': 'value2'})
                else:
                    self.assertEqual(kwargs['params'], {'query_param': 'value1'})
                    self.assertEqual(kwargs['json'], {})
                self.assertIn('Authorization', kwargs['headers'])
                self.assertEqual(kwargs['headers']['Authorization'], 'Bearer test_bearer_token')
                self.assertEqual(response, expected_response)
                mock_request.reset_mock()

    @patch('wildcard_core.tool_registry.tools.rest_api.RestAPIHandler.requests.request')
    async def test_execute_all_methods_with_api_key_header_auth(self, mock_request):
        for method in self.methods:
            with self.subTest(method=method):
                # Setup mock response
                mock_response = Mock()
                expected_response = {'status': f'{method} success'}
                mock_response.json.return_value = expected_response
                mock_response.raise_for_status = Mock()
                mock_request.return_value = mock_response

                # Create schema for each method with API Key in header
                schema = self.create_schema(method=method, path=f'/{method.lower()}-api-key-header', auth_scheme='api_key_header')

                handler = RestAPIHandler(
                    name=f'{method}HandlerAPIKeyHeader',
                    action_id=f'{method.lower()}_handler_api_key_header',
                    schema=schema,
                    description=f'{method.upper()} handler with API Key in header',
                    base_url='https://api.example.com',
                    auth=self.auth_api_key_header
                )

                # Execute
                if method in ['POST', 'PUT', 'PATCH', 'DELETE']:
                    response = await handler.execute(body_param='value2')
                else:
                    response = await handler.execute(query_param='value1')

                # Assert
                mock_request.assert_called_once()
                args, kwargs = mock_request.call_args
                self.assertEqual(args[0], method.lower())
                self.assertEqual(kwargs['url'], f'https://api.example.com/{method.lower()}-api-key-header')
                if method in ['POST', 'PUT', 'PATCH', 'DELETE']:
                    self.assertEqual(kwargs['params'], {})
                    self.assertEqual(kwargs['json'], {'body_param': 'value2'})
                else:
                    self.assertEqual(kwargs['params'], {'query_param': 'value1'})
                    self.assertEqual(kwargs['json'], {})
                self.assertIn('X-API-KEY', kwargs['headers'])
                self.assertEqual(kwargs['headers']['X-API-KEY'], 'test_api_key_header')
                self.assertEqual(response, expected_response)
                mock_request.reset_mock()

    @patch('wildcard_core.tool_registry.tools.rest_api.RestAPIHandler.requests.request')
    async def test_execute_all_methods_with_api_key_query_auth(self, mock_request):
        for method in self.methods:
            with self.subTest(method=method):
                # Setup mock response
                mock_response = Mock()
                expected_response = {'status': f'{method} success'}
                mock_response.json.return_value = expected_response
                mock_response.raise_for_status = Mock()
                mock_request.return_value = mock_response

                # Create schema for each method with API Key in query
                schema = self.create_schema(method=method, path=f'/{method.lower()}-api-key-query', auth_scheme='api_key_query')

                handler = RestAPIHandler(
                    name=f'{method}HandlerAPIKeyQuery',
                    action_id=f'{method.lower()}_handler_api_key_query',
                    schema=schema,
                    description=f'{method.upper()} handler with API Key in query parameters',
                    base_url='https://api.example.com',
                    auth=self.auth_api_key_query
                )

                # Execute
                if method in ['POST', 'PUT', 'PATCH', 'DELETE']:
                    response = await handler.execute(body_param='value2')
                else:
                    response = await handler.execute(query_param='value1')

                # Assert
                mock_request.assert_called_once()
                args, kwargs = mock_request.call_args
                self.assertEqual(args[0], method.lower())
                self.assertEqual(kwargs['url'], f'https://api.example.com/{method.lower()}-api-key-query')
                if method in ['POST', 'PUT', 'PATCH', 'DELETE']:
                    expected_params = {'api_key': 'test_api_key_query'}
                    self.assertEqual(kwargs['params'], expected_params)
                    self.assertEqual(kwargs['json'], {'body_param': 'value2'})
                else:
                    expected_params = {
                        'query_param': 'value1',
                        'api_key': 'test_api_key_query'
                    }
                    self.assertEqual(kwargs['params'], expected_params)
                    self.assertEqual(kwargs['json'], {})
                self.assertNotIn('Authorization', kwargs['headers'])
                self.assertEqual(response, expected_response)
                mock_request.reset_mock()

    # Additional tests for edge cases, error handling, and non-JSON responses can be added similarly

    @patch('wildcard_core.tool_registry.tools.rest_api.RestAPIHandler.requests.request')
    async def test_execute_non_json_response(self, mock_request):
        # Setup mock response
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("No JSON")
        mock_response.text = 'Non-JSON response'
        mock_response.raise_for_status = Mock()
        mock_request.return_value = mock_response

        # Create schema for GET with no auth
        schema = self.create_schema(method='GET', path='/non-json', auth_scheme='none')

        handler = RestAPIHandler(
            name='NonJSONHandler',
            action_id='non_json_handler',
            schema=schema,
            description='Handler expecting non-JSON response',
            base_url='https://api.example.com',
            auth=self.auth_none
        )

        # Execute
        response = await handler.execute(query_param='value1')

        # Assert
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(kwargs['url'], 'https://api.example.com/non-json')
        self.assertEqual(response, 'Non-JSON response')

    @patch('wildcard_core.tool_registry.tools.rest_api.RestAPIHandler.requests.request')
    async def test_execute_http_error(self, mock_request):
        # Setup mock response
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Client Error")
        mock_request.return_value = mock_response

        # Create schema for GET with no auth
        schema = self.create_schema(method='GET', path='/error-endpoint', auth_scheme='none')

        handler = RestAPIHandler(
            name='ErrorHandler',
            action_id='error_handler',
            schema=schema,
            description='Handler expecting HTTP error',
            base_url='https://api.example.com',
            auth=self.auth_none
        )

        # Execute & Assert
        with self.assertRaises(requests.HTTPError):
            await handler.execute(query_param='value1')

if __name__ == '__main__':
    unittest.main()