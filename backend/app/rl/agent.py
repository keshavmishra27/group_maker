# agent.py
import random

class SimpleRLAgent:
    def select_action(self, state):
        # Priority 1: Ensure 1 Senior (Reward +3)
        if state["senior"] == 0:
            return 0
            
        # Priority 2: Ensure 1 Intermediate (Reward +2)
        if state["intermediate"] == 0:
            return 1
            
        # Priority 3: Ensure 1 Junior (Reward +1) - ✅ ADDED THIS
        if state["junior"] == 0:
            return 2

        # Priority 4: If we have S+I+J (Size 3+), we have max reward (6).
        # We can stop now to keep groups small/efficient.
        if state["group_size"] >= 3:
            return 3  # STOP

        # Fallback (fills up to 5 members if needed)
        return random.choice([0, 1, 2])