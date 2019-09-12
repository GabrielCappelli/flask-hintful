# Getting Started

## Installation

Install using pip

```pip install flask-hintful```

## Creating the FlaskHintful object

Import Flask and FlaskHintful, then pass an instance of your Flask application to the constructor of FlaskHintful.

```python
from flask import Flask
from flask_hintful import FlaskHintful

app = Flask('My API')
api = FlaskHintful(app)
```

## Creating your API routes

Use type hints to describe your parameters/return types and Flask Hintful will take care of serializing/deserializing them, as well as generating the OpenApi documentation automatically!

```python
@api.route('/')
def get_dataclasses(foo: int, bar: str = None) -> List[DataclassModel]:
    '''Returns list of DataclassModel using query args'''
    pass

@api.route('/<id>')
def get_dataclass(id: str) -> DataclassModel:
    '''Returns DataclassModel using path arg'''
    pass

@api.route('/', methods=['POST'])
def create_dataclass(model: DataclassModel) -> DataclassModel:
    '''Creates a DataclassModel using POST and request body'''
    return model
```

For Marshmallow Schema see [Using Marshmallow Schemas](#Using-Marshmallow-Schemas)


## Registering routes and Blueprints

Use the FlaskHintful object to register routes using the `@route` decorator

```python
@api.route('/api/test')
def view_func():
    pass
```

Or register a Flask Blueprint that contains your view funcs.

```python
flask_bp = Blueprint('flask_bp', __name__)

@flask_bp.route('/api/test')
def view_func():
    pass

api.register_blueprint(flask_bp)
```

## Using Marshmallow Schemas

When using an object that has a Marshmallow Schema Flask Hintful needs a reference to that schema.

By default Flask Hintful search for schemas in an attribute  `__marshmallow__`, if you wish to change that behaviour look at [Subclassing](subclassing.md).

Your Marshmallow Schema must also return an instance of your model when using `load` or `loads`, so you'll have to to use the `post_load` decorator to instantiate your object.

Example Marshmallow Schema:

```python
from marshmallow import Schema, fields, post_load

class MarshmallowModel():
    def __init__(self,
                 str_field,
                 int_field
                 ):
        self.str_field = str_field
        self.int_field = int_field

class MarshmallowModelSchema(Schema):
    str_field = fields.Str()
    int_field = fields.Int()

    @post_load
    def make_some_model(self, data, **kwargs):
        return MarshmallowModel(**data)

# Sets MarshmallowModelSchema as a schema for MarshmallowModel
setattr(MarshmallowModel, '__marshmallow__', MarshmallowModelSchema)

# Flask Hintful will pick  MarshmallowModel from type hints and use the Schema's dump/load to serialize/deserialize it
@api.route('/', methods=['POST'])
def create_model(model: MarshmallowModel) -> MarshmallowModel:
    '''Creates a MarshmallowModel'''
    return model
```
