import logging

from aiohttp import web
from aiohttp.abc import BaseRequest

from handler import moyscklad_handler
from handler.moyscklad_handler import MoysckladHandler
from webhook.routes.default_hook import get_json_response

_logger = logging.getLogger(__name__)

routes = web.RouteTableDef()


@routes.post('/moyscklad/')
async def handle_moyscklad_hook(request: BaseRequest):
    response = await get_json_response(request)
    result = False
    _logger.debug(response)

    if isinstance(moyscklad_handler, MoysckladHandler):
        result = await moyscklad_handler.handle_webhook(response)

    return web.json_response({
        'ok': result
    })
