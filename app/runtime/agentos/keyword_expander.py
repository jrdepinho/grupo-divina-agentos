from __future__ import annotations


EXPANSIONS = {

    "planner": [
        "planner",
        "planning",
        "plan",
    ],

    "deploy": [
        "deploy",
        "deployment",
    ],

    "produto": [
        "produto",
        "product",
        "products",
    ],

    "cliente": [
        "cliente",
        "clientes",
        "customer",
        "customers",
    ],

    "estoque": [
        "estoque",
        "inventory",
        "stock",
    ],

    "financeiro": [
        "financeiro",
        "financial",
        "finance",
        "billing",
    ],

}


class KeywordExpander:

    def expand(
        self,
        keywords: list[str],
    ) -> list[str]:

        expanded = []

        for word in keywords:

            expanded.append(word)

            expanded.extend(
                EXPANSIONS.get(
                    word,
                    [],
                )
            )

        return sorted(
            set(expanded)
        )
