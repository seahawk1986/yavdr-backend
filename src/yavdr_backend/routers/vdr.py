import asyncio
from collections.abc import AsyncGenerator
import contextlib
import datetime

import json
import os
import tempfile
import uuid

import pkgconfig

from enum import IntFlag, StrEnum
from pathlib import Path
from typing import Any
from pydantic import Field, BaseModel
from fastapi import (
    APIRouter,
    Depends,
    Request,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
)
from sse_starlette.sse import EventSourceResponse

# from pydantic.errors import DataclassTypeError
# from pydantic.main import BaseModel

# import pydbus2vdr
from fastapi.responses import FileResponse
import sdbus
from starlette.responses import JSONResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_503_SERVICE_UNAVAILABLE,
)

from yavdr_backend.tools.channel_interfaces import Channel


from .auth import get_current_active_user, User
from yavdr_backend.tools import (
    vdr_plugin_config,
    async_send_svdrpcommand,
    read_vdr_arguments,
    write_argument_file,
    PluginConfig,
)
from yavdr_backend.interfaces.vdr_channels import DeTvdrVdrChannelInterface
from yavdr_backend.interfaces.vdr_epg import DeTvdrVdrEpgInterface
from yavdr_backend.interfaces.vdr_plugins import DeTvdrVdrPluginmanagerInterface
from yavdr_backend.interfaces.vdr_recordings import DeTvdrVdrRecordingInterface
from yavdr_backend.interfaces.vdr_timers import DeTvdrVdrTimerInterface, DetailedTimer
from yavdr_backend.interfaces.vdr_setup import DeTvdrVdrSetupInterface
from yavdr_backend.interfaces.vdr_skin import DeTvdrVdrSkinInterface
from yavdr_backend.interfaces.vdr_status import (
    signal_generator as vdr_status_event_generator,
)
from yavdr_backend.interfaces.system_backend import (
    AllowedVDRConfigfiles,
    Status,
    YavdrSystemBackend,
    YAVDR_BACKEND_INTERFACE,
    allowed_vdr_config_files_options,
)


# from tools.epg import DVB_CONTENT_NIBBLE, DVB_DATA_TYPE, DVB_SERVICE_TYPE

router = APIRouter()


class Message(BaseModel):
    msg: str


# def set_vdr(vdr):
#     if vdr is None:
#         try:
#             vdr = pydbus2vdr.DBus2VDR()
#         except GLib.Error:
#             # Don't stop if vdr has no dbus interface
#             vdr = None
#             print("could not init pydbus2vdr.DBus2VDR :(")
#     return vdr


# def dbus_error_wrapper(f):
#     global vdr
#     vdr = set_vdr(vdr)

#     @wraps(f)
#     def wrapper(*args, **kwds):
#         try:
#             return f(*args, **kwds)
#         except (AttributeError, GLib.GError):
#             global vdr
#             vdr = set_vdr(None)
#             try:
#                 return f(*args, **kwds)
#             except (AttributeError, GLib.GError):
#                 raise HTTPException(status_code=503, detail="VDR did not respond")

#     return wrapper


class Recording(BaseModel):
    RecNum: int
    Path: str
    Name: str
    FullName: str | None = None
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
    InfoChannelID: str | None = None
    InfoChannelName: str | None = None
    InfoTitle: str | None = None
    InfoShortText: str | None = None
    InfoDescription: str | None = None
    InfoAux: str | None = None
    InfoFramesPerSecond: float | None = None


