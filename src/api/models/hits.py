from pydantic import BaseModel


class HitEntry(BaseModel):
    repo_name: str
    branch: str
    language: str
    url: str
    sha: str

