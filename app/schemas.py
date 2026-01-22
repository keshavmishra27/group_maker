from pydantic import BaseModel

class MemberCreate(BaseModel):
    name: str
    category: str

class MemberResponse(BaseModel):
    id: int
    name: str
    category: str

    class Config:
        orm_mode = True
