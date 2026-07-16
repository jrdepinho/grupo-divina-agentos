from collections import defaultdict

from agentos.services.dependency_service import DependencyService


class ArchitectureGraph:

    def build(self):

        deps = DependencyService().build()

        nodes = []
        edges = []

        reverse = defaultdict(list)

        for source, imports in deps.items():

            nodes.append(
                {
                    "id": source,
                    "type": "python"
                }
            )

            for target in imports:

                edges.append(
                    {
                        "from": source,
                        "to": target
                    }
                )

                reverse[target].append(source)

        central = sorted(
            reverse.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:20]

        return {
            "nodes": nodes,
            "edges": edges,
            "central_modules": [
                {
                    "module": k,
                    "used_by": len(v)
                }
                for k, v in central
            ]
        }


if __name__ == "__main__":

    import json

    print(
        json.dumps(
            ArchitectureGraph().build(),
            indent=2
        )
    )
