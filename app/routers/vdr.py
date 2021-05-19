from typing import List, Optional
from functools import wraps
from fastapi import APIRouter, Depends, HTTPException

import pydbus2vdr
from gi.repository import GLib
from pydantic import BaseModel
from starlette.responses import JSONResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_503_SERVICE_UNAVAILABLE,
)

from .auth import get_current_active_user, User
from tools import SVDRPClient, vdr_plugins

router = APIRouter()

vdr = None


class Message(BaseModel):
    msg: str


def set_vdr(vdr):
    if vdr is None:
        try:
            vdr = pydbus2vdr.DBus2VDR()
        except GLib.Error:
            # Don't stop if vdr has no dbus interface
            vdr = None
            print("could not init pydbus2vdr.DBus2VDR :(")
    return vdr


def dbus_error_wrapper(f):
    global vdr
    vdr = set_vdr(vdr)

    @wraps(f)
    def wrapper(*args, **kwds):
        try:
            return f(*args, **kwds)
        except (AttributeError, GLib.GError):
            global vdr
            vdr = set_vdr(None)
            try:
                return f(*args, **kwds)
            except (AttributeError, GLib.GError):
                raise HTTPException(status_code=503, detail="VDR did not respond")

    return wrapper


class Recordings(BaseModel):
    RecNum: int
    Path: str
    Name: str
    FullName: Optional[str]
    Title: str
    title: str  # this is either InfoTitle or Name
    searchTitle: str
    Start: int
    Priority: int
    Lifetime: int
    HierarchyLevels: int
    FramesPerSecond: float
    NumFrames: int
    LengthInSeconds: int
    duration: str
    FileSizeMB: int
    IsPesRecording: bool
    IsNew: bool
    IsEdited: bool
    InfoChannelID: Optional[str]
    InfoChannelName: Optional[str]
    InfoTitle: Optional[str]
    InfoShortText: Optional[str]
    InfoDescription: Optional[str]
    InfoAux: Optional[str]
    InfoFramesPerSecond: Optional[str]


@router.get("/vdr/recordings", response_model=List[Recordings])
@dbus_error_wrapper
def get_vdr_recordings(*, current_user: User = Depends(get_current_active_user)):
    recordings = []
    for n, r in vdr.Recordings.List():
        try:
            new_rec = {}
            for (k, v) in r:
                k = k.replace("/", "")
                # print(k, v)
                new_rec[k] = v
            new_rec["RecNum"] = int(n)

            ls = new_rec["LengthInSeconds"]
            hours = ls // 3600
            minutes = (ls % 3600) // 60
            seconds = (ls % 3600) % 60
            new_rec["duration"] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            title = new_rec.get("InfoTitle", new_rec["Name"])

            subtitle = new_rec.get("InfoShortText")
            if subtitle:
                title = f"{title} - {subtitle}"

            new_rec["title"] = title
            new_rec["searchTitle"] = title.lower()
            recordings.append(new_rec)
        except Exception as err:
            print(err)
    # print(recordings)
    return recordings


class RecNum(BaseModel):
    RecNum: int


def getSVDRP_Recording_ID_by_name(title):
    # TODO: we need a better way to match the recordings
    #       than just comparing the "Title" sent by dbus2vdr
    with SVDRPClient("localhost", 6419) as svdrp:
        for rec in svdrp.send_cmd_and_get_response("lstr"):
            resp, resp_ok, data = rec
            print(data.split(maxsplit=4))
            rec_id, rec_date, rec_time, duration, path = data.split(maxsplit=4)
            comp_title = " ".join((rec_date, rec_time + " ", path))
            print(comp_title, title)
            if comp_title == title:
                print(comp_title, "==", title, "?")
                return rec_id


@router.post(
    "/vdr/recordings/play",
    responses={
        HTTP_200_OK: {
            "model": Message,
            "description": "replay request sent successfully",
        },
        HTTP_400_BAD_REQUEST: {"model": Message, "description": "invalid rec number"},
        HTTP_503_SERVICE_UNAVAILABLE: {
            "model": Message,
            "description": "vdr is not available",
        },
    },
)
@dbus_error_wrapper
def play_recording(
    *, rec_num: RecNum, current_user: User = Depends(get_current_active_user)
):
    print("play_recording called with", rec_num)

    rec_num = int(rec_num.RecNum)
    if rec_num >= 0:
        success = vdr.Recordings.Play(rec_num, -1)
        print("got response for playing rec by num:", success)
    else:
        success = False

    if not success:
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST,
            content={"msg": "only positive numbers are allowed"},
        )


