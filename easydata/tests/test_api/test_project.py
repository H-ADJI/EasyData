'''
File: test_project.py
File Created: Tuesday, 25th October 2022 11:52:35 am
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
from fastapi import status
from easydata.tests.conftest import test_client, verified_user, auth_headers, project_data, created_project
from easydata.models import project
from httpx import AsyncClient, Response


async def test_projects_ressource_isprotected(test_client: AsyncClient, project_data: dict):

    response: Response = await test_client.post("project", json=project_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_create_project(test_client: AsyncClient, project_data: dict, auth_headers: dict):

    response: Response = await test_client.post("project", json=project_data, headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED


async def test_get_project(test_client: AsyncClient, project_data: dict, auth_headers: dict, created_project: project.Project_read):

    response: Response = await test_client.get(f"project/{created_project.id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()


async def test_update_project(test_client: AsyncClient, auth_headers: dict, created_project: project.Project_read):
    updated_field = {"title": "udpated title"}
    response: Response = await test_client.patch(f"project/{created_project.id}", json=updated_field, headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json().get("title") == updated_field.get("title")


async def test_delete_project(test_client: AsyncClient,auth_headers: dict, created_project: project.Project_read):

    response: Response = await test_client.delete(f"project/{created_project.id}", headers=auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response: Response = await test_client.get(f"project/{created_project.id}", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
