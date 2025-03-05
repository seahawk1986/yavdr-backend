import datetime
import enum
import socket
from fastapi import APIRouter, Security
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict

from systemd import journal

from .auth import User, get_current_active_user

router = APIRouter()

hostname = socket.gethostname()

class ReverseReader(journal.Reader):
    def __next__(self):
        ans = self.get_previous()
        if ans:
            return ans
        raise StopIteration()

class LogRequestOptions(BaseModel):
    timestamp: datetime.datetime|None = None
    timedelta_s: int| None = None
    message_uuid: str|None = None
    n_entries: int| None = None
    identifier: str|None = None
    forward: bool = True

def create_alias(name: str) -> str:
    return name.lstrip('_')

class LogEntry(BaseModel):
    model_config = ConfigDict(
        # alias_generator=create_alias,
        extra="ignore"
    )
    # SOURCE_MONOTONIC_TIMESTAMP: datetime.timedelta|None = None
    TRANSPORT: str
    SYSLOG_FACILITY: int|None = None
    SYSLOG_IDENTIFIER: str|None = None
    SYSLOG_TIMESTAMP: str|None = None
    # BOOT_ID: UUID
    # MACHINE_ID: UUID
    HOSTNAME: str
    # RUNTIME_SCOPE: str
    PRIORITY: int
    MESSAGE: str
    REALTIME_TIMESTAMP: datetime.datetime|None = None
    # MONOTONIC_TIMESTAMP: datetime.timedelta|None = None
    CURSOR: str|None = None


class Direction(enum.StrEnum):
    forward = "forward"
    backward = "backward"

class PredefinedStart(enum.StrEnum):
    boot = 'boot'
    now = 'now'

@router.get("/logs/")
def read_scope(
    start: PredefinedStart|str,
    direction: Direction,
    n_entries: int,
    uuid: str|None = None,
    current_user: User = Security(get_current_active_user, scopes=["log"])  # NOTE: this is the way to implement scope-based access
) -> list[LogEntry]:
    match direction:
        case Direction.forward:
            reader = journal.Reader
        case Direction.backward:
            reader = ReverseReader
    with reader() as r:
        match start:
            case 'boot':
                r.this_boot()
            case 'now':
                dt = r.get_end()
                r.seek_realtime(dt)
            case _:
                timestamp = datetime.datetime.fromisoformat(start.replace(' ', '+'))
                r.seek_realtime(timestamp)

        response = []
        for n, e in zip(range(n_entries), r):
            # avoid to repeat an entry
            if uuid and e.get('__CURSOR') == uuid:
                continue
            response.append({k.lstrip('_'): v for k, v in e.items()})
        if direction == Direction.backward:
            response.reverse()
        return response

@router.get('/logs/time_limits')
def time_limits() -> tuple[datetime.datetime, datetime.datetime]:
    r = journal.Reader()
    return r.get_start(), r.get_end()



@router.get('/logs/download')
def download_log(start: str, end: str|None = None) -> StreamingResponse: # , current_user: User = Security(get_current_active_user, scopes=["log"])
    headers = {
        'Content-Disposition': "attachment; filename*=utf-8''{}".format(f"{start}_{hostname}_log.txt")
    }
    def iterlog():
        nonlocal start
        r = journal.Reader()
        match start:
            case 'boot':
                r.this_boot()
            case _:
                timestamp = datetime.datetime.fromisoformat(start.replace(' ', '+'))
                r.seek_realtime(timestamp)
        for e in r:
            timestamp = e['__REALTIME_TIMESTAMP']
            yield f"{timestamp.strftime("%b %d %H:%M:%S")} {e['_HOSTNAME']}: {e['MESSAGE']}\n"
    return StreamingResponse(iterlog(), headers=headers, media_type="text/plain")
