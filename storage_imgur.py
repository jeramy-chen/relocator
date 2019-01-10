import base64
from asyncio import AbstractEventLoop
from concurrent.futures import Executor
from imgurpython import ImgurClient

from logger import create_logger
from storage import Storage

logger = create_logger(__name__)


class StorageImgur(Storage):
    """
    >>> from logging import CRITICAL
    >>> logger = create_logger(__name__, CRITICAL)
    >>> from PIL import Image
    >>> from io import BytesIO
    >>> img = Image.new('RGB', (100, 100), 255)
    >>> img_output = BytesIO()
    >>> img.save(img_output, format='JPEG')

    >>> import configparser
    >>> config = configparser.ConfigParser()
    >>> _ = config.read('config.ini')

    >>> import asyncio
    >>> loop = asyncio.get_event_loop()
    >>> storage = loop.run_until_complete(StorageImgur.create(config, loop))
    >>> cb = lambda _, url_new: print(url_new)

    >>> loop.run_until_complete(storage.store_batch([img_output.getvalue()]*2, cb)) # doctest: +ELLIPSIS
    http...
    http...
    >>> loop.run_until_complete(storage.store_batch(['abc'.encode()], cb))
    None
    >>> loop.run_until_complete(storage.store_batch([None], cb))
    None
    >>> loop.close()
    """
    @classmethod
    async def create(cls, config, loop: AbstractEventLoop, executor: Executor = None):
        client_id = config.get('credentials_imgur', 'client_id')
        client_secret = config.get('credentials_imgur', 'client_secret')

        client = await loop.run_in_executor(executor, ImgurClient, client_id, client_secret)

        return cls(client, loop, executor)

    def __init__(self, client, loop, executor):
        self._client = client
        self._executor = executor
        super().__init__(loop)

    async def _store(self, content):
        try:
            b64 = base64.b64encode(content)
            data = {
                'image': b64,
                'type': 'base64',
            }
            response = await self._loop.run_in_executor(self._executor, self._client.make_request, 'POST', 'upload', data)
            url = response['link']
        except Exception as e:
            logger.error(str(e))
            return None

        return url if url else None


if __name__ == "__main__":
    import doctest
    doctest.testmod()
