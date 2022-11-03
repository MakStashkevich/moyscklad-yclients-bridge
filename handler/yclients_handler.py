import asyncio
import datetime
import logging

from pony.orm import db_session

from database.database import YClientsData
from request.api import ApiException
from request.yclients_api import YClientsApi
from settings import get_yclients_settings, get_timezone, get_webserver_settings, get_global_settings

_logger = logging.getLogger(__name__)


class YClientsHandler:
    api: YClientsApi = None
    company_id: int = None
    storage_id: int = None
    master_id: int = None

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
        await self.prepare_master_id()
        await self.update_db_data()

    @db_session
    async def prepare_db_data(self):
        _logger.debug("Prepare db data ...")
        data = YClientsData.get(id=1)
        if isinstance(data, YClientsData):
            self.company_id = data.company_id
            self.storage_id = data.storage_id
            self.api.access_token = data.access_token
            _logger.debug("Saved data from db ...")

    @db_session
    async def update_db_data(self):
        _logger.debug("Update db data ...")
        data = YClientsData.get(id=1)
        if isinstance(data, YClientsData) and (
                data.company_id != self.company_id or
                data.storage_id != self.storage_id or
                data.access_token != self.api.access_token
        ):
            data.company_id = self.company_id
            data.storage_id = self.storage_id
            data.access_token = self.api.access_token
            data.updated_at = datetime.datetime.now(tz=get_timezone())
            _logger.debug("Updated data on db ...")
        else:
            YClientsData(
                company_id=self.company_id,
                storage_id=self.storage_id,
                access_token=self.api.access_token
            )
            _logger.debug("Saved (created) data on db ...")

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

    async def prepare_master_id(self):
        _logger.debug("Prepare master id ...")
        if not self.master_id:
            staff_list = await self.api.get_staff_data(company_id=self.company_id)
            if type(staff_list) is list and len(staff_list) > 0:
                self.master_id = int(staff_list[0]['id'])
        if not self.master_id:
            raise RuntimeError("Master id not found")
        _logger.debug(f"Master id:{self.master_id} found!")

    async def handle_webhook(self, response: dict) -> bool:
        from handler.yclients_sync import sync_yclients_products_with_moyscklad
        _logger.debug("Start handle YClients webhook ...")
        if type(response) is list:
            _logger.error(f"Handle YClients webhook not be a list: {response}")
            return False

        try:
            company_id = int(response['company_id'])
            if company_id != self.company_id:
                _logger.error(f"Handle MoyScklad webhook have not correct of company_id: {company_id}")
                return False

            data = response['data']
            if type(data) is not dict:
                _logger.error(f"Handle MoyScklad webhook have not correct type of data: {data}")
                return False

            resource = response['resource']
            status = response['status']

            # Складские операции: продажа, списание, приход товара
            good_operations = ['goods_operations_sale', 'goods_operations_stolen', 'goods_operations_receipt']
            if resource in good_operations and status in ['create', 'update']:
                storage_id = int(data['storage']['id'])
                if storage_id != self.storage_id:
                    _logger.error(f"Handle MoyScklad webhook have not correct of storage_id: {storage_id}")
                    return False

                product_good = data['good']
                product_good_id = int(product_good['id'])
                product_title = product_good['title']
                product_cost = int(data['cost_per_unit'])

                _logger.info(f"Handle MoyScklad webhook get created {resource} with product: {product_title}")

                # Start synchronisation process
                asyncio.ensure_future(sync_yclients_products_with_moyscklad(
                    yclients_api=self.api,
                    yclients_company_id=self.company_id,
                    yclients_storage_id=self.storage_id,
                    product_good_id=product_good_id,
                    product_title=product_title,
                    product_cost=product_cost
                ))

            # Создание, изменение, удаление товара
            elif resource == 'good' and status in ['create', 'update', 'delete']:
                product_label = data['label']
                product_good_id = int(data['good_id'])
                product_title = data['title']
                product_cost = int(data['cost'])
                product_article = data['article']

                _logger.info(f"Handle MoyScklad webhook get {status} product: {product_label}")

                # Start synchronisation process
                if status == 'update':
                    asyncio.ensure_future(sync_yclients_products_with_moyscklad(
                        yclients_api=self.api,
                        yclients_company_id=self.company_id,
                        yclients_storage_id=self.storage_id,
                        product_good_id=product_good_id,
                        product_title=product_title,
                        product_article=product_article,
                        product_cost=product_cost
                    ))
            else:
                _logger.error(f"Handle MoyScklad webhook not understand request ...")
                return False
        except KeyError as ex:
            _logger.error(f"Handle MoyScklad webhook have a key error: {ex}")
            return False
        except (ApiException, Exception) as ex:
            message = ex.message if isinstance(ex, ApiException) else str(ex)
            _logger.error(f"Handle MoyScklad webhook is failed: {message}")
            if get_global_settings().is_debug:
                _logger.exception(ex)
            return False

        return True


yclients = YClientsHandler()
