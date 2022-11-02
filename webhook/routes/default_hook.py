import logging
from json import JSONDecodeError

from aiohttp import web
from aiohttp.abc import BaseRequest

_logger = logging.getLogger(__name__)

routes = web.RouteTableDef()


@routes.get('/')
async def handle_default(request: BaseRequest):
    return web.json_response({
        'ok': True
    })


async def get_json_response(request: BaseRequest) -> dict:
    try:
        response = await request.json()
    except JSONDecodeError:
        response = {}

    return response
