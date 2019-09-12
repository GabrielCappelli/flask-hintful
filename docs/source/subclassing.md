# Subclassing

You can subclass `Serializer` or `Deserializer` to change how we detect and serialize/deserialize `Dataclasses` or `Marshmallow Schemas`.

## Subclassing Marshmallow

Your subclass will need to implement these methods on Serializer:

 * `is_marshmallow_model`
 * `serialize_marshmallow_model`
 * `serialize_marshmallow_model_to_dict`

And these methods on Deserializer:
 * `is_marshmallow_model`
 * `deserialize_marshmallow_model`

Example:

```python
from typing import T, Type, Union

from flask import Blueprint, Flask
from flask_hintful import Deserializer, FlaskHintful, Serializer

class MySerializer(Serializer):

    def is_marshmallow_model(data: T) -> bool:
        '''Returns True if Data is a Marshmallow object'''
        pass

    def serialize_marshmallow_model(data: T) -> str:
        '''Serializes Marshmallow object data into a JSON str'''
        pass

    def serialize_marshmallow_model_to_dict(data: T) -> dict:
        '''Serializes Marshmallow object data into a dict'''
        pass


class MyDeserializer(Deserializer):

    @staticmethod
    def is_marshmallow_model(type_: Type) -> bool:
        '''Returns True if type_ is a marshmallow'''
        pass

    @staticmethod
    def deserialize_marshmallow_model(data: Union[str, dict], type_: Type) -> T:
        '''Returns deserialized data into instance of type_'''
        pass


app = Flask('My API')
api = FlaskHintful(app,
                   serializer=MySerializer(),
                   deserializer=MyDeserializer())
```

## Subclassing Dataclass

Your subclass will need to implement these methods on Serializer:

 * `is_dataclass`
 * `serialize_dataclass`
 * `serialize_dataclass_to_dict`

And these methods on Deserializer:
 * `is_dataclass`
 * `deserialize_dataclass`

Example:

```python
from typing import T, Type, Union

from flask import Blueprint, Flask
from flask_hintful import Deserializer, FlaskHintful, Serializer

class MySerializer(Serializer):

    def is_dataclass(data: T) -> bool:
        '''Returns True if Data is a Dataclass'''
        pass

    def serialize_dataclass(data: T) -> str:
        '''Serializes Dataclass data into a JSON str'''
        pass

    def serialize_dataclass_to_dict(data: T) -> dict:
        '''Serializes Dataclass data into a dict'''
        pass


class MyDeserializer(Deserializer):

    @staticmethod
    def is_dataclass(type_: Type) -> bool:
        '''Returns True if type_ is a Dataclass'''
        pass

    @staticmethod
    def deserialize_dataclass(data: Union[str, dict], type_: Type) -> T:
        '''Returns deserialized data into instance of type_'''
        pass


app = Flask('My API')
api = FlaskHintful(app,
                   serializer=MySerializer(),
                   deserializer=MyDeserializer())
```
