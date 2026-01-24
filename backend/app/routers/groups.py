from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..crud import generate_group_rl_from_db

router = APIRouter(prefix="/groups", tags=["Groups"])

@router.get("/generate")
def generate_group(db: Session = Depends(get_db)):
    group, reward = generate_group_rl_from_db(db)
    return {
        "reward": reward,
        "members": group
    }

#backend\app\rl\trainer.py
from backend.app.rl.trainer import generate_all_groups_deterministic
from backend.app.models import Member
@router.get("/generate-all")
def generate_all_groups(db: Session = Depends(get_db)):
    members = db.query(Member).all()

    members_data = [
        {
            "id": m.id,
            "name": m.name,
            "category": m.category
        }
        for m in members
    ]

    groups = generate_all_groups_deterministic(members_data)

    return {
        "total_students": len(members_data),
        "students_used": len(groups) * 3,
        "total_groups": len(groups),
        "groups": groups
    }
