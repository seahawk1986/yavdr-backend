import asyncio
from async_svdrp import SVDRP

async def main():
    async with SVDRP() as svdrp:
        channels = await svdrp.send_cmd("LSTC")
        print(max_channel_number := int(channels[-1].decode().split()[0]))
        for channel_number in range(50, max_channel_number + 1):
            print(f"svdrpsend clre {channel_number=}")


asyncio.run(main())
