import asyncio
from uuid import UUID
from typing import Iterable
import copy

from logger import init_logger
from record import JobRecords
from storage import Storage
from retriever import Retriever

_logger = init_logger(__name__)


class Relocator:
    """
    >>> from storage_stub import StorageStub
    >>> from retriever_stub import RetrieverStub
    >>> from logging import CRITICAL
    >>> _ = init_logger(__name__, CRITICAL)
    >>> loop = asyncio.get_event_loop()
    >>> relocator = Relocator(RetrieverStub(loop), StorageStub(loop), loop)
    >>> relocator.start(('url1', 'url1', 'url2')) # doctest: +ELLIPSIS
    UUID('...')

    >>> def run_until_all_complete(loop):
    ...     pending = asyncio.Task.all_tasks(loop)
    ...     loop.run_until_complete(asyncio.gather(*pending))

    >>> run_until_all_complete(loop) # doctest: +ELLIPSIS
    Retrieving: url...
    Retrieving: url...
    >>> run_until_all_complete(loop) # doctest: +ELLIPSIS
    Stored: url.../uploaded
    Stored: url.../uploaded
    >>> loop.close()
    >>> for job in relocator.status.jobs:
    ...     for reloc in job.relocation:
    ...         print(reloc.url_new) # doctest: +ELLIPSIS
    url.../uploaded
    url.../uploaded
    """
    def __init__(self, retriever: Retriever, storage: Storage, loop: asyncio.AbstractEventLoop):
        self._storage = storage
        self._retriever = retriever
        self._jobs = JobRecords()
        self._loop = loop

    def start(self, urls: Iterable[str]) -> UUID:
        urls_unique = set(urls)
        job_id = self._jobs.create_job(urls_unique)
        batch = self._retriever.retrieve_batch(urls_unique, lambda url, content: self._on_retrieved(job_id, url, content))
        asyncio.ensure_future(batch, loop=self._loop)
        _logger.debug('Started retriever for {}, {} url'.format(str(job_id), len(urls_unique)))
        return job_id

    def _on_retrieved(self, job_id, url: str, content: bytes):
        _logger.debug('Retrieved {} bytes: {}, {}'.format(len(content), str(job_id), url))
        if not content:
            self._jobs.commit(job_id, url, None)
        else:
            batch = self._storage.store_batch([content], lambda _, url_new: self._jobs.commit(job_id, url, url_new))
            asyncio.ensure_future(batch, loop=self._loop)
            _logger.debug('Started storage')

    @property
    def status(self) -> JobRecords:
        return copy.deepcopy(self._jobs)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