@router.get("/vdr/recordings", response_model=list[Recording])
async def get_vdr_recordings(current_user: User = Depends(get_current_active_user)) -> list[Recording]:
    with contextlib.closing(sdbus.sd_bus_open_system()) as bus:
        vdr_recordings = DeTvdrVdrRecordingInterface.new_proxy(
            "de.tvdr.vdr",
            "/Recordings",
            bus=bus,
        )
        recordings: list[Recording] = []
        for n, r in await vdr_recordings.list():
            try:
                new_rec: dict[str, Any] = {}
                for k, v in r:
                    k = k.replace("/", "")
                    # print(k, v, type(v))
                    if isinstance(v, tuple): # pyright: ignore[reportUnnecessaryIsInstance]
                        new_rec[k] = v[-1]
                    else:
                        new_rec[k] = v
                new_rec["RecNum"] = int(n)

                ls = new_rec["LengthInSeconds"]
                hours = ls // 3600
                minutes = (ls % 3600) // 60
                seconds = (ls % 3600) % 60
                new_rec["duration"] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                title: str = new_rec.get("InfoTitle", new_rec["Name"])

                subtitle = new_rec.get("InfoShortText")
                if subtitle:
                    title = f"{title} - {subtitle}"

                new_rec["title"] = title
                new_rec["searchTitle"] = title.lower()
                recordings.append(Recording(**new_rec))
            except Exception as err:
                print("Error:", err)
        # print(recordings)
        return sorted(recordings, key=lambda r: r.Start, reverse=True)


class RecNum(BaseModel):
    RecNum: int


async def getSVDRP_Recording_ID_by_name(title: str):
    # TODO: we need a better way to match the recordings
    #       than just comparing the "Title" sent by dbus2vdr
    async for line in async_send_svdrpcommand("lstr"):
        _code, data = line.strip().split("-", maxsplit=1)
        print(data.split(maxsplit=4))
        rec_id, rec_date, rec_time, _duration, path = data.split(maxsplit=4)
        comp_title = " ".join((rec_date, rec_time + " ", path))
        print(comp_title, title)
        if comp_title == title:
            print(comp_title, "==", title, "?")
            return rec_id


class ReplayData(BaseModel):
    RecNum: int
    continue_replay: int


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
async def play_recording(
    *, data: ReplayData, current_user: User = Depends(get_current_active_user)
):
    with contextlib.closing(sdbus.sd_bus_open_system()) as bus:
        vdr_recordings = DeTvdrVdrRecordingInterface.new_proxy(
            "de.tvdr.vdr",
            "/Recordings",
            bus=bus,
        )
        print("play_recording called with", data)

        rec_num = data.RecNum
        if rec_num >= 0:
            success = await vdr_recordings.play(("i", rec_num), ("i", data.continue_replay))
            print("got response for playing rec by num:", success)
        else:
            success = False

        if not success:
            return JSONResponse(
                status_code=HTTP_400_BAD_REQUEST,
                content={"msg": "only positive numbers are allowed"},
            )
        return JSONResponse(status_code=HTTP_200_OK, content={"msg": f"playing recording {data.RecNum}"})


class Plugin(BaseModel):
    name: str
    version: str


@router.get("/vdr/plugins")
async def get_vdr_plugins(
    *, current_user: User = Depends(get_current_active_user)
) -> list[Plugin]:
    vdr_plugins = DeTvdrVdrPluginmanagerInterface.new_proxy(
        "de.tvdr.vdr", "/Plugins", bus=sdbus.sd_bus_open_system()
    )
    plugins = await vdr_plugins.list()
    return [Plugin(name=n, version=v) for n, v in plugins]


@router.get("/vdr/start_arguments")
async def get_vdr_start_arguments(
    current_user: User = Depends(get_current_active_user),
):
    return read_vdr_arguments()


@router.put("/vdr/start_arguments")
async def write_args_config(
    config: PluginConfig, _User: User=Depends(get_current_active_user)
):
    await write_argument_file(config)
    return True


@router.get("/vdr/current_epg")
async def get_current_epg(current_user: User = Depends(get_current_active_user)):
    vdr_epg = DeTvdrVdrEpgInterface.new_proxy(
        "de.tvdr.vdr", "/EPG", bus=sdbus.sd_bus_open_system()
    )
    data = await vdr_epg.now("")
    return data


