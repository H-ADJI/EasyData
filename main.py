'''
File: main.py
File Created: Monday, 18th July 2022 10:54:36 am
Author: KHALIL HADJI
-----
Copyright:  HENCEFORTH 2022
'''
from beanie import init_beanie
from nsa.api.router import router
from nsa.database.database import db
from beanie import init_beanie
from fastapi import FastAPI
from nsa.api.routes.authentication import create_super_user
from nsa.configs.configs import env_settings
from nsa.configs.event_handlers import startup_handler, shutdown_handler
from nsa.database.models import Project, User, ScrapingPlan, JobScheduling

# app = FastAPI()


def get_app() -> FastAPI:
    app = FastAPI(title="NSA", version="0.0.1")
    app.include_router(router)
    app.add_event_handler(event_type="startup", func=startup_handler(app=app))
    app.add_event_handler(event_type="shutdown",
                          func=shutdown_handler(app=app))
    return app


app = get_app()


@ app.get("/")
async def root():
    return {"message": "Hello"}
