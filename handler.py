from asyncio import AbstractEventLoop
from aiohttp import web
from json.decoder import JSONDecodeError
import itertools

from logger import init_logger
from relocator import Relocator
from storage_imgur import StorageImgur
from retriever_impl import RetrieverImpl
import request_format
import response_format

_logger = init_logger(__name__)


class Handlers:

    @classmethod
    async def create(cls, config, loop: AbstractEventLoop):
        storage = await StorageImgur.create(config, loop)
        retriever = RetrieverImpl(loop)
        relocator = Relocator(retriever, storage, loop)
        return cls(relocator)

    def __init__(self, relocator: Relocator):
        self._relocator = relocator

    @property
    def routes(self):
        self._JOB_ID_MATCH = 'job_id'

        return [web.get('/v1/images/upload/:{{{}}}'.format(self._JOB_ID_MATCH), self._report_job_status, allow_head=False),
                web.get('/v1/images', self._report_uploaded, allow_head=False),
                web.post('/v1/images/upload', self._start_job)]

    async def _start_job(self, request: web.Request):
        _logger.debug('Got a request')

        if not request.can_read_body:
            _logger.info('invalid http body')
            raise web.HTTPBadRequest(reason='HTTP body not readable')

        try:
            req = await request.json()
        except JSONDecodeError as e:
            _logger.info(str(e))
            raise web.HTTPBadRequest(reason='HTTP body malformed: {}'.format(str(e)))

        URL_KEY = 'urls'

        try:
            urls = req[URL_KEY]
        except KeyError as e:
            _logger.info(str(e))
            raise web.HTTPBadRequest(reason='Key not found: {}'.format(str(e)))

        if (not isinstance(urls, list)) or any(not isinstance(url, str) for url in urls):
            _logger.info('invalid urls')
            raise web.HTTPBadRequest(reason='{} value should be a list of url'.format(URL_KEY))

        job_id = self._relocator.start(urls)
        data = response_format.format_job_id(job_id)
        return web.json_response(data)

    async def _report_job_status(self, request: web.Request):
        _logger.debug('Got a request')

        try:
            job_id = request_format.format_job_id(request.match_info[self._JOB_ID_MATCH])
        except ValueError as e:
            _logger.info(str(e))
            raise web.HTTPBadRequest(reason='Job id malformed: {}'.format(str(e)))

        try:
            job = self._relocator.status.query_job(job_id)
        except KeyError as e:
            _logger.info(str(e))
            raise web.HTTPNotFound(reason='Job id not found: {}'.format(str(e)))

        data = response_format.format_job_status(job)
        return web.json_response(data)

    async def _report_uploaded(self, _: web.Request):
        _logger.debug('Got a request')
        reloc = itertools.chain.from_iterable(job.relocation for job in self._relocator.status.jobs)
        data = response_format.format_uploaded_list(reloc)
        return web.json_response(data)
