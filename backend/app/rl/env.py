import random

class GroupEnv:
    def __init__(self, members):
        self.members = members
        self.reset()

    def reset(self):
        self.group = []
        self.done = False
        return self._state()

    def _state(self):
        return {
            "group_size": len(self.group),
            "senior": sum(1 for m in self.group if m["category"] == "senior"),
            "intermediate": sum(1 for m in self.group if m["category"] == "intermediate"),
            "junior": sum(1 for m in self.group if m["category"] == "junior"),
        }

    def step(self, action):
        reward = 0

        if action == 3:  # STOP
            self.done = True
            return self._state(), self._evaluate(), self.done

        category = ["senior", "intermediate", "junior"][action]
        candidates = [m for m in self.members if m["category"] == category]

        if not candidates or len(self.group) >= 5:
            return self._state(), -1, False

        self.group.append(random.choice(candidates))

        if len(self.group) >= 5:
            self.done = True
            reward = self._evaluate()

        return self._state(), reward, self.done

    def _evaluate(self):
        s = self._state()

        if s["group_size"] < 3 or s["group_size"] > 5:
            return -2

        reward = 0
        reward += 2 if s["senior"] >= 1 else -reward
        reward += 2 if s["intermediate"] >= 1 else -reward
        reward += 2 if s["junior"] >= 1 else -reward

        if reward == 0:
            return "made group successfully"
        
        else:
            return "failed to make group kindly try again on hitting generate group btn"

    
    def compute_reward(group):
        roles = [m.category for m in group]

        reward = 0
        if "senior" in roles:
            reward += 3
        if "intermediate" in roles:
            reward += 2
        if "junior" in roles:
            reward += 1

        return reward
