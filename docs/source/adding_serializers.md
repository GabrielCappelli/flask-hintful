# Custom Serializers/Deserializers

You can add or replace serializers/deserializers for any "basic" types. For customizing Marshmallow/Dataclass behaviour you'll need to do [Subclassing](subclassing.md).

Do note that adding a (de)serializer to an existing type will override the [default](#Default-Serializers).

## Adding Serializers

On your FlaskHintful instance use `.serializer.add_serializer`

You will need to provide a callable that can receive an instance of the type and return a `str`.

Example, custom serializer that serializes bools to TRUE and FALSE:
```python
def my_bool_serializer(data: bool) -> str:
    return str(data).upper()

api.serializer.add_serializer(bool, my_bool_serializer)
```

## Adding Deserializers

On your FlaskHintful instance use `.deserializer.add_deserializer`

You will need to provide a callable that can receive a `str` and return an instance of that type.

Example, custom deserializer that deserializes `'yay'` to `True`:
```python
def my_bool_deserializer(data: str) -> bool:
    if data.lower() == 'yay':
        return True
    return False

api.deserializer.add_deserializer(bool, my_bool_deserializer)
```

## Default Serializers

For "basic" types


```python
self.serializers: Dict[Type, Callable] = {
    dict: lambda d: json.dumps(d, default=isodate_json_encoder),
    str: str,
    int: str,
    float: str,
    bool: str,
    date: lambda d: d.isoformat(),
    datetime: lambda d: d.isoformat(),
}
```


## Default Deserializers

For "basic" types

```python
self.deserializers: Dict[Type, Callable] = {
    dict: json.loads,
    str: str,
    int: int,
    float: float,
    bool: str_to_bool,
    datetime: date_parser,
    date: lambda d: date_parser(d).date()
}
```
