from celery import Task
# TODO change project name
from nsa.services.utils import logger
from nsa.services.async_sync import AioThread, async_to_sync


class BaseTask(Task):
    """base task for most tasks to follow
    """
    abstract: bool = True

    # Celery Startup Function
    # Connect the broadcast service
    # broadcast: Broadcast = Broadcast(
    # f"redis://{REDIS_CONTAINER_NAME}:6379")
    # Event loop to support async/await in normal environment
    aio_thread: AioThread = AioThread()

    def __init__(self):
        """Start the thread
        """

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Log the exceptions at retry."""
        logger.warning(
            f'Task {task_id} has failed we are retring its execution')
        super(BaseTask, self).on_retry(exc, task_id, args, kwargs, einfo)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Log the exceptions."""
        logger.error(f'Task {task_id} failed definitely;')
        super(BaseTask, self).on_failure(exc, task_id, args, kwargs, einfo)

    def on_success(self, retval, task_id, args, kwargs):
        """Log + Code to execute on success
        """
        logger.info(f'Task {task_id} Succeeded')
        super(BaseTask, self).on_success(retval, task_id, args, kwargs)
        # Here to add the publish subscribe logic
        # if there is a return value
        if retval is not None:
            #  arg by arg
            for arg in args:
                # check if arg has topic variable
                if hasattr(arg, "get") and arg.get('TOPIC') is not None:
                    # Send the data back to the suer
                    # async_to_sync(BaseTask.aio_thread,
                    #   BaseTask.broadcast.publish(arg.get('TOPIC'), retval)
                    #   )
                    # leave the loop
                    break

    def __del__(self):
        """Destruction of the value
        """
