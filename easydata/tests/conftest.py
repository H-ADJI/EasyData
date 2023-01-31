'''
File: conftest.py
File Created: Wednesday, 26th October 2022 10:19:38 am
Author: KHALIL HADJI
-----
Copyright:  HENCEFORTH 2022
'''
from datetime import datetime, timedelta
import motor.motor_asyncio
from easydata.configs.configs import env_settings
from easydata.constants.enums import SchedulingJobStatus
import asyncio
from easydata.database.models import Project, User, ScrapingPlan, JobScheduling, JobExecutionHistory
from easydata.models import project, scraping_plan, scheduling
from beanie import init_beanie
from fastapi import FastAPI
from typing import Generator
from httpx import AsyncClient, Response
import pytest
from easydata.main import get_app
import pytz
from beanie import PydanticObjectId
from freezegun import freeze_time
from easydata.services.utils import construct_aio_threading, destruct_aio_threading
from easydata.services.base_task import BaseTask
from easydata.services.async_sync import async_to_sync

FROZEN_TIME = "2022-07-15T12:30:00"

BASE_URL: str = 'http://localhost:8000/api'



@pytest.fixture()
async def celery_mongo_is_ready(aio_thread):
    DB_NAME = env_settings.MONGO_TEST_DB_NAME
    MONGO_USER = env_settings.MONGO_INITDB_ROOT_USERNAME
    MONGO_PASSWORD = env_settings.MONGO_INITDB_ROOT_PASSWORD
    MONGO_HOST = env_settings.MONGO_HOST
    MONGO_PORT = env_settings.MONGO_PORT
    DATABASE_URL = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}"
    client: motor.motor_asyncio.core.AgnosticClient = motor.motor_asyncio.AsyncIOMotorClient(
        DATABASE_URL, uuidRepresentation="standard"
    )
    db = client[DB_NAME]
    async_to_sync(aio_thread=BaseTask.aio_thread, coroutine=init_beanie(
        database=db,
        document_models=[Project, User, ScrapingPlan,
                         JobScheduling, JobExecutionHistory],
    ))
    yield
    async_to_sync(aio_thread=BaseTask.aio_thread,
                  coroutine=client.drop_database(db))


@pytest.fixture()
async def mongo_is_ready(aio_thread):
    DB_NAME = env_settings.MONGO_TEST_DB_NAME
    MONGO_USER = env_settings.MONGO_INITDB_ROOT_USERNAME
    MONGO_PASSWORD = env_settings.MONGO_INITDB_ROOT_PASSWORD
    MONGO_HOST = env_settings.MONGO_HOST
    MONGO_PORT = env_settings.MONGO_PORT
    DATABASE_URL = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}"
    client: motor.motor_asyncio.core.AgnosticClient = motor.motor_asyncio.AsyncIOMotorClient(
        DATABASE_URL, uuidRepresentation="standard"
    )
    db = client[DB_NAME]
    await init_beanie(
        database=db,
        document_models=[Project, User, ScrapingPlan,
                         JobScheduling, JobExecutionHistory],
    )
    yield
    await client.drop_database(db)


@ pytest.fixture(scope='function')
def app(mongo_is_ready) -> FastAPI:
    """Return instance of the fast API instance
    """
    return get_app(testing=True)


@ pytest.fixture(scope="session")
def event_loop():
    # get the current event loop
    loop = asyncio.get_event_loop()

    yield loop


@ pytest.fixture
async def test_client(app: FastAPI) -> Generator:
    """Return fast api test client
    """
    async with AsyncClient(app=app, base_url=BASE_URL, follow_redirects=True) as c:
        yield c


@ pytest.fixture
async def verified_user(test_client: AsyncClient) -> Generator:
    """Create a dummy user
    """
    user = {
        "email": "test@company.com",
        "password": "test_password",
        "first_name": "test",
        "last_name": "user"
    }
    response: Response = await test_client.post("/auth/register", json=user)
    yield user


@ pytest.fixture
async def auth_headers(test_client: AsyncClient, verified_user: dict):
    """ get auth token """
    data = {"username": f"{verified_user.get('email')}",
            "password": f"{verified_user.get('password')}"
            }

    # Authenticate admin
    response: Response = await test_client.post("/auth/login", data=data)
    # get access token
    token = response.json().get("access_token")
    # authorization header
    headers = {"Authorization": f"Bearer {token}"}
    # yield headers
    yield headers


