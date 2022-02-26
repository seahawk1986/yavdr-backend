import pydbus

bus = pydbus.SystemBus()
pulsectl = bus.get("org.yavdr.PulseDBusCtl")


def get_pulseaudio_sinks():
    return pulsectl.ListSinks()


def set_pulseaudio_default_sink(sink: str):
    return pulsectl.SetDefaultSink(sink)


if __name__ == '__main__':
    print(get_pulseaudio_sinks())