@router.get("/vdr/current_channel_epg")
async def get_current_channel_epg(
    current_user: User = Depends(get_current_active_user),
):
    vdr_channels = DeTvdrVdrChannelInterface.new_proxy(
        "de.tvdr.vdr", "/Channels", bus=sdbus.sd_bus_open_system()
    )
    vdr_epg = DeTvdrVdrEpgInterface.new_proxy(
        "de.tvdr.vdr", "/EPG", bus=sdbus.sd_bus_open_system()
    )
    _, current_channel = await vdr_channels.current()
    print(f"current channel: {current_channel}")
    data = await vdr_epg.now(current_channel), await vdr_epg.next(current_channel)
    return data


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


class TimerDetails(BaseModel):
    status_flags: int
    raw: str
    id: int
    channel_id: str
    channel_name: str
    remote: str
    channel_id: str
    day_weekdays: str
    start: int
    stop: int
    time_span: str
    duration: int
    priority: int
    lifetime: int
    filename: str
    aux: str
    event_id: int
    is_recording: bool
    is_pending: bool
    in_vps_margin: bool


class ChannelData(BaseModel):
    name: str
    freq: int
    params: str
    source: str
    srate: int
    vpid: int
    apid: int
    tpid: int
    ca: int
    sid: int
    nid: int
    tid: int
    rid: int


@router.get("/vdr/timers", response_model=list[TimerDetails])
async def get_vdr_timers(
    *, current_user: User = Depends(get_current_active_user)
) -> list[TimerDetails]:
    vdr_channels = DeTvdrVdrChannelInterface.new_proxy(
        "de.tvdr.vdr", "/Channels", bus=sdbus.sd_bus_open_system()
    )
    vdr_timers = DeTvdrVdrTimerInterface.new_proxy(
        "de.tvdr.vdr", "/Timers", bus=sdbus.sd_bus_open_system()
    )
    # TODO: use svdrp, so we get the timer id, too
    timers = [
        line[4:].split(maxsplit=1)
        async for line in async_send_svdrpcommand("LSTT")
        if line.startswith("250")
    ]
    print(timers)
    timers_detailed = (
        await vdr_timers.list_detailed()
    )  # TODO: do we want to use the more detailed vdr.Timers.ListDetailed ?
    channels_raw, *_ = await vdr_channels.list("")
    channel_ids: dict[str, str] = {}
    for channel in channels_raw:
        _chan_num, chan_str = channel
        (
            name,
            freq,
            params,
            source,
            _srate,
            _vpid,
            _apid,
            _tpid,
            _ca,
            sid,
            nid,
            tid,
            rid,
        ) = chan_str.split(":")
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

    t_data: list[TimerDetails] = []
    for timer in timers_detailed:
        d = DetailedTimer(*timer)

        start_formatted = f"{d.start:04d}"
        stop_formatted = f"{d.stop:04d}"
        start_h = start_formatted[:2]
        start_m = start_formatted[2:]
        stop_h = stop_formatted[:2]
        stop_m = stop_formatted[2:]
        timespan_str = f"{start_h}:{start_m} - {stop_h}:{stop_m}"
        try:
            # try to get the day as a datetime.date
            day_start = datetime.date.fromisoformat(d.day_weekdays)
            t_start = datetime.time(hour=int(start_h), minute=int(start_m))
            t_stop = datetime.time(hour=int(stop_h), minute=int(stop_m))

            # check if the end point in hours is smaller than the start point - in this case we have a day change
            day_stop = (
                day_start + datetime.timedelta(days=1)
                if (t_stop < t_start)
                else day_start
            )

            start = datetime.datetime.combine(day_start, t_start).timestamp()
            stop = datetime.datetime.combine(day_stop, t_stop).timestamp()

        except ValueError as err:
            # TODO: handle VDR's repeating timers
            print("special repeat timer by VDR:", err)
            start = 0
            stop = 0
            duration = 0
            continue

        duration = stop - start

        t_data.append(
            TimerDetails(
                id=d.id,
                status_flags=d.flags,
                raw=f"{d.flags}:{d.channel_id}:{d.day_weekdays}:{d.start}:{d.stop}:{d.lifetime}:{d.priority}:{d.aux}",
                remote=d.remote,
                channel_id=d.channel_id,
                channel_name=channel_ids.get(d.channel_id, "?"),
                day_weekdays=d.day_weekdays,
                event_id=d.event_id,
                start=int(start),
                stop=int(stop),
                time_span=timespan_str,
                duration=int(duration),
                priority=d.priority,
                lifetime=d.lifetime,
                filename=d.filename,
                aux=d.aux,
                is_recording=d.is_recording,
                is_pending=d.is_pending,
                in_vps_margin=d.in_vps_margin,
            )
        )
    return t_data


