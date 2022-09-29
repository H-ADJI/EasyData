'''
File: project.py
File Created: Tuesday, 20th September 2022 11:54:51 am
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
from nsa.models.project import Project_update, ProjectBase, Project_read
from nsa.database.models import Project, User
from nsa.api.routes.authentication import current_user
from fastapi import Depends, APIRouter, status, HTTPException
from beanie.exceptions import DocumentNotFound
from beanie.operators import And
from beanie import PydanticObjectId
from nsa.utils.utils import none_remover

from typing import List

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED, response_model=Project_read)
async def create_project(project: ProjectBase, user: User = Depends(current_user)):
    new_project: Project = Project(owner_id=user.id, **project.dict())
    await new_project.insert()
    return new_project.dict()


@router.get("", status_code=status.HTTP_200_OK, response_model=List[Project_read])
async def get_all_projects(user: User = Depends(current_user)):
    all_projects = Project.find(Project.owner_id == user.id)
    all_projects_list = await all_projects.to_list()
    return all_projects_list


@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=Project_read)
async def get_one_projects(id: PydanticObjectId, user: User = Depends(current_user)):
    # project = await Project.find_one(Project.id == id)
    project = await Project.find_one(And({Project.id: id}, {Project.owner_id: user.id}))
    if project == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Could not find the following project : {id}")
    return project


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def get_one_projects(id: PydanticObjectId, user: User = Depends(current_user)):
    project = await Project.find_one(And({Project.id: id}, {Project.owner_id: user.id}))
    if project == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Could not find the following project : {id}")
    await project.delete()
    return f"deleted {id}"


@router.patch("/{id}", status_code=status.HTTP_201_CREATED, response_model=Project_read)
async def update_project(id: PydanticObjectId, project_updates: Project_update, user: User = Depends(current_user)):
    old_project = await Project.find_one(And({Project.id: id}, {Project.owner_id: user.id}))
    if old_project == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Could not find the following project : {id}")
    project_updates_dict = none_remover(project_updates)
    merged_attrs = {**old_project.dict(), **project_updates_dict}
    new_project = Project(**merged_attrs)
    try:
        await new_project.replace()
    except DocumentNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Could not find the following project : {id}")

    return new_project
