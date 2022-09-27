from celery import Celery
from nsa.configs.celery_config import CELERY_CONFIG
celery_app: Celery = Celery(
    'tasks', broker='amqp://guest:guest@rabbitmq:5672//')

# celery_app.conf.beat_schedule = {
#     'every 5 sec': {
#         'task': 'nsa.celery.tasks.pool_db',
#         'schedule': 5,
#     },
# }

celery_app.conf.update(CELERY_CONFIG)


@celery_app.task
def pool_db():
    print("LOOKING IF THERE IS ANY JOB TO RUN")
