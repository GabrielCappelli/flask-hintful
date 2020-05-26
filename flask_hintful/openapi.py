import re
from dataclasses import is_dataclass
from typing import Callable, List

from flask import Response, current_app, jsonify
from openapi_specgen import (OpenApi,
                             OpenApiParam, OpenApiPath, OpenApiResponse,
                             OpenApiSecurity)
from openapi_specgen.security import ApiKeyAuth, BasicAuth, BearerAuth
from .utils import get_func_sig


class OpenApiProvider():
    '''Provides automatically generation of OpenApi specification for registered paths.
    '''

    def __init__(self):
        self.openapi_paths: List[OpenApiPath] = []
        self.openapi_security: OpenApiSecurity = OpenApiSecurity()

    def add_security(self, auth_list: List[str]):
        '''Adds authentication types to OpenApiSecurity at root level

        Args:
            auth_list: (List[str]). Items in List must be in (Basic, Bearer, ApiKey).
        '''
        if any(auth.lower() == 'basic' for auth in auth_list):
            self.openapi_security.basic_auth = BasicAuth()
        if any(auth.lower() == 'bearer' for auth in auth_list):
            self.openapi_security.bearer_auth = BearerAuth()
        if any(auth.lower() == 'apikey' for auth in auth_list):
            self.openapi_security.api_key_auth = ApiKeyAuth()

    def add_openapi_path(self, rule: str, methods: List[str], view_func: Callable):
        '''Add a new OpenApi Path for each method. Inspects view_func's type hints to be able to determine
        the appropriate paramater types.

            Args:
                rule (str): HTTP Path that the view_func will be registered in Flask
                methods (List[str]): List of HTTP Methods this path can receive
                view_func (Callable): Function that is called when this HTTP path is invoked
        '''
        func_sig = get_func_sig(view_func)
        openapi_params = []
        body = None

        for param_name, param in func_sig['params'].items():
            if hasattr(param.annotation, '__marshmallow__'):
                body = param.annotation.__marshmallow__
            elif is_dataclass(param.annotation):
                body = param.annotation
            elif f'<{param_name}>' in re.findall('<.*?>', rule):
                openapi_params.append(
                    OpenApiParam(
                        param_name,
                        'path',
                        data_type=param.annotation if param.annotation is not param.empty else str,
                        default=param.default if param.default is not param.empty else None,
                        required=param.default is param.empty
                    )
                )
            else:
                openapi_params.append(
                    OpenApiParam(
                        param_name,
                        'query',
                        data_type=param.annotation if param.annotation is not param.empty else str,
                        default=param.default if param.default is not param.empty else None,
                        required=param.default is param.empty
                    )
                )

        response_type = func_sig['return'] if func_sig['return'] is not func_sig['empty'] else str

        if hasattr(response_type, '__marshmallow__'):
            response_type = response_type.__marshmallow__

        openapi_response = OpenApiResponse('', data_type=response_type)

        for method in methods:
            self.openapi_paths.append(
                OpenApiPath(
                    rule.replace('<', '{').replace('>', '}'),
                    method.lower(),
                    [openapi_response],
                    openapi_params,
                    descr=func_sig['doc'],
                    request_body=body
                )
            )

    def get_openapi_spec(self) -> Response:
        '''Generates the OpenApi specification based on all registered Paths.

        Returns:
            Response: A Flask response containing the OpenApi spec as json
        '''
        return jsonify(
            OpenApi(current_app.name, self.openapi_paths, security=self.openapi_security).as_dict()
        )

    @staticmethod
    def get_openapi_ui() -> str:
        '''OpenApi UI provided by SwaggerUI

        Returns:
            str: SwaggerUI html
        '''
        openapi_json_path = current_app.config.get('FLASK_HINTFUL_OPENAPI_JSON_URL', '/openapi.json')
        return '''
                <! doctype html>
                <html>
                <head>
                <link type="text/css" rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui.css">
                <title>
                </title>
                </head>
                <body>
                <div id="swagger-ui">
                </div>
                <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-bundle.js"></script>
                <!-- `SwaggerUIBundle` is now available on the page -->
                <script>

                const ui = SwaggerUIBundle({{
                    url: '{}',
                    dom_id: '#swagger-ui',
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIBundle.SwaggerUIStandalonePreset
                    ],
                    layout: "BaseLayout",
                    deepLinking: true
                }})
                </script>
                </body>
                </html>
            '''.format(openapi_json_path)
