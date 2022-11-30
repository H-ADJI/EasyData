'''
File: article.py
File Created: Monday, 7th November 2022 2:41:01 pm
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
from pydantic import BaseModel
from typing import Optional, List


class Article(BaseModel):
    title: str
    url: str
    date: str
    image: str
    extra: Optional[dict]


class Comment(BaseModel):
    author: str
    content: str
    date: str
    extra: Optional[dict]


class ArticleDetail(BaseModel):
    content: str
    title: str
    date: str
    url: str
    category: Optional[str]
    author: Optional[str]
    video: Optional[str]
    image: Optional[str]
    comments: Optional[List[Comment]]
