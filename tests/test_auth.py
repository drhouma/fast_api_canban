from http.client import HTTPException

from app.tests.conf_test import *
import pytest
import jwt

from app.security import SECRET_KEY, algo


# user is registered and returned data is not compromised
def test_register_user(client, user_data):
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 201
    data = response.json()

    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "hashed_password" not in data
    assert "password" not in data

def test_register_user_with_existing_email(client, register_user, user_data):
    response = client.post("/auth/register", json=user_data)

    assert response.status_code == 409

    assert response.json()["detail"] == "User with that email already exists."


def test_register_user_with_invalid_email(client, user_data):
    user_data["email"] = "invalid_email"
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 422

def test_login_with_correct_credentials(client, register_user ,user_data):
    response = client.post(
        "/auth/login",
        data={
            "username": user_data["email"],
            "password": user_data["password"]
        }
    )
    # login success
    assert response.status_code == 200

    data = response.json()
    # there is my jwt
    assert "access_token" in data.keys()
    assert data["token_type"] == "bearer"

def test_login_with_wrong_password(client, user_data, register_user):
    response = client.post(
        "/auth/login",
        data={
            "username": user_data["email"],
            "password": user_data["password"] + "1"
        }
    )
    assert response.status_code == 401

    data = response.json()
    assert data["detail"] == "Incorrect email or password"

def test_login_with_nonexistent_user(client, user_data):
    response = client.post(
        "/auth/login",
        data={
            "username": user_data["email"]+"1",
            "password": user_data["password"]
        }
    )
    assert response.status_code == 401

    data = response.json()
    assert data["detail"] == "Incorrect email or password"

def test_get_current_user(client, user_data, register_user, auth_headers):
        response = client.get(
            "/auth/me",
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["email"] == user_data["email"]


def test_get_current_user_without_token(client, user_data, register_user, auth_headers):
    response = client.get(
        "/auth/me",
        headers=None
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
