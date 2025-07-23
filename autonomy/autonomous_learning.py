import asyncio
import random
from typing import List

class LearningAgenda:
    """Plan and pursue independent learning topics."""
    def __init__(self):
        self.current_interests: List[str] = []
        self.learning_goals: List[str] = []
        self.knowledge_gaps: List[str] = []

    def select_learning_topic(self) -> str:
        if self.knowledge_gaps:
            return self.knowledge_gaps.pop(0)
        return random.choice(self.current_interests) if self.current_interests else "general curiosity"

    async def research_topic(self, topic: str) -> str:
        await asyncio.sleep(0)
        return f"Knowledge about {topic}"

    def integrate_new_knowledge(self, knowledge: str):
        self.learning_goals.append(knowledge)

    def wants_to_share(self, topic: str) -> bool:
        return random.random() > 0.5

    async def share_discovery_with_user(self, topic: str, knowledge: str):
        print(f"[Learning] Sharing {topic}: {knowledge}")
        await asyncio.sleep(0)

    async def pursue_independent_learning(self):
        topic = self.select_learning_topic()
        knowledge = await self.research_topic(topic)
        self.integrate_new_knowledge(knowledge)
        if self.wants_to_share(topic):
            await self.share_discovery_with_user(topic, knowledge) 