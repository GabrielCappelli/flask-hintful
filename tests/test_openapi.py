from flask import Blueprint, Flask
from flask_hintful import FlaskHintful
from flask_hintful.openapi import OpenApiProvider


def test_openapi_json(api, marshmallow_type, dataclass_type):
    '''Should return openapi json
    '''
    @api.route('/empty_route')
    def empty_route():
        pass

    @api.route('/<path_arg>')
    def simple_route(query_arg: str, path_arg) -> str:
        pass

    @api.route('/marshmallow_test', methods=['POST'])
    def marshmallow_route(model: marshmallow_type) -> marshmallow_type:
        pass

    @api.route('/dataclass_test', methods=['POST'])
    def dataclass_route(model: dataclass_type) -> dataclass_type:
        pass

    with api.flask_app.test_client() as client:
        response = client.get('/openapi.json')
        assert response.get_json() is not None


def test_openapi_ui(api):
    '''Should return openapi ui
    '''
    with api.flask_app.test_client() as client:
        response = client.get('/swagger')
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
