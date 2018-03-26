from apistar.test import TestClient
from app import app


def test_http_request():
    """
    Testing a view, using the test client.
    """
    client = TestClient(app)
    response = client.get('http://localhost/')
    assert response.status_code == 200
    assert response.json() == {'message': 'Welcome to API Star!'}
