import logging

from aiohttp import web
from aiohttp.abc import BaseRequest

from handler.yclients_handler import YClientsHandler, yclients
from webhook.routes.default_hook import get_json_response

_logger = logging.getLogger(__name__)

routes = web.RouteTableDef()


@routes.post('/yclients/')
async def handle_yclients_hook(request: BaseRequest):
    response = await get_json_response(request)
    result = False
    _logger.debug(response)

    if isinstance(yclients, YClientsHandler):
        result = await yclients.handle_webhook(response)

    return web.json_response({
        'ok': result
    })
