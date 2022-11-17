
import datetime
from typing import List, Union
from celery.signals import worker_ready, beat_init
from nsa.database.models import JobScheduling, JobExecutionHistory, ScrapedData
from nsa.models.scheduling import Exact_date_trigger_read, Interval_trigger_read
from nsa.services.async_sync import async_to_sync
from nsa.services.base_task import BaseTask
from nsa.configs.configs import env_settings
from nsa.services.celery.celery import celery_app
from nsa.constants.enums import SchedulingJobStatus, JobHistoryStatus
from nsa.services.utils import construct_aio_threading, logger, db_session, simulate_user_current_time
from beanie import PydanticObjectId, Document
from nsa.core.execute import GeneralPurposeScraper
from nsa.core.engine import Browser
DB_NAME = env_settings.MONGO_DB_NAME
MONGO_USER = env_settings.MONGO_INITDB_ROOT_USERNAME
MONGO_PASSWORD = env_settings.MONGO_INITDB_ROOT_PASSWORD
MONGO_HOST = env_settings.MONGO_HOST
MONGO_PORT = env_settings.MONGO_PORT
TESTING = env_settings.TESTING


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


@beat_init.connect
def startup_celery_beat(**kwargs):
    """Setup Celery result backend so that tasks with
    return result can communicate directly with websockets
    """
    logger.info('Startup celery beat process')
    construct_aio_threading(BaseTask.aio_thread)
    async_to_sync(aio_thread=BaseTask.aio_thread, coroutine=db_session())
    logger.info('FINISHED : Startup celery beat process')


@worker_ready.connect
def startup_celery_worker(**kwargs):
    """Setup Celery result backend so that tasks with
    return result can communicate directly with websockets
    """
    logger.info('Startup celery worker process')
    # Starting the Aiothread (Thread that manages the event loop)
    construct_aio_threading(BaseTask.aio_thread)
    async_to_sync(aio_thread=BaseTask.aio_thread, coroutine=db_session())
    logger.info('FINISHED : Startup celery worker process')
    global browser
    browser = async_to_sync(
        aio_thread=BaseTask.aio_thread, coroutine=Browser())


def check_pending_job(job: JobScheduling):
    if job.next_run:
        trigger: Union[Interval_trigger_read,
                       Exact_date_trigger_read] = job.interval or job.exact_date

        now_time = simulate_user_current_time(
            user_tz=trigger.timezone)
        if job.next_run <= now_time:
            return True
    return False


def compute_next_run(job: JobScheduling):
    next_run: datetime.datetime = job.next_run + datetime.timedelta(days=job.interval.days + job.interval.weeks*7,
                                                                    hours=job.interval.hours, minutes=job.interval.minutes, seconds=job.interval.seconds)
    now_time = simulate_user_current_time(
        user_tz=job.interval.timezone)
    # this is the case where the scheduled interval ends

    if next_run > job.interval.end_date or job.interval.end_date <= now_time:
        return None
    return next_run


async def update_job_status(job: JobScheduling, status: SchedulingJobStatus, next_run: datetime.datetime = None):
    job.status = status
    job.next_run = next_run
    await job.save()


@celery_app.task
def pool_db():
    logger.info(
        f"POOLING DB AT {datetime.datetime.now().replace(tzinfo=None)}")
    waiting_jobs: List[JobScheduling] = async_to_sync(
        aio_thread=BaseTask.aio_thread, coroutine=fetching_waiting_jobs())
    recuring_jobs: List[JobScheduling] = async_to_sync(
        aio_thread=BaseTask.aio_thread, coroutine=fetching_reoccurent_jobs())
    if waiting_jobs:
        for job in waiting_jobs:
            if check_pending_job(job):
                # if time arrive run job and create history with pending status
                job_history = JobExecutionHistory(
                    job_id=job.id, created_at=datetime.datetime.now(), status=JobHistoryStatus.PENDING)
                async_to_sync(
                    aio_thread=BaseTask.aio_thread, coroutine=job_history.save())
                if TESTING:
                    run_jobs.s(str(job.id)).apply()
                else:
                    run_jobs.delay(str(job.id))

                #  if interval then compute next run and change status to recurring or done

                if job.interval:
                    next_run = compute_next_run(job=job)
                    if next_run:
                        async_to_sync(
                            aio_thread=BaseTask.aio_thread, coroutine=update_job_status(
                                job=job, status=SchedulingJobStatus.REOCCURING, next_run=next_run))

                    else:
                        async_to_sync(
                            aio_thread=BaseTask.aio_thread, coroutine=update_job_status(
                                job=job, status=SchedulingJobStatus.DONE))

                #  if exact date then change status done
                else:

                    async_to_sync(aio_thread=BaseTask.aio_thread, coroutine=update_job_status(
                        job=job, status=SchedulingJobStatus.DONE))
    if recuring_jobs:
        for job in recuring_jobs:
            if check_pending_job(job):
                # if time arrive run job and create history with pending status
                job_history = JobExecutionHistory(
                    job_id=job.id, created_at=datetime.datetime.now(), status=JobHistoryStatus.PENDING)
                async_to_sync(
                    aio_thread=BaseTask.aio_thread, coroutine=job_history.save())
                if TESTING:
                    run_jobs.s(str(job.id)).apply()
                else:
                    run_jobs.delay(str(job.id))

                next_run = compute_next_run(job=job)

                if next_run:
                    async_to_sync(
                        aio_thread=BaseTask.aio_thread, coroutine=update_job_status(
                            job=job, status=SchedulingJobStatus.REOCCURING, next_run=next_run))
                else:
                    async_to_sync(
                        aio_thread=BaseTask.aio_thread, coroutine=update_job_status(
                            job=job, status=SchedulingJobStatus.DONE))


