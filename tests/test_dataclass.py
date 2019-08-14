import json
from dataclasses import dataclass
from datetime import date, datetime

from dateutil.tz import tzoffset


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


SOME_MODEL = {
    'str_field': 'test_string',
    'int_field': 1,
    'float_field': 1.5,
    'bool_field': True,
    'list_field': [1, 2, 'str'],
    'date_field': '2019-09-08',
    'datetime_field': '2019-07-06T05:04:03-01:00',
    'nested_field': {
        'str_field': 'nested_str'
    }
}


def test_marshmallow(api):
    '''Should successfully serialize and deserialize a dataclass model
    '''
    @api.route('/', methods=['POST'])
    def _(model: DataclassModel) -> DataclassModel:
        assert model.str_field == 'test_string'
        assert model.int_field == 1
        assert model.float_field == 1.5
        assert model.bool_field == True
        assert model.list_field == [1, 2, 'str']
        assert model.date_field == date(2019, 9, 8)
        assert model.datetime_field == datetime(2019, 7, 6, 5, 4, 3, 0, tzoffset(None, -3600))
        assert model.nested_field.str_field == 'nested_str'
        return model

    with api.flask_app.test_client() as client:
        response = client.post(json=json.dumps(SOME_MODEL))
        assert response.get_json() == SOME_MODEL
