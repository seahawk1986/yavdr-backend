import logging

from enum import IntEnum
from typing import Any, Iterable, List, Tuple, Mapping
from pydantic import BaseModel, constr
from pydantic.types import PositiveInt
try:
    from pydantic.utils import generate_model_signature
except ImportError:
    from pydantic.v1.utils import generate_model_signature


class DVB_DATA_TYPE(IntEnum):
    MPEG2_VIDEO = 1
    MPEG2_AUDIO = 2
    TXT = 3
    AC3_AUDIO = 4
    H264_VIDEO = 5
    AAC_AUDIO = 6
    DTS_AUDIO = 7
    SRM_CPCM_DATA = 8
    HEVC_VIDEO_AC4_AUDIO = 9


class DVB_SERVICE_TYPE(IntEnum):
    DIGITAL_TELEVISION_SERVICE = 0x01
    DIGITAL_RADIO_SERVICE = 0x0A
    HEVC_DIGITAL_TELEVISION_SERVICE = 0x1F


class DVB_CONTENT_NIBBLE(IntEnum):
    UNDEFINED = 0x00
    MOVIE_DRAMA = 0x10
    DETECTIVE_THRILLER = 0x11
    ADVENTURE_WESTERN_WAR = 0x12

    """ Table 28 of https://www.etsi.org/deliver/etsi_en/300400_300499/300468/01.12.01_40/en_300468v011201o.pdf
    Content_nibble_level_1 Content_nibble_level_2 Description
    0x0 0x0 to 0xF undefined content

    Movie/Drama:
    0x1 0x0 movie/drama (general)
    0x1 0x1 detective/thriller
    0x1 0x2 adventure/western/war
    0x1 0x3 science fiction/fantasy/horror
    0x1 0x4 comedy
    0x1 0x5 soap/melodrama/folkloric
    0x1 0x6 romance
    0x1 0x7 serious/classical/religious/historical movie/drama
    0x1 0x8 adult movie/drama
    0x1 0x9 to 0xE reserved for future use
    0x1 0xF user defined

    News/Current affairs:
    0x2 0x0 news/current affairs (general)
    0x2 0x1 news/weather report
    0x2 0x2 news magazine
    0x2 0x3 documentary
    0x2 0x4 discussion/interview/debate
    0x2 0x5 to 0xE reserved for future use
    0x2 0xF user defined

    Show/Game show:
    0x3 0x0 show/game show (general)
    0x3 0x1 game show/quiz/contest
    0x3 0x2 variety show
    0x3 0x3 talk show
    0x3 0x4 to 0xE reserved for future use
    0x3 0xF user defined

    Sports:
    0x4 0x0 sports (general)
    0x4 0x1 special events (Olympic Games, World Cup, etc.)
    0x4 0x2 sports magazines
    0x4 0x3 football/soccer
    0x4 0x4 tennis/squash
    0x4 0x5 team sports (excluding football)
    0x4 0x6 athletics
    0x4 0x7 motor sport
    0x4 0x8 water sport
    0x4 0x9 winter sports
    0x4 0xA equestrian
    0x4 0xB martial sports
    0x4 0xC to 0xE reserved for future use
    0x4 0xF user defined
    """


class EPG(BaseModel):
    channels: Mapping[str, Mapping[str, Any]]


class EpgEntry(BaseModel):
    channel_id: constr(min_length=1)
    channel_short_name: str
    channel_name: str

    event_id: str
    event_start: int
    event_duration: int
    event_table_id: int
    event_version: int

    event_title: str
    event_subtitle: str

    datastreams: List[Tuple[DVB_DATA_TYPE, str, constr(min_length=2, max_length=2)]]
    stream_type: int
    language: str
    description: str

    vps_start: int
    genres: List[DVB_CONTENT_NIBBLE]


def parse_epg_entry(line_gen: Iterable) -> EpgEntry:

    yield EpgEntry(
        channel_id,
        channel_short_name,
        channel_name, event_id,
        event_start,
        event_duration,
        event_table_id,
        event_version,
        datastreams,
        stream_type,
        language,
        vps_start,
        genres,
        )


def parse_channel(line: str):
    global channel_id, channel_name
    _, channel_id, channel_name = line.split(maxsplit=2)
    return channel_id, channel_name


def finish_channel_parsing():
    global channel_id, short_name, channel_name, channel_short_name
    channel_id = ""
    channel_name = ""
    channel_short_name = ""


def parse_event(line: str):
    global event_id, start_time, duration, table_id, version
    _, event_id, start_time, duration, table_id, version, *_ = line.split()
    event_id = int(event_id)
    start_time = int(start_time)
    duration = int(duration)
    table_id = int(table_id, 16)
    version = int(version, 16)
    return event_id, start_time, duration, table_id, version


def parse_title(line: str):
    global epg_title
    _, epg_title = line.split(maxsplit=1)


