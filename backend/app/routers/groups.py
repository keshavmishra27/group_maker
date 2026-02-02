from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from collections import defaultdict
from backend.app.database import get_db
from backend.app.models import Member
from backend.app.rl.trainer import generate_all_groups_deterministic
from backend.app.models import Domain

router = APIRouter(prefix="/groups", tags=["Groups"])


@router.get("/generate")
def generate_group(db: Session = Depends(get_db)):
    from backend.app.rl.trainer import generate_group_rl_from_db
    group, reward = generate_group_rl_from_db(db)
    return {
        "reward": reward,
        "members": group
    }


@router.get("/generate-all")
def generate_all_groups(db: Session = Depends(get_db)):
    domains = db.query(Domain).all()
    response = []

    for domain in domains:
        members_data = [
            {
                "id": m.id,
                "name": m.name,
                "category": m.category
            }
            for m in domain.members
        ]

        if len(members_data) < 3:
            continue

        groups = generate_all_groups_deterministic(members_data)

        response.append({
            "domain": domain.name,
            "total_students": len(members_data),
            "total_groups": len(groups),
            "groups": groups
        })

    return response