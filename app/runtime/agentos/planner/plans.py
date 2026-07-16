from __future__ import annotations

from dataclasses import asdict

from app.runtime.agentos.capability_metadata import get_metadata


def step(action: str, args: dict):

    data = {
        "action": action,
        "args": args,
    }

    data["metadata"] = asdict(
        get_metadata(action)
    )

    return data


def chat_plan(goal: str):

    return [
        step(
            "chat.complete",
            {
                "goal": goal,
            },
        )
    ]


def search_plan(query: str):

    return [
        step(
            "developer.search",
            {
                "text": query,
            },
        )
    ]


def read_plan(path: str):

    return [
        step(
            "developer.read",
            {
                "path": path,
            },
        )
    ]


def compile_plan():

    return [
        step(
            "developer.compile",
            {},
        ),
        step(
            "developer.validate",
            {},
        ),
    ]


def capabilities_plan():

    return [
        step(
            "admin.capabilities",
            {},
        )
    ]


def developer_plan(goal: str):

    return [

        step(
            "context.read",
            {
                "goal": goal,
            },
        ),

        step(
            "developer.search",
            {
                "text": goal,
            },
        ),

        step(
            "developer.compile",
            {},
        ),

        step(
            "developer.validate",
            {},
        ),

    ]