class TimerStatus(IntFlag):
    INACTIVE = 0
    PENDING = 1
    INSTANT_REC = 2
    VPS = 4
    IS_RECORDING = 8


class TimerData(BaseModel):
    active: int = Field(default=TimerStatus.PENDING)
    channel_id: str | int
    dt_start: datetime.datetime
    dt_end: datetime.datetime
    title: str
    prio: int = Field(default=50)
    lifetime: int = Field(default=99)
    aux: str = Field(default="")


@router.post("/vdr/newt")
async def create_timer(
    timer: TimerData, current_user: User = Depends(get_current_active_user)
):
    print(
        f"NEWT {timer.active}:{timer.channel_id}:{timer.dt_start.strftime('%Y-%m-%d')}:{timer.dt_start.strftime('%H%M')}:{timer.dt_end.strftime('%H%M')}:{timer.prio}:{timer.lifetime}:{timer.title}:{timer.aux}"
    )
    # TODO: get time before/after timer
    async for line in async_send_svdrpcommand(
        f"NEWT {timer.active}:{timer.channel_id}:{timer.dt_start.strftime('%Y-%m-%d')}:{timer.dt_start.strftime('%H%M')}:{timer.dt_end.strftime('%H%M')}:{timer.prio}:{timer.lifetime}:{timer.title}:{timer.aux}"
    ):
        print(line)


class ChannelMapping(BaseModel):
    channel_number: int
    channel_string: str


# channelMapping = dict[int, str]


@router.get("/vdr/channels")
async def get_vdr_channels(
    current_user: User = Depends(get_current_active_user),
) -> list[ChannelMapping]:
    vdr_channels = DeTvdrVdrChannelInterface.new_proxy(
        "de.tvdr.vdr", "/Channels", bus=sdbus.sd_bus_open_system()
    )

    channels: list[ChannelMapping] = []
    channels_raw, _status_code, _message = await vdr_channels.list(":groups")
    print(f"{channels_raw=}")
    for channel in channels_raw:
        print(f"{channel=}")
        chan_num, chan_str = channel
        channels.append(
            ChannelMapping(channel_number=chan_num, channel_string=chan_str)
        )
    return channels


@router.post("/vdr/channels")
def save_vdr_channels(channel_list: list[str]):
    print(channel_list)
    channels_conf = Path(
        "/tmp/channels.conf"
    )  # TODO: make this location configurable resp. read it from VDR
    config_dir = Path(
        os.environ.get(
            "VDR_CONFIG_DIR",
            pkgconfig.variables("vdr").get("configdir", "/var/lib/vdr"), # pyright: ignore[reportUnknownMemberType]
        )
    )
    print(f"{config_dir=}")
    # TODO: stop vdr - can we do this as an ansible run command?
    # write channels.conf
    channels_conf.write_text("\n".join(channel_list))

    # TODO: start vdr again (if it was stopped)


@router.post("/vdr/channels", response_model=tuple[bool, str])
def upload_vdr_channels(
    channels: list[str], current_user: User = Depends(get_current_active_user)
):
    for c in channels:
        print(c)
    return True, "ok"


