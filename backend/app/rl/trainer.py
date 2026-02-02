from .env import GroupEnv
from .agent import SimpleRLAgent
from collections import defaultdict


def generate_group_rl(members):
    env = GroupEnv(members)
    agent = SimpleRLAgent()

    state = env.reset()
    MAX_STEPS = 10
    steps = 0

    while steps < MAX_STEPS:
        action = agent.select_action(state)
        state, reward, done = env.step(action)
        steps += 1

        if done:
            return env.group, reward

    return env.group, reward


def generate_all_groups_deterministic(members):
    seniors = [m for m in members if m["category"] == "senior"]
    intermediates = [m for m in members if m["category"] == "intermediate"]
    juniors = [m for m in members if m["category"] == "junior"]

    groups = []
    group_id = 1

    while seniors and intermediates and juniors:
        group = [
            seniors.pop(0),
            intermediates.pop(0),
            juniors.pop(0),
        ]

        if intermediates:
            group.append(intermediates.pop(0))

        groups.append({
            "group_id": group_id,
            "group": group,
            "reward": 6
        })

        group_id += 1

    return groups


def generate_group_rl_from_db(db, domain_id=None):
    from backend.app.models import Member, Domain

    if domain_id:
        
        domain = db.query(Domain).filter(Domain.id == domain_id).first()
        if not domain:
            return [], 0
        members = domain.members
    else:
        
        members = db.query(Member).all()

    members_data = [
        {
            "id": m.id,
            "name": m.name,
            "category": m.category
        }
        for m in members
    ]

    if len(members_data) < 3:
        return [], 0

    return generate_group_rl(members_data)