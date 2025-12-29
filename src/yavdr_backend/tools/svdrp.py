#!/usr/bin/env python3
import telnetlib
import logging
from collections import namedtuple
import cchardet
SVDRPResponse = namedtuple("SVDRPResponse", "code, cont, data")


# TODO: replace with an asyncio version and without the obsolete telnet library

# --------------------------------------------------------------------------- #
# roughly based on https://kfalck.net/2011/01/08/autorecord-vdr-programs-via-svdrp/
class SVDRPClient:
    def __init__(self, host, port, timeout=10):
        self.telnet = telnetlib.Telnet()
        self.host = host
        self.port = port
        self.timeout = timeout
        self.encoding = 'ascii'
        self.changed_encoding = False

    def __enter__(self):
        self.telnet.open(self.host, self.port)
        self.read_greeting()
        return self

    def __exit__(self, type, value, traceback):
        self.send_command('QUIT')
        self.telnet.read_all()
        self.telnet.close()

    def _read_single_line(self):
        return self.telnet.read_until(b'\n', self.timeout)

    def read_line(self):
        line = self.decode(self._read_single_line()).rstrip('\r\n')
        if len(line) < 4:
            return None
        return SVDRPResponse(int(line[0:3]), line[3] == '-', line[4:])

    def decode(self, line):
        try:
            return line.decode(self.encoding)
        except Exception:
            logging.debug(f"could not decode '{line}, fallback to cchardet'", exc_info=True)
            return line.decode(cchardet.detect(line).get('encoding', 'ascii'), errors="surrogateescape")

    def read_greeting(self):
        code, cont, data = self.read_line()
        if not code == 220:
            raise ValueError("unexpected response")
        self.encoding = data.rsplit(';', 1)[-1].strip().lower()

    def send_command(self, line):
        logging.debug("encoding: %s", self.encoding)
        self.telnet.write((line + '\r\n').encode(self.encoding, errors="surrogateescape"))

    def read_response(self):
        cont = True
        while cont:
            line_content = self.read_line()
            if line_content.code in (221, 451, 500, 501, 502, 504, 550, 554):
                raise ValueError(line_content.data)
            cont = line_content.cont
            yield line_content.data

    def send_cmd_and_get_response(self, cmd):
        self.send_command(cmd)
        for data in self.read_response():
            yield data
# --------------------------------------------------------------------------- #


if __name__ == '__main__':
    with SVDRPClient('localhost', 6419) as svdrp:
        for data in svdrp.send_cmd_and_get_response("LSTC"):
            print(data)
