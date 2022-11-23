'''
File: scheduling.py
File Created: Thursday, 22nd September 2022 12:17:38 pm
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''

from typing import Optional
from pydantic import BaseModel, validator
from datetime import datetime, timedelta
from beanie import PydanticObjectId
from nsa.configs.configs import env_settings
from nsa.constants.enums import SchedulingJobStatus
from fastapi import HTTPException, status
import pytz
from croniter import croniter


def simulate_user_current_time(user_tz: str):
    user_tz = pytz.timezone(user_tz)
    # this simulate the current datetime from the user perspective but removes time zone info
    now = datetime.now().astimezone(tz=user_tz).replace(tzinfo=None)
    return now


class Interval_trigger_read(BaseModel):
    weeks: int = 0
    days: int = 0
    hours: int = 0
    minutes: int = 0
    seconds: int = 0
    timezone: str
    start_date:  datetime
    end_date:  datetime

    @validator("start_date")
    def startdate_to_naive(cls, start_date: datetime):
        #  making the date timezone naive in case user sends tz aware datetime
        start_date = start_date.replace(tzinfo=None)
        return start_date

    @validator("end_date")
    def end_date_to_naive(cls, end_date: datetime):
        #  making the date timezone naive in case user sends tz aware datetime
        end_date = end_date.replace(tzinfo=None)
        return end_date


class Interval_trigger_write(Interval_trigger_read):
    weeks: int = 0
    days: int = 0
    hours: int = 0
    minutes: int = 0
    seconds: int = 0
    timezone: str
    start_date: datetime
    end_date: datetime

    @validator("timezone")
    def min_accepted_interval(cls, seconds, values):
        interval = values["weeks"]*7*24*60*60 + values["days"]*24*60 * \
            60 + values["hours"]*60*60 + \
            values["minutes"]*60 + values["seconds"]
        if interval < env_settings.MIN_ACCEPTED_INTERVAL*60:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                detail=f"interval should be at least {env_settings.MIN_ACCEPTED_INTERVAL} minutes, you gave {(interval/60):.3} minutes")
        return seconds

    @validator("start_date")
    def start_date_min_val(cls, start_date: datetime, values):
        now = simulate_user_current_time(user_tz=values["timezone"])
        if start_date <= now + timedelta(minutes=env_settings.MIN_JOB_SCHEDULING_OFFSET):

            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                detail=f"start date should be at least {env_settings.MIN_JOB_SCHEDULING_OFFSET} minute from now")
        return start_date

    @validator("end_date")
    def end_date_min_val(cls, end_date: datetime, values):
        if end_date <= values["start_date"] + timedelta(minutes=env_settings.MIN_JOB_SCHEDULING_OFFSET):
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                detail=f"end date should be at least {env_settings.MIN_JOB_SCHEDULING_OFFSET} minute away from start date")
        return end_date


class Exact_date_trigger_read(BaseModel):
    timezone: str
    date: datetime

    @validator("date")
    def date_to_naive(cls, date: datetime):
        #  making the date timezone naive in case it is read as tz aware datetime
        date = date.replace(tzinfo=None)
        return date


class Exact_date_trigger_write(Exact_date_trigger_read):
    timezone: str
    date: datetime

    @validator("date")
    def start_date_min_val(cls, date: datetime, values):
        now = simulate_user_current_time(user_tz=values["timezone"])
        if date <= now + timedelta(minutes=env_settings.MIN_JOB_SCHEDULING_OFFSET):
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                detail=f"The scheduling date should be at least {env_settings.MIN_JOB_SCHEDULING_OFFSET} minute from now, But you gave {date:%Y-%m-%d %H:%M}")
        return date


class CronSchedulingRead(BaseModel):
    cron_expression: str
    timezone: str


class CronSchedulingWrite(CronSchedulingRead):

    @validator("cron_expression")
    def valid_cron(cls, cron_expression: str):
        if croniter.is_valid(cron_expression):
            return cron_expression
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail="Invalid cron expression. Use https://crontab.guru to check what went wrong")


class SchedulingBase(BaseModel):
    plan_id: PydanticObjectId
    interval: Optional[Interval_trigger_write]
    cron: Optional[CronSchedulingWrite]
    exact_date: Optional[Exact_date_trigger_write]
    input_data: Optional[dict]

    @validator("exact_date")
    def either_interval_or_date(cls, date, values: dict):
        if values.get("interval") and values.get("cron") and date:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                detail="You should either choose an interval, a cron expression or an exact date, not all three")
        if values.get("interval") and date:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                detail="You should either choose an interval or an exact date, not both")
        if values.get("interval") and values.get("cron"):
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                detail="You should either choose an interval or cron, not both")
        if values.get("cron") and date:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                detail="You should either choose cron or an exact date, not both")
        return date


class Scheduling_read(SchedulingBase):
    owner_id:  PydanticObjectId
    next_run: datetime
    status: SchedulingJobStatus
    id: Optional[PydanticObjectId]


class Scheduling_write(SchedulingBase):
    pass


class Scheduling_update(SchedulingBase):
    __annotations__ = {k: Optional[v]
                       for k, v in SchedulingBase.__annotations__.items()}
