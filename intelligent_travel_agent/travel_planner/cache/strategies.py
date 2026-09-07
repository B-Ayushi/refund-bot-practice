import hashlib
import json

def cache_key(operation: str, parameters: object) -> str:
    payload = json.dumps(parameters, sort_keys=True, default=str)
    return f"{operation}:{hashlib.sha256(payload.encode()).hexdigest()}"
