'''
File: main.py
File Created: Tuesday, 25th October 2022 10:31:45 am
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
from nsa.api.router import router
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from nsa.configs.event_handlers import startup_handler, shutdown_handler


def get_app() -> FastAPI:
    app = FastAPI(title="NSA", version="0.0.1")
    app.include_router(router)
    app.add_event_handler(event_type="startup", func=startup_handler(app=app))
    app.add_event_handler(event_type="shutdown",
                          func=shutdown_handler(app=app))
    return app


app = get_app()


@ app.get("/", tags=["Root"], summary="Redirects to projects list", description="Redirects to '/api/project'")
async def root():
    return RedirectResponse(url='/api/job')
