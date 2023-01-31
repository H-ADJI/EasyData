'''
File: user.py
File Created: Friday, 16th September 2022 4:48:19 pm
Author: KHALIL HADJI 
-----
Copyright:  H-adji 2022
'''
'''
File: user.py
File Created: Thursday, 15th September 2022 4:08:38 pm
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''




import uuid
from fastapi_users import schemas
from pydantic import Field
class UserRead(schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(schemas.BaseUserCreate):
    first_name: str
    last_name: str
    password: str = Field(min_length=8)


class UserUpdate(schemas.BaseUserUpdate):
    pass
