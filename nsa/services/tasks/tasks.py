import datetime
import pytz
from typing import List
from celery.signals import worker_ready, worker_init, worker_process_init, beat_init
from nsa.database.models import Project, User, ScrapingPlan, JobScheduling, JobExecutionHistory
from nsa.database.database import db, DATABASE_URL
from nsa.models.scheduling import Interval_trigger
# from nsa.services.async_sync import async_to_sync
from nsa.services.base_task import BaseTask
from nsa.configs.configs import env_settings
from nsa.services.celery.celery import celery_app
from nsa.constants.enums import SchedulingJobStatus, JobHistoryStatus
from nsa.services.utils import construct_aio_threading, logger
from asgiref.sync import async_to_sync
from nsa.configs.configs import env_settings
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient
from beanie import init_beanie
DB_NAME = env_settings.MONGO_DB_NAME
MONGO_USER = env_settings.MONGO_INITDB_ROOT_USERNAME
MONGO_PASSWORD = env_settings.MONGO_INITDB_ROOT_PASSWORD
MONGO_HOST = env_settings.MONGO_HOST
MONGO_PORT = env_settings.MONGO_PORT

client = AsyncIOMotorClient(
    DATABASE_URL, uuidRepresentation="standard"
)

db = client[DB_NAME]


async def fetching_waiting_jobs():
    waiting_jobs = JobScheduling.find(
        JobScheduling.status == SchedulingJobStatus.WAITING)
    waiting_jobs_list = await waiting_jobs.to_list()
    return waiting_jobs_list


async def fetching_reoccurent_jobs():
    reoccuring_jobs = JobScheduling.find(
        JobScheduling.status == SchedulingJobStatus.REOCCURING)
    reoccuring_jobs_list = await reoccuring_jobs.to_list()
    return reoccuring_jobs_list


async def db_session():
    # init beanie doesnt work

    await init_beanie(
        database=db,
        document_models=[Project, User, ScrapingPlan, JobScheduling],
    )


# @worker_ready.connect
# def startup_celery_ecosystem(**kwargs):
#     """Setup Celery result backend so that tasks with
#     return result can communicate directly with websockets
#     """
#     logger.info('Startup celery worker process')
#     async_to_sync(db_session)()
#     logger.info('FINISHED : Startup celery worker process')


# @beat_init.connect
# def startup_celery_ecosystem(**kwargs):
#     """Setup Celery result backend so that tasks with
#     return result can communicate directly with websockets
#     """
#     logger.info('Startup celery beat process')
#     async_to_sync(db_session)()
#     logger.info('FINISHED : Startup celery beat process')

def check_waiting_job(job: JobScheduling):
    if job.next_run:
        now_time_stamp = datetime.datetime.now().timestamp()
        if now_time_stamp - 60*env_settings.JOB_INTERVAL_RANGE_SHIFT <= job.next_run <= now_time_stamp + 60*env_settings.JOB_INTERVAL_RANGE_SHIFT:
            return True
    else:
        raise AttributeError(
            "A job retrieved from the database should have the run date")


def compute_next_run(job: JobScheduling):
    next_run: datetime.datetime = job.next_run + datetime.timedelta(days=job.interval.days + job.interval.weeks*7,
                                                                    hours=job.interval.hours, minutes=job.interval.minutes, seconds=job.interval.seconds)
    # this is the case where the scheduled interval ends
    if next_run > job.interval.end_date:
        return None
    else:
        timezone = job.interval.timezone
        user_tz = pytz.timezone(timezone)
        next_run_with_tz = next_run.astimezone(user_tz)
        next_run_timestamp = next_run_with_tz.timestamp()
        return next_run_timestamp


async def update_job_status(job: JobScheduling, status: SchedulingJobStatus):
    job.status = status
    await job.replace()


async def update_next_run(job: JobScheduling, next_run: float):
    job.next_run = next_run
    await job.replace()


async def test_query_motor():
    client = AsyncIOMotorClient(
        DATABASE_URL, uuidRepresentation="standard"
    )

    db = client[DB_NAME]

    user_collection = db["User"]
    result = await user_collection.find().to_list(length=5)
    return result


@celery_app.task
def pool_db():
    logger.info("POOLING DB")
    # users = async_to_sync(test_query_motor)()
    # logger.info(f"POOLING  RESULTS {users}")

    # waiting_jobs: List[JobScheduling] = async_to_sync(fetching_waiting_jobs)()
    # recuring_jobs: List[JobScheduling] = async_to_sync(
    #     fetching_reoccurent_jobs)()

    # for job in waiting_jobs:
    #     if check_waiting_job(job):
    #         # if time arrive run job and create history with pending status
    #         run_jobs.delay(job.id)
    #         job_history = JobExecutionHistory(
    #             job_id=job.id, worker_id=None, created_at=datetime.datetime.now(), status=JobHistoryStatus.PENDING)
    #         job_history.save()
    #         #  if interval then compute next run and change status to recurring or done
    #         if job.interval:
    #             next_run = compute_next_run(job=job)
    #             if next_run:
    #                 update_job_status(
    #                     job=job, status=SchedulingJobStatus.REOCCURING)
    #             else:
    #                 update_job_status(job=job, status=SchedulingJobStatus.DONE)

    #         #  if exact date then change status done
    #         else:
    #             update_job_status(job=job, status=SchedulingJobStatus.DONE)
    # for job in recuring_jobs:
    #     if check_waiting_job(job):
    #         run_jobs.delay(job.id)
    #         next_run = compute_next_run(job=job)
    #         job_history = JobExecutionHistory(
    #             job_id=job.id, worker_id=None, created_at=datetime.datetime.now(), status=JobHistoryStatus.PENDING)
    #         if next_run:
    #             update_job_status(
    #                 job=job, status=SchedulingJobStatus.REOCCURING)
    #         else:
    #             update_job_status(job=job, status=SchedulingJobStatus.DONE)


@celery_app.task
def run_jobs(
    job_id
):
    # when the job is consumed by a worker insert datetime
    job_history: JobExecutionHistory = JobExecutionHistory.find_one(
        JobExecutionHistory.job_id == job_id)
    job_history.claimed_at = datetime.datetime.now()
    job_history.save()

    # call the scraping methods here
    # after scraping save data to db

    # when scraping ends insert  completion datetime
    job_history: JobExecutionHistory = JobExecutionHistory.find_one(
        JobExecutionHistory.job_id == job_id)
    job_history.ended_at = datetime.datetime.now()
    job_history.save()
