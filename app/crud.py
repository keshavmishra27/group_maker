from sqlalchemy.orm import Session
from .models import Member
from .schemas import MemberCreate
from .rl.trainer import generate_group_rl

def create_member(db: Session, member: MemberCreate):
    db_member = Member(
        name=member.name,
        category=member.category
    )
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member

def get_all_members(db: Session):
    return db.query(Member).all()

def generate_group_rl_from_db(db: Session):
    members = db.query(Member).all()

    member_dicts = [
        {"id": m.id, "name": m.name, "category": m.category}
        for m in members
    ]

    group, reward = generate_group_rl(member_dicts)
    return group, reward
