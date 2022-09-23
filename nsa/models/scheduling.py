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
from fastapi import HTTPException, status


class Interval_trigger(BaseModel):
    weeks: int
    days: int
    hours: int
    minutes: int
    seconds: int
    start_date:  datetime
    end_date:  datetime
    timezone: float

    @validator("start_date")
    def start_date_min_val(cls, start_date):
        if start_date <= datetime.now() + timedelta(minutes=env_settings.MIN_JOB_SCHEDULING_OFFSET):
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                detail=f"start date should be at least {env_settings.MIN_JOB_SCHEDULING_OFFSET} minute from now")
        return start_date

    @validator("end_date")
    def end_date_min_val(cls, end_date, values):
        if end_date <= values["start_date"] + timedelta(minutes=env_settings.MIN_JOB_SCHEDULING_OFFSET):
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                detail=f"end date should be at least {env_settings.MIN_JOB_SCHEDULING_OFFSET} minute away from start date")
        return end_date


class Exact_date_trigger(BaseModel):
    date: Optional[datetime]
    timezone: float

    @validator("date")
    def start_date_min_val(cls, date):
        if date <= datetime.now() + timedelta(minutes=env_settings.MIN_JOB_SCHEDULING_OFFSET):
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                detail=f"The scheduling date should be at least {env_settings.MIN_JOB_SCHEDULING_OFFSET} minute from now")
        return date


class SchedulingBase(BaseModel):
    plan_id: PydanticObjectId
    interval: Optional[Interval_trigger]
    date: Optional[Exact_date_trigger]
    input_data: dict

    @validator("date")
    def either_interval_or_date(cls, date, values):
        if values["interval"] and date:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                detail="You should either choose an interval for recurring executions or an exact date for delayed execution")
        return date


class Scheduling_read(SchedulingBase):
    owner_id:  PydanticObjectId
    next_run: Optional[datetime]


class Scheduling_write(SchedulingBase):
    pass


class Scheduling_update(SchedulingBase):
    __annotations__ = {k: Optional[v]
                       for k, v in SchedulingBase.__annotations__.items()}
