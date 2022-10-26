'''
File: test_login.py
File Created: Wednesday, 26th October 2022 3:01:31 pm
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from fastapi.responses import Response
from httpx import AsyncClient

@pytest.mark.asyncio
class TestRegister:
    async def test_empty_body(self, test_client: TestClient):
        response: Response = await test_client.post("/user/register", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_missing_email(self, test_client: TestClient):
        json = {"password": "morethan8"}
        response: Response = await test_client.post("/auth/register", json=json)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_missing_first_last_names(self, test_client: TestClient):
        json = {"email": "test@test.test", "password": "morethan8"}
        response: Response = await test_client.post("/auth/register", json=json)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_password_validator(self, test_client: TestClient):
        json = {"first_name": "first_test", "last_name": "last_test",
                "email": "test@test.test", "password": "less8"}
        response: Response = await test_client.post("/auth/register", json=json)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_existing_email(self, user_verified: TestClient):
        test_client, user = user_verified
        json = {"first_name": "first_test", "last_name": "last_test",
                "email": user["email"], "password": "morethan8"}
        response: Response = await test_client.post("/auth/register", json=json)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize("email", ["email.email", "email@email", "email.email.email"])
    async def test_invalid_email(self, test_client: TestClient, email):
        json = {"first_name": "first_test", "last_name": "last_test",
                "email": email, "password": "morethan8"}
        response: Response = await test_client.post("/auth/register", json=json)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
class TestLogin:
    async def test_not_existing_account(self, test_client: TestClient):
        data = {"username": "test@test.test", "password": "morethan8"}
        response: Response = await test_client.post("/auth/jwt/login", data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_missing_email(self, user_verified):
        test_client, user = user_verified
        data = {"password": "morethan8"}
        response: Response = await test_client.post("/auth/jwt/login", data=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_missing_password(self, user_verified):
        test_client, user = user_verified
        data = {"username": "test@test.test"}
        response: Response = await test_client.post("/auth/jwt/login", data=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_bad_credentials(self, user_verified):
        test_client, user = user_verified
        data = {"username": "test@test.test", "password": "notterealpassword"}
        response: Response = await test_client.post("/auth/jwt/login", data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_login(self, user_verified):
        test_client, user = user_verified
        data = {"username": user["email"], "password": user["password"]}
        response: Response = await test_client.post("/auth/jwt/login", data=data)
        assert response.status_code == status.HTTP_200_OK

    async def test_user_auth_headers(self, user_auth_headers):
        test_client, user, headers = user_auth_headers
        response: Response = await test_client.get("/users/me", headers=headers)
        assert response.status_code == status.HTTP_200_OK
