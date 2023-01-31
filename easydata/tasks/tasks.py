import datetime
from typing import List, Union
from celery.signals import worker_ready, beat_init
from easydata.database.models import JobScheduling, JobExecutionHistory, ScrapedData, ScrapingPlan
from easydata.models.scheduling import Exact_date_trigger_read, Interval_trigger_read
from easydata.services.async_sync import async_to_sync
from easydata.services.base_task import BaseTask
from easydata.configs.configs import env_settings
from easydata.services.celery.celery import celery_app
from easydata.constants.enums import SchedulingJobStatus, JobHistoryStatus
from easydata.services.scheduling import check_pending_job, compute_next_run, fetching_job_by_status
from easydata.services.utils import construct_aio_threading, logger, db_session
from beanie import PydanticObjectId, Document
from easydata.core.execute import GeneralPurposeScraper
from easydata.core.engine import Browser
DB_NAME = env_settings.MONGO_DB_NAME
MONGO_USER = env_settings.MONGO_INITDB_ROOT_USERNAME
MONGO_PASSWORD = env_settings.MONGO_INITDB_ROOT_PASSWORD
MONGO_HOST = env_settings.MONGO_HOST
MONGO_PORT = env_settings.MONGO_PORT
TESTING = env_settings.TESTING


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


async def update_job_status(job: JobScheduling, status: SchedulingJobStatus, next_run: datetime.datetime = None):
    job.status = status
    job.next_run = next_run
    await job.save()


def push_job_to_queue(job_id: PydanticObjectId, input_data_id: PydanticObjectId = None):
    kwargs = {"job_id": str(job_id)}
    if input_data_id:
        kwargs.update({"input_data_id": str(input_data_id)})
    if TESTING:
        run_jobs.s(job_id=str(job_id)).apply()
    else:
        run_jobs.apply_async(kwargs=kwargs)


@celery_app.task
def pool_db():
    logger.info(
        f"POOLING DB AT {datetime.datetime.now().replace(tzinfo=None)}")
    waiting_jobs: List[JobScheduling] = async_to_sync(
        aio_thread=BaseTask.aio_thread, coroutine=fetching_job_by_status(status=SchedulingJobStatus.WAITING))
    recuring_jobs: List[JobScheduling] = async_to_sync(
        aio_thread=BaseTask.aio_thread, coroutine=fetching_job_by_status(status=SchedulingJobStatus.REOCCURING))
    ready_jobs: List[JobScheduling] = async_to_sync(
        aio_thread=BaseTask.aio_thread, coroutine=fetching_job_by_status(status=SchedulingJobStatus.READY))
    if ready_jobs:
        for job in ready_jobs:
            job_history = JobExecutionHistory(
                job_id=job.id, created_at=datetime.datetime.now(), status=JobHistoryStatus.PENDING)
            async_to_sync(
                aio_thread=BaseTask.aio_thread, coroutine=job_history.save())
            push_job_to_queue(job_id=job.id, input_data_id=job.input_data_id)
            async_to_sync(
                aio_thread=BaseTask.aio_thread, coroutine=update_job_status(
                    job=job, status=SchedulingJobStatus.DONE))
    if waiting_jobs:
        for job in waiting_jobs:
            if check_pending_job(job):
                # if time arrive run job and create history with pending status
                job_history = JobExecutionHistory(
                    job_id=job.id, created_at=datetime.datetime.now(), status=JobHistoryStatus.PENDING)
                async_to_sync(
                    aio_thread=BaseTask.aio_thread, coroutine=job_history.save())
                push_job_to_queue(job_id=job.id)

                if job.interval or job.cron:
                    next_run = compute_next_run(job=job)
                    if next_run:
                        async_to_sync(
                            aio_thread=BaseTask.aio_thread, coroutine=update_job_status(
                                job=job, status=SchedulingJobStatus.REOCCURING, next_run=next_run))
                    else:
                        async_to_sync(
                            aio_thread=BaseTask.aio_thread, coroutine=update_job_status(
                                job=job, status=SchedulingJobStatus.DONE))

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
                push_job_to_queue(job_id=job.id)
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
def run_jobs(job_id: str, input_data_id: str = None):
    # ------------------parsing IDs to pydantic class for db queries--------
    job_id = PydanticObjectId(oid=job_id)
    urls = None
    if input_data_id:
        input_data_id = PydanticObjectId(oid=input_data_id)
        input_data: ScrapedData = async_to_sync(
            aio_thread=BaseTask.aio_thread, coroutine=find_by_id(model=ScrapedData, id=PydanticObjectId(oid=input_data_id)))
        urls = [article.url for article in input_data.articles]
    # ----------------------------------------------------------------------

    # ------------------ logging when the job was consumed ------------------
    job_history: JobExecutionHistory = async_to_sync(
        aio_thread=BaseTask.aio_thread, coroutine=find_by_job_id(model=JobExecutionHistory, id=job_id))
    job_history.claimed_at = datetime.datetime.now()
    async_to_sync(
        aio_thread=BaseTask.aio_thread, coroutine=job_history.save())
    # ----------------------------------------------------------------------

    # ------------------ retrieve scraping plan and execute it -------------
    job: JobScheduling = async_to_sync(
        aio_thread=BaseTask.aio_thread, coroutine=find_by_id(model=JobScheduling, id=job_id))
    scraper = GeneralPurposeScraper(browser=browser)
    plan: ScrapingPlan = async_to_sync(
        aio_thread=BaseTask.aio_thread, coroutine=find_by_id(model=ScrapingPlan, id=job.plan_id))
    # call the scraping methods here
    data: dict = async_to_sync(
        aio_thread=BaseTask.aio_thread, coroutine=scraper.scrape(plan=plan.plan, input_data={"urls": urls}))
    # ----------------------------------------------------------------------

    # ------------------ after scraping save data to db --------------------
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
    # ----------------------------------------------------------------------

    # -------- logging completion datetime and error if there is any -------
    job_history.ended_at = datetime.datetime.now()
    if error:
        job_history.status = JobHistoryStatus.FAILED
        job_history.execution_error = error
    else:
        job_history.status = JobHistoryStatus.SUCCESS

    async_to_sync(
        aio_thread=BaseTask.aio_thread, coroutine=job_history.save())
    # ----------------------------------------------------------------------

    if job.child_id:
        child_job: JobScheduling = async_to_sync(
            aio_thread=BaseTask.aio_thread, coroutine=find_by_id(model=JobScheduling, id=job.child_id))
        child_job.status = SchedulingJobStatus.READY
        child_job.input_data_id = data.id
        async_to_sync(
            aio_thread=BaseTask.aio_thread, coroutine=child_job.save())
