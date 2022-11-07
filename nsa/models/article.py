'''
File: article.py
File Created: Monday, 7th November 2022 2:41:01 pm
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
from pydantic import BaseModel
from typing import Optional


class NewsArticle(BaseModel):
    title: str
    url: str
    date: str
    image: str
    extra: Optional[dict]
