from typing import Annotated
from pydantic import BaseModel, Field, SecretStr, StringConstraints

USERNAME_REGEX = r"^[a-z_][a-z0-9_-]*$"

class Login(BaseModel):
    username: Annotated[str, StringConstraints(pattern=USERNAME_REGEX, min_length=1, max_length=32, strip_whitespace=True)]
    password: Annotated[SecretStr, Field(min_length=1, max_length=512)]
