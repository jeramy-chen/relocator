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
    >>> cb = lambda url, content: print(url, content)
    >>> loop.run_until_complete(retriever.retrieve_batch([URL] * 2, cb)) # doctest: +ELLIPSIS
    http://example.com b'...Example Domain...'
    http://example.com b'...Example Domain...'
    >>> loop.run_until_complete(retriever.retrieve_batch(['http://'], cb))
    http:// None
    >>> loop.run_until_complete(retriever.retrieve_batch(['h'], cb))
    h None
    >>> loop.close()
    """
    def __init__(self, loop: AbstractEventLoop, executor: Executor = None):
        self._executor = executor
        super().__init__(loop)

    async def _retrieve(self, url):
        try:
            response = await self._loop.run_in_executor(self._executor, requests.get, url)
            content = response.content
        except Exception:
            return None

        return content if content else None


if __name__ == "__main__":
    import doctest
    doctest.testmod()
