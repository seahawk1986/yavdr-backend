from pydantic import BaseModel

class OutputConfig(BaseModel):
    connector: str
    resolution: str
    refreshrate: int

class XorgConfig(BaseModel):
    primary: OutputConfig
    secondary: OutputConfig|None = None