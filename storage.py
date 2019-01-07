from abc import ABC, abstractmethod
from typing import Iterable, Callable
import asyncio


class Storage(ABC):

    @abstractmethod
    async def _store(self, content: bytes) -> str:
        pass

    async def _store_each(self, content: bytes, on_each_complete: Callable[[bytes, str], None]):
        url = await self._store(content)
        on_each_complete(content, url)

    async def store_batch(self, contents: Iterable[bytes], on_each_complete: Callable[[bytes, str], None]):
        batch = (self._store_each(content, on_each_complete) for content in contents)
        await asyncio.gather(*batch, return_exceptions=True)
