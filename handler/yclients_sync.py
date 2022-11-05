import logging

from handler.moyscklad_handler import moyscklad
from request.api import ApiException
from request.yclients_api import YClientsApi
from settings import get_global_settings

_logger = logging.getLogger(__name__)
_settings = get_global_settings()

is_process = False
moyscklad_api = moyscklad.api


async def sync_yclients_products_with_moyscklad(
        yclients_api: YClientsApi,
        yclients_company_id: int,
        yclients_storage_id: int,
        product_good_id: int = None,
        product_title: str = None,
        product_article: str = None,
        product_cost: int = None,
) -> bool:
    global is_process
    is_process = True

    _logger.info("Start synchronisation YClients products with MoyScklad ...")
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
            if amount_data['storage_id'] == yclients_storage_id:
                amount = int(amount_data['amount'])

        return amount

    try:
        if product_good_id is not None and product_good_id > 0:
            _logger.debug(f"Find YClients product article by good id:{product_good_id} ...")
            product = await yclients_api.get_products(
                company_id=yclients_company_id,
                good_id=product_good_id
            )

            if type(product) is not dict:
                _logger.error("Found YClients product data is not type dict and not parsed ...")
                return False

            product_amount = get_amount_product(product)
            if product_amount < 1:
                _logger.debug(
                    f"YClients Product not found amount with storage_id:{yclients_storage_id} ... Continue ...")
                return False

            product_title = product_title if product_title is not None else product['title']
            product_article = product_article if product_article is not None else product['article']
            product_cost = product_cost if product_cost is not None else int(product['cost'])

            # Add found product to list
            add_update_yclients_product(product_title, product_article, product_amount, product_cost)
        else:
            # Product not found -> Get all products of storage
            _logger.debug("Get all YClients products of storage ...")
            products = await yclients_api.get_all_products(company_id=yclients_company_id)

            if type(products) is not list:
                _logger.error("Found YClients products data is not type list and not parsed ...")
                return False

            # Parse all products and pack them
            _logger.debug("Parse all YClients products and pack them ...")
            for product in products:
                if 'actual_amounts' not in product:
                    _logger.debug("YClients Product not found actual_amounts param ... Continue ...")
                    continue

                product_title = product['title']
                product_article = product['article']
                product_cost = int(product['cost'])

                product_amount = get_amount_product(product)
                if product_amount < 1:
                    _logger.debug(
                        f"YClients Product:{product_article} not found amount with storage_id:{yclients_storage_id} ... Continue ...")
                    continue

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

        if len(update_moyscklad_products) > 0:
            _logger.info("Update MoyScklad products ...")
            await moyscklad_api.set_products(update_moyscklad_products)

        if len(update_moyscklad_receipts) > 0 or len(update_moyscklad_loss) > 0:
            _logger.debug("Get first MoyScklad organization ...")
            first_organization = await moyscklad_api.get_first_organization()
            if first_organization is None:
                _logger.error("MoyScklad first organization is none ...")
                return False
            organization_meta = {"meta": first_organization['meta']}

            _logger.debug("Get first MoyScklad store ...")
            first_store = await moyscklad_api.get_first_store()
            if first_store is None:
                _logger.error("MoyScklad first store is none ...")
                return False
            store_meta = {"meta": first_store['meta']}

            if len(update_moyscklad_receipts) > 0:
                _logger.info("Update MoyScklad receipts ...")
                await moyscklad_api.set_receipts(
                    description="YClients Sync",
                    organization_meta=organization_meta,
                    store_meta=store_meta,
                    positions=update_moyscklad_receipts
                )

            if len(update_moyscklad_loss) > 0:
                _logger.info("Update MoyScklad loss ...")
                await moyscklad_api.set_loss(
                    description="YClients Sync",
                    organization_meta=organization_meta,
                    store_meta=store_meta,
                    positions=update_moyscklad_loss
                )
    except KeyError as ex:
        _logger.error(f"Synchronisation MoyScklad order with YClients have a key error: {ex}")
        return False
    except (ApiException, Exception) as ex:
        message = ex.message if isinstance(ex, ApiException) else str(ex)
        _logger.error(f"Synchronisation MoyScklad order with YClients is failed: {message}")
        if _settings.is_debug:
            _logger.exception(ex)
        return False
    finally:
        is_process = False

    _logger.info("Success synchronisation YClients products with MoyScklad!")
    return True
