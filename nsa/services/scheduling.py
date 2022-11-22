'''
File: scheduling.py
File Created: Tuesday, 22nd November 2022 10:22:23 am
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''

import datetime
from typing import Union
from nsa.database.models import JobScheduling
from nsa.models.scheduling import Exact_date_trigger_read, Interval_trigger_read
from nsa.constants.enums import SchedulingJobStatus
import pytz

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


def simulate_user_current_time(user_tz: str):
    user_tz = pytz.timezone(user_tz)
    # this simulate the current datetime from the user perspective but removes time zone info
    now = datetime.now().astimezone(tz=user_tz).replace(tzinfo=None)
    return now


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
