from .models import MemoryRecord

class PreferenceStore:
    def __init__(self) -> None:
        self._records: dict[str, dict[str, MemoryRecord]] = {}

    def put(self, session_id: str, record: MemoryRecord) -> None:
        self._records.setdefault(session_id, {})[record.key] = record

    def get_all(self, session_id: str) -> dict[str, MemoryRecord]:
        return dict(self._records.get(session_id, {}))

    def delete(self, session_id: str, key: str) -> None:
        self._records.get(session_id, {}).pop(key, None)