@router.post("/vdr/channelfile")
async def upload_channels_conf(file: UploadFile) -> bool:
    tmp = Path("/var/cache/yavdr-webfrontend/channel_lists/")
    tmp.mkdir(parents=True, exist_ok=True)
    print(f"{file.filename} {file.size}")
    if not file.filename:
        file.filename = "channels.conf"
    content = await file.read()
    # TODO: validate channels.conf
    (p := (tmp / file.filename)).write_bytes(content)
    print(f"wrote file {p}")
    return True


@router.get("/vdr/channels_with_groups", response_model=list[Channel])
async def get_vdr_channels_with_groups(
    current_user: User = Depends(get_current_active_user),
) -> list[Channel]:
    channels: list[Channel] = []
    async for line in async_send_svdrpcommand("lstc :ids :groups"):
        _code, r = line.strip().split("-", maxsplit=1)
        # print(r)
        # GROUP_RE = re.compile(r'(?P<number>\d+)\s:((?P<group_offset>@\d+)\s)?(?P<group_name>.+)')
        # TODO: make channel group parsing work
        number, other = r.split(maxsplit=1)
        if other.startswith(":"):  # check for channel group
            if other[1] == "@":
                # group with offset value
                offset, group_name = other[2:].split(maxsplit=1)
                offset = int(offset)
            else:
                # group without offset
                group_name = other[1:]
                offset = 0

            group = Channel(
                number=offset,
                channel_id=f"{group_name}-{number}-{uuid.uuid4()}",
                channel_string=f":{f'@{offset} ' if offset else ''}{group_name}",
                is_group=True,
                is_radio=False,
                name=group_name,
                ca="0",
                provider="",
                source="",
            )
            # print("got group:", group)
            channels.append(group)
        else:
            channel_id, other = other.split(maxsplit=1)
            # channel entry
            try:
                (
                    name,
                    _frequency,
                    _parameters,
                    source,
                    _srate,
                    vpid,
                    _apid,
                    _tpid,
                    ca,
                    _sid,
                    _nid,
                    _tid,
                    _rid,
                    *_channel_data,
                ) = other.split(":")

                number = int(number)
                name, _, provider = name.partition(";")
                name, _, _short_name = name.partition(",")
                # if nid == "0" and sid == "0":
                #     # If a channel has both NID and TID set to 0,
                #     # the channel ID will use the Frequency instead of the TID.
                #     # For satellite channels an additional offset of
                #     # 100000, 200000, 300000 or 400000 is added to that number,
                #     # depending on the Polarization (H, V, L or R, respectively).
                #     # This is necessary because on some satellites the same
                #     # frequency is used for two different transponders, with opposite polarization.
                #     tf = frequency
                #     while tf > 20000:
                #         tf /= 1000
                #     if source.startswith("S") and parameters:
                #         match parameters[0]:
                #             case "H":
                #                 tf += 100000
                #             case "V":
                #                 tf += 200000
                #             case "L":
                #                 tf += 300000
                #             case "R":
                #                 tf += 400000
                #     tid = tf
                # channel_id = f"{source}-{nid}-{tid}-{sid}-{rid}"
            except Exception as err:
                print(f"could not process {other=}")
                print(err)
                continue

            is_radio = False
            try:
                radio_vpid = int(vpid)
                if radio_vpid <= 1:
                    is_radio = True
            except ValueError:
                pass

            channels.append(
                Channel(
                    number=number,
                    channel_id=channel_id,
                    channel_string=other,
                    is_group=False,
                    is_radio=is_radio,
                    name=name,
                    provider=provider,
                    source=source,
                    ca=ca,
                )
            )
    return channels


@router.delete("/vdr/channels/{channel_id}")
async def delete_channel(channel_id: str, _User: User=Depends(get_current_active_user)):
    async for line in async_send_svdrpcommand(f"DELC {channel_id}"):
        print(line)


@router.get("/vdr/plugin_config", response_model=list[vdr_plugin_config.PluginConfig])
async def get_plugin_config(current_user: User = Depends(get_current_active_user)) -> list[PluginConfig]:
    return list(vdr_plugin_config.read_plugins().values())


