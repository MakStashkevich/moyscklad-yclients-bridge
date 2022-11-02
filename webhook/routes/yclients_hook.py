import logging

from aiohttp import web
from aiohttp.abc import BaseRequest

from handler import yclients_handler, YClientsHandler
from webhook.routes.default_hook import get_json_response

_logger = logging.getLogger(__name__)

routes = web.RouteTableDef()


@routes.post('/yclients/')
async def handle_yclients_hook(request: BaseRequest):
    response = await get_json_response(request)
    result = False
    _logger.debug(response)

    if isinstance(yclients_handler, YClientsHandler):
        result = await yclients_handler.handle_webhook(response)

    return web.json_response({
        'ok': result
    })
