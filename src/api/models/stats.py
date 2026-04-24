from pydantic import BaseModel


class Health(BaseModel):
    uptime_seconds: int
    up_since: str  # human-readable timestamp


class StatsEntry(BaseModel):
    timestamp: float
    repos_scraped: int
    secrets_count: int
    errors_count: int

