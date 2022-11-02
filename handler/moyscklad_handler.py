import datetime
import logging

from pony.orm import db_session

from database.database import MoyscladData
from request.moyscklad_api import MoysckladApi, MoyscladApiWebhookActionType
from settings import get_timezone, get_webserver_settings

_logger = logging.getLogger(__name__)


class MoysckladHandler:
    api: MoysckladApi = None

    def __init__(self):
        self.api = MoysckladApi()

    async def connect(self):
        _logger.debug("Try connect to Moysclad ...")
        await self.prepare()

        webserver_settings = get_webserver_settings()
        webserver_hook_url = f"http://{webserver_settings.webserver_host}:{webserver_settings.webserver_port}/moyscklad/"

        current_webhooks = await self.api.get_webhooks()
        webhook_rows = current_webhooks['rows']

        # https://dev.moysklad.ru/doc/api/remap/1.2/dictionaries/#suschnosti-nastrojki-pol-zowatelq
        # Нижний раздел «Стартовые экраны»
        webhook_entity_type = "customerorder"
        webhook_connected = False
        webhooks_meta = []

        for webhook_data in webhook_rows:
            webhooks_meta.append({"meta": webhook_data['meta']})
            if webhook_data['entityType'] == webhook_entity_type and \
                    webhook_data['url'] == webserver_hook_url and \
                    webhook_data['method'] == "POST" and \
                    webhook_data['enabled'] is True:
                webhook_connected = True
                break

        if not webhook_connected:
            if len(webhooks_meta) > 0:
                res = await self.api.delete_webhooks(webhooks_meta)
                if type(res) is list:
                    for r in res:
                        _logger.debug(r['info'])

            await self.api.set_webhook(
                url=webserver_hook_url,
                entity_type=webhook_entity_type,
                action=MoyscladApiWebhookActionType.CREATE
            )

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
        _logger.debug("have moysclad handle webhook")
