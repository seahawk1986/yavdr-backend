from pathlib import Path
from pydantic import BaseModel

class PluginConfig(BaseModel):
    name: str
    enabled: bool
    prio: int
    arguments: str = ""
    help: str = ""


class ArgumentFile(BaseModel):
    filename: Path
    name: str
    prio: int
    enabled: bool
    static: bool
    args: str
    help: str
    warning: None|str = None
