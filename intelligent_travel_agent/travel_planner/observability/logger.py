import json
import logging
from typing import Any

class StructuredLogger:
    def __init__(self, name: str = "travel_planner") -> None:
        self._logger = logging.getLogger(name)

    def event(self, event: str, **fields: Any) -> None:
        self._logger.info(json.dumps({"event": event, **fields}, default=str))

logger = StructuredLogger()
