import asyncio
import logging
from time import time

import aiohttp
from aiohttp import ClientSession, ClientResponse

from settings import get_global_settings

_logger = logging.getLogger(__name__)
_client_timeout_sec = aiohttp.ClientTimeout(total=30)
_next_request_time = 0


class ApiException(Exception):
    def __init__(self, message: str):
        self.message = message


class ApiResponse:
    status: int = 200
    response: dict | list = None

    def __init__(self, status: int, response: dict | list):
        self.status = status
        self.response = response


async def on_request_start(session, trace_config_ctx, params):
    _logger.debug("Starting %s request for %s. I will send: %s" % (params.method, params.url, params.headers))


trace_config = aiohttp.TraceConfig()
if get_global_settings().is_trace_requests:
    trace_config.on_request_start.append(on_request_start)


class Api:
    @property
    def header(self) -> dict:
        return {
            "Accept": "application/json",
            # "Cache-Control": "no-cache"
        }

    @staticmethod
    async def synchronisation_requests_sleep(load_ms: int = 3000) -> None:
        """
        :param load_ms: Задержка между всеми запросами (в милли-сек)
        :return: None
        """
        current_ms = round(time() * 1000)
        global _next_request_time

        if _next_request_time > current_ms:
            load_sec = (_next_request_time - current_ms) / 1000
            _logger.debug(f"Load request on: {load_sec} seconds")
            await asyncio.sleep(load_sec)

        _next_request_time = current_ms + load_ms

    async def handle_error(self, response: ClientResponse):
        req_method = response.request_info.method
        res_status = response.status
        if (req_method == "GET" and res_status != 200) or (
                req_method == "POST" and res_status != 200 and res_status != 201):
            raise ApiException(message=f"{req_method} Status is not be {res_status}: {response.reason}")

    async def get(self, url: str, params: dict = None, header: dict = None) -> ApiResponse:
        await Api.synchronisation_requests_sleep()
        async with ClientSession(trace_configs=[trace_config], timeout=_client_timeout_sec,
                                 headers=self.header if header is None else header) as c:
            response = await c.get(url, params=params, allow_redirects=False)
            if response.status != 200:
                await self.handle_error(response)

        return ApiResponse(response.status, await response.json())

    async def post(self, url: str, params: dict | list = None, header: dict = None) -> ApiResponse:
        await Api.synchronisation_requests_sleep()
        async with ClientSession(trace_configs=[trace_config], timeout=_client_timeout_sec,
                                 headers=self.header if header is None else header) as c:
            response = await c.post(url, json=params, ssl=False)
            if response.status != 200 and response.status != 201:
                await self.handle_error(response)

        return ApiResponse(response.status, await response.json())
