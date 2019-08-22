from functools import wraps


def test_decorated_func(api):
    '''Should be able to able to follow wrapped funcs
    '''

    def some_decorator(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            return func(*args, **kwargs)
        return decorator

    @api.route('/test')
    @some_decorator
    def _(arg: str) -> str:
        return arg

    with api.flask_app.test_client() as client:
        resp = client.get('/test?arg=some_arg')

    assert resp.get_data(as_text=True) == 'some_arg'
    assert api.openapi_provider.openapi_paths[0].params[0].name == 'arg'
    assert api.openapi_provider.openapi_paths[0].responses[0].data_type == str
