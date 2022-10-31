'''
File: test_schedule.py
File Created: Wednesday, 26th October 2022 4:23:07 pm
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
import pytest
from fastapi import status
from nsa.tests.conftest import test_client, verified_user, auth_headers, project_data, created_project, valid_scraping_plan, created_scraping_plan, valid_scheduling_interval, soon_scheduling_exact_date, small_interval, soon_end_date_interval, soon_start_date_interval, valid_scheduling_exact_date
from nsa.database.models import User
from nsa.models import project, scraping_plan, scheduling
from httpx import AsyncClient, Response


async def test_scheduling_ressource_is_protected(test_client: AsyncClient, valid_scraping_plan: dict):
    response: Response = await test_client.get("/job")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_get_scheduled_job(test_client: AsyncClient, auth_headers: dict, created_job: scheduling.Scheduling_read):

    response: Response = await test_client.get(f"job/{created_job.id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()


async def test_delete_scheduled_job(test_client: AsyncClient, auth_headers: dict, created_job: scheduling.Scheduling_read):

    response: Response = await test_client.delete(f"job/{created_job.id}", headers=auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response: Response = await test_client.get(f"job/{created_job.id}", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


class TestValidSchedulingInterval:
    async def test_scheduling_interval_create(self, test_client: AsyncClient, auth_headers: dict, valid_scheduling_interval: dict):

        response: Response = await test_client.post("/job", json=valid_scheduling_interval, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED

    async def test_scheduling_small_interval(self, test_client: AsyncClient, auth_headers: dict, small_interval: dict):

        response: Response = await test_client.post("/job", json=small_interval, headers=auth_headers)
        assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE

    async def test_scheduling_interval_start_date_to_soon(self, test_client: AsyncClient, auth_headers: dict, soon_start_date_interval: dict):
        response: Response = await test_client.post("/job", json=soon_start_date_interval, headers=auth_headers)
        assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE

    async def test_scheduling_interval_end_date_to_soon(self, test_client: AsyncClient, auth_headers: dict, soon_end_date_interval: dict):
        response: Response = await test_client.post("/job", json=soon_end_date_interval, headers=auth_headers)
        assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE


class TestValidSchedulingExactDate:
    async def test_scheduling_exact_date_create(self, test_client: AsyncClient, auth_headers: dict, valid_scheduling_exact_date: dict):
        response: Response = await test_client.post("/job", json=valid_scheduling_exact_date, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED

    async def test_scheduling_date_to_soon(self, test_client: AsyncClient, auth_headers: dict, soon_scheduling_exact_date: dict):
        response: Response = await test_client.post("/job", json=soon_scheduling_exact_date, headers=auth_headers)
        assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
