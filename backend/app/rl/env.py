# env.py
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
        # Action 3: STOP
        if action == 3: 
            self.done = True
            return self._state(), self._evaluate(), self.done

        category_map = ["senior", "intermediate", "junior"]
        
        # Safety check for invalid action
        if action >= len(category_map):
             return self._state(), -1, False
             
        category = category_map[action]

        # ✅ FIX: Filter out members who are ALREADY in the group
        # We use m["id"] to ensure uniqueness if dicts are recreated
        current_ids = {g["id"] for g in self.group}
        candidates = [
            m for m in self.members 
            if m["category"] == category and m["id"] not in current_ids
        ]

        # If no candidates available for this category (or all used), punish agent
        if not candidates:
            return self._state(), -1, False 

        # Add member
        self.group.append(random.choice(candidates))

        # Check if group is full (max 5)
        if len(self.group) >= 5:
            self.done = True
            reward = self._evaluate()
            return self._state(), reward, self.done

        return self._state(), 0, self.done

    def _evaluate(self):
        s = self._state()

        # Constraints: Group must be between 3 and 5 members
        if s["group_size"] < 3 or s["group_size"] > 5:
            return -2

        reward = 0
        if s["senior"] >= 1: reward += 3
        if s["intermediate"] >= 1: reward += 2
        if s["junior"] >= 1: reward += 1

        return reward