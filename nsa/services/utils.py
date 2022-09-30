'''
File: utils.py
File Created: Friday, 23rd September 2022 11:07:41 am
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
from pydantic import BaseModel


def none_remover(model: BaseModel) -> dict:
    original = model.dict()
    filtered = {k: v for k, v in original.items() if v is not None}
    original.clear()
    original.update(filtered)
    return original
