'''
Filename:rotator.py 
Created Date: 
Author: 

Copyright (c) 2021 H-adji
'''
import datetime


class Rotator:
    """Rotate file if over a specific size or at a specific time
    """

    def __init__(self, *, size, at):
        """ size ([type]): Size to rotate
            at ([type]): time to rotate
        """
        now = datetime.datetime.now()

        self._size_limit = size
        self._time_limit = now.replace(
            hour=at.hour, minute=at.minute, second=at.second)

        if now >= self._time_limit:
            # The current time is already past the target time so it would rotate already.
            # Add one day to prevent an immediate rotation.
            self._time_limit += datetime.timedelta(days=1)

    def should_rotate(self, message, file):
        """Should i rotate
        """
        file.seek(0, 2)
        if file.tell() + len(message) > self._size_limit:
            return True
        if message.record["time"].timestamp() > self._time_limit.timestamp():
            self._time_limit += datetime.timedelta(days=1)
            return True
        return False
