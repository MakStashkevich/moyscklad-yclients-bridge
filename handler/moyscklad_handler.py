import asyncio
import datetime
import logging

from pony.orm import db_session

from database.database import MoyscladData
from request.api import ApiException
from request.moyscklad_api import MoysckladApi, MoyscladApiWebhookActionType
from settings import get_timezone, get_webserver_settings, get_global_settings

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
        webhook_entity_type = "customerorder"
        webhook_connected = False
        webhooks_meta = []

        for webhook_data in webhook_rows:
            webhooks_meta.append({"meta": webhook_data['meta']})
            if webhook_data['entityType'] == webhook_entity_type and \
                    webhook_data['url'] == webserver_hook_url and \
                    webhook_data['method'] == "POST" and \
                    webhook_data['enabled'] is True:
                _logger.debug("Found connected webhook ...")
                webhook_connected = True
                break

        if not webhook_connected:
            _logger.debug("Webhook not found ...")
            if len(webhooks_meta) > 0:
                _logger.debug("Delete all connected webhooks ...")
                res = await self.api.delete_webhooks(webhooks_meta)
                if type(res) is list:
                    for r in res:
                        _logger.debug(r['info'])

            _logger.debug("Set new webhook ...")
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

    async def handle_webhook(self, response: dict | list) -> bool:
        from handler.moyscklad_sync import sync_moyscklad_order_with_yclients
        _logger.debug("Start handle MoyScklad webhook ...")
        if type(response) is list:
            _logger.error(f"Handle MoyScklad webhook not be a list: {response}")
            return False

        try:
            event = response['events'][0]
            event_meta = event['meta']
            if event['action'] == "CREATE" and event_meta['type'] == "customerorder":
                _logger.info("MoyScklad order found ...")

                # Order
                # https://dev.moysklad.ru/doc/api/remap/1.2/documents/#dokumenty-zakaz-pokupatelq-poluchit-zakaz-pokupatelq
                _logger.debug("Get MoyScklad order data ...")
                req = await self.api.get(event_meta['href'])
                customer_order = req.response
                order_name = customer_order['name']
                # order_description = customer_order['description'] if 'description' in customer_order else ''
                order_sum = int(float(customer_order['sum']) / 100)
                order_state = customer_order['state']
                order_agent = customer_order['agent']
                order_positions = customer_order['positions']

                # Start synchronisation process
                asyncio.ensure_future(sync_moyscklad_order_with_yclients(
                    moyscklad_api=self.api,
                    order_name=order_name,
                    order_sum=order_sum,
                    order_state=order_state,
                    order_agent=order_agent,
                    order_positions=order_positions
                ))
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


moyscklad = MoysckladHandler()
