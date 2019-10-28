from flask import Blueprint, Flask

from .deserializer import Deserializer
from .openapi import OpenApiProvider
from .serializer import Serializer
from .wrapper import BlueprintWrapper, view_func_wrapper


class FlaskHintful():
    '''The FlaskHintful object implements `route` and `register_blueprints` that mimic those of Flask. These
    will wrap your view funcs to serialize/deserialize HTTP query/path/body and pass them as params to your
    view functions.

    It inspect types hints in your view funcs to attempt to serialize/deserialize arguments to the expected
    types.

    It will also inspect all registered routes and automatically generate a OpenApi specification.

    Args:
        flask_app (Flask): Instance of the underlying Flask application
        serializer (Serializer, optional): Serialization provider. Defaults to Serializer().
        deserializer (Deserializer, optional): Deserialization provider. Defaults to Deserializer().
        openapi_provider (OpenApiProvider, optional): OpenApiProvider. Defaults to OpenApiProvider().
    '''

    def __init__(self,
                 flask_app: Flask,
                 serializer=None,
                 deserializer=None,
                 openapi_provider=None
                 ):
        self.flask_app = flask_app
        self.serializer = serializer or Serializer()
        self.deserializer = deserializer or Deserializer()
        self.openapi_provider = openapi_provider or OpenApiProvider()
        self.flask_app.add_url_rule(
            flask_app.config.get('FLASK_HINTFUL_OPENAPI_JSON_URL', '/openapi.json'),
            view_func=self.openapi_provider.get_openapi_spec
        )
        self.flask_app.add_url_rule(
            flask_app.config.get('FLASK_HINTFUL_OPENAPI_UI_URL', '/swagger'),
            view_func=self.openapi_provider.get_openapi_ui
        )

    def route(self, rule: str, **options):
        '''Wrap the decorated function using view_func_wrapper then register the wrapped func
        within the underlying Flask application.

        Args:
            rule (str): HTTP path to register this view func.
        '''
        def decorator(view_func):
            wrapped_view_func = view_func_wrapper(
                view_func,
                self.serializer,
                self.deserializer
            )
            self.flask_app.route(rule, **options)(wrapped_view_func)
            self.openapi_provider.add_openapi_path(rule, options.get('methods', ['GET']), view_func)
            return view_func
        return decorator

    def register_blueprint(self, blueprint: Blueprint):
        '''Wraps all view funcs declared on blueprint using BlueprintWrapper, then registers the
        Blueprint within the underlying Flask application.

        Args:
            blueprint (Blueprint): Flask Blueprint
        '''
        bp_wrapper = BlueprintWrapper(self, blueprint.url_prefix)
        for i, func in enumerate(blueprint.deferred_functions):
            if func.__qualname__ == 'Blueprint.add_url_rule.<locals>.<lambda>':
                blueprint.deferred_functions[i] = func(bp_wrapper)
        self.flask_app.register_blueprint(blueprint)
