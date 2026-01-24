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

def generate_all_groups_rl(members):
    unassigned = members.copy()
    all_groups = []
    replay_buffer = []

    while len(unassigned) >= 3:
        env = GroupEnv(unassigned)
        agent = SimpleRLAgent()

        state = env.reset()

        MAX_STEPS = 10
        steps = 0
        group = []

        while True:
            action = agent.select_action(state)
            state, reward, done = env.step(action)
            steps += 1

            if done or steps >= MAX_STEPS:
                group = env.group
                break

        # 🔒 SAFETY: no progress → exit outer loop
        if not group:
            break

        replay_buffer.append({
            "group": group,
            "reward": reward
        })

        all_groups.append({
            "group": group,
            "reward": reward
        })

        used_ids = {m["id"] for m in group}
        unassigned = [
            m for m in unassigned
            if m["id"] not in used_ids
        ]

    return all_groups, replay_buffer


