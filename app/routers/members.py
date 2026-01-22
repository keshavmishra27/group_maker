from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import create_member, get_all_members
from ..schemas import MemberCreate, MemberResponse

router = APIRouter(prefix="/members", tags=["Members"])

@router.post("/", response_model=MemberResponse)
def add_member(member: MemberCreate, db: Session = Depends(get_db)):
    return create_member(db, member)

@router.get("/", response_model=list[MemberResponse])
def list_members(db: Session = Depends(get_db)):
    return get_all_members(db)
