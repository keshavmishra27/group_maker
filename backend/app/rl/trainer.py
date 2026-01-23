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
