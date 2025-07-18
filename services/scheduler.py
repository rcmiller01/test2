import time
from core.normal_engine import emit_normal_thought_if_idle

NORMAL_THOUGHT_INTERVAL = 900  # 15 minutes

def run_normal_engine_scheduler():
    while True:
        emit_normal_thought_if_idle()
        time.sleep(NORMAL_THOUGHT_INTERVAL)
