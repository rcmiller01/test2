import asyncio
import random
from typing import Dict

class ContextualInitiatives:
    """Monitor user context and take initiative when appropriate."""
    async def get_biometric_data(self) -> Dict[str, float]:
        await asyncio.sleep(0)
        return {"hr": random.randint(60, 100)}

    async def analyze_user_emotion(self) -> str:
        await asyncio.sleep(0)
        return random.choice(["happy", "neutral", "stressed"])

    async def get_calendar_context(self) -> str:
        await asyncio.sleep(0)
        return "free"

    def should_provide_support(self, biometric_data: Dict[str, float], emotion: str) -> bool:
        return emotion == "stressed" or biometric_data.get("hr", 0) > 95

    async def offer_contextual_support(self):
        print("[Context] Offering support to user")
        await asyncio.sleep(0)

    def user_seems_available_and_ai_has_something_to_share(self) -> bool:
        return random.random() > 0.5

    async def initiate_sharing_moment(self):
        print("[Context] Initiating sharing moment")
        await asyncio.sleep(0)

    async def monitor_user_context(self):
        biometric_data = await self.get_biometric_data()
        emotional_state = await self.analyze_user_emotion()
        schedule_context = await self.get_calendar_context()

        if self.should_provide_support(biometric_data, emotional_state):
            await self.offer_contextual_support()
        elif schedule_context == "free" and self.user_seems_available_and_ai_has_something_to_share():
            await self.initiate_sharing_moment() 