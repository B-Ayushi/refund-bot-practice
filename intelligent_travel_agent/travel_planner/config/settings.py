from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    max_validation_iterations: int = 3
    max_clarification_attempts: int = 3
    max_review_cycles: int = 2
    cache_ttl_seconds: int = 300

settings = Settings()
