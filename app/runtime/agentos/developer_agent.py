from __future__ import annotations

from app.runtime.agentos.project_intelligence import ProjectIntelligence


class DeveloperAgent:

    def __init__(self):
        self.pi = ProjectIntelligence()

    def resolve(self, goal: str):

        context = self.pi.build_context(goal)

        return {
            "goal": goal,
            "context": context,
            "actions": [],
        }
