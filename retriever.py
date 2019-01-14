from abc import ABC, abstractmethod
from typing import Iterable, Callable
import asyncio

from logger import init_logger

_logger = init_logger(__name__)


class Retriever(ABC):

    def __init__(self, loop: asyncio.AbstractEventLoop = None):
        self._loop = loop

    @abstractmethod
    async def _retrieve(self, url: str) -> bytes:
        pass

    async def _retrieve_each(self, url: str, on_each_complete: Callable[[str, bytes], None]):
        content = await self._retrieve(url)
        _logger.debug(url)
        on_each_complete(url, content)

    async def retrieve_batch(self, urls: Iterable[str], on_each_complete: Callable[[str, bytes], None]):
        batch = (self._retrieve_each(url, on_each_complete) for url in urls)
        await asyncio.gather(*batch, loop=self._loop, return_exceptions=True)
