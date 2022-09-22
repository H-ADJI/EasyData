'''
File: user.py
File Created: Friday, 16th September 2022 4:48:19 pm
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
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
class UserRead(schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(schemas.BaseUserCreate):
    first_name: str
    last_name: str


class UserUpdate(schemas.BaseUserUpdate):
    pass