@router.get("/vdr/plugins")
@dbus_error_wrapper
def get_vdr_plugins(current_user: User = Depends(get_current_active_user)):
    return [p._asdict() for p in vdr.Plugins.list()]


class Timer(BaseModel):
    status: int
    raw: str
    channel: str
    channelname: str
    day: str
    start: int
    stop: int
    time: str
    priority: int
    lifetime: int
    filename: str
    aux: str


@router.get("/vdr/timers", response_model=List[Timer])
@dbus_error_wrapper
def get_vdr_timers(current_user: User = Depends(get_current_active_user)):
    timers = vdr.Timers.List()
    channels_raw, *_ = vdr.Channels.List()
    channel_ids = {}
    for channel in channels_raw:
        chan_num, chan_str = channel
        name, freq, params, source, srate, vpid, apid, tpid, ca, sid, nid, tid, rid = chan_str.split(
            ":"
        )
        if nid == "0" and tid == "0":
            if source.startswith("S"):
                offsets = {"H": 10000, "V": 20000, "L": 30000, "R": 40000}
                offset = offsets[params[0]]
            else:
                offset = 0
            tid = str(int(freq) + offset)

        fields = [source, nid, tid, sid]

        # the last part can be omitted if RID is 0
        if rid != "0":
            fields.append(rid)
        chan_id = "-".join(fields)
        channel_name = name.split(";")[0]
        channel_ids[chan_id] = channel_name

    t_data = []
    for timer in timers:
        (
            status,
            channel,
            day,
            start,
            stop,
            priority,
            lifetime,
            filename,
            aux,
        ) = timer.split(":")

        time = f"{start[:2]}:{start[2:]} - {stop[:2]}:{stop[2:]}"

        t_data.append(
            Timer(
                **{
                    "raw": timer,
                    "status": int(status),
                    "channel": channel,
                    "day": day,
                    "start": int(start),
                    "stop": int(stop),
                    "time": time,
                    "priority": int(priority),
                    "lifetime": int(lifetime),
                    "filename": filename,
                    "aux": aux,
                    "channelname": channel_ids.get(channel, "?"),
                }
            )
        )
    return t_data


class Channel(BaseModel):
    number: int
    channel_string: str
    is_group: bool
    name: str
    provider: str = ""
    ca: str = '0000'
    source: str


@router.get("/vdr/channels")
@dbus_error_wrapper
def get_vdr_channels(
    current_user: User = Depends(get_current_active_user)
) -> List[Channel]:
    channels = []
    channels_raw, *_ = vdr.Channels.List()
    for channel in channels_raw:
        chan_num, chan_str = channel
        channels.append({"channel_number": chan_num, "channel_string": chan_str})
    return channels


@router.get("/vdr/channels_with_groups", response_model=List[Channel])
def get_vdr_channels_with_groups(current_user: User = Depends(get_current_active_user)):
    channels = []
    with SVDRPClient("localhost", 6419) as svdrp:
        for r in svdrp.send_cmd_and_get_response("lstc :groups"):
            number, channel_string = r.split(maxsplit=1)
            if channel_string.startswith(':'):  # channel group
                if channel_string[1] == '@':  # group number with channel number
                    group_number, name = channel_string[2:].split(" ", maxsplit=1)
                else:
                    name = channel_string[1:]

                channels.append(
                    Channel(
                        number=number,
                        channel_string=channel_string,
                        is_group=True,
                        name=name,
                        ca=0,
                        provider="",
                        source="",
                    ))
            else:
                try:
                    name, frequency, parameters, source, srate, vpid, apid, tpid, ca, sid, nid, tid, rid, *channel_data = channel_string.split(":")
                except Exception as err:
                    print(f"could not process {channel_string=}")
                    print(err)

                number = int(number)
                name, _, provider = name.partition(';')
                name, _, short_name = name.partition(',')

                channels.append(
                    Channel(
                        number=number,
                        channel_string=channel_string,
                        is_group=False,
                        name=name,
                        provider=provider,
                        source=source,
                        ca=ca,
                    )
                )
    return channels


@router.get("/vdr/plugin_config", response_model=List[vdr_plugins.PluginConfig])
def get_plugin_config(current_user: User = Depends(get_current_active_user)):
    return list(vdr_plugins.read_plugins())


@router.post("/vdr/plugin_config",
    responses={
        HTTP_200_OK: {
            "model": Message,
            "description": "config written successfully",
        },
        HTTP_400_BAD_REQUEST: {"model": Message, "description": "invalid rec number"},
        HTTP_503_SERVICE_UNAVAILABLE: {
            "model": Message,
            "description": "vdr is not available",
        },
    },
)
def write_plugin_config(current_user: User = Depends(get_current_active_user)):
    return 
