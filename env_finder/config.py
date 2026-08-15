from functools import lru_cache

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Config(BaseSettings):
    github_pat: str          = Field(description="Github Personal Access Token, required for scraping")
    error_delay: float       = Field(default=5.0, description="Sleep delay after encountering an error during scraping")


    # For displaying a custom error message
    @field_validator("github_pat", mode="before")
    def pat_is_set(cls, v: str):
        if not v:
            raise ValueError("A Github PAT is required for this program to work. Add it to .env as 'GITHUB_PAT'")
        return v


@lru_cache
def get_config():
    return Config()