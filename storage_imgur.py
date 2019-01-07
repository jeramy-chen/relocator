import base64
from asyncio import AbstractEventLoop
from concurrent.futures import Executor
from imgurpython import ImgurClient
from storage import Storage


class StorageImgur(Storage):
    """
    >>> from PIL import Image
    >>> from io import BytesIO
    >>> img = Image.new('RGB', (100, 100), 255)
    >>> img_output = BytesIO()
    >>> img.save(img_output, format='JPEG')

    >>> import configparser
    >>> config = configparser.ConfigParser()
    >>> _ = config.read('config.ini')

    >>> async def test_storage_imgur(config, loop, contents):
    ...     storage = await StorageImgur.create(config, loop)
    ...     await storage.store_batch(contents, lambda _, url_new: print(url_new))

    >>> import asyncio
    >>> loop = asyncio.get_event_loop()
    >>> loop.run_until_complete(test_storage_imgur(config, loop, [img_output.getvalue()]*2)) # doctest: +ELLIPSIS
    http...
    http...
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
        self._loop = loop

    async def _store(self, content):
        b64 = base64.b64encode(content)

        data = {
            'image': b64,
            'type': 'base64',
        }

        response = await self._loop.run_in_executor(self._executor, self._client.make_request, 'POST', 'upload', data)
        # TODO: error handling
        return response['link']


if __name__ == "__main__":
    import doctest
    doctest.testmod()
