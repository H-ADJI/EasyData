
import pytest
from fastapi import status
from easydata.tests.conftest import test_client, verified_user, auth_headers, project_data, created_project, valid_scraping_plan, created_scraping_plan
from easydata.database.models import User
from easydata.models import project, scraping_plan
from httpx import AsyncClient, Response


async def test_scraping_plan_ressource_is_protected(test_client: AsyncClient, valid_scraping_plan: dict):

    response: Response = await test_client.post("plan", json=valid_scraping_plan)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_create_valide_scraping_plan(test_client: AsyncClient, valid_scraping_plan: dict, auth_headers: dict):

    response: Response = await test_client.post("plan", json=valid_scraping_plan, headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED


async def test_create_invalide_scraping_plan(test_client: AsyncClient, valid_scraping_plan: dict, auth_headers: dict):
    invalid_scraping_plan = valid_scraping_plan.get(
        "plan").update({"interecations": []})
    response: Response = await test_client.post("plan", json=invalid_scraping_plan, headers=auth_headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


async def test_get_scraping_plan(test_client: AsyncClient,  auth_headers: dict, created_scraping_plan: scraping_plan.Scraping_plan_read):

    response: Response = await test_client.get(f"plan/{created_scraping_plan.id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()


async def test_update_with_valid_plan(test_client: AsyncClient, auth_headers: dict, created_scraping_plan: scraping_plan.Scraping_plan_read):
    updated_field = {"title": "udpated plan title"}
    response: Response = await test_client.patch(f"plan/{created_scraping_plan.id}", json=updated_field, headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json().get("title") == updated_field.get("title")


async def test_update_with_invalid_plan(test_client: AsyncClient, auth_headers: dict, created_scraping_plan: scraping_plan.Scraping_plan_read):
    updated_field = {"plan": {"interaction": []}}
    response: Response = await test_client.patch(f"plan/{created_scraping_plan.id}", json=updated_field, headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED

async def test_delete_scraping_plan(test_client: AsyncClient,  auth_headers: dict, created_scraping_plan: scraping_plan.Scraping_plan_read):

    response: Response = await test_client.delete(f"plan/{created_scraping_plan.id}", headers=auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response: Response = await test_client.get(f"plan/{created_scraping_plan.id}", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
