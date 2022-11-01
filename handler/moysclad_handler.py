import datetime
import logging

from pony.orm import db_session

from database.database import MoyscladData
from request.moysclad_api import MoyscladApi
from settings import get_timezone

_logger = logging.getLogger(__name__)


class MoyscladHandler:
    api: MoyscladApi = None

    def __init__(self):
        self.api = MoyscladApi()

    async def connect(self):
        _logger.debug("Try connect to Moysclad ...")
        await self.prepare()
        # await self.api.set_webhook(url="", action=MoyscladApiWebhookActionType.CREATE)
        _logger.info("Successful connected to Moysclad!")

    async def prepare(self):
        await self.prepare_db_data()
        await self.api.get_access_token()
        await self.update_db_data()

    @db_session
    async def prepare_db_data(self):
        _logger.debug("Prepare db data ...")
        data = MoyscladData.get(id=1)
        if isinstance(data, MoyscladData):
            self.api.access_token = data.access_token

    @db_session
    async def update_db_data(self):
        _logger.debug("Update db data ...")
        data = MoyscladData.get(id=1)
        if isinstance(data, MoyscladData):
            data.access_token = self.api.access_token
            data.updated_at = datetime.datetime.now(tz=get_timezone())
        else:
            MoyscladData(access_token=self.api.access_token)

    async def handle_webhook(self, response: dict):
        pass