@ pytest.fixture
def project_data():
    project_data = {
        "description": "some description",
        "title": "some title",
        "url": "https://some-random-url.io",
        "tags": [
            "#1"
            "#2"
            "#3",
        ],
        "image": "some image url"
    }
    yield project_data


@pytest.fixture
async def created_project(test_client, auth_headers, project_data):
    response: Response = await test_client.post("project", json=project_data, headers=auth_headers)

    yield project.Project_read(**response.json())


@pytest.fixture
def valid_scraping_plan():
    scraping_plan = {
        "title": "unit testing",
        "website": "test_website.com",
        "plan": {
            "interactions": [
                {
                    "do_once": "visit_page",
                    "description": "visiting the home page for the website",
                    "inputs": {
                        "url": "https://www.test_website.com/"
                    }
                }
            ]
        }
    }
    yield scraping_plan


@pytest.fixture
async def created_scraping_plan(test_client, auth_headers, valid_scraping_plan):
    response: Response = await test_client.post("plan", json=valid_scraping_plan, headers=auth_headers)

    yield scraping_plan.Scraping_plan_read(**response.json())


@pytest.fixture
async def created_job(test_client: AsyncClient, auth_headers, valid_scheduling_interval):
    response: Response = await test_client.post("job", json=valid_scheduling_interval, headers=auth_headers)
    yield scheduling.Scheduling_read(**response.json())


@pytest.fixture
def valid_scheduling_interval():
    start_time = datetime.now(tz=pytz.timezone(
        "Africa/Casablanca")) + timedelta(minutes=env_settings.MIN_JOB_SCHEDULING_OFFSET + 5)
    end_time = start_time + \
        timedelta(minutes=env_settings.MIN_JOB_SCHEDULING_OFFSET + 5)
    job_scheduling = {
        "plan_id": "635f9a89538ace78a21e010a",
        "interval": {
            "hours": 1,
            "start_date": start_time.isoformat(),
            "end_date": end_time.isoformat(),
            "timezone": "Africa/Casablanca"
        }
    }
    yield job_scheduling


@pytest.fixture
def soon_end_date_interval():
    start_time = datetime.now(tz=pytz.timezone(
        "Africa/Casablanca")) + timedelta(minutes=env_settings.MIN_JOB_SCHEDULING_OFFSET*5)
    end_time = start_time + \
        timedelta(minutes=env_settings.MIN_JOB_SCHEDULING_OFFSET/2)
    job_scheduling = {
        "plan_id": "635f9a89538ace78a21e010a",
        "interval": {
            "hours": 1,
            "start_date": start_time.isoformat(),
            "end_date": end_time.isoformat(),
            "timezone": "Africa/Casablanca"
        }
    }
    yield job_scheduling


@pytest.fixture
def soon_start_date_interval():
    start_time = datetime.now(tz=pytz.timezone(
        "Africa/Casablanca")) + timedelta(minutes=env_settings.MIN_JOB_SCHEDULING_OFFSET/2)
    end_time = start_time + \
        timedelta(minutes=env_settings.MIN_JOB_SCHEDULING_OFFSET*5)
    job_scheduling = {
        "plan_id": "635f9a89538ace78a21e010a",
        "interval": {
            "hours": 1,
            "start_date": start_time.isoformat(),
            "end_date": end_time.isoformat(),
            "timezone": "Africa/Casablanca"
        }
    }
    yield job_scheduling


@pytest.fixture
def small_interval():
    start_time = datetime.now(tz=pytz.timezone(
        "Africa/Casablanca")) + timedelta(minutes=env_settings.MIN_JOB_SCHEDULING_OFFSET*5)
    end_time = start_time + \
        timedelta(minutes=env_settings.MIN_JOB_SCHEDULING_OFFSET*5)
    job_scheduling = {
        "plan_id": "635f9a89538ace78a21e010a",
        "interval": {
            "minutes": env_settings.MIN_ACCEPTED_INTERVAL/5,
            "start_date": start_time.isoformat(),
            "end_date": end_time.isoformat(),
            "timezone": "Africa/Casablanca"
        }
    }
    yield job_scheduling


