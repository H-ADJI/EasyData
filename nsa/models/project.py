'''
File: project.py
File Created: Monday, 19th September 2022 5:00:22 pm
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
from datetime import datetime
from pydantic import BaseModel
from typing import List, Union


class Project(BaseModel):
    description: str
    title: str
    tags: List[str]
    image: str


class Scraping_plan(BaseModel):
    plan: dict


class Analytics(BaseModel):
    plan: dict


class Frequency(BaseModel):
    weeks: int
    days: int
    hours: int
    minutes: int
    seconds: int
    start_date: datetime
    end_date: datetime
    timezone: str


class Date(BaseModel):
    run_date: datetime
    timezone: str
