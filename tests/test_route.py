from flask import Blueprint


def test_register_route(api):
    '''Should be able to successfully register a route
    '''
    @api.route('/test_api_route')
    def _():
        return 'api_route'
    with api.flask_app.test_client() as client:
        response = client.get('/test_api_route')
    assert response.get_data(as_text=True) == 'api_route'


def test_register_blueprint(api):
    '''Should be able to register all routes on a Blueprint
    '''
    bp = Blueprint('test_bp', __name__, url_prefix='/blueprint')

    @bp.route('/first_route')
    def _():
        return 'first_route'

    @bp.route('/second_route')
    def __():
        return 'second_route'

    api.register_blueprint(bp)

    with api.flask_app.test_client() as client:
        response = client.get('/blueprint/first_route')
        assert response.get_data(as_text=True) == 'first_route'

    with api.flask_app.test_client() as client:
        response = client.get('/blueprint/second_route')
        assert response.get_data(as_text=True) == 'second_route'
