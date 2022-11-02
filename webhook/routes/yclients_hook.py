import logging

from aiohttp import web

_logger = logging.getLogger(__name__)

routes = web.RouteTableDef()


@routes.get('/yclients/')
async def handle_yclients_hook(req):
    return web.json_response({
        'ok': True
    })
