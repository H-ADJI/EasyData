'''
File: project.py
File Created: Tuesday, 20th September 2022 11:54:51 am
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
from fastapi import Depends, APIRouter, status, HTTPException
from nsa.models.project import Project_update, ProjectBase, Project_read
from nsa.database.models import Project
from beanie.exceptions import DocumentNotFound
from typing import List
from .authentication import current_user

router = APIRouter()

@router.post("", status_code=status.HTTP_201_CREATED, response_model=Project_read)
async def create_project(project: ProjectBase):
    new_project: Project = Project(**project.dict())
    await new_project.insert()
    return new_project.dict()


@router.get("", status_code=status.HTTP_200_OK, response_model=List[Project_read])
async def get_all_projects():
    all_projects = Project.find_all()
    all_projects_list = await all_projects.to_list()
    return all_projects_list


@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=Project_read)
async def get_one_projects(id: str):
    project = await Project.get(document_id=id)
    if project == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Could not find the following project : {id}")
    return project


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def get_one_projects(id: str):
    project = await Project.get(document_id=id)
    if project == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Could not find the following project : {id}")
    await project.delete()
    return f"deleted {id}"


@router.patch("/{id}", status_code=status.HTTP_201_CREATED)
async def update_project(id: str, project_updates: Project_update):
    old_project = await Project.get(document_id=id)
    if old_project == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Could not find the following project : {id}")
    merged_attrs = {**old_project.dict(), **project_updates.dict()}
    new_project = Project(**merged_attrs)
    try:
        await new_project.replace()
    except DocumentNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Could not find the following project : {id}")

    return new_project
