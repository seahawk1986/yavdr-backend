from dataclasses import dataclass
from pydantic import BaseModel
import pathlib
import re
from typing import Protocol

CHANNEL_GROUP_WITH_NUMBER_RE = re.compile(r':(@(?P<number>\d+)\s*)?(?P<name>.*)?')
CHANNEL_ENTRY_RE = re.compile(r'(?P<name>[^;]*);(?P<provider>[^;]*):')

CHANNELS_CONF = pathlib.Path('/var/lib/vdr/channels.conf')

channel_counter = 1

class DVBParams:
    ...

@dataclass
class Channel:
    name: str
    short_name: str
    frequency: int
    params: DVBParams



with open(CHANNELS_CONF) as f:
    for line in f:
        if line.startswith(':'):
            # channel group5
            # print(line, end='')
            if m := re.match(CHANNEL_GROUP_WITH_NUMBER_RE, line):
                print(d := m.groupdict())
                if n := d.get('number'):
                     channel_counter = max(int(n), channel_counter)
        else:
            # channel entry
            ...
            if m := re.match(CHANNEL_ENTRY_RE, line):
                # print(channel_counter, d := m.groupdict())
                channel_counter += 1

