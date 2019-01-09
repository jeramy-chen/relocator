import asyncio
import configparser
from aiohttp import web
from handler import Handlers


async def start_async_app(loop):
    config = configparser.ConfigParser()
    config.read('config.ini')
    handlers = await Handlers.create(config, loop)
    app = web.Application()
    app.router.add_routes(handlers.routes)
    runner = web.AppRunner(app)
    await runner.setup()
    host = config.get('server', 'host')
    port = int(config.get('server', 'port'))
    site = web.TCPSite(runner, host, port)
    await site.start()

loop = asyncio.get_event_loop()
asyncio.ensure_future(start_async_app(loop))
loop.run_forever()
loop.close()
