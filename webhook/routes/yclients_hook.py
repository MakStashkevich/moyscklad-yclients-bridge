import logging

from aiohttp import web
from aiohttp.abc import BaseRequest

from webhook.routes import get_json_response

_logger = logging.getLogger(__name__)

routes = web.RouteTableDef()


@routes.post('/yclients/')
async def handle_yclients_hook(request: BaseRequest):
    response = await get_json_response(request)
    _logger.debug(response)
    return web.json_response({
        'ok': True
    })
