import datetime
from enum import StrEnum
from pathlib import Path
import subprocess
from typing import Annotated, Any, List, Optional
import uuid
from fastapi import APIRouter, Depends, UploadFile, WebSocket, WebSocketDisconnect

# from pydantic.errors import DataclassTypeError
# from pydantic.main import BaseModel

# import pydbus2vdr
from fastapi.responses import FileResponse
from pydantic import BaseModel
import sdbus
from starlette.responses import JSONResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_503_SERVICE_UNAVAILABLE,
)

from .auth import get_current_active_user, User
from tools import SVDRPClient, vdr_plugin_config
from interfaces.vdr_channels import DeTvdrVdrChannelInterface
from interfaces.vdr_epg import DeTvdrVdrEpgInterface
from interfaces.vdr_plugins import DeTvdrVdrPluginmanagerInterface
from interfaces.vdr_recordings import DeTvdrVdrRecordingInterface
from interfaces.vdr_timers import DeTvdrVdrTimerInterface
from interfaces.vdr_setup import DeTvdrVdrSetupInterface
from interfaces.vdr_skin import DeTvdrVdrSkinInterface


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


class Recordings(BaseModel):
    RecNum: int
    Path: str
    Name: str
    FullName: Optional[str] = None
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
    InfoChannelID: Optional[str] = None
    InfoChannelName: Optional[str] = None
    InfoTitle: Optional[str] = None
    InfoShortText: Optional[str] = None
    InfoDescription: Optional[str] = None
    InfoAux: Optional[str] = None
    InfoFramesPerSecond: Optional[float] = None


