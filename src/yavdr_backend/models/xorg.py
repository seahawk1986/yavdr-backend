from typing import Annotated, Any
from pydantic import BaseModel, BeforeValidator


class OutputConfig(BaseModel):
    connector: str
    resolution: str
    refreshrate: int

def falsy_to_none(x: dict[str, Any]|None) -> Any:
    return x or None

LeniantOptional = Annotated[OutputConfig|None, BeforeValidator(falsy_to_none)]

class XorgConfig(BaseModel):
    primary: OutputConfig
    secondary: LeniantOptional = None