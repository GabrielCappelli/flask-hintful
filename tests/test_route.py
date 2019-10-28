from unittest.mock import Mock

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


def test_register_blueprint_before_after_requests(api):
    '''Should be able to register Blueprints with before/after requests
    '''
    bp = Blueprint('test_bp', __name__, url_prefix='/blueprint')

    mock = Mock()

    @bp.before_request
    def before_request():
        mock.before_request()

    @bp.before_app_first_request
    def before_app_first_request():
        mock.before_first_request()

    @bp.after_request
    def after_request(response):
        mock.after_request()
        return response

    @bp.route('/first_route')
    def _():
        return 'first_route'

    api.register_blueprint(bp)

    with api.flask_app.test_client() as client:
        response = client.get('/blueprint/first_route')
        assert response.get_data(as_text=True) == 'first_route'
        response = client.get('/blueprint/first_route')
        assert response.get_data(as_text=True) == 'first_route'

    mock.before_first_request.assert_called_once()
    assert mock.before_request.call_count == 2
    assert mock.after_request.call_count == 2
