'''
File: scheduling.py
File Created: Thursday, 22nd September 2022 12:17:38 pm
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''

from typing import List, Union, Optional
from pydantic import BaseModel
from datetime import datetime
from beanie import PydanticObjectId


class Interval_trigger(BaseModel):
    weeks: int
    days: int
    hours: int
    minutes: int
    seconds: int
    start_date:  datetime
    end_date:  datetime


class SchedulingBase(BaseModel):
    plan_id: PydanticObjectId
    interval: Interval_trigger
    interval: Interval_trigger
    date: datetime
    timezone: str
    input_data: dict


class Scheduling_read(SchedulingBase):
    owner_id:  PydanticObjectId


class Scheduling_write(SchedulingBase):
    ...


class Scheduling_update(SchedulingBase):
    __annotations__ = {k: Optional[v]
                       for k, v in SchedulingBase.__annotations__.items()}
