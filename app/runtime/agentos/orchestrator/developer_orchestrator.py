from __future__ import annotations

from app.runtime.agentos.goal_analyzer import GoalAnalyzer
from app.runtime.agentos.candidate_ranker import CandidateRanker
from app.runtime.agentos.context_reducer import ContextReducer


class DeveloperOrchestrator:

    def build(self, goal: str, context: dict):

        analysis = GoalAnalyzer().analyze(goal)

        reduced = ContextReducer().reduce(
            goal,
            context,
        )

        candidates = CandidateRanker().rank(
            analysis,
            reduced,
        )

        candidates = sorted(
            candidates,
            key=lambda c: c.score,
            reverse=True,
        )

        candidates = [
            c for c in candidates
            if c.score >= 140
        ]

        candidates = candidates[:5]

        return {
            "analysis": analysis,
            "context": reduced,
            "candidates": candidates,
        }
