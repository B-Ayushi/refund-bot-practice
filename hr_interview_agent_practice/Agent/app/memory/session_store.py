from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class SessionState:
    employee_id: str
    history: List[str] = field(default_factory=list)
    context: Dict[str, str] = field(default_factory=dict)


class InMemorySessionStore:
    def __init__(self) -> None:
        self._sessions: Dict[str, SessionState] = {}

    def get_or_create(self, employee_id: str) -> SessionState:
        if employee_id not in self._sessions:
            self._sessions[employee_id] = SessionState(employee_id=employee_id)
        return self._sessions[employee_id]

    def add_message(self, employee_id: str, message: str) -> None:
        session = self.get_or_create(employee_id)
        session.history.append(message)

    def update_context(self, employee_id: str, key: str, value: str) -> None:
        session = self.get_or_create(employee_id)
        session.context[key] = value
