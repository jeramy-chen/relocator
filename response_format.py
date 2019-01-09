from typing import Iterable
from datetime import datetime
from uuid import UUID
from record import RelocationRecord, JobRecord


def _format_job_id(job_id: UUID) -> str:
    return str(job_id)


def _format_time(time: datetime) -> str:
    return time.isoformat()


def format_job_id(job_id: UUID) -> dict:
    return {'jobId': _format_job_id(job_id)}


def format_job_status(job: JobRecord) -> dict:
    """
    >>> import datetime
    >>> job = JobRecord(1, datetime.datetime.utcnow(), ['a', 'b'])
    >>> format_job_status(job) # doctest: +ELLIPSIS
    {'id': '1', 'created': '2...', 'finished': None, 'status': 'pending', 'uploaded': {'pending': ['a', 'b'], 'complete': [], 'failed': []}}

    >>> job.commit(datetime.datetime.utcnow(), 'a')
    >>> format_job_status(job) # doctest: +ELLIPSIS
    {'id': '1', 'created': '2...', 'finished': None, 'status': 'in-progress', 'uploaded': {'pending': ['b'], 'complete': [], 'failed': ['a']}}

    >>> job.commit(datetime.datetime.utcnow(), 'a', 'A')
    >>> format_job_status(job) # doctest: +ELLIPSIS
    {'id': '1', 'created': '2...', 'finished': None, 'status': 'in-progress', 'uploaded': {'pending': ['b'], 'complete': ['A'], 'failed': []}}

    >>> job.commit(datetime.datetime.utcnow(), 'b')
    >>> format_job_status(job) # doctest: +ELLIPSIS
    {'id': '1', 'created': '2...', 'finished': '2...', 'status': 'complete', 'uploaded': {'pending': [], 'complete': ['A'], 'failed': ['b']}}

    >>> job.commit(datetime.datetime.utcnow(), 'a')
    >>> format_job_status(job) # doctest: +ELLIPSIS
    {'id': '1', 'created': '2...', 'finished': '2...', 'status': 'complete', 'uploaded': {'pending': [], 'complete': [], 'failed': ['a', 'b']}}

    >>> job.commit(datetime.datetime.utcnow(), 'a', 'A')
    >>> job.commit(datetime.datetime.utcnow(), 'b', 'B')
    >>> format_job_status(job) # doctest: +ELLIPSIS
    {'id': '1', 'created': '2...', 'finished': '2...', 'status': 'complete', 'uploaded': {'pending': [], 'complete': ['A', 'B'], 'failed': []}}
    """
    pending = [reloc.url_old for reloc in filter(lambda r: r.is_pending, job.relocation)]
    failed = [reloc.url_old for reloc in filter(lambda r: r.is_failed, job.relocation)]
    complete = [reloc.url_new for reloc in filter(lambda r: r.is_stored, job.relocation)]

    if not pending:
        finished_time = _format_time(job.update_time)
        job_state = "complete"
    else:
        finished_time = None
        if complete or failed:
            job_state = 'in-progress'
        else:
            job_state = 'pending'

    status = {
        "id": _format_job_id(job.id),
        "created": _format_time(job.create_time),
        "finished": finished_time,
        "status": job_state,
        "uploaded": {
            "pending": pending,
            "complete": complete,
            "failed": failed
        }
    }

    return status


def format_uploaded_list(relocation: Iterable[RelocationRecord]) -> dict:
    """
    >>> reolc = RelocationRecord('a')
    >>> reolc.commit(0)
    >>> format_uploaded_list([reolc])
    {'uploaded': []}

    >>> reolc.commit(1, 'A')
    >>> format_uploaded_list([reolc])
    {'uploaded': ['A']}
    """
    uploaded = {
        "uploaded": []
    }

    for reloc in filter(lambda r: r.is_stored, relocation):
        uploaded['uploaded'].append(reloc.url_new)

    return uploaded


if __name__ == "__main__":
    import doctest
    doctest.testmod()
