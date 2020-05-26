
from dataclasses import fields, is_dataclass
from datetime import date, datetime
from typing import Callable, Dict, List, T, Type, Union

from dateutil.parser import parse as date_parser
from flask import json


class Deserializer():
    '''Provides deserialization for Flask Hintful.

    Default deserializers:
        dict: flask.json.loads,
        str: str,
        int: int,
        float: float,
        bool: flask_hintful.deserializer.str_to_bool,
        datetime: dateutil.parser.parse,
        date: lambda d: date_parser(d).date()

    Dataclasses and classes with a __marshmallow__ attribute are also supported.
    '''

    def __init__(self):
        self.deserializers: Dict[Type, Callable] = {
            dict: json.loads,
            str: str,
            int: int,
            float: float,
            bool: str_to_bool,
            datetime: date_parser,
            date: lambda d: date_parser(d).date()
        }

    def add_deserializer(self, type_: Type, deserializer_func: Callable):
        '''Adds a deserializer for type `type_`

        `serializer_func` must be able to deserialize any str or dict and return an
        instance of type `type_`

        Args:
            type_ (Type): Any python type
            deserializer_func (Callable):
        '''
        self.deserializers[type_] = deserializer_func

    def deserialize_args(self, args, params, body=None) -> dict:
        '''Deserializes all args and body by finding the expected type's from params.
        Args that are found in params are ignored, unless params contains a VAR_KEYWORD
        param (e.g, **kwargs).
        Since body does not have a name assumes that any param that is a Dataclass or Marshmallow Model
        is supposed to receive the body.

        Args:
            args ([werkzeug.datastructures.MultiDict]): Args from a Flask request
            body ([str]): JSON Body from a Flask request
            params ([dict]): Parameters from inspect.signature

        Returns:
            dict: A dict with all deserialized args
        '''
        deserialized_args = {}
        for param_name, param in params.items():
            if param_name in args:
                arg = args.poplist(param_name)
                deserialized_args[param_name] = arg if len(arg) > 1 else arg[0]
                if param.annotation != param.empty:
                    deserialized_args[param_name] = self.deserialize(arg, param.annotation)
            else:
                if param.kind == param.VAR_KEYWORD:
                    deserialized_args.update(args)
                if body is not None:
                    if self.is_dataclass(param.annotation) or self.is_marshmallow_model(param.annotation):
                        deserialized_args[param_name] = self.deserialize(
                            body, params[param_name].annotation
                        )
        return deserialized_args

    def deserialize(self, data: Union[List, str, dict], type_: Type[T]) -> T:
        '''Deserializes `data` into an instance of `type_` using the registered
        deserializer that matches the type of `type_`.
        If data is a dataclass recursively serializes all fields and passes a dict to the default constructor.
        If data has an attribute __marshmallow__ assumes it's a Marshmallow Schema and uses Schema.load()

        Raises:
            TypeError: If there arent any registered deserializers for data
            and data is not a dataclass nor has a __marshmallow__ attribute.

        Args:
            data (Union[List, str, dict]): Data to be deserialized as type_
            type_ (T): Any type

        Returns:
            T: An instance of type_
        '''
        deserializer = self.deserializers.get(type_)
        if issubclass(type_, list):
            return data
        if isinstance(data, list):
            data = data[0]
        if deserializer is not None:
            return deserializer(data)
        if self.is_dataclass(type_):
            return self.deserialize_dataclass(data, type_)
        if self.is_marshmallow_model(type_):
            return self.deserialize_marshmallow_model(data, type_)
        raise TypeError(f'Cannot deserialize type {type_}')

    @staticmethod
    def is_dataclass(type_: Type) -> bool:
        '''Determines if type_ is a dataclass or not using dataclasses.is_dataclass

        Args:
            data (T): Any python object

        Returns:
            bool: True if data is a dataclass, False otherwise
        '''
        if is_dataclass(type_):
            return True
        return False

    def deserialize_dataclass(self, data: Union[str, dict], type_: Type[T]) -> T:
        '''Uses dataclasses.asdict to transform `data` into a dict, then uses the
        registered dict serializer to serialize this dataclass

        Args:
            data (T): A python dataclass

        Returns:
            str: string representation of data
        '''
        if isinstance(data, str):
            parsed_data = json.loads(data)
        else:
            parsed_data = data
        for field in fields(type_):
            if parsed_data.get(field.name) and field.type not in [str, int, float, bool]:
                parsed_data[field.name] = self.deserialize(parsed_data[field.name], field.type)
        return type_(**parsed_data)

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
    def deserialize_marshmallow_model(data: Union[str, dict], type_: Type) -> str:
        '''Uses marshmallow.Schema.load or loads to deserialize `data`. Assumes that
        data makes it's schema available in __marshmallow__ attrbute

        Args:
            data (T): A marshmallow model

        Returns:
            str: string representation of data
        '''
        if isinstance(data, str):
            return type_.__marshmallow__().loads(data)
        return type_.__marshmallow__().load(data)


def str_to_bool(data: str) -> bool:
    '''Parse data into bool.

    Args:
        data (str): Any string

    Raises:
        ValueError: If str is not in either TRUE_STRS or FALSE_STRS

    Returns:
        bool: True if str is in TRUE_STRS, False if str is in FALSE_STRS.
    '''
    if data.lower() in TRUE_STRS:
        return True
    if data.lower() in FALSE_STRS:
        return False
    raise ValueError(f'{data} not in accepted values {TRUE_STRS}, {FALSE_STRS}')


TRUE_STRS: List[str] = ['true', '1', 't', 'y']
FALSE_STRS: List[str] = ['false', '0', 'f', 'n']
