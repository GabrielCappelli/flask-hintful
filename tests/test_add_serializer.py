from unittest.mock import Mock


def test_add_serializer(api):
    '''Should be able to add a serializer
    '''
    mock = Mock()
    api.serializer.add_serializer(str, mock)

    @api.route('/')
    def _():
        return 'test_str'

    with api.flask_app.test_client() as client:
        client.get('/')

    mock.assert_called_with('test_str')


def test_add_deserializer(api):
    '''Should be able to add a deserializer
    '''
    mock = Mock()
    api.deserializer.add_deserializer(str, mock)

    @api.route('/')
    def _(arg: str):
        pass

    with api.flask_app.test_client() as client:
        client.get('/?arg=test_str')

    mock.assert_called_with('test_str')
