from os import name
from unicodedata import category
from pydantic import BaseModel
from typing import Literal, List, Optional

class MemberCreate(BaseModel):
    name: str
    category: Literal["junior", "intermediate", "senior"]

class MemberCreateWithDomains(BaseModel):
    name: str
    category: Literal["junior", "intermediate", "senior"]
    domain_ids: Optional[List[int]] = []   # list of domain IDs to assign

class MemberResponse(BaseModel):
    id: int
    name: str
    category: str

    class Config:
        orm_mode = True

class MemberBulkCreate(BaseModel):
    members: List[MemberCreate]
