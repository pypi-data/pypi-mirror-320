from typing import AsyncIterator

from aiohttp import StreamReader


class AsyncSSEDecoder(object):
    def __init__(self, source: StreamReader) -> None:
        self.source = source

    async def _read(self) -> AsyncIterator[bytes]:
        data = b""
        async for chunk in self.source:
            for line in chunk.splitlines(True):
                data += line
                if data.endswith((b"\r\r", b"\n\n", b"\r\n\r\n")):
                    yield data
                    data = b""
        if data:
            yield data

    async def next(self) -> AsyncIterator[bytes]:
        async for chunk in self._read():
            for line in chunk.splitlines():
                # skip comment
                if line.startswith(b":"):
                    continue

                if b":" in line:
                    field, value = line.split(b":", 1)
                else:
                    field, value = line, b""

                if field == b"data" and len(value) > 0:
                    yield value
