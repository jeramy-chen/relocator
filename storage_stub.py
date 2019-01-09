import asyncio
from storage import Storage


class StorageStub(Storage):
    def __init__(self, loop: asyncio.AbstractEventLoop):
        super().__init__(loop)

    async def _store(self, content):
        await asyncio.sleep(1, self._loop)
        url_new = '{}/uploaded'.format(content.decode())
        print('Stored: {}'.format(url_new))
        return url_new
