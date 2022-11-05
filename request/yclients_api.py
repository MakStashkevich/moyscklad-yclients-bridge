import enum
from datetime import datetime

from aiohttp import ClientResponse

from request.api import Api, ApiException, cache_result_request
from settings import get_global_settings, get_yclients_settings, get_timezone


class YClientsApiStorageOperationType(enum.Enum):
    SELL = 1  # Продажа
    COMING = 3  # Приход
    WRITE_OFF = 4  # Списание
    MOVING = 5  # Перемещение


class YClientsApiGoodOperationType(enum.Enum):
    SELL = COMING = 1  # Продажа / Приход
    WRITE_OFF = 4  # Списание


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
            "Authorization": auth
        }

    @staticmethod
    def raise_failure_response(response: dict | list) -> None:
        if type(response) is list:
            raise ApiException(f'Response YClients Api not accepted list response: {response}')

        if response['success'] is False:
            message = response['meta']['message']
            raise ApiException(f'Response YClients Api not success: {message}')

    async def handle_error(self, response: ClientResponse):
        json = await response.json()
        if type(json) is dict and 'success' in json and json['success'] is False:
            error = json['meta']['message'] if 'meta' in json and 'message' in json['meta'] else response.reason
            raise ApiException(f"YClients Api Error: {error}")

        await super().handle_error(response)

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

    @cache_result_request
    async def get_companies(self) -> dict:
        """
        https://developers.yclients.com/ru/#tag/Kompanii/operation/Получить%20список%20компаний
        :return:
        """
        url = YClientsApi.URL.format(method="companies")
        req = await self.get(url, {
            "my": 1
        })

        response = req.response
        self.raise_failure_response(response)
        return response['data']

    @cache_result_request
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

    @cache_result_request
    async def get_products(self, company_id: int, good_id: int = 0,
                           *, count: int = 1000, page: int = 1, term: str = None) -> dict | list:
        """
        https://developers.yclients.com/ru/#tag/Tovary/operation/Получить%20товары
        :return:
        """
        url = YClientsApi.URL.format(method="goods") + str(company_id) + "/"
        if good_id is not None and good_id > 0:
            url += str(good_id)

        query_params = {
            "count": count,
            "page": page
        }
        if term is not None:
            query_params['term'] = term  # Наименование, артикул или штрихкод

        req = await self.get(url, query_params)

        response = req.response
        self.raise_failure_response(response)
        return response['data']

    @cache_result_request
    async def get_product_good_id_by_article(self, company_id: int, article: str) -> int:
        products = await self.get_products(
            company_id=company_id,
            term=article
        )

        if type(products) is not list:
            return 0

        # Parse all products and search good_id
        for product in products:
            product_article = product['article'] if 'article' in product else None
            if product_article is not None and len(product_article) > 0 and 'good_id' in product:
                return int(product['good_id'])

        return 0

    async def set_client(self, company_id: int, name: str, phone: str,
                         *,
                         email: str = None,
                         comment: str = None) -> dict:
        """
        https://developers.yclients.com/ru/#tag/Klienty/operation/Добавить%20клиента
        :return:
        """
        url = YClientsApi.URL.format(method="clients") + str(company_id)
        params = {
            "name": name,
            "phone": phone
        }
        if email is not None:
            params["email"] = email
        if comment is not None:
            params["comment"] = comment
        req = await self.post(url, params)

        response = req.response
        self.raise_failure_response(response)
        return response['data']

    @cache_result_request
    async def get_client_search(self, company_id: int,
                                *,
                                page: int = 1,
                                page_size: int = 100,
                                fields: list = None,
                                order_by: str = "id",
                                order_by_direction: str = "DESC",
                                operation: str = "AND",
                                filters: list = None) -> dict:
        """
        https://developers.yclients.com/ru/#tag/Klienty/operation/Получить%20список%20клиентов
        :return:
        """
        fields = fields if fields is not None else ['id', 'name', 'phone', 'email']
        filters = filters if filters is not None else []

        url = YClientsApi.URL.format(method="company") + str(company_id) + "/clients/search"
        params = {
            "page": page,
            "page_size": page_size,
            "fields": fields,
            "order_by": order_by,
            "order_by_direction": order_by_direction,
            "operation": operation,
            "filters": filters
        }
        req = await self.post(url, params)

        response = req.response
        self.raise_failure_response(response)
        return response['data']

    @cache_result_request
    async def get_client_search_by_value(self, company_id: int, value: str,
                                         *, page: int = 1, page_size: int = 100) -> dict:
        return await self.get_client_search(
            company_id=company_id,
            page=page,
            page_size=page_size,
            fields=['id', 'name', 'phone', 'email'],
            order_by="id",
            order_by_direction="DESC",
            operation="AND",
            filters=[
                {
                    "type": "quick_search",
                    "state": {
                        "value": value
                    }
                }
            ]
        )

    @cache_result_request
    async def get_staff_data(self, company_id: int, staff_id: int = None) -> dict:
        url = YClientsApi.URL.format(method="company") + str(company_id) + "/staff/"
        if staff_id is not None and staff_id > 0:
            url += str(staff_id)

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
                                    comment: str = None,
                                    create_date: str = None) -> dict:
        """
        https://developers.yclients.com/ru/#tag/Skladskie-operacii/operation/Создание%20складской%20операции
        :return:
        """
        url = YClientsApi.URL.format(method="storage_operations/operation") + str(company_id)
        params = {
            "type_id": type_id.value,
            "storage_id": storage_id,
            "goods_transactions": goods_transactions,
            "create_date": create_date if create_date is not None else str(datetime.now(tz=get_timezone()))
        }
        if master_id is not None:
            params["master_id"] = master_id
        if comment is not None:
            params["comment"] = comment
        req = await self.post(url, params)

        response = req.response
        self.raise_failure_response(response)
        return response['data']

    async def set_finance_transaction(self, company_id: int,
                                      *,
                                      expense_id: int = None,
                                      amount: int = None,
                                      account_id: int = None,
                                      client_id: int = None,
                                      supplier_id: int = None,
                                      master_id: int = None,
                                      comment: str = None,
                                      date: str = None) -> dict:
        """
        https://developers.yclients.com/ru/#tag/Finansovye-tranzakcii/operation/Создание%20финансовой%20транзакции
        :return:
        """
        url = YClientsApi.URL.format(method="finance_transactions") + str(company_id)
        params = {
            "date": date if date is not None else str(datetime.now(tz=get_timezone()))
        }
        if expense_id is not None:
            params["expense_id"] = expense_id
        if amount is not None:
            params["amount"] = amount
        if account_id is not None:
            params["account_id"] = account_id
        if client_id is not None:
            params["client_id"] = client_id
        if supplier_id is not None:
            params["supplier_id"] = supplier_id
        if master_id is not None:
            params["master_id"] = master_id
        if comment is not None:
            params["comment"] = comment

        req = await self.post(url, params)
        response = req.response
        self.raise_failure_response(response)
        return response['data']

    async def get_hook_settings(self, company_id: int) -> dict:
        url = YClientsApi.URL.format(method='hooks_settings') + str(company_id)
        req = await self.get(url)

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
