from __future__ import annotations

from app.core.model_router import ModelRouter


class MCPRouter:
    """MCP-style routing layer for model coordination and task delegation."""

    def __init__(self) -> None:
        self.model_router = ModelRouter()

    def route_task(self, message: str) -> dict:
        decision = self.model_router.route(message)
        return {
            "route": decision["model_size"],
            "model": "small-model" if decision["model_size"] == "small" else "large-model",
            "reason": decision["reason"],
            "metadata": {
                "routing_strategy": "mcp",
                "safety_check": "enabled",
                "policy_enforced": True,
            },
        }
