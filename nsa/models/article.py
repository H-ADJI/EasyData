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
    title:  Optional[str]
    url:  Optional[str]
    date:  Optional[str]
    image:  Optional[str]
    extra: Optional[dict]


class Comment(BaseModel):
    author: str
    content: str
    date: str
    extra: Optional[dict]


class ArticleDetail(BaseModel):
    content:  Optional[str]
    title:  Optional[str]
    date:  Optional[str]
    url:  str
    category: Optional[str]
    author: Optional[str]
    video: Optional[List[dict]]
    image: Optional[List[dict]]
    comments: Optional[List[Comment]]
