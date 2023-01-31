'''
File: celery_config.py
File Created: Monday, 26th September 2022 3:38:09 pm
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
from easydata.configs.configs import env_settings
from easydata.constants.tasks import TASKS_MODULE
BEAT_SCHEDULE = {
    "pooling_db": {
        'task': 'nsa.tasks.tasks.pool_db',
        'schedule': env_settings.DB_POLLING_INTERVAL,
    }
}
CELERY_CONFIG = {
    "broker_url": env_settings.CELERY_BROKER_URL,
    "beat_schedule": BEAT_SCHEDULE,
    "imports": (TASKS_MODULE)
}
