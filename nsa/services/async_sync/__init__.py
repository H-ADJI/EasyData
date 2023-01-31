'''
Filename: __init__.py
Created Date: Monday, March 29th 2021, 4:12:05 pm
Author: Lamalem-Nizar

Copyright (c) 2021 Henceforth

Summary: To run async functions in sync mode
'''
from .async_sync import AioThread, async_to_sync

# Expose only the mentioned libraries
__all__ = ["AioThread", "async_to_sync"]
