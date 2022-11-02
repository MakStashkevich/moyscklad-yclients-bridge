from json import JSONDecodeError

from aiohttp.abc import BaseRequest

from .moyscklad_hook import routes as moyscklad_routes
from .yclients_hook import routes as yclients_routes

routes = [
    *yclients_routes,
    *moyscklad_routes,
]


async def get_json_response(request: BaseRequest) -> dict:
    try:
        response = await request.json()
    except JSONDecodeError:
        response = {}

    return response
