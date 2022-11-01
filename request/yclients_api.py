import datetime
import enum

from request.api import Api, ApiResponse, ApiException
from settings import get_global_settings, get_yclients_settings, get_timezone


class YClientsApiStorageOperationType(enum.Enum):
    SELL = 1  # Продажа
    COMING = 3  # Приход
    WRITE_OFF = 4  # Списание
    MOVING = 5  # Перемещение


class YClientsApi(Api):
    URL: str = "https://api.yclients.com/api/v1/{method}/"

    def __init__(self):
        self.access_token = None

    @property
    def header(self) -> dict:
        if self.access_token:
            auth = "Bearer {}, User {}".format(get_yclients_settings().yclients_api_partner_token, self.access_token)
        else:
            auth = "Bearer {}".format(get_yclients_settings().yclients_api_partner_token)

        return {
            "Accept": "application/vnd.yclients.v2+json",
            "Accept-Language": get_global_settings().language,
            "Authorization": auth,
            "Content-Type": "application/json",
            "Cache-Control": "no-cache"
        }

    @staticmethod
    def raise_failure_response(response: dict) -> None:
        if response['success'] is False:
            message = response['meta']['message']
            raise ApiException(f'Response YClients Api not success: {message}')

    async def get_access_token(self) -> str:
        """
        https://developers.yclients.com/ru/#tag/Avtorizaciya/operation/Авторизовать%20пользователя
        :return:
        """
        if not self.access_token:
            url = YClientsApi.URL.format(method="auth")
            settings = get_yclients_settings()
            req = await self.post(url, {
                "login": settings.yclients_login,
                "password": settings.yclients_password
            })
            response = req.response
            self.raise_failure_response(response)
            self.access_token = str(response['data']['user_token'])

        return self.access_token

    async def get_companies(self) -> dict:
        """
        https://developers.yclients.com/ru/#tag/Kompanii/operation/Получить%20список%20компаний
        :return:
        """
        url = YClientsApi.URL.format(method="companies") + '?my=1'
        req = await self.get(url)

        response = req.response
        self.raise_failure_response(response)
        return response['data']

    async def get_storages(self, company_id: int) -> dict:
        """
        https://developers.yclients.com/ru/#tag/Sklady/operation/Получить%20склады%20компании
        :return:
        """
        url = YClientsApi.URL.format(method="storages") + str(company_id)
        req = await self.get(url)

        response = req.response
        self.raise_failure_response(response)
        return response['data']

    async def get_products(self, company_id: int) -> dict:
        """
        https://developers.yclients.com/ru/#tag/Tovary/operation/Получить%20товары
        :return:
        """
        url = YClientsApi.URL.format(method="goods") + str(company_id) + "?count=1000&page=1"
        req = await self.get(url)

        response = req.response
        self.raise_failure_response(response)
        return response['data']

    async def get_product(self, company_id: int, good_id: int) -> dict:
        """
        https://developers.yclients.com/ru/#tag/Tovary/operation/Получить%20товары
        :return:
        """
        url = YClientsApi.URL.format(method="goods") + "/".join([str(company_id), str(good_id)])
        req = await self.get(url)

        response = req.response
        self.raise_failure_response(response)
        return response['data']

    async def set_storage_operation(self, company_id: int,
                                    type_id: YClientsApiStorageOperationType,
                                    storage_id: int,
                                    goods_transactions: list,
                                    *,
                                    master_id: int = None,
                                    comment: str = None) -> dict:
        """
        https://developers.yclients.com/ru/#tag/Skladskie-operacii/operation/Создание%20складской%20операции
        :return:
        """
        url = YClientsApi.URL.format(method="storage_operations/operation") + str(company_id)
        params = {
            "type_id": type_id.value,
            "storage_id": storage_id,
            "goods_transactions": goods_transactions,
            "create_date": datetime.datetime.now(tz=get_timezone())
        }
        if master_id is not None:
            params["master_id"] = master_id
        if comment is not None:
            params["comment"] = comment
        req = await self.post(url, params)

        response = req.response
        self.raise_failure_response(response)
        return response['data']

    async def set_hook_settings(self, company_id: int, urls: list, active: bool = True,
                                *,
                                salon: bool = False,
                                service_category: bool = False,
                                service: bool = False,
                                good: bool = False,
                                master: bool = False,
                                client: bool = False,
                                record: bool = False,
                                goods_operations_sale: bool = False,
                                goods_operations_receipt: bool = False,
                                goods_operations_consumable: bool = False,
                                goods_operations_stolen: bool = False,
                                goods_operations_move: bool = False,
                                finances_operation: bool = False,
                                self_sending: bool = True) -> dict:
        """
        https://developers.yclients.com/ru/#tag/Uvedomleniya-o-sobytiyah-webhooks/operation/Изменить%20настройки%20уведомлений%20о%20событиях
        :return:
        """
        url = YClientsApi.URL.format(method='hooks_settings') + str(company_id)
        req = await self.post(url, {
            "urls": urls,
            "active": active,
            "salon": salon,
            "service_category": service_category,
            "service": service,
            "good": good,
            "master": master,
            "client": client,
            "record": record,
            "goods_operations_sale": goods_operations_sale,
            "goods_operations_receipt": goods_operations_receipt,
            "goods_operations_consumable": goods_operations_consumable,
            "goods_operations_stolen": goods_operations_stolen,
            "goods_operations_move": goods_operations_move,
            "finances_operation": finances_operation,
            "self_sending": self_sending
        })

        response = req.response
        self.raise_failure_response(response)
        return response['data']
