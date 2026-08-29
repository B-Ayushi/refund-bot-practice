from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class Settings:
    app_name: Final[str] = "hr-support-agent"
    max_requests_per_minute: Final[int] = 5000
    simple_request_latency_ms: Final[int] = 2000
    complex_request_latency_ms: Final[int] = 10000
    annual_leave_days: Final[int] = 20
    sick_leave_days: Final[int] = 10
    manager_approval_threshold_days: Final[int] = 5
    payroll_dispute_limit_inr: Final[int] = 50000


settings = Settings()