# @router.post(
#     "/vdr/plugin_config",
#     responses={
#         HTTP_200_OK: {
#             "model": Message,
#             "description": "config written successfully",
#         },
#         HTTP_400_BAD_REQUEST: {"model": Message, "description": "invalid arguments"},
#         HTTP_503_SERVICE_UNAVAILABLE: {
#             "model": Message,
#             "description": "vdr is not available",
#         },
#     },
# )
# def write_plugin_config(
#     plugin_config: PluginConfig, current_user: User = Depends(get_current_active_user)
# ):
#     if plugin_config.enabled:
#         # TODO: link from AVAILDIR to CONFDIR
#         config_str = (
#             "\n".join(plugin_config.arguments)
#             if isinstance(plugin_config.arguments, list)
#             else plugin_config.arguments
#         )
#         print(f"setting {plugin_config.name} to \n '{config_str}'")
#         vdr_plugin_config.write_config_file(plugin_config.name, config_str)

#     return


@router.websocket("/vdr/svdrp/ws")
async def websocket_endpoint(
    websocket: WebSocket,
):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            # TODO: establish connection with VDR if needed, communicate with VDR, return answer
            # we need to keep track of the command sent by the client -
            # so establishing a new session per request is probably the easiest method
            # on the other hand this slows things down - can we keep a session alive for each client?
            # Also do we need to check the response in the proxy or can we just pass things along?
            # SVDRP response codes
            # 214 Hilfetext
            # 215 EPG Eintrag
            # 216 Image grab data (base 64)
            # 220 VDR-Service bereit
            # 221 VDR-Service schließt Sende-Kanal
            # 250 Angeforderte Aktion okay, beendet
            # 354 Start senden von EPG-Daten
            # 451 Angeforderte Aktion abgebrochen: lokaler Fehler bei der Bearbeitung
            # 500 Syntax-Fehler, unbekannter Befehl
            # 501 Syntax-Fehler in Parameter oder Argument
            # 502 Befehl nicht implementiert
            # 504 Befehls-Parameter nicht implementiert
            # 550 Angeforderte Aktion nicht ausgeführt
            # 554 Transaktion fehlgeschlagen
            #
            # can we reuse a once established connection?
            await websocket.send_text(f"got {data}")
    except WebSocketDisconnect:
        print("Websocket connection lost")


class AudioChannel(BaseModel):
    number: int
    desc: str
    selected: bool


@router.get("/vdr/audiochannel")
async def get_audiochannels() -> list[AudioChannel]:
    audio_options: list[AudioChannel] = []
    async for line in async_send_svdrpcommand("AUDI"):
        line = line[4:]
        try:
            option_nr, desc, sel = line.split(maxsplit=2)
            n = int(option_nr)
            selected = True if sel.startswith("*") else False
            audio_options.append(AudioChannel(number=n, desc=desc, selected=selected))
        except Exception as e:
            print("failed to parse response:", e)

    return audio_options


@router.post("/vdr/audiochannel")
async def set_audiochannel(channel_nr: int) -> tuple[bool, AudioChannel|str]:
    async for line in async_send_svdrpcommand(f"AUDI {channel_nr}"):
        line = line.strip()[4:]
        if line.startswith(f"{channel_nr} "):
            option_nr, desc, _sel = line.split(maxsplit=2)
            return True, AudioChannel(number=int(option_nr), desc=desc, selected=True)
    return False, "setting the audio channel failed"


class EpgEntry(BaseModel):
    event_id: str
    channel_id: str
    start: datetime.datetime
    start_ts: int
    duration: datetime.timedelta
    table_id: str
    version: str
    title: str
    subtitle: str | None = None
    description: str | None = None
    genre: str | None = None
    streams: list[str] = Field(default_factory=lambda: list())
    vps: datetime.datetime | None = None


