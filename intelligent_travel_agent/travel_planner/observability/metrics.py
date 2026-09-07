from collections import Counter

class Metrics:
    def __init__(self) -> None:
        self.counters: Counter[str] = Counter()

    def increment(self, name: str) -> None:
        self.counters[name] += 1

metrics = Metrics()
