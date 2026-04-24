from pydantic import BaseModel


# temp class
class Severity:
    pass


class Secret(BaseModel):
    repo_name: str
    url: str
    severity: Severity
    key: str
    value: str

