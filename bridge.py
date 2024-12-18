import asyncio
import logging
import sys

import webhook.webserver
from database.database import bind_database
from handler.moyscklad_handler import moyscklad
from handler.yclients_handler import yclients
from request.api import ApiException
from settings import get_global_settings

logging.basicConfig(
    level=logging.INFO if not get_global_settings().is_debug else logging.DEBUG,
    format='[%(asctime)s][%(name)s][%(levelname)s]: %(message)s'
)
_logger = logging.getLogger(__name__)


async def bridge_process():
    await bind_database()

    try:
        await yclients.connect()
        await moyscklad.connect()
        await webhook.webserver.connect()

        # wait forever
        await asyncio.Event().wait()
    except (ApiException, Exception) as ex:
        message = ex.message if isinstance(ex, ApiException) else str(ex)
        _logger.error(f"Bridge not connected! {message}")
        if get_global_settings().is_debug:
            _logger.exception(ex)
        sys.exit(1)


if __name__ == '__main__':
    try:
        asyncio.run(bridge_process())
    except KeyboardInterrupt:
        pass
