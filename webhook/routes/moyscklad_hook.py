import logging

from aiohttp import web

_logger = logging.getLogger(__name__)

routes = web.RouteTableDef()


@routes.get('/moyscklad/')
async def handle_moyscklad_hook(req):
    return web.json_response({
        'ok': True
    })
