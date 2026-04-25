from pydantic import BaseModel, Field


class Health(BaseModel):
    uptime_seconds:      int = Field(description="Total uptime of the tool in seconds")
    up_since_epoch_ms: float = Field(description="Starting time of the tool in seconds relative to the epoch")
    up_since_utc:        str = Field(description="Total uptime of the tool as a human-readable timestamp")


class StatsEntry(BaseModel):
    timestamp_ms: float = Field(description="Timestamp of when the stats entry was created")
    repos_scraped:  int = Field(description="Number of repos scraped at given time")
    secrets_count:  int = Field(description="Number of secrets found at given time")
    errors_count:   int = Field(description="Number of errors that have occurred during the scraping session up until this point")

