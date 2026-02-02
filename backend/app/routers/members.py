from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from backend.app.database import get_db
from backend.app.models import Member, Domain

router = APIRouter(prefix="/members", tags=["Members"])

@router.get("/")
def get_members(domain_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    if domain_id:
        
        domain = db.query(Domain).filter(Domain.id == domain_id).first()
        if not domain:
            return []
        
        return [
            {
                "id": m.id,
                "name": m.name,
                "category": m.category
            }
            for m in domain.members
        ]
    else:
        
        members = db.query(Member).all()
        return [
            {
                "id": m.id,
                "name": m.name,
                "category": m.category
            }
            for m in members
        ]