from datetime import date, datetime

from dateutil.tz import tzoffset
from flask import request
from flask.json import JSONEncoder


def test_view_arg(api):
    '''Should successfully serialize and parametrize path args
    '''

    @api.route('/<str_arg>/<int_arg>/<float_arg>/<bool_arg>/<date_arg>/<datetime_arg>')
    def _(str_arg: str, int_arg: int, float_arg: float,
          bool_arg: bool, date_arg: date, datetime_arg: datetime):
        # asserts everything was deserialized properly
        assert str_arg == 'test'
        assert int_arg == 1
        assert float_arg == 1.5
        assert bool_arg is True
        assert date_arg == date(2019, 9, 8)
        assert datetime_arg == datetime(2019, 7, 6, 5, 4, 3, 0, tzoffset(None, -3600))
        return {
            'str_arg': str_arg,
            'int_arg': int_arg,
            'float_arg': float_arg,
            'bool_arg': bool_arg,
            'date_arg': date_arg,
            'datetime_arg': datetime_arg
        }

    with api.flask_app.test_client() as client:
        response = client.get(
            '/test/1/1.5/true/2019-09-08/2019-07-06T05:04:03-01:00')
    # asserts everything was serialized properly
    assert response.get_json().get('str_arg') == 'test'
    assert response.get_json().get('int_arg') == 1
    assert response.get_json().get('float_arg') == 1.5
    assert response.get_json().get('bool_arg') is True
    assert response.get_json().get('date_arg') == '2019-09-08'
    assert response.get_json().get('datetime_arg') == '2019-07-06T05:04:03-01:00'


def test_query_args(api):
    '''Should successfully serialize and parametrize query args
    '''

    @api.route('/')
    def _(str_arg: str, int_arg: int, float_arg: float,
          bool_arg: bool, list_arg: list, date_arg: date, datetime_arg: datetime):
        # asserts everything was deserialized properly
        assert str_arg == 'test'
        assert int_arg == 1
        assert float_arg == 1.5
        assert bool_arg is True
        assert list_arg == ['item1', 'item2']
        assert date_arg == date(2019, 9, 8)
        assert datetime_arg == datetime(2019, 7, 6, 5, 4, 3, 0, tzoffset(None, -3600))
        return {
            'str_arg': str_arg,
            'int_arg': int_arg,
            'float_arg': float_arg,
            'bool_arg': bool_arg,
            'list_arg': list_arg,
            'date_arg': date_arg,
            'datetime_arg': datetime_arg
        }
    with api.flask_app.test_client() as client:
        response = client.get(
            '/?str_arg=test' +
            '&int_arg=1' +
            '&float_arg=1.5' +
            '&bool_arg=true' +
            '&list_arg=item1' +
            '&list_arg=item2' +
            '&date_arg=2019-09-08' +
            '&datetime_arg=2019-07-06T05:04:03-01:00')
    # asserts everything was serialized properly
    assert response.get_json().get('str_arg') == 'test'
    assert response.get_json().get('int_arg') == 1
    assert response.get_json().get('float_arg') == 1.5
    assert response.get_json().get('bool_arg') is True
    assert response.get_json().get('list_arg') == ['item1', 'item2']
    assert response.get_json().get('date_arg') == '2019-09-08'
    assert response.get_json().get('datetime_arg') == '2019-07-06T05:04:03-01:00'


def test_extra_query_args(api):
    '''Should not serialize and parametrize args that are not expected by the view func
    '''
    @api.route('/')
    def _(arg: str):
        assert arg == 'test_one'
        assert request.args['extra_arg'] == 'test_extra'

    with api.flask_app.test_client() as client:
        client.get('/?arg=test_one&extra_arg=test_extra')


def test_kwargs(api):
    '''Should send all extra args to **kwargs
    '''
    @api.route('/')
    def _(arg, **kwargs):
        kwargs['arg'] = arg
        assert kwargs['arg'] == 'arg'
        assert kwargs['arg_kw1'] == 'kw1'
        assert kwargs['arg_kw2'] == 'kw2'
        return kwargs

    with api.flask_app.test_client() as client:
        response = client.get('/?arg=arg&arg_kw1=kw1&arg_kw2=kw2')

    assert response.get_json().get('arg') == 'arg'
    assert response.get_json().get('arg_kw1') == 'kw1'
    assert response.get_json().get('arg_kw2') == 'kw2'
