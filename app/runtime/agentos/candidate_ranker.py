from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.runtime.agentos.goal_analyzer import GoalAnalysis


@dataclass
class Candidate:
    path: str
    score: float
    reason: str


class CandidateRanker:

    def rank(
        self,
        analysis: GoalAnalysis,
        context: dict,
    ) -> list[Candidate]:

        candidates = []

        keywords = {
            k.lower()
            for k in analysis.keywords
        }

        #
        # MODULES
        #
        for module in context.get(
            "modules",
            [],
        ):

            path = module.get(
                "name",
                "",
            )

            lower = path.lower()

            score = 0.0

            #
            # keyword match
            #
            filename = Path(path).name.lower()
            stem = Path(path).stem.lower()
            parent = Path(path).parent.as_posix().lower()

            for kw in keywords:

                kw = kw.lower()

                # arquivo exato
                if kw == filename:
                    score += 500

                # nome do arquivo sem extensão
                elif kw == stem:
                    score += 400

                # arquivo contém palavra
                elif kw in filename:
                    score += 250

                # diretório contém palavra
                elif kw in parent:
                    score += 80

                # caminho completo
                elif kw in lower:
                    score += 40

            #
            # prioridade runtime
            #
            if lower.startswith(
                "app/runtime"
            ):
                score += 100

            #
            # project intelligence
            #
            if "project_intelligence" in lower:
                score += 40

            #
            # backup perde prioridade
            #
            if ".bak" in lower:
                score -= 200

            if "backup" in lower:
                score -= 200

            #
            # planning
            #
            if "planning" in lower:
                score += 60

            if score:

                candidates.append(
                    Candidate(
                        path=path,
                        score=score,
                        reason="module",
                    )
                )

        #
        # SERVICES
        #
        for service in context.get(
            "services",
            [],
        ):

            lower = service.lower()

            score = 0

            for kw in keywords:

                if kw in lower:
                    score += 20

            if score:

                candidates.append(
                    Candidate(
                        path=service,
                        score=score,
                        reason="service",
                    )
                )

        #
        # TODOS
        #
        for todo in context.get(
            "todos",
            [],
        ):

            text = todo.get(
                "text",
                "",
            ).lower()

            score = 0

            for kw in keywords:

                if kw in text:
                    score += 10

            if score:

                candidates.append(
                    Candidate(
                        path=todo.get(
                            "file",
                            "<todo>",
                        ),
                        score=score,
                        reason="todo",
                    )
                )

        candidates.sort(
            key=lambda c: c.score,
            reverse=True,
        )

        return candidates
