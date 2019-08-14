from flask import Response, jsonify


def test_response_class(api):
    '''Should successfully wrap a Flask Response object
    '''
    @api.route('/response_class')
    def _():
        return jsonify({'arg': 'test'})
    with api.flask_app.test_client() as client:
        response = client.get('/response_class')
    assert response.get_json().get('arg') == 'test'


def test_len_2_status(api):
    '''Should successfully wrap a tuple with data,status
    '''
    @api.route('/len_2_status')
    def _():
        return {'arg': 'test'}, 202
    with api.flask_app.test_client() as client:
        response = client.get('/len_2_status')
    assert response.status_code == 202
    assert response.get_json().get('arg') == 'test'
    assert response.headers['Content-Type'] == 'application/json'


def test_len_2_headers(api):
    '''Should successfully wrap a tuple with data,header
    '''
    @api.route('/len_2_headers')
    def _():
        return {'arg': 'test'}, {'Some-Header': 'test'}
    with api.flask_app.test_client() as client:
        response = client.get('/len_2_headers')
    assert response.status_code == 200
    assert response.get_json().get('arg') == 'test'
    assert response.headers['Some-Header'] == 'test'
    assert response.headers['Content-Type'] == 'application/json'


def test_len_3(api):
    '''Should successfully wrap a tuple with data,status,header
    '''
    @api.route('/len_3')
    def _():
        return {'arg': 'test'}, 202, {'Some-Header': 'test'}
    with api.flask_app.test_client() as client:
        response = client.get('/len_3')
    assert response.status_code == 202
    assert response.get_json().get('arg') == 'test'
    assert response.headers['Content-Type'] == 'application/json'
