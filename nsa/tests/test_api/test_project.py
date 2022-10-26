'''
File: test_project.py
File Created: Tuesday, 25th October 2022 11:52:35 am
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
from fastapi.testclient import TestClient
from nsa.main import app
from nsa.models.user import UserRead
from nsa.database.models import User
from nsa.tests.conftest import test_db_session
test_client = TestClient(app)


def test_read_main():

    response = test_client.get("/")
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}


def test_create_user(test_db_session):
    payload = {
        "email": "test@example.com",
        "password": "test_password",
        "first_name": "test",
        "last_name": "test"
    }
    # response = test_client.post("/api/user/register", json=payload)
    # assert response.status_code == 201
    # user = UserRead(**response.json())
    # print(response.json())
    # assert user.email == payload.get("email")
