import json
from datetime import date, datetime
from unittest.mock import Mock

import pytest
from dateutil.tz import tzoffset
from werkzeug.datastructures import MultiDict

from flask_hintful.deserializer import (FALSE_STRS, TRUE_STRS, Deserializer,
                                        str_to_bool)
from flask_hintful.utils import get_func_sig

from .conftest import NestedModel


def test_deserialize():
    '''Should be able to deserialize common types
    '''
    _ = Deserializer()
    assert _.deserialize('{"foo": "bar"}', dict) == {'foo': 'bar'}
    assert _.deserialize('some_string', str) == 'some_string'
    assert _.deserialize('1', int) == 1
    assert _.deserialize('1.1', float) == 1.1
    assert _.deserialize('True', bool)
    assert _.deserialize('2019-09-08', date) == date(2019, 9, 8)
    assert _.deserialize(
        '2019-07-06T05:04:03-01:00', datetime) == datetime(2019, 7, 6, 5, 4, 3, 0, tzoffset(None, -3600))


def test_deserialize_dataclass(dataclass_type, model_dict):
    '''Should be able to deserialize a dataclass
    '''
    deserializer = Deserializer()
    deserialized_dataclass = deserializer.deserialize(json.dumps(model_dict), dataclass_type)
    expected_dataclass = dataclass_type(**model_dict)
    expected_dataclass.date_field = date(2019, 9, 8)
    expected_dataclass.datetime_field = datetime(2019, 7, 6, 5, 4, 3, tzinfo=tzoffset(None, -3600))
    expected_dataclass.nested_field = NestedModel(**model_dict['nested_field'])
    assert deserialized_dataclass == expected_dataclass


def test_deserialize_marshmallow_dict(marshmallow_type, model_dict):
    '''Should be able to deserialize a dict to marshmallow
    '''
    deserializer = Deserializer()
    marshmallow_obj = marshmallow_type.__marshmallow__().load(model_dict).data
    deserialized_marshmallow = deserializer.deserialize(model_dict, marshmallow_type)
    assert marshmallow_obj == deserialized_marshmallow


def test_deserialize_marshmallow_str(marshmallow_type, model_dict):
    '''Should be able to deserialize a str to marshmallow
    '''
    deserializer = Deserializer()
    marshmallow_obj = marshmallow_type.__marshmallow__().load(model_dict).data
    deserialized_marshmallow = deserializer.deserialize(json.dumps(model_dict), marshmallow_type)
    assert marshmallow_obj == deserialized_marshmallow


def test_deserialize_invalid_type(simple_type):
    '''Should throw TypeError when a type that we can`t DEserialize is passed
    '''
    with pytest.raises(TypeError):
        Deserializer().deserialize('', simple_type)


def test_add_deserializer():
    '''Should be able to add a deserializer
    '''
    mock = Mock()
    deserializer = Deserializer()
    deserializer.add_deserializer(str, mock)
    deserializer.deserialize('test_str', str)
    mock.assert_called_with('test_str')


def test_deserialize_args(marshmallow_type, model_dict):
    '''Should be able to deserialize Flask args/body
    '''
    def _(foo: str, body: marshmallow_type):
        pass
    func_sig = get_func_sig(_)
    deserializer = Deserializer()
    args = MultiDict([('foo', 'bar')])
    deserialized_args = deserializer.deserialize_args(args, func_sig['params'], model_dict)
    assert deserialized_args['foo'] == 'bar'
    assert deserialized_args['body'] == marshmallow_type.__marshmallow__().load(model_dict).data


def test_str_to_bool():
    '''Should be able to deserialize strs to bool
    '''
    for false_str in FALSE_STRS:
        assert not str_to_bool(false_str)
    for true_str in TRUE_STRS:
        assert str_to_bool(true_str)
    with pytest.raises(ValueError):
        str_to_bool('invalid_str')
