from collections import defaultdict

from agentos.services.architecture_graph import ArchitectureGraph


class ImpactAnalysisService:

    def analyze(self, target: str):

        graph = ArchitectureGraph().build()

        reverse = defaultdict(list)

        for edge in graph["edges"]:
            reverse[edge["to"]].append(edge["from"])

        direct = []

        for edge in graph["edges"]:
            if edge["from"] == target:
                direct.append(edge["to"])

        return {
            "target": target,
            "direct_dependencies": sorted(set(direct)),
            "reverse_dependencies": sorted(set(reverse.get(target, []))),
            "risk": self._risk(
                len(direct),
                len(reverse.get(target, [])),
            ),
        }

    def _risk(self, direct, reverse):

        score = direct + reverse

        if score >= 20:
            return "critical"

        if score >= 10:
            return "high"

        if score >= 5:
            return "medium"

        return "low"


if __name__ == "__main__":

    import json

    svc = ImpactAnalysisService()

    print(
        json.dumps(
            svc.analyze(
                "agentos/services/git_service.py"
            ),
            indent=2,
        )
    )
