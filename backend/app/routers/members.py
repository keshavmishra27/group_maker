from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import create_member, create_members_bulk, get_all_members
from ..schemas import MemberCreate, MemberResponse

router = APIRouter(prefix="/members", tags=["Members"])

@router.post("/", response_model=MemberResponse)
def add_member(member: MemberCreate, db: Session = Depends(get_db)):
    return create_member(db, member)

@router.get("/", response_model=list[MemberResponse])
def list_members(db: Session = Depends(get_db)):
    return get_all_members(db)

from ..schemas import MemberBulkCreate

@router.post("/bulk", response_model=list[MemberResponse])
def add_members_bulk(
    payload: MemberBulkCreate,
    db: Session = Depends(get_db)
):
    return create_members_bulk(db, payload.members)

