import pytest
from fastapi.testclient import TestClient

from app.main import app

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def user_data():
    return {
        "username": "",
        "email": "",
        "password": ""
    }

@pytest.fixture
def register_user(client, user_data):
    response = client.post(
        "/auth/register",
        json=user_data
    )

    return response.status_code == 200

def auth_headers(client, register_user):
    response = client.post(
        "/auth/login",
        data= {
            "username": register_user.username,
            "password": register_user.password
        }
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}
