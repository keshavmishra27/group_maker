from os import name
from unicodedata import category
from pydantic import BaseModel
from typing import Literal

class MemberCreate(BaseModel):
    name: str
    category: Literal["junior", "intermediate", "senior"]

class MemberResponse(BaseModel):
    id: int
    name: str
    category: str

    class Config:
        orm_mode = True

from typing import List
from pydantic import BaseModel

class MemberBulkCreate(BaseModel):
    members: List[MemberCreate]

