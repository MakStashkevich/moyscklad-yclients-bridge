import datetime
import logging

from pony.orm import db_session

from database.database import YClientsData
from request.yclients_api import YClientsApi
from settings import get_yclients_settings, get_timezone, get_webserver_settings

_logger = logging.getLogger(__name__)


class YClientsHandler:
    api: YClientsApi = None
    company_id: int = None
    storage_id: int = None

    def __init__(self):
        self.api = YClientsApi()

    async def connect(self):
        _logger.debug("Try connect to YClients ...")
        await self.prepare()

        webserver_settings = get_webserver_settings()
        webserver_hook_url = f"http://{webserver_settings.webserver_host}:{webserver_settings.webserver_port}/yclients/"

        current_webhooks = await self.api.get_hook_settings(self.company_id)
        if webserver_hook_url not in current_webhooks['urls']:
            _logger.debug("Webhook not found ...")
            _logger.debug("Set new webhook ...")
            await self.api.set_hook_settings(
                company_id=self.company_id,
                urls=[webserver_hook_url],
                active=True,  # уведомления активны
                good=True,  # товар
                goods_operations_sale=True,  # продажа товара
                goods_operations_receipt=True,  # приход товара
                goods_operations_consumable=True,  # списание расходника
                goods_operations_stolen=True,  # списание товара
                self_sending=True,  # создатель webhook получает события, которые инициированы им
            )

        _logger.info("Successful connected to YClients!")

    async def prepare(self):
        await self.prepare_db_data()
        await self.api.get_access_token()
        await self.prepare_company_id()
        await self.prepare_storage_id()
        await self.update_db_data()

    @db_session
    async def prepare_db_data(self):
        _logger.debug("Prepare db data ...")
        data = YClientsData.get(id=1)
        if isinstance(data, YClientsData):
            self.company_id = data.company_id
            self.storage_id = data.storage_id
            self.api.access_token = data.access_token

    @db_session
    async def update_db_data(self):
        _logger.debug("Update db data ...")
        data = YClientsData.get(id=1)
        if isinstance(data, YClientsData):
            data.company_id = self.company_id
            data.storage_id = self.storage_id
            data.access_token = self.api.access_token
            data.updated_at = datetime.datetime.now(tz=get_timezone())
        else:
            YClientsData(company_id=self.company_id, storage_id=self.storage_id, access_token=self.api.access_token)

    async def prepare_company_id(self):
        _logger.debug("Prepare company id ...")
        if not self.company_id:
            settings = get_yclients_settings()
            companies = await self.api.get_companies()
            for company in companies:
                title = str(company['title'])
                if title.lower() == settings.yclients_company_name.lower():
                    self.company_id = int(company['id'])
                    break
        if not self.company_id:
            raise RuntimeError("Company id not found")
        _logger.debug(f"Company id:{self.company_id} found!")

    async def prepare_storage_id(self):
        _logger.debug("Prepare storage id ...")
        if not self.storage_id:
            settings = get_yclients_settings()
            storages = await self.api.get_storages(company_id=self.company_id)
            for storage in storages:
                is_for_sale = bool(storage['for_sale'])
                title = str(storage['title'])
                if is_for_sale and title.lower() == settings.yclients_storage_name.lower():
                    self.storage_id = int(storage['id'])
                    break
        if not self.storage_id:
            raise RuntimeError("Storage id not found")
        _logger.debug(f"Storage id:{self.storage_id} found!")

    async def handle_webhook(self, response: dict):
        _logger.debug("Start handle webhook ...")