class EventEntryFields(StrEnum):
    START = "E"
    TITLE = "T"
    SUBTITLE = "S"
    DESCRIPTION = "D"
    GENRE = "G"
    PARENTAL_RATING = "R"
    STREAMS = "X"
    VPS = "V"
    END = "e"


@router.get("/vdr/epg")
async def get_channel_epg(channel_id: str) -> list[EpgEntry]:
    epg_entries: list[EpgEntry] = []
    entry: None | EpgEntry = None
    try:
        event_data = {}
        async for line in async_send_svdrpcommand(f"LSTE {channel_id}"):
            _code, line = line.strip().split("-", maxsplit=1)
            field_type, _, other = line.partition(" ")
            match field_type:
                case EventEntryFields.START:
                    _, e_id, start, duration, tid, version = line.split()
                    event_data: dict[str, Any] = {
                        "event_id": e_id,
                        "start": datetime.datetime.fromtimestamp(int(start)),
                        "start_ts": start,
                        "duration": datetime.timedelta(seconds=int(duration)),
                        "table_id": tid,
                        "version": version,
                        "channel_id": channel_id,
                    }
                case EventEntryFields.TITLE:
                    event_data["title"] = other
                case EventEntryFields.SUBTITLE:
                    event_data["subtitle"] = other
                case EventEntryFields.DESCRIPTION:
                    event_data["description"] = other
                case EventEntryFields.GENRE:
                    event_data["genre"] = other
                case EventEntryFields.VPS:
                    event_data["vps"] = datetime.datetime.fromtimestamp(int(other))
                case EventEntryFields.END:
                    # end of Entry
                    entry = EpgEntry(**event_data)
                    epg_entries.append(entry)
                case _:
                    pass
    except ValueError:
        pass
    return epg_entries


class StringEntry(BaseModel):
    name: str
    value: str
    max_value: int


class ThreeIntEntry(BaseModel):
    name: str
    value: int
    min_value: int
    max_value: int


class Int64Entry(BaseModel):
    name: str
    value: int


VDRSetupEntry = StringEntry | ThreeIntEntry | Int64Entry


@router.get("/vdr/setup")
async def get_setup(key: str | None = None) -> list[VDRSetupEntry] | Any:
    with contextlib.closing(sdbus.sd_bus_open_system()) as bus:
        setup_proxy = DeTvdrVdrSetupInterface.new_proxy("de.tvdr.vdr", "/Setup", bus)
        if key is None:
            setup_data = await setup_proxy.list()
            revised_data: list[VDRSetupEntry] = []
            for name, values in setup_data:
                # print(f"{name}: {values[0]=}: {values[1]=}")
                match values[0]:
                    case "(iii)":
                        value, min_value, max_value = values[1]
                        e = ThreeIntEntry(
                            name=name, value=value, min_value=min_value, max_value=max_value
                        )
                        revised_data.append(e)
                    case "(si)":
                        value, max_value = values[1]
                        e = StringEntry(name=name, value=value, max_value=max_value)
                        revised_data.append(e)
                    case "x":
                        value = values[1]
                        e = Int64Entry(name=name, value=value)
                        revised_data.append(e)
                    case _:
                        print(f"unkown data: {values}")
            return revised_data
        else:
            (_s, value), _r, _m = await setup_proxy.get(key)
            return value


@router.post("/vdr/setup")
async def set_setup(key: str, value: int | str):
    with contextlib.closing(sdbus.sd_bus_open_system()) as bus:
        setup_proxy = DeTvdrVdrSetupInterface.new_proxy("de.tvdr.vdr", "/Setup", bus)
        setup_data = await setup_proxy.list()
        for name, values in setup_data:
            if name == key:
                signature, _ = values
                s_type = signature.lstrip("(")[0]
                print(f"sending {key=}, ({s_type=}, {value=})")
                if s_type in ("i", "x"):
                    value = int(value)
                r, m = await setup_proxy.set(key, (s_type, value))
                print(r, m)
                return r, m


