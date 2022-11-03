import base64
import enum
from datetime import datetime

from aiohttp import ClientResponse

from request.api import Api, ApiException
from settings import get_global_settings, get_moysclad_settings


class MoyscladApiWebhookActionType(enum.Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class MoysckladApi(Api):
    URL_ENTITY: str = "https://online.moysklad.ru/api/remap/1.2/entity/{method}/"
    URL_REPORT: str = "https://online.moysklad.ru/api/remap/1.2/report/{method}/"
    URL_SECURITY: str = "https://online.moysklad.ru/api/remap/1.2/security/{method}/"

    def __init__(self):
        self.access_token = None

    @property
    def header(self) -> dict:
        return {
            "Accept": "application/json;charset=utf-8",
            "Accept-Language": get_global_settings().language,
            "Authorization": "Bearer {}".format(self.access_token),
            "Content-Type": "application/json"
        }

    async def handle_error(self, response: ClientResponse):
        """
        https://dev.moysklad.ru/doc/api/remap/1.2/#mojsklad-json-api-obschie-swedeniq-obrabotka-oshibok
        :return:
        """
        json = await response.json()
        if type(json) is dict and 'errors' in json and type(json['errors']) is list:
            error = json['errors'][0]
            raise ApiException("MoyScklad Api Error: " + error['error'] + f" ({error['code']}: {error['moreInfo']})")

        await super().handle_error(response)

    async def get_access_token(self) -> str:
        """
        https://dev.moysklad.ru/doc/api/remap/1.2/#mojsklad-json-api-obschie-swedeniq-autentifikaciq
        :return:
        """
        if not self.access_token:
            url = MoysckladApi.URL_SECURITY.format(method="token")
            settings = get_moysclad_settings()
            login_header = self.header

            # RFC2045-MIME base64
            rfc2045 = base64.b64encode(
                bytes(f'{settings.moysclad_login}:{settings.moysclad_password}'.encode('ascii'))
            ).decode('utf-8')
            login_header["Authorization"] = "Basic {}".format(rfc2045)

            req = await self.post(url, header=login_header)
            self.access_token = str(req.response['access_token'])

        return self.access_token

    async def get_products(self, limit: int = 1000, offset: int = 0) -> dict:
        """
        https://dev.moysklad.ru/doc/api/remap/1.2/dictionaries/#suschnosti-towar-poluchit-spisok-towarow
        :return:
        """
        url = MoysckladApi.URL_ENTITY.format(method="product")
        req = await self.get(url, params={
            "limit": limit,
            "offset": offset
        })
        return req.response

    async def set_products(self, products_list: list) -> dict:
        """
        https://dev.moysklad.ru/doc/api/remap/1.2/dictionaries/#suschnosti-towar-massowoe-sozdanie-i-obnowlenie-towarow
        :return:
        """
        url = MoysckladApi.URL_ENTITY.format(method="product")
        req = await self.post(url, products_list)
        return req.response

    async def get_organization_all(self, limit: int = 1000, offset: int = 0) -> dict:
        """
        https://dev.moysklad.ru/doc/api/remap/1.2/dictionaries/#suschnosti-jurlico-poluchit-spisok-urlic
        :return:
        """
        url = MoysckladApi.URL_ENTITY.format(method="organization")
        req = await self.get(url, params={
            "limit": limit,
            "offset": offset
        })
        return req.response

    async def get_first_organization(self) -> dict | None:
        organization_all = await self.get_organization_all()
        organization_rows = organization_all['rows']

        if type(organization_rows) is list and len(organization_rows) > 0:
            return organization_rows[0]

        return None

    async def get_store_all(self, limit: int = 1000, offset: int = 0) -> dict:
        """
        https://dev.moysklad.ru/doc/api/remap/1.2/dictionaries/#suschnosti-sklad-poluchit-sklady
        :return:
        """
        url = MoysckladApi.URL_ENTITY.format(method="store")
        req = await self.get(url, params={
            "limit": limit,
            "offset": offset
        })
        return req.response

    async def get_first_store(self) -> dict | None:
        store_all = await self.get_store_all()
        store_rows = store_all['rows']

        if type(store_rows) is list and len(store_rows) > 0:
            return store_rows[0]

        return None

    async def get_stock_all(self) -> dict:
        """
        https://dev.moysklad.ru/doc/api/remap/1.2/reports/#otchety-otchet-ostatki-poluchit-wse-ostatki
        :return:
        """
        url = MoysckladApi.URL_REPORT.format(method="stock/all")
        req = await self.get(url)
        return req.response

    async def set_receipts(self, organization_meta: dict, store_meta: dict, positions: list,
                           *, name: str = None, description: str = None, moment: str = None) -> dict:
        """
        https://dev.moysklad.ru/doc/api/remap/1.2/documents/#dokumenty-oprihodowanie-sozdat-oprihodowaniq
        :return:
        """
        url = MoysckladApi.URL_ENTITY.format(method="enter")
        params = {
            "moment": moment if moment is not None else str(datetime.now(tz=get_global_settings().timezone)),
            "organization": organization_meta,
            "store": store_meta,
            "positions": positions
        }
        if name is not None:
            params['name'] = name
        if description is not None:
            params['description'] = description

        req = await self.post(url, params=params)
        return req.response

    async def set_loss(self, organization_meta: dict, store_meta: dict, positions: list,
                       *, name: str = None, description: str = None, moment: str = None) -> dict:
        """
        https://dev.moysklad.ru/doc/api/remap/1.2/documents/#dokumenty-spisanie-sozdat-spisanie
        :return:
        """
        url = MoysckladApi.URL_ENTITY.format(method="loss")
        params = {
            "moment": moment if moment is not None else str(datetime.now(tz=get_global_settings().timezone)),
            "organization": organization_meta,
            "store": store_meta,
            "positions": positions
        }
        if name is not None:
            params['name'] = name
        if description is not None:
            params['description'] = description

        req = await self.post(url, params=params)
        return req.response

    async def get_webhooks(self) -> dict:
        """
        https://dev.moysklad.ru/doc/api/remap/1.2/dictionaries/#suschnosti-veb-huki-poluchit-spisok-web-hukow
        :return:
        """
        url = MoysckladApi.URL_ENTITY.format(method="webhook")
        req = await self.get(url)
        return req.response

    async def delete_webhooks(self, webhooks_meta: list) -> dict:
        """
        https://dev.moysklad.ru/doc/api/remap/1.2/dictionaries/#suschnosti-veb-huki-poluchit-spisok-web-hukow
        :return:
        """
        url = MoysckladApi.URL_ENTITY.format(method="webhook/delete")
        req = await self.post(url, webhooks_meta)
        return req.response

    async def set_webhook(self, url: str, entity_type: str,
                          action: MoyscladApiWebhookActionType = MoyscladApiWebhookActionType.CREATE) -> dict:
        """
        https://dev.moysklad.ru/doc/api/remap/1.2/dictionaries/#suschnosti-veb-huki-sozdat-web-huk
        :return:
        """
        req_url = MoysckladApi.URL_ENTITY.format(method="webhook")
        params = {
            "url": url,
            "action": action.value,
            "entityType": entity_type
        }
        if action == MoyscladApiWebhookActionType.UPDATE:
            params["diffType"] = "FIELDS"
        req = await self.post(req_url, params)
        return req.response