@router.get("/vdr/recordings", response_model=List[Recordings])
async def get_vdr_recordings():  # *, current_user: User = Depends(get_current_active_user)):
    vdr_recordings = DeTvdrVdrRecordingInterface.new_proxy(
        "de.tvdr.vdr", "/Recordings", bus=sdbus.sd_bus_open_system(),
    )
    recordings = []
    for n, r in await vdr_recordings.list():
        try:
            new_rec = {}
            for k, v in r:
                k = k.replace("/", "")
                # print(k, v, type(v))
                if isinstance(v, tuple):
                    new_rec[k] = v[-1]
                else:
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
            print("Error:", err)
    # print(recordings)
    return sorted(recordings, key=lambda r: r.get("Start"), reverse=True)


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
    vdr_recordings = DeTvdrVdrRecordingInterface.new_proxy(
        "de.tvdr.vdr", "/Recordings", bus=sdbus.sd_bus_open_system(),
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


@router.get("/vdr/current_epg")
async def get_current_epg(current_user: User = Depends(get_current_active_user)):
    vdr_epg = DeTvdrVdrEpgInterface.new_proxy("de.tvdr.vdr", "/EPG", bus=sdbus.sd_bus_open_system())
    data = await vdr_epg.now("")
    return data


@router.get("/vdr/current_channel_epg")
async def get_current_channel_epg(
    current_user: User = Depends(get_current_active_user),
):
    vdr_channels = DeTvdrVdrChannelInterface.new_proxy("de.tvdr.vdr", "/Channels", bus=sdbus.sd_bus_open_system())
    vdr_epg = DeTvdrVdrEpgInterface.new_proxy("de.tvdr.vdr", "/EPG", bus=sdbus.sd_bus_open_system())
    _, current_channel = await vdr_channels.current()
    print(f"current channel: {current_channel}")
    data = await vdr_epg.now(current_channel), await vdr_epg.next(current_channel)
    return data


class Timer(BaseModel):
    status: int
    raw: str
    channel: str
    channelname: str
    day: int
    start: int
    stop: int
    time: str
    priority: int
    lifetime: int
    filename: str
    aux: str


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


@router.get("/vdr/timers", response_model=List[Timer])
async def get_vdr_timers(*, current_user: User = Depends(get_current_active_user)):
    vdr_channels = DeTvdrVdrChannelInterface.new_proxy("de.tvdr.vdr", "/Channels", bus=sdbus.sd_bus_open_system())
    vdr_timers = DeTvdrVdrTimerInterface.new_proxy("de.tvdr.vdr", "/Timers", bus=sdbus.sd_bus_open_system())
    timers = (
        await vdr_timers.list()
    )  # TODO: do we want to use the more detailed vdr.Timers.ListDetailed ?
    channels_raw, *_ = await vdr_channels.list("")
    channel_ids = {}
    for channel in channels_raw:
        chan_num, chan_str = channel
        (
            name,
            freq,
            params,
            source,
            srate,
            vpid,
            apid,
            tpid,
            ca,
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
        start = datetime.datetime.strptime(
            f"{day} {start}", "%Y-%m-%d %H%M"
        ).timestamp()
        stop = datetime.datetime.strptime(f"{day} {stop}", "%Y-%m-%d %H%M").timestamp()

        t_data.append(
            Timer(
                **{
                    "raw": timer,
                    "status": int(status),
                    "channel": channel,
                    "day": start,
                    "start": start,
                    "stop": stop,
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
    channel_id: str
    channel_string: str
    is_group: bool
    is_radio: bool
    name: str
    provider: str = ""
    ca: str = "0000"
    source: str


@router.get("/vdr/channels")
async def get_vdr_channels(
    current_user: User = Depends(get_current_active_user),
):
    vdr_channels = DeTvdrVdrChannelInterface.new_proxy("de.tvdr.vdr", "/Channels", bus=sdbus.sd_bus_open_system())

    channels = []
    channels_raw, status_code, message = await vdr_channels.list(":groups")
    print(f"{channels_raw=}")
    for channel in channels_raw:
        print(f"{channel=}")
        chan_num, chan_str = channel
        channels.append({"channel_number": chan_num, "channel_string": chan_str})
    return channels


@router.post("/vdr/channels")
def save_vdr_channels(channel_list: list[str]):
    print(channel_list)
    channels_conf = "/tmp/channels.conf"  # TODO: make this location configurable resp. read it from VDR
    r = subprocess.run(
        ["pkg-config", "vdr", "--variable=configdir"],
        universal_newlines=True,
        capture_output=True,
    )
    print(config_dir := r.stdout)
    # TODO: stop vdr - can we do this as an ansible run command?
    # write channels.conf
    with open(channels_conf, "w") as f:
        f.writelines(channel_list)

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
    tmp = Path('/var/cache/yavdr-webfrontend/channel_lists/')
    tmp.mkdir(parents=True, exist_ok=True)
    print(f"{file.filename} {file.size}")
    if not file.filename:
        file.filename = "channels.conf"
    content = await file.read()
    # TODO: validate channels.conf
    (p := (tmp / file.filename)).write_bytes(content)
    print(f"wrote file {p}")
    return True



@router.get("/vdr/channels_with_groups", response_model=List[Channel])
def get_vdr_channels_with_groups(current_user: User = Depends(get_current_active_user)):
    channels = []
    with SVDRPClient("localhost", 6419) as svdrp:
        for r in svdrp.send_cmd_and_get_response("lstc :ids :groups"):
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
                        frequency,
                        parameters,
                        source,
                        srate,
                        vpid,
                        apid,
                        tpid,
                        ca,
                        sid,
                        nid,
                        tid,
                        rid,
                        *channel_data,
                    ) = other.split(":")

                    number = int(number)
                    name, _, provider = name.partition(";")
                    name, _, short_name = name.partition(",")
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
def delete_channel(channel_id: str, User=Depends(get_current_active_user)):
    with SVDRPClient("localhost", 6419) as svdrp:
        response = svdrp.send_cmd_and_get_response(f"DELC {channel_id}")
        for line in response:
            print(line)


@router.get("/vdr/plugin_config", response_model=List[vdr_plugin_config.PluginConfig])
async def get_plugin_config(current_user: User = Depends(get_current_active_user)):
    return list(vdr_plugin_config.read_plugins().values())


@router.post(
    "/vdr/plugin_config",
    responses={
        HTTP_200_OK: {
            "model": Message,
            "description": "config written successfully",
        },
        HTTP_400_BAD_REQUEST: {"model": Message, "description": "invalid arguments"},
        HTTP_503_SERVICE_UNAVAILABLE: {
            "model": Message,
            "description": "vdr is not available",
        },
    },
)

class PluginConfig(BaseModel):
    name: str
    priority: int
    is_enabled: bool
    config: list[str] | str

def write_plugin_config(plugin_configs: list[PluginConfig], current_user: User = Depends(get_current_active_user)):
    for p in plugin_configs:
        if p.is_enabled:
            # TODO: link from AVAILDIR to CONFDIR
            ...
        config_str = '\n'.join(p.config) if isinstance(p.config, list) else p.config

        

    return


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
def get_audiochannels() -> list[AudioChannel]:
    with SVDRPClient("localhost", 6419) as svdrp:
        audio_options = []
        for line in svdrp.send_cmd_and_get_response('AUDI'):
            try:
                option_nr, desc, sel = line.split(maxsplit=2)
                n = int(option_nr)
                selected = True if sel.startswith('*') else False
                audio_options.append({'number': n, 'desc': desc, 'selected': selected})
            except Exception as e:
                print("failed to parse response:", e)
            
    return audio_options

@router.post("/vdr/audiochannel")
def set_audiochannel(channel: int):
    with SVDRPClient("localhost", 6419) as svdrp:
        r = []
        for line in svdrp.send_cmd_and_get_response(f'AUDI {channel}'):
            if line.startswith(f"{channel} "):
                r.append(line)
    return True, "".join(r)


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

VDRSetupEntry = StringEntry|ThreeIntEntry|Int64Entry


@router.get('/vdr/setup')
async def get_setup(key: str|None = None) -> list[VDRSetupEntry]|Any:
    bus = sdbus.sd_bus_open_system()
    setup_proxy = DeTvdrVdrSetupInterface.new_proxy('de.tvdr.vdr','/Setup', bus)
    if key is None:
        setup_data = await setup_proxy.list()
        revised_data: list[VDRSetupEntry] = []
        for (name, values) in setup_data:
            # print(f"{name}: {values[0]=}: {values[1]=}")
            match(values[0]):
                case '(iii)':
                    value, min_value, max_value = values[1]
                    e = ThreeIntEntry(name=name, value=value, min_value=min_value, max_value=max_value)
                    revised_data.append(e)
                case '(si)':
                    value, max_value = values[1]
                    e = StringEntry(name=name, value=value, max_value=max_value)
                    revised_data.append(e)
                case 'x':
                    value = values[1]
                    e = Int64Entry(name=name, value=value)
                    revised_data.append(e)
                case _:
                    print(f"unkown data: {values}")
        return revised_data
    else:
        (s, value), r, m = await setup_proxy.get(key)
        return value


@router.post('/vdr/setup')
async def set_setup(key: str, value: int|str):
    bus = sdbus.sd_bus_open_system()
    setup_proxy = DeTvdrVdrSetupInterface.new_proxy('de.tvdr.vdr','/Setup', bus)
    setup_data = await setup_proxy.list()
    for name, values in setup_data:
        if name == key:
            signature, _ = values
            s_type = signature.lstrip('(')[0]
            print(f"sending {key=}, ({s_type=}, {value=})")
            if s_type in ('i', 'x'):
                value = int(value)
            r, m = await setup_proxy.set(key, (s_type, value))
            print(r, m)
            return r, m


class VDRSkin(BaseModel):
    index: int
    name: str
    description: str

@router.get('/vdr/skins')
async def get_skins():
    bus = sdbus.sd_bus_open_system()
    skin_proxy = DeTvdrVdrSkinInterface.new_proxy('de.tvdr.vdr','/Skin', bus)
    code, data = await skin_proxy.list_skins()
    if code == 900:
        # print(data)
        skins = [
            VDRSkin(index=index, name=name, description=description) for
            index, name, description in data
        ]
        return skins
    
class AllowedConfigfiles(StrEnum):
    CHANNELS = "channels.conf"
    REMOTE = "remote.conf"
    KEYMACROS = "keymacros.conf"
    DISQC = "diseqc.conf"
    SOURCES = "sources.conf"
    SETUP = "setup.conf"


@router.get('/vdr/configfile')
async def get_configfile(filename: AllowedConfigfiles):
    print(f"got request for {filename=}")
    VDR_CONFIG_DIR = Path('/var/lib/vdr')
    return FileResponse(VDR_CONFIG_DIR/filename)

@router.post('/vdr/configfile/{filename}')
async def upload_configfile(filename: AllowedConfigfiles, file: UploadFile) -> bool:
    # tmp = Path('/var/cache/yavdr-webfrontend/channel_lists/')
    # tmp.mkdir(parents=True, exist_ok=True)
    BASEDIR = Path('/tmp/')
    print(f"got {filename=} with {file.size=} and {file.content_type=}, {file.headers}")
    content = await file.read()
    # TODO: validate channels.conf
    (p := (BASEDIR / filename)).write_bytes(content)
    print(f"wrote file {p}")
    return True

    