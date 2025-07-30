"""n8n agent for routing utility tasks via webhook workflows."""

import logging
from typing import Dict, Any
import requests


class N8nAgent:
    """Route tasks to n8n workflows registered by task type."""

    def __init__(self) -> None:
        self._registry: Dict[str, str] = {}
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            log_file = "logs/agent_n8n.log"
            handler = logging.FileHandler(log_file)
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def register_workflow(self, task_type: str, url: str) -> None:
        """Register an n8n webhook URL for a task type."""
        self._registry[task_type] = url
        self.logger.info(f"Registered workflow for {task_type}: {url}")

    def execute(self, task_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a registered workflow with payload.

        Args:
            task_type: Name of the task to execute.
            payload: Data to send to the workflow webhook.

        Returns:
            Response dictionary containing status and optional data.
        """
        url = self._registry.get(task_type)
        if not url:
            msg = f"No workflow registered for task type: {task_type}"
            self.logger.error(msg)
            return {"status": "error", "summary": msg}

        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json() if response.content else {}
            summary = data.get("message", "task executed")
            result = {"status": "success", "summary": summary, "data": data}
            self.logger.info(f"Executed {task_type} via {url}")
            return result
        except requests.RequestException as exc:
            self.logger.error(f"HTTP error for {task_type}: {exc}")
            return {"status": "error", "summary": str(exc)}
        except Exception as exc:  # Fallback for unexpected errors
            self.logger.error(f"Unhandled error for {task_type}: {exc}")
            return {"status": "error", "summary": str(exc)}
