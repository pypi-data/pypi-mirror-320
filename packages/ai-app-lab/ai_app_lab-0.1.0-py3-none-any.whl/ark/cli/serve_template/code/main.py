from typing import AsyncIterable

from ark.core.idl.maas_protocol import MaasChatRequest, MaasChatResponse
from ark.core.launcher.local.serve import launch_serve
from ark.core.task import task


@task(distributed=False)
async def main(request: MaasChatRequest) -> AsyncIterable[MaasChatResponse]:
    # Your code here
    response = MaasChatResponse()
    yield response


if __name__ == "__main__":
    launch_serve(package_path="main")
