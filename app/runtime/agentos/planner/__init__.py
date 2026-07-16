from .planner import Planner

planner = Planner()

def plan(goal: str, context=None):
    return planner.build(goal, context)

__all__ = ["Planner", "plan"]
