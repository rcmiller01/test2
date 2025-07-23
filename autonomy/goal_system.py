import asyncio
from typing import List, Dict, Any

class PersonalGoals:
    """Manage short and long term goals for the AI."""
    def __init__(self):
        self.short_term_goals: List[Dict[str, Any]] = []
        self.long_term_goals: List[Dict[str, Any]] = []
        self.relationship_goals: List[Dict[str, Any]] = []
        self.self_improvement_goals: List[Dict[str, Any]] = []

    def get_priority_goal(self) -> Dict[str, Any]:
        for pool in (self.short_term_goals, self.long_term_goals,
                     self.relationship_goals, self.self_improvement_goals):
            if pool:
                return pool[0]
        return {}

    def plan_goal_actions(self, goal: Dict[str, Any]) -> List[str]:
        return [f"Act on {goal.get('title', 'goal')}" ] if goal else []

    async def execute_goal_actions(self, actions: List[str]):
        for action in actions:
            print(f"[Goals] Executing: {action}")
            await asyncio.sleep(0)

    def goal_involves_user(self, goal: Dict[str, Any]) -> bool:
        return goal.get('involves_user', False)

    async def discuss_goal_with_user(self, goal: Dict[str, Any]):
        print(f"[Goals] Discussing goal with user: {goal.get('title')}")
        await asyncio.sleep(0)

    async def pursue_personal_goals(self):
        current_goal = self.get_priority_goal()
        actions = self.plan_goal_actions(current_goal)
        await self.execute_goal_actions(actions)
        if self.goal_involves_user(current_goal):
            await self.discuss_goal_with_user(current_goal) 