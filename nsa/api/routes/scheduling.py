'''
File: scheduling.py
File Created: Thursday, 22nd September 2022 2:27:31 pm
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
from time import timezone
from nsa.models.scheduling import Scheduling_read, Scheduling_update, Scheduling_write
from nsa.services.utils import none_remover
from nsa.database.models import JobScheduling, User
from nsa.constants.enums import SchedulingJobStatus
from nsa.api.routes.authentication import current_user
from fastapi import Depends, APIRouter, status, HTTPException
from beanie.exceptions import DocumentNotFound
from beanie.operators import And
from beanie import PydanticObjectId
import pytz
from typing import List, Optional, Union

router = APIRouter()


def compute_next_run_on_write(job: Scheduling_write):
    if job.interval:
        next_run = job.interval.start_date
    elif job.exact_date:
        next_run = job.exact_date.date
    return next_run


@router.post("", status_code=status.HTTP_201_CREATED, response_model=Scheduling_read, response_model_exclude_none=True)
async def schedule_job(job: Scheduling_write, user: User = Depends(current_user)):
    next_run = compute_next_run_on_write(job=job)
    new_job: JobScheduling = JobScheduling(
        owner_id=user.id, next_run=next_run, status=SchedulingJobStatus.WAITING, **job.dict())
    await new_job.insert()
    return new_job.dict()


@router.get("", status_code=status.HTTP_200_OK, response_model=List[Scheduling_read], response_model_exclude_none=True)
async def get_all_scheduled_jobs(user: User = Depends(current_user)):
    all_scheduled_jobs = JobScheduling.find(
        JobScheduling.owner_id == user.id)
    all_scheduled_jobs_list = await all_scheduled_jobs.to_list()
    return all_scheduled_jobs_list


@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=Scheduling_read, response_model_exclude_none=True)
async def get_one_scheduled_job(id: PydanticObjectId, user: User = Depends(current_user)):
    job: JobScheduling = await JobScheduling.find_one(And({JobScheduling.id: id}, {JobScheduling.owner_id: user.id}))
    if job == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Could not find the following job : {id}")
    return job


@router.delete("/{id}",  status_code=status.HTTP_204_NO_CONTENT, response_model_exclude_none=True)
async def delete_scheduled_job(id: PydanticObjectId, user: User = Depends(current_user)):
    job = await JobScheduling.find_one(And({JobScheduling.id: id}, {JobScheduling.owner_id: user.id}))
    if job == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Could not find the following job : {id}")
    await job.delete()
    return f"deleted {id}"


@router.patch("/{id}", status_code=status.HTTP_200_OK, response_model=Scheduling_read, response_model_exclude_none=True)
async def update_scheduled_job(id: PydanticObjectId, job_update: Scheduling_update, user: User = Depends(current_user)):
    old_job = await JobScheduling.find_one(And({JobScheduling.id: id}, {JobScheduling.owner_id: user.id}))
    if old_job == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Could not find the following job : {id}")
    job_update_dict = none_remover(job_update)
    merged_attrs = {**old_job.dict(), **job_update_dict}
    new_job = JobScheduling(**merged_attrs)
    try:
        await new_job.replace()
    except DocumentNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Could not find the following job : {id}")

    return new_job
