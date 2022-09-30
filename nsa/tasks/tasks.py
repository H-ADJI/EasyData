from nsa.database.models import JobScheduling
from nsa.services.celery.celery import celery_app


async def fetching_waiting_jobs():
    print("this is running async")
    waiting_jobs = JobScheduling.find(
        JobScheduling.input_data == {})
    waiting_jobs_list = await waiting_jobs.to_list()
    return waiting_jobs_list


@celery_app.task
def pool_db():
    print("fetching db for tasks to run")
