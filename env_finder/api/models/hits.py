from pydantic import BaseModel, Field

from env_finder.api.models._shared_fields import REPO_NAME, SECRET_FILE_URL


class HitEntry(BaseModel):
    repo_name: str = REPO_NAME
    branch:    str = Field(description="Branch name")
    language:  str = Field(description="Main Language of the Repository")
    url:       str = SECRET_FILE_URL
    sha:       str = Field(description="SHA of the file the credential was found in")

