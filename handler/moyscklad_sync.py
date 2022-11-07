import logging

from handler.yclients_handler import yclients
from request.api import ApiException
from request.moyscklad_api import MoysckladApi
from request.yclients_api import YClientsApiGoodOperationType, YClientsApiStorageOperationType
from settings import get_global_settings

_logger = logging.getLogger(__name__)
_settings = get_global_settings()

yclients_api = yclients.api


async def sync_moyscklad_order_with_yclients(
        moyscklad_api: MoysckladApi,
        order_name: str,
        order_sum: int,
        order_state: dict,
        order_agent: dict,
        order_positions: dict
) -> bool:
    _logger.info("Start synchronisation MoyScklad order with YClients ...")
    try:
        # Order Positions Metadata
        _logger.debug("Get MoyScklad order positions metadata ...")
        req = await moyscklad_api.get(order_positions['meta']['href'])
        positions = req.response
        _logger.debug(positions)
        positions_rows = positions['rows'] if 'rows' in positions else None

        # Check have positions rows
        if positions_rows is None or len(positions_rows) < 1:
            _logger.error("MoyScklad order positions not found ...")
            return False

        # Order State Metadata
        # https://dev.moysklad.ru/doc/api/remap/1.2/dictionaries/#suschnosti-statusy-dokumentow-statusy
        _logger.debug("Get MoyScklad state metadata ...")
        req = await moyscklad_api.get(order_state['meta']['href'])
        state = req.response
        state_type = state['stateType'] if 'stateType' in state else None
        if state_type != "Successful":
            _logger.error("MoyScklad state type not successful ...")
            return False

        # Order Agent Metadata
        # https://dev.moysklad.ru/doc/api/remap/1.2/dictionaries/#suschnosti-kontragent-poluchit-kontragenta
        _logger.debug("Get MoyScklad order agent metadata ...")
        req = await moyscklad_api.get(order_agent['meta']['href'])
        agent = req.response
        agent_name = agent['name']
        agent_email = agent['email'] if 'email' in agent else None
        agent_phone = agent['phone'] if 'phone' in agent else None
        agent_company_type = agent['companyType']

        # Check is individual agent & create him
        yclients_client_id = 0
        if agent_company_type == "individual" and agent_phone is not None and len(agent_phone) > 0:
            # Search Agent on YClients by email
            _logger.debug(f"Search YClients agent by email {agent_email} ...")
            yclients_found_clients = await yclients_api.get_client_search_by_value(
                company_id=yclients.company_id,
                value=agent_email
            )

            # Search Agent on YClients by phone number
            if len(yclients_found_clients) < 1:
                _logger.debug(f"Search YClients agent by phone number {agent_phone} ...")
                yclients_found_clients = await yclients_api.get_client_search_by_value(
                    company_id=yclients.company_id,
                    value=agent_phone
                )

            if len(yclients_found_clients) > 0:
                yclients_client_id = yclients_found_clients[0]['id']
                _logger.debug(f"Found YClients agent with id:{yclients_client_id} ...")
            else:
                # Create Agent on YClients
                _logger.debug("Create new YClients agent ...")
                yclients_client = await yclients_api.set_client(
                    company_id=yclients.company_id,
                    name=agent_name,
                    phone=agent_phone,
                    email=agent_email,
                    comment=f"MoyScklad Synchronisation Agent"
                )
                yclients_client_id = int(yclients_client['id'])
                _logger.debug(f"Created new YClients agent with id:{yclients_client_id} ...")

        # Create new YClients finance transaction
        # _logger.debug("Create new YClients finance transaction ...")
        # finance_transaction = await yclients_api.set_finance_transaction(
        #     company_id=yclients.company_id,
        #     amount=order_sum,
        #     client_id=(
        #         yclients_client_id
        #         if yclients_client_id is not None and yclients_client_id > 0
        #         else None
        #     ),
        #     comment=f"MoyScklad Synchronisation Order ({order_name})"
        # )
        # finance_document_id = int(finance_transaction['document_id'])

        # Номер документа каким-то образом сам устанавливается при создании складской операции...
        finance_document_id = 0

        # Parse order positions assortment
        goods_transactions = []
        for row in positions_rows:
            row_quantity = int(row['quantity'])
            row_price = int(float(row['price']) / 100)
            row_discount = int(row['discount'])
            row_assortment = row['assortment']

            # Position Product Metadata
            # https://dev.moysklad.ru/doc/api/remap/1.2/dictionaries/#suschnosti-towar-poluchit-towar
            _logger.debug("Get MoyScklad position product metadata ...")
            req = await moyscklad_api.get(row_assortment['meta']['href'])
            product = req.response
            # product_name = product['name']
            # product_code = product['code'] if 'code' in product else ''
            product_article = product['article'] if 'article' in product else ''

            if 'salePrices' in product:
                product_sale_prices = product['salePrices']
                product_price = int(float(product_sale_prices[0]['value']) / 100)
            else:
                _logger.debug("SalePrices not found -> Calculate product price ...")
                product_price = int(row_price / row_quantity)

            # Search yclients product good id by article
            _logger.debug("Search YClients product good id by article ...")
            yclients_current_product_good_id = await yclients_api.get_product_good_id_by_article(
                company_id=yclients.company_id,
                article=product_article
            )

            # Check exists yclients product good id
            if yclients_current_product_good_id > 0:
                _logger.debug("YClients product good id is exists ...")

                # Add YClients product to future storage transaction
                _logger.debug(f"Add YClients product:{product_article} to future storage transaction ...")
                product_good_data = {
                    "document_id": finance_document_id,
                    "good_id": yclients_current_product_good_id,
                    "amount": row_quantity,
                    "cost_per_unit": product_price,
                    "discount": row_discount,
                    "cost": row_price,
                    "operation_unit_type": YClientsApiGoodOperationType.SELL.value,
                    "comment": f"MoyScklad Synchronisation Product ({product_article})"
                }
                if yclients_client_id is not None and yclients_client_id > 0:
                    product_good_data['client_id'] = yclients_client_id

                # Add new good transaction
                goods_transactions.append(product_good_data)

        # Create YClients product storage operation
        _logger.debug("Create YClients product storage operation ...")
        await yclients_api.set_storage_operation(
            company_id=yclients.company_id,
            type_id=YClientsApiStorageOperationType.SELL,
            storage_id=yclients.storage_id,
            master_id=yclients.master_id,
            goods_transactions=goods_transactions,
            comment=f'MoyScklad Synchronisation Order ({order_name})'
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

    _logger.info("Success synchronisation MoyScklad order with YClients!")
    return True
