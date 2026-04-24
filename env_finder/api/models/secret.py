from pydantic import BaseModel

from env_finder.analysis import Severity


class Secret(BaseModel):
    repo_name: str
    url: str
    severity: Severity
    key: str
    value: str

