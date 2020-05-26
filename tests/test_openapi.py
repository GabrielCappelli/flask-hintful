from flask import Blueprint, Flask
from flask_hintful import FlaskHintful
from flask_hintful.openapi import OpenApiProvider


def test_openapi_json(api):
    '''Should return openapi json from custom url
    '''
    app = Flask(__name__)
    app.config['FLASK_HINTFUL_OPENAPI_JSON_URL'] = '/custom_openapi.json'

    api = FlaskHintful(app)
    with api.flask_app.test_client() as client:
        response = client.get('/custom_openapi.json')
        assert response.get_json() is not None


def test_openapi_ui(api):
    '''Should return openapi ui from custom url
    '''
    app = Flask(__name__)
    app.config['FLASK_HINTFUL_OPENAPI_UI_URL'] = '/custom_swagger'

    api = FlaskHintful(app)
    with api.flask_app.test_client() as client:
        response = client.get('/custom_swagger')
        assert response.get_data(as_text=True) is not None


def test_openapi_blueprint():
    '''Should successfully register Blueprint Paths
    '''
    openapi = OpenApiProvider()
    app = Flask(__name__)
    api = FlaskHintful(app, openapi_provider=openapi)
    bp = Blueprint('test_bp', __name__, url_prefix='/bp_route/')

    @bp.route('/<id>')
    def api_route(id: str, foo: str = 'bar') -> str:
        pass

    api.register_blueprint(bp)

    assert openapi.openapi_paths[0].path == '/bp_route/{id}'
    assert openapi.openapi_paths[0].method == 'get'


def test_openapi_args():
    '''Should successfully register query and path args
    '''
    openapi = OpenApiProvider()
    app = Flask(__name__)
    api = FlaskHintful(app, openapi_provider=openapi)

    @api.route('/route/<id>')
    def api_route(id: str, foo: str = 'bar') -> str:
        pass

    assert openapi.openapi_paths[0].path == '/route/{id}'
    assert openapi.openapi_paths[0].method == 'get'
    assert openapi.openapi_paths[0].responses[0].data_type == str

    assert openapi.openapi_paths[0].params[0].name == 'id'
    assert openapi.openapi_paths[0].params[0].data_type == str
    assert openapi.openapi_paths[0].params[0].location == 'path'
    assert openapi.openapi_paths[0].params[0].required

    assert openapi.openapi_paths[0].params[1].name == 'foo'
    assert openapi.openapi_paths[0].params[1].data_type == str
    assert openapi.openapi_paths[0].params[1].location == 'query'
    assert not openapi.openapi_paths[0].params[1].required
    assert openapi.openapi_paths[0].params[1].default == 'bar'


def test_openapi_request_body(marshmallow_type, dataclass_type):
    '''Should successfully register objects as request body
    '''
    openapi = OpenApiProvider()
    app = Flask(__name__)
    api = FlaskHintful(app, openapi_provider=openapi)

    @api.route('/marshmallow_test', methods=['POST'])
    def marshmallow_route(_: marshmallow_type) -> marshmallow_type:
        pass

    @api.route('/dataclass_test', methods=['POST'])
    def dataclass_route(_: dataclass_type) -> dataclass_type:
        pass

    assert openapi.openapi_paths[0].path == '/marshmallow_test'
    assert openapi.openapi_paths[0].method == 'post'
    assert openapi.openapi_paths[0].responses[0].data_type == marshmallow_type.__marshmallow__
    assert openapi.openapi_paths[0].request_body == marshmallow_type.__marshmallow__

    assert openapi.openapi_paths[1].path == '/dataclass_test'
    assert openapi.openapi_paths[1].method == 'post'
    assert openapi.openapi_paths[1].responses[0].data_type == dataclass_type
    assert openapi.openapi_paths[1].request_body == dataclass_type


def test_openapi_security():
    '''OpenApi provider should succesfully register basic, bearer and apikey authetncation types
    '''
    openapi = OpenApiProvider()
    app = Flask(__name__)
    api = FlaskHintful(app, openapi_provider=openapi, openapi_security=('basic', 'bearer', 'apikey'))

    assert openapi.openapi_security.basic_auth is not None
    assert openapi.openapi_security.bearer_auth is not None
    assert openapi.openapi_security.api_key_auth is not None
