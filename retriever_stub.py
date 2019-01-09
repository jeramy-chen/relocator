import asyncio
from retriever import Retriever


class RetrieverStub(Retriever):
    def __init__(self, loop: asyncio.AbstractEventLoop):
        super().__init__(loop)

    async def _retrieve(self, url):
        print('Retrieving: {}'.format(url))
        await asyncio.sleep(1, self._loop)
        return url.encode()
