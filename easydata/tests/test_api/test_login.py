'''
File: test_login.py
File Created: Wednesday, 26th October 2022 3:01:31 pm
Author: KHALIL HADJI
-----
Copyright:  H-adji 2022
'''
import pytest
from fastapi import status
from fastapi.responses import Response
from easydata.tests.conftest import test_client, verified_user, auth_headers
from httpx import AsyncClient


class TestRegister:
    async def test_empty_body(self, test_client: AsyncClient):
        response: Response = await test_client.post("/auth/register", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_missing_email(self, test_client: AsyncClient):
        json = {"password": "morethan8"}
        response: Response = await test_client.post("/auth/register", json=json)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_missing_first_last_names(self, test_client: AsyncClient):
        json = {"email": "test@test.test", "password": "morethan8"}
        response: Response = await test_client.post("/auth/register", json=json)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_password_validator(self, test_client: AsyncClient):
        json = {"first_name": "first_test", "last_name": "last_test",
                "email": "testing@company.com", "password": ">than8"}
        response: Response = await test_client.post("/auth/register", json=json)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_existing_email(self, test_client: AsyncClient, verified_user):
        json = {"first_name": "first_test", "last_name": "last_test",
                "email": verified_user["email"], "password": "morethan8"}
        response = await test_client.post("/auth/register", json=json)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize("email", ["email.email", "email@email", "email.email.email"])
    async def test_invalid_email(self, test_client: AsyncClient, email):
        json = {"first_name": "first_test", "last_name": "last_test",
                "email": email, "password": "morethan8"}
        response = await test_client.post("/auth/register", json=json)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestLogin:
    async def test_not_existing_account(self, test_client: AsyncClient):
        data = {"username": "test@test.test", "password": "morethan8"}
        response: Response = await test_client.post("/auth/login", data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_missing_email(self, test_client: AsyncClient):
        data = {"password": "morethan8"}
        response: Response = await test_client.post("/auth/login", data=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_missing_password(self, test_client: AsyncClient):
        data = {"username": "test@test.test"}
        response: Response = await test_client.post("/auth/login", data=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_bad_credentials(self, test_client: AsyncClient):
        data = {"username": "test@test.test", "password": "notterealpassword"}
        response: Response = await test_client.post("/auth/login", data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_login(self, test_client: AsyncClient, verified_user):
        data = {"username": verified_user["email"],
                "password": verified_user["password"]}
        response: Response = await test_client.post("/auth/login", data=data)
        assert response.status_code == status.HTTP_200_OK

    async def test_user_auth_headers(self, test_client: AsyncClient, auth_headers):
        response: Response = await test_client.post("/auth/logout", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
