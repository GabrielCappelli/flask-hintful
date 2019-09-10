from functools import wraps
from typing import Callable

from flask import request

from .deserializer import Deserializer
from .serializer import Serializer
from .utils import get_func_sig


def view_func_wrapper(view_func: Callable, serializer: Serializer, deserializer: Deserializer):
    '''Wraps around the view_func to deserialize Flask request view args, args and
    body as parameters for the view_func and serialize the view_func return.

    Args:
        view_func (Callable): Function that will be wrapped
        serializer (Serializer): Serializer to serialize response
        deserializer (Deserializer): Deserializer to deserialize args
    '''
    func_sig = get_func_sig(view_func)

    @wraps(view_func)
    def decorator(**_):
        args = request.args.copy()
        args.update(request.view_args)
        deserialized_args = deserializer.deserialize_args(
            args, func_sig['params'], request.get_json()
        )
        response = view_func(**deserialized_args)
        return serializer.serialize_response(response)
    return decorator


class BlueprintWrapper():
    '''This class is used to help wrap view funcs registered using a Flask Blueprint.

    Args:
        app (FlaskHintful): FlaskHintful api to register the Blueprints routes on
        url_prefix (str, optional): [description]. Defaults to ''.
    '''

    def __init__(self, app, url_prefix: str = ''):
        self.app = app
        self.url_prefix = url_prefix

    def add_url_rule(self, rule, endpoint, view_func, **options):
        '''Wraps view_func with view_func_wrapper, then return a lambda expression as is
        expected by Flask Blueprint`s deferred_functions.
        '''
        wrapped_view_func = view_func_wrapper(view_func, self.app.serializer, self.app.deserializer)
        prefixed_rule = ''
        if self.url_prefix:
            prefixed_rule = '/'.join((self.url_prefix.rstrip('/'), rule.lstrip('/')))
        self.app.openapi_provider.add_openapi_path(
            prefixed_rule or rule, options.get('methods', ['GET']), view_func)
        return lambda s: s.add_url_rule(rule, endpoint, wrapped_view_func, **options)