def parse_short_text(line: str):
    global short_text
    _, short_text = line.split(maxsplit=1)


def parse_description(line: str):
    global description
    _, desc = line.split(maxsplit=1)
    description = "\n".join(desc.split('|'))


def parse_genre(line: str):
    global genres
    genres = []
    genres.extend(line.split()[1:])


def parse_parental_rating(line: str):
    global parental_rating
    _, parental_rating = line.split(maxsplit=1)


def parse_av_stream(line: str):
    global av_streams
    av_streams = []


def parse_vps(line: str):
    global vps
    _, vps = int(line.split(maxsplit=1))
    return vps


def finish_event_parsing():
    return EpgEntry()


parse_actions = {
    "T ": parse_title,
    "S ": parse_short_text,
    "D ": parse_description,
    "G ": parse_genre,
    "R ": parse_parental_rating,
    "X ": parse_av_stream,
    "V ": parse_vps,
}


def test_epgparser():
    epg_data = """C T-8468-12547-801 BR Fernsehen Nord HD
E 13233 1632467700 2700 4F 1E
T Querbeet Classix
D Themen:|* Hausbäume für kleine Gärten|* Zwiebelblüher im Topf|* Pastinake für Babys|* Hostavielfalt auf dem Balkon|* Beruf Staudengärtner|* 25 Jahre Landesgartenschau Dinkelsbühl|* Küchengarten von Schloss Hof in Österreich
G 90
X 3 01 deu Teletext-Untertitel
V 1632467700
e
c
C T-8468-12291-770 arte HD
E 9408 1632470100 3300 4E 17
T Öl. Macht. Geschichte (1/2)
S Aufstieg und Fall
D Die Entdeckung des Erdöls glich einem Wunder: Petroleumlampen erhellten Wohnzimmer wie nie zuvor, ölbetriebene Maschinen arbeiteten so effektiv wie 50 Arbeitskräfte. Seine Kraft bescherte der Menschheit ein nie gekanntes Wirtschaftswachstum. John D. Rockefeller wurde durch Öl zum ersten Milliardär der Geschichte. Aber der Rohstoff sollte zwei Weltkriege entscheidend beeinflussen.|Anhand zahlreicher Fundstücke aus internationalen Archiven und mittels Interviews entsteht ein vielschichtiges Porträt eines Rohstoffs, der über viele Jahrzehnte - und bis heute unverändert - unseren Alltag prägt.
G 80 82
R 6
X 3 01 deu Teletext-Untertitel
V 1632470400
e
E 9409 1632473400 3300 4E 17
T Öl. Macht. Geschichte (2/2)
S Gier und Verderben
D Macht und Erdöl sind untrennbar verbunden. Als wichtigste Energiequelle bestimmt Erdöl über Aufschwung und Niedergang, über Konsum, Armut und Kriege. Wie das schwarze Gold bestehende Machtverhältnisse über Nacht verändern kann, bekam der Westen 1973 zu spüren: Die OPEC verringert die gelieferte Ölmenge als Strafe für die Einmischung in den arabisch-israelischen Krieg. Plötzlich machte Öl Politik. Damals hatte man es versäumt, Technologien für den Einsatz erneuerbarer Technologien zu entwickeln.
G 80 82
R 6
X 3 01 deu Teletext-Untertitel
V 1632473400
e
E 9410 1632476700 1800 50 16
T 42 - Die Antwort auf fast alles
S Können wir uns durch die Erdkugel graben?
D "42 - Die Antwort auf fast alles" ist die neue Wissensserie von ARTE, die durch große und kleine Fragen der Menschheit navigiert, originell, assoziativ, um die Ecke gedacht und getragen von einer prägnanten Stimme: Nora Tschirner macht sich Gedanken, sammelt Informationen, ordnet Material und gibt uns den Durchblick.|In dieser Folge: Wir fliegen hoch hinaus, erkunden das Weltall, aber was ist mit der anderen Richtung? Unter unseren Füßen herrscht im wahrsten Sinne des Wortes Dunkelheit. Geologen zitieren gerne den Bergmannsspruch: "Vor der Hacke ist es duster." Und so ist es.
X 3 01 deu Teletext-Untertitel
V 1632476700
e
c"""
    lines = (line for line in epg_data.splitlines() if line)
    try:
        for line in lines:
            if not line.startswith('C '):
                continue
            # we got a channel section
            while (line := next(lines)) != 'c':
                if line == 'E ':
                    # we got a epg entry section
                    # parse time information
                    while (line := next(lines)) != 'e':
                        # parse additional epg entry data
                        if (action := parse_actions.get(line, None)):
                            action(line)
                    # yield EpgEntry
                    
            # parse_action.get(l[:2], lambda l: logging.warn(f"invalid line: {l}"))(line)
    except StopIteration:
        # lines has been exhausted
        pass


if __name__ == '__main__':
    test_epgparser()
