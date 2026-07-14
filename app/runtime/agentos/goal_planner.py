from dataclasses import dataclass

@dataclass
class Step:
    action: str
    args: dict

class GoalPlanner:

    def build(self, goal: str):

        g = goal.lower()

        if "erp" in g:
            return [
                Step("admin.plan_execute", {"plan":"diagnose"}),
                Step("erp.modules_summary", {}),
                Step("admin.plan_execute", {"plan":"validate_v2"}),
            ]

        if "frontend" in g:
            return [
                Step("frontend.status", {}),
                Step("frontend.list", {}),
            ]

        if "supabase" in g:
            return [
                Step("supabase.metadata_counts", {}),
            ]

        return [
            Step("goal.echo", {"goal":goal})
        ]
