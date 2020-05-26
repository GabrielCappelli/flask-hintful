import json
from datetime import date, datetime
from unittest.mock import Mock

import pytest
from dateutil.tz import tzoffset
from flask import jsonify
from flask_hintful import Serializer


def test_serialize():
    '''Should be able to serialize common types
    '''
    serializer = Serializer()
    assert serializer.serialize({'foo': 'bar'}) == '{"foo": "bar"}'
    assert serializer.serialize('some_string') == 'some_string'
    assert serializer.serialize(1) == '1'
    assert serializer.serialize(1.1) == '1.1'
    assert serializer.serialize(True) == 'True'
    assert serializer.serialize(date(2019, 9, 8)) == '2019-09-08'
    assert serializer.serialize(
        datetime(2019, 7, 6, 5, 4, 3, 0, tzoffset(None, -3600))
    ) == '2019-07-06T05:04:03-01:00'


def test_serialize_list(dataclass_type, marshmallow_type, model_dict):
    '''Should be able to serialize a dataclass
    '''
    serializer = Serializer()
    expected_list = '[1, 1.0, true, {"foo": "bar"}, {"bool_field": true, "date_field": "2019-09-08", "datetime_field": "2019-07-06T05:04:03-01:00", "float_field": 1.5, "int_field": 1, "list_field": ["1", "2", "str"], "nested_field": {"str_field": "nested_str"}, "str_field": "test_string"}, {"bool_field": true, "date_field": "2019-09-08", "datetime_field": "2019-07-06T05:04:03-01:00", "float_field": 1.5, "int_field": 1, "list_field": ["1", "2", "str"], "nested_field": {"str_field": "nested_str"}, "str_field": "test_string"}]'
    deserialized_list = serializer.serialize(
        [1, 1.0, True, {'foo': 'bar'},
         dataclass_type(**model_dict),
         marshmallow_type.__marshmallow__().load(model_dict)]
    )
    assert expected_list == deserialized_list


def test_serialize_dataclass(dataclass_type, model_dict):
    '''Should be able to serialize a dataclass
    '''
    serializer = Serializer()
    serialized_dataclass = serializer.serialize(dataclass_type(**model_dict))
    assert json.loads(serialized_dataclass) == model_dict


def test_serialize_marshmallow(marshmallow_type, model_dict):
    '''Should be able to serialize a marshmallow
    '''
    serializer = Serializer()
    marshmallow_obj = marshmallow_type.__marshmallow__().load(model_dict)
    serialized_marshmallow = serializer.serialize(marshmallow_obj)
    assert serialized_marshmallow == marshmallow_type.__marshmallow__().dumps(marshmallow_obj)


def test_serialize_invalid_type(simple_type):
    '''Should throw TypeError when a type that we can`t serialize is passed
    '''
    with pytest.raises(TypeError):
        Serializer().serialize(simple_type())


def test_add_serializer():
    '''Should be able to add a deserializer
    '''
    serializer = Serializer()
    mock = Mock()
    serializer.add_serializer(str, mock)
    serializer.serialize('test_str')
    mock.assert_called_with('test_str')


def test_serialize_response_class(api):
    '''Should successfully wrap a Flask Response object
    '''
    @api.route('/response_class')
    def _():
        return jsonify({'arg': 'test'})
    with api.flask_app.test_client() as client:
        response = client.get('/response_class')
    assert response.get_json().get('arg') == 'test'


def test_serialize_tuple_data_status(api):
    '''Should successfully serialize a tuple with data,status
    '''
    @api.route('/len_2_status')
    def _():
        return {'arg': 'test'}, 202
    with api.flask_app.test_client() as client:
        response = client.get('/len_2_status')
    assert response.status_code == 202
    assert response.get_json().get('arg') == 'test'
    assert response.headers['Content-Type'] == 'application/json'


def test_serialize_tuple_data_header(api):
    '''Should successfully serialize a tuple with data,header
    '''
    @api.route('/len_2_headers')
    def _():
        return {'arg': 'test'}, {'Some-Header': 'test'}
    with api.flask_app.test_client() as client:
        response = client.get('/len_2_headers')
    assert response.status_code == 200
    assert response.get_json().get('arg') == 'test'
    assert response.headers['Some-Header'] == 'test'
    assert response.headers['Content-Type'] == 'application/json'


def test_serialize_tuple_data_status_header(api):
    '''Should successfully wrap a tuple with data,status,header
    '''
    @api.route('/len_3')
    def _():
        return {'arg': 'test'}, 202, {'Some-Header': 'test'}
    with api.flask_app.test_client() as client:
        response = client.get('/len_3')
    assert response.status_code == 202
    assert response.get_json().get('arg') == 'test'
    assert response.headers['Content-Type'] == 'application/json'
