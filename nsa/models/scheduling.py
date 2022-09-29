'''
File: scheduling.py
File Created: Thursday, 22nd September 2022 12:17:38 pm
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''

from typing import List, Union, Optional
from pydantic import BaseModel, validator
from datetime import datetime, timedelta
from beanie import PydanticObjectId
from nsa.configs.configs import env_settings
from nsa.constants.enums import SchedulingJobStatus
from fastapi import HTTPException, status
import pytz


class Interval_trigger(BaseModel):
    weeks: int = 0
    days: int = 0
    hours: int = 0
    minutes: int = 0
    seconds: int = 0
    timezone: str
    start_date:  datetime
    end_date:  datetime

    @validator("seconds")
    def min_accepted_interval(cls, seconds, values):
        interval = values["weeks"]*7*24*60*60 + values["days"]*24*60 * \
            60 + values["hours"]*60*60 + values["minutes"]*60 + seconds
        if interval < env_settings.MIN_ACCEPTED_INTERVAL*60:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                detail=f"interval should be at least {env_settings.MIN_ACCEPTED_INTERVAL} minutes, you gave {(interval/60):.3} minutes")
        return seconds

    @validator("start_date")
    def start_date_min_val(cls, start_date: datetime, values):
        user_tz = pytz.timezone(values["timezone"])

        if start_date.astimezone(tz=user_tz) <= datetime.now().astimezone(tz=user_tz) + timedelta(minutes=env_settings.MIN_JOB_SCHEDULING_OFFSET):
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                detail=f"start date should be at least {env_settings.MIN_JOB_SCHEDULING_OFFSET} minute from now")
        return start_date

    @validator("end_date")
    def end_date_min_val(cls, end_date: datetime, values):
        user_tz = pytz.timezone(values["timezone"])
        if end_date.astimezone(tz=user_tz) <= values["start_date"] + timedelta(minutes=env_settings.MIN_JOB_SCHEDULING_OFFSET):
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                detail=f"end date should be at least {env_settings.MIN_JOB_SCHEDULING_OFFSET} minute away from start date")
        return end_date


class Exact_date_trigger(BaseModel):
    timezone: str
    date: datetime

    @validator("date")
    def start_date_min_val(cls, date: datetime, values):
        user_tz = pytz.timezone(values["timezone"])

        if date.astimezone(tz=user_tz) <= datetime.now().astimezone(tz=user_tz) + timedelta(minutes=env_settings.MIN_JOB_SCHEDULING_OFFSET):
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                detail=f"The scheduling date should be at least {env_settings.MIN_JOB_SCHEDULING_OFFSET} minute from now, But you gave {date:%Y-%m-%d %H:%M}")
        return date


class SchedulingBase(BaseModel):
    plan_id: PydanticObjectId
    interval: Optional[Interval_trigger]
    exact_date: Optional[Exact_date_trigger]
    input_data: dict

    @validator("exact_date")
    def either_interval_or_date(cls, date, values):
        if values["interval"] and date:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                detail="You should either choose an interval for recurring executions or an exact date for delayed execution Not both")
        return date


class Scheduling_read(SchedulingBase):
    owner_id:  PydanticObjectId
    next_run: float
    status: SchedulingJobStatus


class Scheduling_write(SchedulingBase):
    pass


class Scheduling_update(SchedulingBase):
    __annotations__ = {k: Optional[v]
                       for k, v in SchedulingBase.__annotations__.items()}
