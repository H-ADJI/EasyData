'''
Filename: pub_sub.py
Created Date: 
Author: 

Copyright (c) 2021 Henceforth

Summary : This is a copy of the repo `https://github.com/Mulugruntz/celery-pubsub`
there was a version problem so it was not possible to be installed we worked with it locally
'''
import re
import celery
# TODo update project name
from easydata.services.utils import logger

__all__ = ['publish', 'publish_now', 'subscribe', 'unsubscribe', ]


class PubSubManager(object):
    def __init__(self):
        super(PubSubManager, self).__init__()
        self.subscribed = set()
        self.jobs = {}

    def publish(self, topic, *args, **kwargs):
        result = self.get_jobs(topic).delay(*args, **kwargs)
        return result

    def publish_now(self, topic, *args, **kwargs):
        result = self.get_jobs(topic).apply(args=args, kwargs=kwargs)
        return result

    def publish_later(self, topic, countdown, *args, **kwargs):
        # use countdown to execute commande later
        result = self.get_jobs(topic).apply_async(
            args=args, kwargs=kwargs, countdown=countdown)
        return result

    def subscribe(self, topic, task):
        key = (topic, self._topic_to_re(topic), task)
        if key not in self.subscribed:
            self.subscribed.add(key)
            self.jobs = {}

    def unsubscribe(self, topic, task):
        key = (topic, self._topic_to_re(topic), task)
        if key in self.subscribed:
            self.subscribed.discard(key)
            self.jobs = {}

    def get_jobs(self, topic):
        if topic not in self.jobs:
            self._gen_jobs(topic)
        return self.jobs[topic]

    def _gen_jobs(self, topic):
        jobs = []
        for job in self.subscribed:
            if job[1].match(topic):
                jobs.append(job[2].s())
        self.jobs[topic] = celery.group(jobs)

    @staticmethod
    def _topic_to_re(topic):
        assert isinstance(topic, str)
        re_topic = (
            topic
            .replace('.', r'\.')
            .replace('*', r'[^.]+')
            .replace('#', r'.+')
        )
        return re.compile(r'^{}$'.format(re_topic))


_pubsub_manager = None
if _pubsub_manager is None:
    _pubsub_manager = PubSubManager()


def publish(topic: str, *args: tuple, **kwargs: dict):
    logger.info(f"publish to topic => {topic}")
    return _pubsub_manager.publish(topic, *args, **kwargs)


def publish_now(topic: str, *args: tuple, **kwargs: dict):
    logger.info(f"publish sync to topic => {topic}")
    return _pubsub_manager.publish_now(topic, *args, **kwargs)


def publish_later(topic: str, countdown: int, *args: tuple, **kwargs: dict):
    """Publish task after the passing of some countdown in seconds
    """
    logger.info(
        f"publish task later after {countdown} seconds to topic => {topic}")
    return _pubsub_manager.publish_later(topic, countdown, *args, **kwargs)


def subscribe(topic: str, task: celery.Task):
    logger.info(f"Subscribe topic => {topic}")
    return _pubsub_manager.subscribe(topic, task)


def unsubscribe(topic: str, task: celery.Task):
    logger.info(f"Unsubscribe topic => {topic}")
    return _pubsub_manager.unsubscribe(topic, task)
