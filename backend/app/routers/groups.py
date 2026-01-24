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
from backend.app.rl.trainer import generate_all_groups_rl

@router.get("/generate-all")
def generate_all_groups(db: Session = Depends(get_db)):
    from backend.app.models import Member
    members = db.query(Member).all()
    members_data = []
    for m in members:
        members_data.append({
            "id": m.id,
            "name": m.name,
            "category": m.category
        })

    groups, replay_buffer = generate_all_groups_rl(members_data)

    return {
    "total_groups": len(groups),
    "groups": [
        {
            "members": [
                {
                    "id": m["id"],
                    "name": m["name"],
                    "category": m["category"]
                }
                for m in g["group"]
            ],
            "reward": g["reward"]
        }
        for g in groups
    ]
}
