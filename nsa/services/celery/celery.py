'''
File: celery.py
File Created: Friday, 30th September 2022 11:49:26 am
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
from celery import Celery
from nsa.configs.celery_config import CELERY_CONFIG
from nsa.services.base_task import BaseTask
celery_app: Celery = Celery(
    'tasks', broker='amqp://guest:guest@rabbitmq:5672//',
    task_cls=BaseTask
)


celery_app.conf.update(CELERY_CONFIG)
