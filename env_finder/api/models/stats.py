from pydantic import BaseModel, Field


class Health(BaseModel):
    uptime_seconds:    int   = Field(description="Total uptime of the tool in seconds")
    up_since_epoch_ms: float = Field(description="Total uptime of the tool in milliseconds since epoch")
    up_since_utc:      str   = Field(description="Total uptime of the tool as a human-readable timestamp")


class StatsEntry(BaseModel):
    timestamp: float
    repos_scraped: int
    secrets_count: int
    errors_count: int

