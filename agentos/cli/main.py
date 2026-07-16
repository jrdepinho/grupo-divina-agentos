import argparse

from agentos.mission.manager import MissionManager
from agentos.memory.store import MemoryStore
from app.runtime.execute_goal import run_goal


def main():

    parser = argparse.ArgumentParser(prog="agentos")

    sub = parser.add_subparsers(dest="command")

    sub.add_parser("doctor")
    sub.add_parser("version")
    sub.add_parser("status")


    goal = sub.add_parser("goal")
    goal.add_argument("goal")
    goal.add_argument("--mode", default="execute")
    goal.add_argument("--approval", default="auto")


    mission = sub.add_parser("mission")
    ma = mission.add_subparsers(dest="action")

    c = ma.add_parser("create")
    c.add_argument("title")
    c.add_argument("--priority", type=int, default=100)
    c.add_argument("--depends", action="append", default=[])

    s = ma.add_parser("start")
    s.add_argument("id")

    d = ma.add_parser("done")
    d.add_argument("id")

    f = ma.add_parser("fail")
    f.add_argument("id")

    ma.add_parser("list")

    h = ma.add_parser("history")
    h.add_argument("id")

    memory = sub.add_parser("memory")
    mem = memory.add_subparsers(dest="action")

    ms = mem.add_parser("set")
    ms.add_argument("key")
    ms.add_argument("value")

    mg = mem.add_parser("get")
    mg.add_argument("key")

    mem.add_parser("list")

    args = parser.parse_args()

    manager = MissionManager()
    memory = MemoryStore()

    if args.command == "mission":

        if args.action == "create":
            print(
                manager.create(
                    args.title,
                    priority=args.priority,
                    depends_on=args.depends
                )
            )
            return

        if args.action == "start":
            manager.start(args.id)
            print("RUNNING")
            return

        if args.action == "done":
            manager.finish(args.id)
            print("DONE")
            return

        if args.action == "fail":
            manager.fail(args.id)
            print("FAILED")
            return

        if args.action == "list":
            for row in manager.list():
                print(row)
            return

        if args.action == "history":
            for row in manager.history(args.id):
                print(row)
            return

    if args.command == "memory":

        if args.action == "set":
            memory.set(args.key, args.value)
            print("OK")
            return

        if args.action == "get":
            print(memory.get(args.key))
            return

        if args.action == "list":
            for row in memory.list():
                print(row)
            return


    if args.command == "goal":

        result = run_goal(
            goal=args.goal,
            mode=args.mode,
            approval=args.approval,
        )

        print(result)
        return

    if args.command == "doctor":
        print("OK")
        return

    if args.command == "version":
        print("AgentOS 0.3.0")
        return

    if args.command == "status":
        print("Running")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
