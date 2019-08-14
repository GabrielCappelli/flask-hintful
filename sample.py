from dataclasses import dataclass
from datetime import date, datetime

from flask import Flask

from flask_hintful import FlaskHintful

app = Flask('My API')
api = FlaskHintful(app)


@dataclass
class NestedModel():
    str_field: str


@dataclass
class DataclassModel():
    str_field: str
    int_field: int
    float_field: float
    boolean_field: bool
    list_field: list
    date_field: date
    datetime_field: datetime
    nested_field: NestedModel


@api.route('/<id>/dataclass_test', methods=['POST'])
def dataclass_route(id: str, query_arg: int, model: DataclassModel) -> DataclassModel:
    '''my dataclass route'''
    return model


app.run()
