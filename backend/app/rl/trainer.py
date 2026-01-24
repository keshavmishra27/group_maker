from .env import GroupEnv
from .agent import SimpleRLAgent

def generate_group_rl(members):
    env = GroupEnv(members)
    agent = SimpleRLAgent()

    state = env.reset()

    while True:
        action = agent.select_action(state)
        state, reward, done = env.step(action)

        if done:
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

        # Optional: add one more intermediate if available
        if intermediates:
            group.append(intermediates.pop(0))

        groups.append({
            "group_id": group_id,
            "group": group,
            "reward": 6
        })
        group_id += 1

    return groups




