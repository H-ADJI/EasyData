from celery.signals import worker_ready
from nsa.database.models import JobScheduling
# from nsa.services.async_sync import async_to_sync
from nsa.services.base_task import BaseTask
from nsa.services.celery.celery import celery_app
from nsa.services.utils import construct_aio_threading, logger
from asgiref.sync import async_to_sync

async def fetching_waiting_jobs():
    print("this is running async")
    waiting_jobs = JobScheduling.find(
        JobScheduling.input_data == {})
    waiting_jobs_list = await waiting_jobs.to_list()
    return waiting_jobs_list


@worker_ready.connect
def startup_celery_ecosystem(**kwargs):
    """Setup Celery result backend so that tasks with
    return result can communicate directly with websockets
    """
    logger.info('Startup celery ecosystem')
    # start the aio threading
    # construct_aio_threading(BaseTask.aio_thread)
    # connect to broadcast
    # async_to_sync(BaseTask.aio_thread, BaseTask.broadcast.connect())


@celery_app.task
def pool_db():
    logger.info("POOLING DB")
    async_to_sync(fetching_waiting_jobs())
