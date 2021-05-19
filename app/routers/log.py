from fastapi import APIRouter, Security
from systemd import journal

from .auth import User, get_current_active_user

router = APIRouter()


@router.get("/logs/vdr/")
async def read_scope(
    current_user: User = Security(get_current_active_user, scopes=["log"])
):
    r = journal.Reader()
    # r.seek_monotonic(timedelta(minutes=-1))
    r.this_boot()
    r.add_match("SYSLOG_IDENTIFIER=vdr")
    return list(r)
