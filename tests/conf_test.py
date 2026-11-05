import pytest
from fastapi.testclient import TestClient

from app.main import app

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

# username, email, password
@pytest.fixture
def user_data():
    return {
        "username": "test",
        "email": "test@mail.ru",
        "password": "123321123"
    }
@pytest.fixture
def user_data2():
    return {
        "username": "test2",
        "email": "test2@mail.ru",
        "password": "123321123"
    }

@pytest.fixture
def register_user(client, user_data):
    response = client.post(
        "/auth/register",
        json=user_data
    )

    return response.status_code == 200

@pytest.fixture
def auth_headers(client, register_user, user_data):
    response = client.post(
        "/auth/login",
        data= {
            "username": user_data["email"],
            "password": user_data["password"]
        }
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}
