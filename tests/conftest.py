import json
from dataclasses import dataclass
from datetime import date, datetime

import pytest
from flask import Flask
from marshmallow import Schema, fields, post_load

from flask_hintful import FlaskHintful


@pytest.fixture
def api():
    app = Flask(__name__)
    return FlaskHintful(app)


@pytest.fixture
def simple_type():
    return SimpleType


@pytest.fixture
def dataclass_type():
    return DataclassModel


@pytest.fixture
def marshmallow_type():
    return MarshmallowModel


@pytest.fixture
def model_dict():
    return {
        'str_field': 'test_string',
        'int_field': 1,
        'float_field': 1.5,
        'bool_field': True,
        'list_field': ['1', '2', 'str'],
        'date_field': '2019-09-08',
        'datetime_field': '2019-07-06T05:04:03-01:00',
        'nested_field': {
            'str_field': 'nested_str'
        }
    }


class SimpleType():
    pass


@dataclass
class NestedModel():
    str_field: str


@dataclass
class DataclassModel():
    str_field: str
    int_field: int
    float_field: float
    bool_field: bool
    list_field: list
    date_field: date
    datetime_field: datetime
    nested_field: NestedModel


class MarshmallowModel():
    def __init__(self,
                 str_field,
                 int_field,
                 float_field,
                 bool_field,
                 list_field,
                 date_field,
                 datetime_field,
                 nested_field
                 ):
        self.str_field = str_field
        self.int_field = int_field
        self.float_field = float_field
        self.bool_field = bool_field
        self.list_field = list_field
        self.date_field = date_field
        self.datetime_field = datetime_field
        self.nested_field = nested_field

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False


class NestedModelSchema(Schema):
    str_field = fields.Str()

    @post_load
    def make_some_model(self, data, **kwargs):
        return NestedModel(**data)


class MarshmallowModelSchema(Schema):
    str_field = fields.Str()
    int_field = fields.Int()
    float_field = fields.Float()
    bool_field = fields.Bool()
    list_field = fields.List(fields.Str())
    date_field = fields.Date()
    datetime_field = fields.DateTime()
    nested_field = fields.Nested('NestedModelSchema')

    @post_load
    def make_some_model(self, data, **kwargs):
        return MarshmallowModel(**data)


setattr(MarshmallowModel, '__marshmallow__', MarshmallowModelSchema)
