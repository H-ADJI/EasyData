'''
File: main.py
File Created: Tuesday, 25th October 2022 10:31:45 am
Author: KHALIL HADJI
-----
Copyright:  HENCEFORTH 2022
'''
from nsa.api.router import router
from nsa.configs.configs import env_settings
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from nsa.configs.event_handlers import startup_handler, shutdown_handler
from fastapi.middleware.cors import CORSMiddleware


def get_app(testing: bool = False) -> FastAPI:
    origins = [
        env_settings.localhost
    ]

    app = FastAPI(title="NSA", version="0.0.1")
    app.include_router(router)
    if not testing:
        app.add_event_handler(event_type="startup",
                              func=startup_handler(app=app))
        app.add_event_handler(event_type="shutdown",
                              func=shutdown_handler(app=app))
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    return app


app = get_app()


@ app.get("/", tags=["Root"], summary="Redirects to projects list", description="Redirects to '/api/project'")
async def root():
    return RedirectResponse(url='/api/job')
