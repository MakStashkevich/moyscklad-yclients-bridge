import asyncio
import datetime
import logging

from pony.orm import db_session

from database.database import YClientsData
from handler.moyscklad_handler import moyscklad
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
            status = resource['status']

            # Складские операции: продажа, списание, приход товара
            good_operations = ['goods_operations_sale', 'goods_operations_stolen', 'goods_operations_receipt']
            if resource in good_operations and status == 'create':
                storage_id = int(data['storage']['id'])
                if storage_id != self.storage_id:
                    _logger.error(f"Handle MoyScklad webhook have not correct of storage_id: {storage_id}")
                    return False

                product_good = data['good']
                product_good_id = int(product_good['id'])
                product_title = product_good['title']
                product_cost = int(product_good['cost_per_unit'])

                _logger.info(f"Handle MoyScklad webhook get created {resource} with product: {product_title}")

                # Start synchronisation process
                asyncio.ensure_future(self.synchronisation_products_with_moyscklad(
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
                    asyncio.ensure_future(self.synchronisation_products_with_moyscklad(
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

    async def synchronisation_products_with_moyscklad(
            self,
            product_good_id: int = None,
            product_title: str = None,
            product_article: str = None,
            product_cost: int = None,
    ) -> bool:
        _logger.info("Start synchronisation YClients products with MoyScklad ...")
        moyscklad_api = moyscklad.api
        update_yclients_products = {}

        def add_update_yclients_product(title: str, article: str, amount: int, cost: int) -> None:
            _logger.debug(f"Add new update YClients product:{product_article} to list ...")
            update_yclients_products[article] = {
                "title": title,
                "amount": amount,
                "cost": cost
            }

        def get_amount_product(product_data: dict) -> int:
            amount = 0
            actual_amounts = product_data['actual_amounts']
            for amount_data in actual_amounts:
                if amount_data['storage_id'] == self.storage_id:
                    amount = int(amount_data['amount'])

            return amount

        try:
            if product_good_id is not None and product_good_id > 0:
                _logger.debug(f"Find YClients product article by good id:{product_good_id} ...")
                product = await self.api.get_products(
                    company_id=self.company_id,
                    good_id=product_good_id
                )

                if type(product) is not dict:
                    _logger.error("Found YClients product data is not type dict and not parsed ...")
                    return False

                product_amount = get_amount_product(product)
                if product_amount < 1:
                    _logger.debug(
                        f"YClients Product not found amount with storage_id:{self.storage_id} ... Continue ...")
                    return False

                product_title = product_title if product_title is not None else product['title']
                product_article = product_article if product_article is not None else product['article']
                product_cost = product_cost if product_cost is not None else int(product['cost'])

                # Add found product to list
                add_update_yclients_product(product_title, product_article, product_amount, product_cost)
            else:
                # Product not found -> Get all products of storage
                _logger.debug("Get all YClients products of storage ...")
                products = await self.api.get_products(
                    company_id=self.company_id,
                    count=1000
                )

                if type(products) is not list:
                    _logger.error("Found YClients products data is not type list and not parsed ...")
                    return False

                # Parse all products and pack them
                _logger.debug("Parse all YClients products and pack them ...")
                for product in products:
                    if 'actual_amounts' not in product:
                        _logger.debug("YClients Product not found actual_amounts param ... Continue ...")
                        continue

                    product_amount = get_amount_product(product)
                    if product_amount < 1:
                        _logger.debug(
                            f"YClients Product not found amount with storage_id:{self.storage_id} ... Continue ...")
                        continue

                    product_title = product['title']
                    product_article = product['article']
                    product_cost = int(product['cost'])

                    # Add found product to list
                    add_update_yclients_product(product_title, product_article, product_amount, product_cost)

            if len(update_yclients_products) < 1:
                _logger.info("YClients Products not found for synchronisation with MoyScklad ...")
                return False

            # Prepare cells
            update_moyscklad_products = []
            update_moyscklad_receipts = []
            update_moyscklad_loss = []

            # Get all MoyScklad stocks
            _logger.debug("Get all MoyScklad stocks ...")
            moyscklad_stocks = await moyscklad_api.get_stock_all()
            moyscklad_stocks_rows = moyscklad_stocks['rows']
            moyscklad_stocks_by_article = {}
            if len(moyscklad_stocks_rows) > 0:
                _logger.debug("Parse all MoyScklad stocks by article ...")
                for stock_row in moyscklad_stocks_rows:
                    stock_row_article = stock_row['article']
                    stock_row_quantity = int(stock_row['quantity'])
                    moyscklad_stocks_by_article[stock_row_article] = stock_row_quantity

            # Parse all MoyScklad products
            _logger.debug("Parse all MoyScklad products ...")
            moyscklad_products = await moyscklad_api.get_products(limit=1000)
            moyscklad_products_rows = moyscklad_products['rows']
            for row in moyscklad_products_rows:
                row_code = row['code']
                if 'article' not in row:
                    _logger.debug(f"MoyScklad product:{row_code} not have article ... Continue ...")
                    continue

                row_article = row['article']
                if row_article not in update_yclients_products:
                    _logger.debug(f"MoyScklad product:{row_code} not need update ... Continue ...")
                    continue

                row_name = row['name']
                row_sale_prices = row['salePrices']
                row_cost = int(float(row_sale_prices[0]['value']) / 1000)

                new_row = {}
                yclients_product = update_yclients_products[row_article]
                if yclients_product['title'] != row_name:
                    new_row["name"] = yclients_product['title']

                if int(yclients_product['cost']) != row_cost:
                    new_sale_prices = row_sale_prices.copy()
                    new_sale_prices[0]['value'] = float(int(yclients_product['cost']) * 1000)
                    new_row["salePrices"] = new_sale_prices

                if len(new_row) > 0:
                    _logger.debug(f"MoyScklad product:{row_code} added to update ...")
                    update_moyscklad_products.append({
                        **new_row,
                        **{"meta": row['meta']}
                    })

                current_amount = 0
                if row_article in moyscklad_stocks_by_article:
                    current_amount = int(moyscklad_stocks_by_article[row_article])

                yclients_amount = int(yclients_product['amount'])
                if yclients_amount > current_amount:
                    update_moyscklad_receipts.append({
                        "quantity": int(yclients_amount - current_amount),  # Количество
                        "price": 0,  # Себестоимость в копейках
                        "assortment": {
                            "meta": row['meta']  # Метаданные товара
                        },
                        "reason": "Updated YClients product",  # Причина оприходования позиции
                        "overhead": 0  # Накладные расходы
                    })
                elif current_amount > 0 and yclients_amount < current_amount:
                    update_moyscklad_loss.append({
                        "quantity": int(current_amount - yclients_amount),  # Количество
                        "price": 0,  # Себестоимость в копейках
                        "assortment": {
                            "meta": row['meta']  # Метаданные товара
                        },
                        "reason": "Updated YClients product",  # Причина оприходования позиции
                        "overhead": 0  # Накладные расходы
                    })

            if len(update_yclients_products) > 0:
                _logger.info("Update MoyScklad products ...")
                await moyscklad_api.set_products(update_moyscklad_products)

            if len(update_moyscklad_receipts) > 0:
                _logger.info("Update MoyScklad receipts ...")
                await moyscklad_api.set_receipts(
                    description="YClients Sync",
                    organization_meta={},
                    store_meta={},
                    positions=update_moyscklad_receipts
                )

            if len(update_moyscklad_loss) > 0:
                _logger.info("Update MoyScklad loss ...")
                await moyscklad_api.set_loss(
                    description="YClients Sync",
                    organization_meta={},
                    store_meta={},
                    positions=update_moyscklad_loss
                )
        except KeyError as ex:
            _logger.error(f"Synchronisation MoyScklad order with YClients have a key error: {ex}")
            return False
        except (ApiException, Exception) as ex:
            message = ex.message if isinstance(ex, ApiException) else str(ex)
            _logger.error(f"Synchronisation MoyScklad order with YClients is failed: {message}")
            if get_global_settings().is_debug:
                _logger.exception(ex)
            return False

        _logger.info("Success synchronisation YClients products with MoyScklad!")
        return True


yclients = YClientsHandler()
