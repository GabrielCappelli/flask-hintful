from .test_dataclass import DataclassModel
from .test_marshmallow import MarshmallowModel


def test_openapi_json(api):
    '''Should return openapi json
    '''
    @api.route('/empty_route')
    def empty_route():
        pass

    @api.route('/<path_arg>')
    def simple_route(query_arg: str, path_arg) -> str:
        pass

    @api.route('/marshmallow_test', methods=['POST'])
    def marshmallow_route(model: MarshmallowModel) -> MarshmallowModel:
        pass

    @api.route('/dataclass_test', methods=['POST'])
    def dataclass_route(model: DataclassModel) -> DataclassModel:
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
