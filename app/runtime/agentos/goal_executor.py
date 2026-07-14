from .goal_planner import GoalPlanner

class GoalExecutor:

    def execute(self, dispatcher, goal):

        planner = GoalPlanner()

        plan = planner.build(goal)

        output=[]

        for step in plan:

            output.append(
                dispatcher.execute(
                    step.action,
                    step.args
                )
            )

        return output
