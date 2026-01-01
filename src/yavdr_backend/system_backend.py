import asyncio
import sdbus
from contextlib import closing
from yavdr_backend.interfaces.system_backend import YAVDR_BACKEND_INTERFACE, YavdrSystemBackend

async def system_backend():
    with closing(sdbus.sd_bus_open_system()) as system_bus:
        await system_bus.request_name_async(YAVDR_BACKEND_INTERFACE, 0)
        backend_interface = YavdrSystemBackend(system_bus)
        _ = backend_interface.export_to_dbus('/', system_bus)
        await backend_interface.run_jobs()
        await asyncio.Future()

def main():
    try:
        asyncio.run(system_backend())
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()