from pydantic import Field


REPO_NAME       = Field(description="User + Repository name; e.g. '<username>/<repo_name>'")
SECRET_FILE_URL = Field(description="URL pointing to the exact file the secret was found in")

