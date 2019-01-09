from typing import Iterable
from datetime import datetime
import uuid
import copy


class RelocationRecord:
    """
    >>> reloc = RelocationRecord('abc')

    >>> reloc.url_new
    >>> reloc.commit_time
    >>> reloc.is_pending
    True
    >>> reloc.is_failed
    False
    >>> reloc.is_stored
    False

    >>> reloc.commit(1)
    >>> reloc.url_new
    >>> reloc.commit_time
    1
    >>> reloc.is_pending
    False
    >>> reloc.is_failed
    True
    >>> reloc.is_stored
    False

    >>> reloc.commit(2, 'xyz')
    >>> reloc.url_new
    'xyz'
    >>> reloc.commit_time
    2
    >>> reloc.is_pending
    False
    >>> reloc.is_failed
    False
    >>> reloc.is_stored
    True

    >>> reloc.url_old
    'abc'
    """
    def __init__(self, url: str):
        self._url_old = url
        self._url_new = None
        self._commit_time = None

    @property
    def url_old(self) -> str:
        return self._url_old

    @property
    def url_new(self) -> str:
        return self._url_new

    @property
    def commit_time(self):
        return self._commit_time

    @property
    def is_pending(self) -> bool:
        return not bool(self.commit_time)

    @property
    def is_failed(self) -> bool:
        return bool(self.commit_time) and not bool(self.url_new)

    @property
    def is_stored(self) -> bool:
        return bool(self.url_new)

    def commit(self, time, url_new: str = None):
        """
        :param time:
        :param url_new: None for failing the relocation
        :return:
        """
        self._url_new = url_new
        self._commit_time = time


class JobRecord:
    """
    >>> job = JobRecord(0, 10, ['abc', 'def'])
    >>> job.update_time
    10

    >>> job.commit(11, 'abc', 'ABC')
    >>> job.update_time
    11

    >>> job.commit(12, 'def', 'DEF')
    >>> job.update_time
    12

    >>> job.id
    0
    >>> job.create_time
    10
    """

    def __init__(self, job_id, create_time, urls: Iterable[str]):
        """
        :param job_id:
        :param create_time:
        :param urls: each url has to be unique
        """
        self._id = job_id
        self._create_time = create_time
        self._update_time = create_time
        self._relocation = dict((url, RelocationRecord(url)) for url in urls)

    @property
    def id(self):
        return self._id

    @property
    def create_time(self):
        return self._create_time

    @property
    def update_time(self):
        return self._update_time

    @property
    def relocation(self) -> Iterable[RelocationRecord]:
        return (copy.deepcopy(reloc) for reloc in self._relocation.values())

    def commit(self, time, url_old: str, url_new: str = None):
        """
        :param time:
        :param url_old:
        :param url_new: None for failing the relocation
        :return:
        """
        self._relocation[url_old].commit(time, url_new)
        self._update_time = max(time, self._update_time)


class JobRecords:
    """
    >>> jobs = JobRecords()
    >>> job1 = jobs.create_job(['a', 'b'])
    >>> job2 = jobs.create_job(['c', 'd', 'e'])
    >>> jobs.query_job(job1).id == job1
    True
    >>> jobs.query_job(job2).id == job2
    True
    >>> jobs.commit(job1, 'a', 'A')
    >>> for relc in jobs.query_job(job1).relocation:
    ...     if 'a' == relc.url_old:
    ...         print('A' == relc.url_new)
    ...     else:
    ...         print('b' == relc.url_old)
    ...         print(relc.url_new is None)
    True
    True
    True
    """
    def __init__(self):
        self._jobs = {}

    def create_job(self, urls: Iterable[str]) -> uuid.UUID:
        """
        :param urls: each url has to be unique
        :return:
        """
        job_id = uuid.uuid4()
        job = JobRecord(job_id, datetime.utcnow(), urls)
        self._jobs[job_id] = job
        return job_id

    def commit(self, job_id: uuid.UUID, url_old: str, url_new: str = None):
        """
        :param job_id:
        :param url_old:
        :param url_new: None for failing the relocation
        :return:
        """
        self._jobs[job_id].commit(datetime.utcnow(), url_old, url_new)

    def query_job(self, job_id: uuid.UUID) -> JobRecord:
        return copy.deepcopy(self._jobs[job_id])

    @property
    def jobs(self) -> Iterable[JobRecord]:
        return (copy.deepcopy(job) for job in self._jobs.values())


if __name__ == "__main__":
    import doctest
    doctest.testmod()
