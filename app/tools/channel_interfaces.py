from pydantic import BaseModel

class ChannelpediaParameters(BaseModel):
    name: str
    provider: str
    frequency: int
    parameter: str
    source: str
    symbolrate: int
    vpid: int|str
    apid: int|str
    tpid: int|str
    caid: int|str
    sid: int
    nid: int
    tid: int
    rid: int
    x_label: str
    x_xmltv_id: str | None
    x_namespace: str | None
    x_timestamp_added: int
    x_last_changed: int
    x_last_confirmed: int
    x_utf8: int
    modulation: str
    x_unique_id: str

class ChannelpediaChannel(BaseModel):
    string: str
    parameters: ChannelpediaParameters

class ChannelpediaSubgroup(BaseModel):
    x_label: str
    channelcount: int
    lang: str
    sortstring: str
    friendlyname: str
    id: int
    channels: list[ChannelpediaChannel]

class Channel(BaseModel):
    number: int
    channel_id: str
    channel_string: str
    is_group: bool
    is_radio: bool
    name: str
    provider: str = ""
    ca: str = "0000"
    source: str

class Subgroup(BaseModel):
    id: str
    title: str
    children: list[Channel]