@ pytest.fixture
def valid_scheduling_exact_date():
    date = datetime.now(tz=pytz.timezone(
        "Africa/Casablanca")) + timedelta(minutes=env_settings.MIN_JOB_SCHEDULING_OFFSET*5)
    job_scheduling = {
        "plan_id": "635f9a89538ace78a21e010a",
        "exact_date": {
            "date": date.isoformat(),
            "timezone": "Africa/Casablanca"
        },
        "input_data": {}
    }
    yield job_scheduling


@ pytest.fixture
def soon_scheduling_exact_date():
    date = datetime.now(tz=pytz.timezone(
        "Africa/Casablanca")) + timedelta(minutes=env_settings.MIN_JOB_SCHEDULING_OFFSET/5)
    job_scheduling = {
        "plan_id": "635f9a89538ace78a21e010a",
        "exact_date": {
            "date": date.isoformat(),
            "timezone": "Africa/Casablanca"
        },
        "input_data": {}
    }
    yield job_scheduling



def generate_date(date: datetime, offset: int):
    return date.replace(tzinfo=None) + timedelta(minutes=offset)


@ pytest.fixture(scope="session")
def aio_thread():
    construct_aio_threading(aio_thread=BaseTask.aio_thread)
    yield
    destruct_aio_threading(aio_thread=BaseTask.aio_thread)


@ pytest.fixture()
async def insert_exact_date_jobs():
    with freeze_time(FROZEN_TIME):
        date = datetime.now(tz=pytz.timezone("Africa/Casablanca"))

        jobs = [
            JobScheduling(** {
                "id": PydanticObjectId(f"555f9a89538ace78a21e01{i + 1}a"),
                "owner_id": PydanticObjectId("666f9a89538ace78a21e010a"),
                "plan_id": PydanticObjectId("777f9a89538ace78a21e010a"),
                "exact_date": {
                    # dates would be : 2022-07-15T12:29:00,  2022-07-15T12:30:00 and 2022-07-15T12:31:00

                    "date": generate_date(offset=i, date=date),
                    "timezone": "Africa/Casablanca"
                },
                # next run is automatically set to date
                "next_run": generate_date(offset=i, date=date),
                "input_data": {},
                "status": SchedulingJobStatus.WAITING
            }) for i in range(-1, 2)
        ]
        async_to_sync(aio_thread=BaseTask.aio_thread,
                      coroutine=JobScheduling.insert_many(jobs))
        yield
        # here delete the jobs
        for job in jobs:
            async_to_sync(aio_thread=BaseTask.aio_thread,
                          coroutine=JobScheduling.find(JobScheduling.id == job.id).delete())


@ pytest.fixture()
async def insert_reoccurent_jobs():
    with freeze_time(FROZEN_TIME):
        date = datetime.now(tz=pytz.timezone("Africa/Casablanca"))
        jobs = [
            JobScheduling(**{
                "id": PydanticObjectId(f"555f9a89538ace78a21e01{i+5}b"),
                "owner_id": PydanticObjectId("666f9a89538ace78a21e010a"),
                "plan_id": PydanticObjectId("777f9a89538ace78a21e010a"),
                "interval": {
                    "minutes": env_settings.MIN_ACCEPTED_INTERVAL,
                    # start dates would be : 2022-07-15T12:28:00, 2022-07-15T12:29:00,  2022-07-15T12:30:00 and 2022-07-15T12:31:00
                    "start_date": generate_date(date=date, offset=i),
                    # end dates would be : 2022-07-15T12:30:00, 2022-07-15T12:31:00,  2022-07-15T12:32:00 and 2022-07-15T12:33:00
                    "end_date": generate_date(date=date, offset=2+i),
                    "timezone": "Africa/Casablanca"
                },
                # next run is automatically set to start_date
                "next_run":  generate_date(date=date, offset=i),
                "input_data": {},
                "status": SchedulingJobStatus.WAITING
            })
            for i in range(-2, 2)
        ]
        async_to_sync(aio_thread=BaseTask.aio_thread,
                      coroutine=JobScheduling.insert_many(jobs))
        yield 
        # here delete the jobs
        for job in jobs:
            async_to_sync(aio_thread=BaseTask.aio_thread,
                          coroutine=JobScheduling.find(JobScheduling.id == job.id).delete())
