'''
File: test_celery_tasks.py
File Created: Tuesday, 1st November 2022 9:59:01 am
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
from nsa.tasks import tasks
from freezegun import freeze_time
from nsa.constants.enums import SchedulingJobStatus, JobHistoryStatus

from pytest import MonkeyPatch
import pytz
from nsa.tests.conftest import FROZEN_TIME, generate_date, mongo_is_ready, test_client, aio_thread, insert_reoccurent_jobs, insert_exact_date_jobs
from nsa.database.models import JobExecutionHistory, JobScheduling
from nsa.services.async_sync import async_to_sync
from nsa.services.base_task import BaseTask


async def test_pool_db_with_reoccurent_job(monkeypatch: MonkeyPatch, celery_mongo_is_ready, aio_thread, insert_reoccurent_jobs):
    with freeze_time(FROZEN_TIME):
        # task call
        tasks.pool_db.apply()
        waiting_jobs = async_to_sync(
            aio_thread=BaseTask.aio_thread, coroutine=JobScheduling.find(JobScheduling.status == SchedulingJobStatus.WAITING).to_list())
        assert len(waiting_jobs) == 1
        done_jobs = async_to_sync(
            aio_thread=BaseTask.aio_thread, coroutine=JobScheduling.find(JobScheduling.status == SchedulingJobStatus.DONE).to_list())
        assert len(done_jobs) == 1
        reoccuring_jobs = async_to_sync(
            aio_thread=BaseTask.aio_thread, coroutine=JobScheduling.find(JobScheduling.status == SchedulingJobStatus.REOCCURING).to_list())
        assert len(reoccuring_jobs) == 2
        job_history = async_to_sync(
            aio_thread=BaseTask.aio_thread, coroutine=JobExecutionHistory.find(JobExecutionHistory.status == JobHistoryStatus.SUCCESS).to_list())
        assert len(job_history) == 3


async def test_pool_db_with_exact_date_job(monkeypatch: MonkeyPatch, celery_mongo_is_ready, aio_thread, insert_exact_date_jobs):
    with freeze_time(FROZEN_TIME):
        # task call
        tasks.pool_db.apply()
        waiting_jobs = async_to_sync(
            aio_thread=BaseTask.aio_thread, coroutine=JobScheduling.find(JobScheduling.status == SchedulingJobStatus.WAITING).to_list())
        assert len(waiting_jobs) == 1
        done_jobs = async_to_sync(
            aio_thread=BaseTask.aio_thread, coroutine=JobScheduling.find(JobScheduling.status == SchedulingJobStatus.DONE).to_list())
        assert len(done_jobs) == 2
        job_history = async_to_sync(
            aio_thread=BaseTask.aio_thread, coroutine=JobExecutionHistory.find(JobExecutionHistory.status == JobHistoryStatus.SUCCESS).to_list())
        assert len(job_history) == 2
