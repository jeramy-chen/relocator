from asyncio import AbstractEventLoop
from concurrent.futures import Executor
import requests
from retriever import Retriever


class RetrieverImpl(Retriever):
    """
    >>> import asyncio
    >>> URL = 'http://example.com'
    >>> loop = asyncio.get_event_loop()
    >>> retriever = RetrieverImpl(loop)
    >>> future = retriever.retrieve_batch([URL] * 2, lambda url, content: print(url, content))
    >>> loop.run_until_complete(future) # doctest: +ELLIPSIS
    http://example.com b'...Example Domain...'
    http://example.com b'...Example Domain...'
    >>> loop.close()
    """
    def __init__(self, loop: AbstractEventLoop, executor: Executor = None):
        self._loop = loop
        self._executor = executor

    async def _retrieve(self, url):
        response = await self._loop.run_in_executor(self._executor, requests.get, url)
        # TODO: error handling
        return response.content


if __name__ == "__main__":
    import doctest
    doctest.testmod()
