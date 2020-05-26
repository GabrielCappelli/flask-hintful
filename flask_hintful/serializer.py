from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from typing import Callable, Dict, T, Type, Union

from flask import Response, json


class Serializer():
    '''Provides serialization for Flask Hintful.

    Default serializers:
        dict: flask.json.dumps,
        str: str,
        int: str,
        float: str,
        bool: str,
        date: lambda d: d.isoformat(),
        datetime: lambda d: d.isoformat(),

    Dataclasses and classes with a __marshmallow__ attribute are also supported.
    '''

    def __init__(self):
        self.serializers: Dict[Type, Callable] = {
            dict: lambda d: json.dumps(d, default=isodate_json_encoder),
            str: str,
            int: str,
            float: str,
            bool: str,
            date: lambda d: d.isoformat(),
            datetime: lambda d: d.isoformat(),
        }

    def add_serializer(self, type_: Type, serializer_func: Callable):
        '''Adds a serializer for type `type_`

        `serializer_func` must be able to serialize any instance of `type_` into a str.

        Args:
            type_ (Type): Any type
            serializer_func (Callable): Callable that can serialize a str/dict into type `t`
        '''
        self.serializers[type_] = serializer_func

    def serialize_response(self, data: T) -> Union[str, tuple, Response]:
        '''Serializes `data` into a response Flask understands.
        If Content-Type was supplied pass the same ahead to Flask, otherwise
        uses 'application/json' as the default Content-Type

        Args:
            data (T): data to be serialized, a tuple return like Flask`s or a Flask Response object.

        Returns:
            Union[str, tuple, Response]: Serialized response in a way Flask understands
        '''
        if isinstance(data, tuple):
            headers: Dict[str, str] = {}
            status = None

            if len(data) == 3:
                body, status, headers = data
            elif len(data) == 2:
                if isinstance(data[1], (int, str)):
                    body, status = data
                else:
                    body, headers = data
            if headers is None or headers.get('Content-Type') is None:
                headers['Content-Type'] = 'application/json'

            if status is not None:
                return self.serialize(body), status, headers
            return self.serialize(body), headers

        if isinstance(data, Response):
            return data
        return self.serialize(data), {'Content-Type': 'application/json'}

    def serialize(self, data: T) -> str:
        '''Serializes `data` into a string using the registered serializers that matches data type.
        Uses `is_dataclass` to determine if `data` is a dataclass, if positive uses `serialize_dataclass`.
        Uses `is_marshmallow_model` to determine if `data` is a model, if positive
        uses `serialize_marshmallow_model`

        Args:
            data (Any): Data to be serialized as a string

        Raises:
            TypeError: If there arent any registered serializers for data
            and data is not a dataclass nor marshmallow model.

        Returns:
            str: string representation of data
        '''
        serializer = self.serializers.get(data.__class__)
        if serializer is not None:
            return serializer(data)
        if self.is_list(data):
            return self.serialize_list(data)
        if self.is_dataclass(data):
            return self.serialize_dataclass(data)
        if self.is_marshmallow_model(data):
            return self.serialize_marshmallow_model(data)
        raise TypeError(f'Cannot serialize type {data.__class__}')

    @staticmethod
    def is_dataclass(data: T) -> bool:
        '''Determines if data is a dataclass or not using dataclasses.is_dataclass

        Args:
            data (T): Any python object

        Returns:
            bool: True if data is a dataclass, False otherwise
        '''
        if is_dataclass(data):
            return True
        return False

    def serialize_dataclass(self, data: T) -> str:
        '''Uses dataclasses.asdict to transform `data` into a dict, then uses the
        registered dict serializer to serialize this dataclass

        Args:
            data (T): A python dataclass

        Returns:
            str: string representation of data
        '''
        return self.serializers.get(dict, json.dumps)(asdict(data))

    @staticmethod
    def serialize_dataclass_to_dict(data: T) -> dict:
        return asdict(data)

    @staticmethod
    def is_marshmallow_model(data: T) -> bool:
        '''Determines if data is a marshmallow object by checking if it has a marshmallow
        schema in __marshmallow__ attribute

        Args:
            data (T): Any python object

        Returns:
            bool: True if data is a marshmallow model, False otherwise
        '''
        if hasattr(data, '__marshmallow__'):
            return True
        return False

    @staticmethod
    def serialize_marshmallow_model(data: T) -> str:
        '''Uses marshmallow.Schema.dumps to serialize `data`. Assumes that
        data makes it's schema available in __marshmallow__ attrbute

        Args:
            data (T): A marshmallow model

        Returns:
            str: string representation of data
        '''
        return data.__marshmallow__().dumps(data)

    @staticmethod
    def serialize_marshmallow_model_to_dict(data: T) -> dict:
        '''Uses marshmallow.Schema.dumps to serialize `data`. Assumes that
        data makes it's schema available in __marshmallow__ attrbute

        Args:
            data (T): A marshmallow model

        Returns:
            str: string representation of data
        '''
        return data.__marshmallow__().dump(data)

    @staticmethod
    def is_list(data: T) -> bool:
        '''Determines if data is a list or not

        Args:
            data (T): Any python object

        Returns:
            bool: True if data is a list , False otherwise
        '''
        if isinstance(data, list):
            return True
        return False

    def serialize_list(self, data: T) -> str:
        '''Serializes list and as items of this list

        Args:
            data (T): A python list

        Returns:
            str: Serialized list with serialized items
        '''
        for i, item in enumerate(data):
            if self.is_dataclass(item):
                data[i] = self.serialize_dataclass_to_dict(item)
            elif self.is_marshmallow_model(item):
                data[i] = self.serialize_marshmallow_model_to_dict(item)
        return json.dumps(data, default=isodate_json_encoder)


def isodate_json_encoder(data):
    if isinstance(data, (date, datetime)):
        return data.isoformat()
