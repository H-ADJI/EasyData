from threading import Thread, Event
from typing import Coroutine, Awaitable
from celery import Celery
from nsa.configs.celery_config import CELERY_CONFIG
from nsa.constants.enums import SchedulingJobStatus
from nsa.database.models import JobScheduling, ScrapingPlan
from beanie.operators import And
from celery import Task
import asyncio
celery_app: Celery = Celery(
    'tasks', broker='amqp://guest:guest@rabbitmq:5672//')


celery_app.conf.update(CELERY_CONFIG)


async def fetching_waiting_jobs():
    print("this is running async")
    waiting_jobs = JobScheduling.find(
        JobScheduling.input_data == {})
    waiting_jobs_list = await waiting_jobs.to_list()
    return waiting_jobs_list


@celery_app.task
def pool_db():
    print("fetching db for tasks to run")
