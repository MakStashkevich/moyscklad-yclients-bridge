import logging

from aiohttp import web
from aiohttp.abc import BaseRequest

from handler import yclients_sync
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


@routes.post('/yclients/sync/')
async def handle_yclients_sync(request: BaseRequest):
    result = False
    color = "yellow"
    text = "В данный момент уже происходит синхронизация..."

    if not yclients_sync.is_process and isinstance(yclients, YClientsHandler):
        result = await yclients_sync.sync_yclients_products_with_moyscklad(
            yclients_api=yclients.api,
            yclients_company_id=yclients.company_id,
            yclients_storage_id=yclients.storage_id
        )
        if not result:
            color = "red"
            text = "Во время синхронизации произошла ошибка..."
        else:
            color = "green"
            text = "Синхронизация прошла успешно!"

    return web.json_response({
        "ok": result,
        "color": color,
        "text": text
    })
