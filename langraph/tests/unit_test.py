import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import graph


result = graph.invoke({"user_query": "where is my order 1001"})
assert result["intent"] == "status"
assert result["result"] == "Delivered"
print(result["result"])