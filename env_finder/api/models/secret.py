from pydantic import BaseModel, Field

from env_finder.analysis import Severity
from env_finder.api.models._shared_fields import REPO_NAME, SECRET_FILE_URL


class Secret(BaseModel):
    repo_name:      str = REPO_NAME
    url:            str = SECRET_FILE_URL
    severity:  Severity = Field(description="Severity level of the secret")
    key:            str = Field(description="Key of the key-value pair")
    value:          str = Field(description="Value of the key-value pair")


