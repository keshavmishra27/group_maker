from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from backend.app.database import get_db
from backend.app.models import Member, Domain
from backend.app.rl.trainer import generate_all_groups_deterministic

router = APIRouter(prefix="/groups", tags=["Groups"])

@router.get("/generate")
def generate_group(domain_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    from backend.app.rl.trainer import generate_group_rl_from_db
    
    
    if domain_id:
        domain = db.query(Domain).filter(Domain.id == domain_id).first()
        if not domain:
            return {"error": "Domain not found", "members": [], "reward": 0}
        
        
        if len(domain.members) < 3:
            return {"error": "Not enough members in this domain (need 3+)", "members": [], "reward": 0}

    
    group, reward = generate_group_rl_from_db(db, domain_id=domain_id)
    
    if not group:
         return {"error": "Could not form a valid group", "members": [], "reward": 0}

    return {
        "reward": reward,
        "members": group
    }


@router.get("/generate-all")
def generate_all_groups(domain_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    if domain_id:
       
        domain = db.query(Domain).filter(Domain.id == domain_id).first()
        if not domain:
            return {"error": "Domain not found"} 
        domains = [domain]
    else:
        
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

        if groups:
            response.append({
                "domain": domain.name,
                "domain_id": domain.id,
                "total_students": len(members_data),
                "total_groups": len(groups),
                "groups": groups
            })

    return response