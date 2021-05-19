import dataclasses
from gi.repository import GLib

glib_loop = GLib.MainLoop()


class VDRStatus:
    # TODO: collect vdr's status events and store them temporarily
    isRecording = False
    channel = None
    timers = []
