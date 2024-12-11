from dataclasses import dataclass, field
from gi.repository import GLib
from typing import Any, Mapping, Set

glib_loop = GLib.MainLoop()

@dataclass
class Timer:
    id: int
    remote: str # (with vdr >= 2.3.1)
    flags: int
    channel_id: str
    day_weekdays: str
    start: int
    stop: int
    priority: int
    lifetime: int
    filename: str
    aux: str
    event_id: int
    recording: bool
    pending: bool
    in_vps_margin: bool

@dataclass
class VDRStatus:
    # TODO: collect vdr's status events and store them temporarily
    isRecording: bool = False
    channel: int = None
    timers: Mapping[int, Any] = field(default_factory=lambda: dict())