async def find_by_id(model: Document, id: PydanticObjectId):
    obj = await model.find_one(model.id == id)
    return obj


async def find_by_job_id(model: JobExecutionHistory, id: PydanticObjectId):
    obj = await model.find_one(model.job_id == id)
    return obj


@celery_app.task
def run_jobs(job_id: str):
    #  THIS IS A TEMPORARY VARIABLE TO DIRECTLY ACCESS PLAN WITHOUT THE NEED TO SAVE IT TO DB ---- TODO: remove later
    plan = {
        "description": "retrieving most viewed articles on hespress",
        "interactions": [
            {
                "do_once": "navigate",
                "inputs": {
                    "url": "https://www.hespress.com/all?most_viewed"
                }
            },
            {
                "do_until": {
                    "single":
                    {
                        "condition_type": "max_element_count",
                        "elements_selector": "//div[@class='cover']//div[@class='card-body']//small",
                        "count": 50
                    }
                },
                "interactions": [
                    {
                        "do_once": "scrape_page",
                        "inputs": {
                            "selectors": [
                                "//div[@class='cover']"
                            ],
                            "include_order": True,
                            "data_to_get": [
                                {
                                    "field_alias": "title",
                                    "kind": "attribute",
                                    "relocate": [
                                            "//a"
                                    ],
                                    "name": [
                                        "title"
                                    ]
                                },
                                {
                                    "field_alias": "image",
                                    "kind": "attribute",
                                    "relocate": [
                                            "//a//img"
                                    ],
                                    "name": [
                                        "src"
                                    ]
                                },
                                {
                                    "field_alias": "date",
                                    "kind": "text",
                                    "relocate": [
                                            "//div[@class='card-body']//small"
                                    ],
                                    "processing": [
                                        {
                                            "function": "arabic_datetime",
                                            "inputs": {
                                                "year_pattern": "\\d{4}",
                                                "months_pattern": "[ا-ي]+(?= \\d{4})",
                                                "days_pattern": "\\b(?<!:)\\d{1,2}(?!:)\\b",
                                                "hours_pattern": "\\d{2}(?=:)",
                                                "minutes_pattern": "(?<=:)\\d{2}"
                                            }
                                        }
                                    ]
                                },
                                {
                                    "field_alias": "url",
                                    "kind": "attribute",
                                    "relocate": [
                                            "//a"
                                    ],
                                    "name": [
                                        "href"
                                    ],
                                    "processing": [
                                        {
                                            "function": "decode_url"
                                        }
                                    ]
                                },
                                {
                                    "field_alias": "extra",
                                    "kind": "nested_field",
                                    "data_to_get": [
                                            {
                                                "field_alias": "category",
                                                "kind": "text",
                                                "relocate": [
                                                    "//span[@class[contains( ., 'cat')]]"
                                                ],
                                                "processing": [
                                                    {
                                                        "function": "strip_whitespaces"
                                                    }
                                                ]
                                            }
                                    ]
                                }
                            ]
                        }
                    },
                    {
                        "do_once": "use_keyboard",
                        "inputs": {
                            "keys": [
                                "PageDown"
                            ]
                        }
                    },
                    {
                        "do_once": "wait_for_dom_mutation",
                        "inputs": {
                            "selectors": [
                                "//div[@class='cover']//div[@class='card-body']//small"
                            ]
                        }
                    }
                ]
            }
        ]
    }
    # when the job is consumed by a worker insert datetime
    job_id = PydanticObjectId(oid=job_id)
    job_history: JobExecutionHistory = async_to_sync(
        aio_thread=BaseTask.aio_thread, coroutine=find_by_job_id(model=JobExecutionHistory, id=job_id))

    job_history.claimed_at = datetime.datetime.now()
    async_to_sync(
        aio_thread=BaseTask.aio_thread, coroutine=job_history.save())

    # call the scraping methods here
    job: JobScheduling = async_to_sync(
        aio_thread=BaseTask.aio_thread, coroutine=find_by_id(model=JobScheduling, id=job_id))

    # retrieve scraping plan and execute it
    scraper = GeneralPurposeScraper()
    data: dict = async_to_sync(
        aio_thread=BaseTask.aio_thread, coroutine=scraper.scrape(browser=browser, plan=plan))
    articles = data.get("scraped_data")
    date_of_scraping = data.get("date_of_scraping")
    total = data.get("total")
    state = data.get("state")
    took = data.get("took")
    error = data.get("error_trace")
    data: ScrapedData = ScrapedData(articles=articles, date_of_scraping=date_of_scraping,
                                    job_id=job_id, state=state, took=took, total=total)
    async_to_sync(
        aio_thread=BaseTask.aio_thread, coroutine=data.save())
    # after scraping save data to db
    # when scraping ends insert completion datetime and error if there is any
    job_history.ended_at = datetime.datetime.now()
    if error:
        job_history.status = JobHistoryStatus.FAILED
    else:
        job_history.status = JobHistoryStatus.SUCCESS
    job_history.execution_error = error
    async_to_sync(
        aio_thread=BaseTask.aio_thread, coroutine=job_history.save())