class VDRSkin(BaseModel):
    index: int
    name: str
    description: str


@router.get("/vdr/skins")
async def get_skins():
    with contextlib.closing(sdbus.sd_bus_open_system()) as bus:
        skin_proxy = DeTvdrVdrSkinInterface.new_proxy("de.tvdr.vdr", "/Skin", bus)
        code, data = await skin_proxy.list_skins()
        if code == 900:
            # print(data)
            skins = [
                VDRSkin(index=index, name=name, description=description)
                for index, name, description in data
            ]
            return skins


@router.get("/vdr/configfile")
async def get_configfile(filename: AllowedVDRConfigfiles):
    path = allowed_vdr_config_files_options[filename].filepath
    print(f"got request for {filename=}")
    return FileResponse(path)


@router.post("/vdr/configfile/{filename}")
async def upload_configfile(filename: AllowedVDRConfigfiles, uploaded_file: UploadFile):
    print(
        f"got {filename=} with {uploaded_file.size=} and {uploaded_file.content_type=}, {uploaded_file.headers}"
    )

    content = await uploaded_file.read()

    async def event_generator():
        with contextlib.closing(sdbus.sd_bus_open_system()) as system_bus:
            backend = YavdrSystemBackend.new_proxy(YAVDR_BACKEND_INTERFACE, "/", system_bus)

            queue: asyncio.Queue[tuple[Status, str]] = asyncio.Queue()

            async def wait_for_done():
                async for event in backend.file_event:
                    print(event)
                    event_type, _msg = event
                    await queue.put((Status(event_type), _msg))
                    if event_type == Status.DONE:
                        print("wait_for_done ends")
                        return

            async def share_file(content: bytes):
                with tempfile.TemporaryFile() as shared_file:
                    shared_file.write(content)
                    shared_file.flush()
                    fd = shared_file.fileno()
                    try:
                        uuid = await backend.save_file(str(filename), fd)
                    except sdbus.DbusFailedError as err:
                        print(f"error awaiting backend.save_file: {err}")
                        await queue.put((Status.DONE, "failed"))
                        return
                    else:
                        await queue.put((Status.STARTING, uuid))

            async with asyncio.TaskGroup() as group:
                group.create_task(wait_for_done())
                group.create_task(share_file(content))
                # TODO: this times out if we need a lot of time
                while True:
                    event: tuple[Status, str] = await queue.get()
                    print("got event:", event)
                    # if request.is_disconnected():
                    #     print("client disconnected ...")
                    #     break

                    state, msg = event
                    yield json.dumps({"state": state, "msg": msg})

                    queue.task_done()
                    if state == Status.DONE:
                        print("done")
                        await asyncio.sleep(1)
                        break

    # TODO: make this two separate things - one for the post request and one streaming response for the status
    return EventSourceResponse(event_generator(), send_timeout=5)


@router.get("/vdr/channel")
async def get_channel() -> str:
    """get the current chanel - format: channel_number channel_name"""
    response = [line async for line in async_send_svdrpcommand("chan")]
    return "\n".join(response)


@router.post("/vdr/channel")
async def switch_channel(channel: str) -> str:
    """switch to the given channel"""
    response = [line async for line in async_send_svdrpcommand(f"chan {channel}")]
    return "\n".join(response)


RETRY_TIMEOUT = 15000  # milisecond


@router.get("/vdr/status")
async def vdr_status_signals(request: Request):
    """forward dbus2vdr's signals as Server Side Events"""

    async def event_generator() -> AsyncGenerator[dict[str, str], None]:
        async with contextlib.aclosing(vdr_status_event_generator()) as g:
            async for status_signal in g:
                if await request.is_disconnected():
                    break

                yield {
                    "event": type(status_signal).__name__,
                    # "retry": RETRY_TIMEOUT,
                    "data": status_signal.model_dump_json(),
                }

    return EventSourceResponse(event_generator(), send_timeout=5)
