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
