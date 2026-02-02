
import random

class SimpleRLAgent:
    def select_action(self, state):
        
        if state["senior"] == 0:
            return 0
            
        if state["intermediate"] == 0:
            return 1
            
        if state["junior"] == 0:
            return 2

        if state["group_size"] >= 3:
            return 3 
            
        return random.choice([0, 1, 2])