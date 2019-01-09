import uuid


def format_job_id(job_id: str) -> uuid.UUID:
    return uuid.UUID(job_id)
