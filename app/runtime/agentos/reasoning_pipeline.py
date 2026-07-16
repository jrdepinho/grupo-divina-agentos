from __future__ import annotations

from app.runtime.agentos.goal_analyzer import GoalAnalyzer
from app.runtime.agentos.candidate_ranker import CandidateRanker
from app.runtime.agentos.developer_reasoner import DeveloperReasoner


class ReasoningPipeline:

    def __init__(self):
        self.goal = GoalAnalyzer()
        self.ranker = CandidateRanker()
        self.reasoner = DeveloperReasoner()

    def build(
        self,
        goal: str,
        project_context: dict,
    ):

        analysis = self.goal.analyze(goal)

        candidates = self.ranker.rank(
            analysis,
            project_context,
        )

        plan = self.reasoner.plan(
            analysis,
            candidates,
            project_context,
        )

        return plan
