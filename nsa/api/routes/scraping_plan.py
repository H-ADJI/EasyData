'''
File: scraping_plan.py
File Created: Wednesday, 21st September 2022 4:43:11 pm
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
from nsa.models.scraping_plan import Scraping_plan_read, Scraping_plan_update, Scraping_plan_write
from nsa.database.models import Scraping_plan, User
from nsa.api.routes.authentication import current_user
from fastapi import Depends, APIRouter, status, HTTPException
from beanie.exceptions import DocumentNotFound
from beanie.operators import And
from beanie import PydanticObjectId

from typing import List

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED, response_model=Scraping_plan_read)
async def create_plan(scraping_plan: Scraping_plan_write, user: User = Depends(current_user)):
    new_plan: Scraping_plan = Scraping_plan(
        owner_id=user.id, **scraping_plan.dict())
    await new_plan.insert()

    return new_plan.dict()


@router.get("", status_code=status.HTTP_200_OK, response_model=List[Scraping_plan_read])
async def get_all_plans(user: User = Depends(current_user)):
    all_plans = Scraping_plan.find(Scraping_plan.owner_id == user.id)
    all_plans_list = await all_plans.to_list()
    return all_plans_list


@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=Scraping_plan_read)
async def get_one_plan(id: PydanticObjectId, user: User = Depends(current_user)):
    plan = await Scraping_plan.find_one(And({Scraping_plan.id: id}, {Scraping_plan.owner_id: user.id}))
    if plan == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Could not find the following plan : {id}")
    return plan


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(id: PydanticObjectId, user: User = Depends(current_user)):
    plan = await Scraping_plan.find_one(And({Scraping_plan.id: id}, {Scraping_plan.owner_id: user.id}))
    if plan == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Could not find the following plan : {id}")
    await plan.delete()
    return f"deleted {id}"


@router.patch("/{id}", status_code=status.HTTP_201_CREATED, response_model=Scraping_plan_read)
async def update_plan(id: PydanticObjectId, plan_updates: Scraping_plan_update, user: User = Depends(current_user)):
    old_plan = await Scraping_plan.find_one(And({Scraping_plan.id: id}, {Scraping_plan.owner_id: user.id}))
    if old_plan == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Could not find the following plan : {id}")
    merged_attrs = {**old_plan.dict(), **plan_updates.dict()}
    new_plan = Scraping_plan(**merged_attrs)
    try:
        await new_plan.replace()
    except DocumentNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Could not find the following plan : {id}")

    return new_plan
