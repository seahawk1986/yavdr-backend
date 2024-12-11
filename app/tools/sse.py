import asyncio
import typing
from fastapi.responses import StreamingResponse
from fastapi import BackgroundTasks
from starlette.types import Send, Scope, Receive
from starlette.concurrency import run_until_first_complete


class SSE_StreamingResponse(StreamingResponse):
    """
    This is a specialized StreamingResponse which can register itself on a list
    of active client connections and forward all messages added to it's messages queue.
        
    """
    is_closed = False

    def __init__(
        self,
        register: typing.List,
        status_code: int = 200,
        headers: dict = None,
        media_type: str = None,
        background: BackgroundTasks = None,
    ) -> None:
        self.messages = asyncio.Queue()
        self.status_code = status_code
        self.media_type = self.media_type if media_type is None else media_type
        self.background = background
        self.init_headers(headers)
        # register class instance
        self.register = register
        self.register.append(self)

    async def stream_messages(self, send: Send) -> None:
        await send(
            {
                "type": "http.response.start",
                "status": self.status_code,
                "headers": self.raw_headers,
            }
        )
        while (chunk := await self.messages.get()) is not None:
            if not isinstance(chunk, bytes):
                chunk = chunk.encode(self.charset)
            print("sending data for", self)
            await send({"type": "http.response.body", "body": chunk, "more_body": True})
        
        await send({"type": "http.response.body", "body": b"", "more_body": False})

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await run_until_first_complete(
            (self.stream_messages, {"send": send}),
            (self.listen_for_disconnect, {"receive": receive}),
        )

        self.register.remove(self)

        if self.background is not None:
            await self.background()