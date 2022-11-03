import base64
import enum

from aiohttp import ClientResponse

from request.api import Api, ApiException
from settings import get_global_settings, get_moysclad_settings


class MoyscladApiWebhookActionType(enum.Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class MoysckladApi(Api):
    URL_ENTITY: str = "https://online.moysklad.ru/api/remap/1.2/entity/{method}/"
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

    async def get_products(self) -> dict:
        """
        https://dev.moysklad.ru/doc/api/remap/1.2/dictionaries/#suschnosti-towar-poluchit-spisok-towarow
        :return:
        """
        url = MoysckladApi.URL_ENTITY.format(method="product")
        req = await self.get(url)
        return req.response

    async def set_products(self, products_list: list) -> dict:
        """
        https://dev.moysklad.ru/doc/api/remap/1.2/dictionaries/#suschnosti-towar-massowoe-sozdanie-i-obnowlenie-towarow
        :return:
        """
        url = MoysckladApi.URL_ENTITY.format(method="product")
        req = await self.post(url, products_list)
        return req.response

    async def set_receipts(self, name: str, organization_meta: dict, store_meta: dict, positions: list) -> dict:
        """
        https://dev.moysklad.ru/doc/api/remap/1.2/documents/#dokumenty-oprihodowanie-sozdat-oprihodowaniq

        "positions": [
          {
            "quantity": 1,
            "price": 0,
            "assortment": {
              "meta": {
                "href": "https://online.moysklad.ru/api/remap/1.2/entity/product/328b0454-2e62-11e6-8a84-bae500000118",
                "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/product/metadata",
                "type": "product",
                "mediaType": "application/json"
              }
            },
            "overhead": 0
          }
        ]

        :return:
        """
        url = MoysckladApi.URL_ENTITY.format(method="enter")
        req = await self.post(url, {
            "name": name,
            "organization": organization_meta,
            "store": store_meta,
            "positions": positions
        })
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
