### Заказы покупателей (customerorder)
```python
{
    "auditContext": {
        "meta": {
            "type": "audit",
            "href": "https://online.moysklad.ru/api/remap/1.2/audit/5ca38ab9-5a90-11ed-0a80-0702000cf514",
        },
        "uid": "@alexkirov",
        "moment": "2022-11-02 12:25:59",
    },
    "events": [
        {
            "meta": {
                "type": "customerorder",
                "href": "https://online.moysklad.ru/api/remap/1.2/entity/customerorder/5c5aba3a-5a90-11ed-0a80-0702000cf50b",
            },
            "action": "CREATE",
            "accountId": "183531a8-1198-11ed-0a80-0f8600022ae1",
        }
    ],
}
```
### Получение данных заказа
```python
{
    "meta": {
        "href": "https://online.moysklad.ru/api/remap/1.2/entity/customerorder/5c5aba3a-5a90-11ed-0a80-0702000cf50b",
        "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/customerorder/metadata",
        "type": "customerorder",
        "mediaType": "application/json",
        "uuidHref": "https://online.moysklad.ru/app/#customerorder/edit?id=5c5aba3a-5a90-11ed-0a80-0702000cf50b",
    },
    "id": "5c5aba3a-5a90-11ed-0a80-0702000cf50b",
    "accountId": "183531a8-1198-11ed-0a80-0f8600022ae1",
    "shared": False,
    "group": {
        "meta": {
            "href": "https://online.moysklad.ru/api/remap/1.2/entity/group/1835779e-1198-11ed-0a80-0f8600022ae2",
            "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/group/metadata",
            "type": "group",
            "mediaType": "application/json",
        }
    },
    "updated": "2022-11-02 12:25:58.957",
    "name": "00005",
    "code": "239441622121",
    "externalCode": "239441622121",
    "moment": "2022-11-02 12:25:16.000",
    "applicable": True,
    "rate": {
        "currency": {
            "meta": {
                "href": "https://online.moysklad.ru/api/remap/1.2/entity/currency/1b178e47-1198-11ed-0a80-0929003359fc",
                "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/currency/metadata",
                "type": "currency",
                "mediaType": "application/json",
                "uuidHref": "https://online.moysklad.ru/app/#currency/edit?id=1b178e47-1198-11ed-0a80-0929003359fc",
            }
        }
    },
    "sum": 288000.0,
    "store": {
        "meta": {
            "href": "https://online.moysklad.ru/api/remap/1.2/entity/store/1b176643-1198-11ed-0a80-0929003359f7",
            "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/store/metadata",
            "type": "store",
            "mediaType": "application/json",
            "uuidHref": "https://online.moysklad.ru/app/#warehouse/edit?id=1b176643-1198-11ed-0a80-0929003359f7",
        }
    },
    "agent": {
        "meta": {
            "href": "https://online.moysklad.ru/api/remap/1.2/entity/counterparty/5b18e9bf-5a90-11ed-0a80-0702000cf4ff",
            "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/counterparty/metadata",
            "type": "counterparty",
            "mediaType": "application/json",
            "uuidHref": "https://online.moysklad.ru/app/#company/edit?id=5b18e9bf-5a90-11ed-0a80-0702000cf4ff",
        }
    },
    "organization": {
        "meta": {
            "href": "https://online.moysklad.ru/api/remap/1.2/entity/organization/1b154d06-1198-11ed-0a80-0929003359f5",
            "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/organization/metadata",
            "type": "organization",
            "mediaType": "application/json",
            "uuidHref": "https://online.moysklad.ru/app/#mycompany/edit?id=1b154d06-1198-11ed-0a80-0929003359f5",
        }
    },
    "state": {
        "meta": {
            "href": "https://online.moysklad.ru/api/remap/1.2/entity/customerorder/metadata/states/1bb40525-1198-11ed-0a80-092900335a2b",
            "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/customerorder/metadata",
            "type": "state",
            "mediaType": "application/json",
        }
    },
    "created": "2022-11-02 12:25:58.959",
    "printed": False,
    "published": False,
    "files": {
        "meta": {
            "href": "https://online.moysklad.ru/api/remap/1.2/entity/customerorder/5c5aba3a-5a90-11ed-0a80-0702000cf50b/files",
            "type": "files",
            "mediaType": "application/json",
            "size": 0,
            "limit": 1000,
            "offset": 0,
        }
    },
    "positions": {
        "meta": {
            "href": "https://online.moysklad.ru/api/remap/1.2/entity/customerorder/5c5aba3a-5a90-11ed-0a80-0702000cf50b/positions",
            "type": "customerorderposition",
            "mediaType": "application/json",
            "size": 1,
            "limit": 1000,
            "offset": 0,
        }
    },
    "vatEnabled": True,
    "vatIncluded": True,
    "vatSum": 0.0,
    "payedSum": 0.0,
    "shippedSum": 0.0,
    "invoicedSum": 0.0,
    "reservedSum": 0.0,
    "salesChannel": {
        "meta": {
            "href": "https://online.moysklad.ru/api/remap/1.2/entity/saleschannel/552c7700-11a1-11ed-0a80-0d830035fd8d",
            "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/saleschannel/metadata",
            "type": "saleschannel",
            "mediaType": "application/json",
            "uuidHref": "https://online.moysklad.ru/app/#saleschannel/edit?id=552c7700-11a1-11ed-0a80-0d830035fd8d",
        }
    },
}
```
### Order Agent
```python
{
    "meta": {
        "href": "https://online.moysklad.ru/api/remap/1.2/entity/counterparty/5b18e9bf-5a90-11ed-0a80-0702000cf4ff",
        "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/counterparty/metadata",
        "type": "counterparty",
        "mediaType": "application/json",
        "uuidHref": "https://online.moysklad.ru/app/#company/edit?id=5b18e9bf-5a90-11ed-0a80-0702000cf4ff",
    },
    "id": "5b18e9bf-5a90-11ed-0a80-0702000cf4ff",
    "accountId": "183531a8-1198-11ed-0a80-0f8600022ae1",
    "shared": False,
    "group": {
        "meta": {
            "href": "https://online.moysklad.ru/api/remap/1.2/entity/group/1835779e-1198-11ed-0a80-0f8600022ae2",
            "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/group/metadata",
            "type": "group",
            "mediaType": "application/json",
        }
    },
    "updated": "2022-11-02 12:25:56.794",
    "name": "тест",
    "externalCode": "3c4f419e8cd958690d0d14b3b89380d3",
    "archived": False,
    "created": "2022-11-02 12:25:56.794",
    "companyType": "individual",
    "email": "test2@gmail.com",
    "phone": "+7 (999) 999-99-99",
    "accounts": {
        "meta": {
            "href": "https://online.moysklad.ru/api/remap/1.2/entity/counterparty/5b18e9bf-5a90-11ed-0a80-0702000cf4ff/accounts",
            "type": "account",
            "mediaType": "application/json",
            "size": 0,
            "limit": 1000,
            "offset": 0,
        }
    },
    "tags": ["bright", "клиенты интернет-магазинов"],
    "notes": {
        "meta": {
            "href": "https://online.moysklad.ru/api/remap/1.2/entity/counterparty/5b18e9bf-5a90-11ed-0a80-0702000cf4ff/notes",
            "type": "note",
            "mediaType": "application/json",
            "size": 0,
            "limit": 1000,
            "offset": 0,
        }
    },
    "salesAmount": 0.0,
    "files": {
        "meta": {
            "href": "https://online.moysklad.ru/api/remap/1.2/entity/counterparty/5b18e9bf-5a90-11ed-0a80-0702000cf4ff/files",
            "type": "files",
            "mediaType": "application/json",
            "size": 0,
            "limit": 1000,
            "offset": 0,
        }
    },
}
```
### Order Store
```python
{
    "meta": {
        "href": "https://online.moysklad.ru/api/remap/1.2/entity/store/1b176643-1198-11ed-0a80-0929003359f7",
        "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/store/metadata",
        "type": "store",
        "mediaType": "application/json",
        "uuidHref": "https://online.moysklad.ru/app/#warehouse/edit?id=1b176643-1198-11ed-0a80-0929003359f7",
    },
    "id": "1b176643-1198-11ed-0a80-0929003359f7",
    "accountId": "183531a8-1198-11ed-0a80-0f8600022ae1",
    "owner": {
        "meta": {
            "href": "https://online.moysklad.ru/api/remap/1.2/entity/employee/1b01b5eb-1198-11ed-0a80-0929003359b3",
            "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/employee/metadata",
            "type": "employee",
            "mediaType": "application/json",
            "uuidHref": "https://online.moysklad.ru/app/#employee/edit?id=1b01b5eb-1198-11ed-0a80-0929003359b3",
        }
    },
    "shared": False,
    "group": {
        "meta": {
            "href": "https://online.moysklad.ru/api/remap/1.2/entity/group/1835779e-1198-11ed-0a80-0f8600022ae2",
            "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/group/metadata",
            "type": "group",
            "mediaType": "application/json",
        }
    },
    "updated": "2022-08-01 15:47:30.557",
    "name": "Основной склад",
    "externalCode": "PncICpNOhiQWZoaDUXZWS2",
    "archived": False,
    "pathName": "",
    "address": "",
}
```
### Order SalesChannel
```python
{
    "meta": {
        "href": "https://online.moysklad.ru/api/remap/1.2/entity/saleschannel/552c7700-11a1-11ed-0a80-0d830035fd8d",
        "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/saleschannel/metadata",
        "type": "saleschannel",
        "mediaType": "application/json",
        "uuidHref": "https://online.moysklad.ru/app/#saleschannel/edit?id=552c7700-11a1-11ed-0a80-0d830035fd8d",
    },
    "id": "552c7700-11a1-11ed-0a80-0d830035fd8d",
    "accountId": "183531a8-1198-11ed-0a80-0f8600022ae1",
    "owner": {
        "meta": {
            "href": "https://online.moysklad.ru/api/remap/1.2/entity/employee/1b01b5eb-1198-11ed-0a80-0929003359b3",
            "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/employee/metadata",
            "type": "employee",
            "mediaType": "application/json",
            "uuidHref": "https://online.moysklad.ru/app/#employee/edit?id=1b01b5eb-1198-11ed-0a80-0929003359b3",
        }
    },
    "shared": False,
    "group": {
        "meta": {
            "href": "https://online.moysklad.ru/api/remap/1.2/entity/group/1835779e-1198-11ed-0a80-0f8600022ae2",
            "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/group/metadata",
            "type": "group",
            "mediaType": "application/json",
        }
    },
    "updated": "2022-08-01 16:53:33.466",
    "name": "Bright",
    "externalCode": "-P10jXAwi0Oa93oyPhKMc1",
    "archived": False,
    "type": "ECOMMERCE",
}
```
### Order Organisation
```python
{
    "meta": {
        "href": "https://online.moysklad.ru/api/remap/1.2/entity/organization/1b154d06-1198-11ed-0a80-0929003359f5",
        "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/organization/metadata",
        "type": "organization",
        "mediaType": "application/json",
        "uuidHref": "https://online.moysklad.ru/app/#mycompany/edit?id=1b154d06-1198-11ed-0a80-0929003359f5",
    },
    "id": "1b154d06-1198-11ed-0a80-0929003359f5",
    "accountId": "183531a8-1198-11ed-0a80-0f8600022ae1",
    "owner": {
        "meta": {
            "href": "https://online.moysklad.ru/api/remap/1.2/entity/employee/1b01b5eb-1198-11ed-0a80-0929003359b3",
            "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/employee/metadata",
            "type": "employee",
            "mediaType": "application/json",
            "uuidHref": "https://online.moysklad.ru/app/#employee/edit?id=1b01b5eb-1198-11ed-0a80-0929003359b3",
        }
    },
    "shared": True,
    "group": {
        "meta": {
            "href": "https://online.moysklad.ru/api/remap/1.2/entity/group/1835779e-1198-11ed-0a80-0f8600022ae2",
            "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/group/metadata",
            "type": "group",
            "mediaType": "application/json",
        }
    },
    "updated": "2022-08-01 15:47:30.438",
    "name": "alexkirov",
    "externalCode": "7GBM60rLh5nZS4pQTKQH10",
    "archived": False,
    "created": "2022-08-01 15:47:30.438",
    "companyType": "legal",
    "legalTitle": "alexkirov",
    "email": "aleksey.m.kirov@gmail.com",
    "accounts": {
        "meta": {
            "href": "https://online.moysklad.ru/api/remap/1.2/entity/organization/1b154d06-1198-11ed-0a80-0929003359f5/accounts",
            "type": "account",
            "mediaType": "application/json",
            "size": 0,
            "limit": 1000,
            "offset": 0,
        }
    },
    "isEgaisEnable": False,
    "payerVat": True,
    "director": "Алексей",
    "directorPosition": "Руководитель организации или иное уполномоченное лицо",
    "chiefAccountant": "Алексей",
}
```
### Order State
```python
{
    "meta": {
        "href": "https://online.moysklad.ru/api/remap/1.2/entity/customerorder/metadata/states/1bb40525-1198-11ed-0a80-092900335a2b",
        "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/customerorder/metadata",
        "type": "state",
        "mediaType": "application/json",
    },
    "id": "1bb40525-1198-11ed-0a80-092900335a2b",
    "accountId": "183531a8-1198-11ed-0a80-0f8600022ae1",
    "name": "Новый",
    "color": 15106326,
    "stateType": "Regular",
    "entityType": "customerorder",
}
```
### Order Files
```python
{
    "context": {
        "employee": {
            "meta": {
                "href": "https://online.moysklad.ru/api/remap/1.2/context/employee",
                "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/employee/metadata",
                "type": "employee",
                "mediaType": "application/json",
            }
        }
    },
    "meta": {
        "href": "https://online.moysklad.ru/api/remap/1.2/entity/customerorder/5c5aba3a-5a90-11ed-0a80-0702000cf50b/files",
        "type": "files",
        "mediaType": "application/json",
        "size": 0,
        "limit": 1000,
        "offset": 0,
    },
    "rows": [],
}
```
### Order Positions
```python
{
    "context": {
        "employee": {
            "meta": {
                "href": "https://online.moysklad.ru/api/remap/1.2/context/employee",
                "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/employee/metadata",
                "type": "employee",
                "mediaType": "application/json",
            }
        }
    },
    "meta": {
        "href": "https://online.moysklad.ru/api/remap/1.2/entity/customerorder/5c5aba3a-5a90-11ed-0a80-0702000cf50b/positions",
        "type": "customerorderposition",
        "mediaType": "application/json",
        "size": 1,
        "limit": 1000,
        "offset": 0,
    },
    "rows": [
        {
            "meta": {
                "href": "https://online.moysklad.ru/api/remap/1.2/entity/customerorder/5c5aba3a-5a90-11ed-0a80-0702000cf50b/positions/5c5ac522-5a90-11ed-0a80-0702000cf50c",
                "type": "customerorderposition",
                "mediaType": "application/json",
            },
            "id": "5c5ac522-5a90-11ed-0a80-0702000cf50c",
            "accountId": "183531a8-1198-11ed-0a80-0f8600022ae1",
            "quantity": 1.0,
            "price": 288000.0,
            "discount": 0.0,
            "vat": 0,
            "vatEnabled": False,
            "assortment": {
                "meta": {
                    "href": "https://online.moysklad.ru/api/remap/1.2/entity/product/6b06f83a-59b8-11ed-0a80-03d4000d2a98",
                    "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/product/metadata",
                    "type": "product",
                    "mediaType": "application/json",
                    "uuidHref": "https://online.moysklad.ru/app/#good/edit?id=6b06ec34-59b8-11ed-0a80-03d4000d2a96",
                }
            },
            "shipped": 0.0,
            "reserve": 0,
        }
    ],
}
```
### Position Assortment Product
```python
{
    "meta": {
        "href": "https://online.moysklad.ru/api/remap/1.2/entity/product/6b06f83a-59b8-11ed-0a80-03d4000d2a98",
        "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/product/metadata",
        "type": "product",
        "mediaType": "application/json",
        "uuidHref": "https://online.moysklad.ru/app/#good/edit?id=6b06ec34-59b8-11ed-0a80-03d4000d2a96",
    },
    "id": "6b06f83a-59b8-11ed-0a80-03d4000d2a98",
    "accountId": "183531a8-1198-11ed-0a80-0f8600022ae1",
    "shared": True,
    "group": {
        "meta": {
            "href": "https://online.moysklad.ru/api/remap/1.2/entity/group/1835779e-1198-11ed-0a80-0f8600022ae2",
            "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/group/metadata",
            "type": "group",
            "mediaType": "application/json",
        }
    },
    "updated": "2022-11-02 11:43:49.011",
    "name": "Skin Regimen Cleansing Cream / Крем Очищающий",
    "code": "4",
    "externalCode": "bygtrcUd5ca9jIfZBxEo",
    "archived": False,
    "pathName": "Товары интернет-магазинов/Bright",
    "productFolder": {
        "meta": {
            "href": "https://online.moysklad.ru/api/remap/1.2/entity/productfolder/0ca17216-59b3-11ed-0a80-0bde000f3d96",
            "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/productfolder/metadata",
            "type": "productfolder",
            "mediaType": "application/json",
            "uuidHref": "https://online.moysklad.ru/app/#good/edit?id=0ca17216-59b3-11ed-0a80-0bde000f3d96",
        }
    },
    "useParentVat": True,
    "uom": {
        "meta": {
            "href": "https://online.moysklad.ru/api/remap/1.2/entity/uom/19f1edc0-fc42-4001-94cb-c9ec9c62ec10",
            "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/uom/metadata",
            "type": "uom",
            "mediaType": "application/json",
        }
    },
    "images": {
        "meta": {
            "href": "https://online.moysklad.ru/api/remap/1.2/entity/product/6b06f83a-59b8-11ed-0a80-03d4000d2a98/images",
            "type": "image",
            "mediaType": "application/json",
            "size": 0,
            "limit": 1000,
            "offset": 0,
        }
    },
    "minPrice": {
        "value": 0.0,
        "currency": {
            "meta": {
                "href": "https://online.moysklad.ru/api/remap/1.2/entity/currency/1b178e47-1198-11ed-0a80-0929003359fc",
                "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/currency/metadata",
                "type": "currency",
                "mediaType": "application/json",
                "uuidHref": "https://online.moysklad.ru/app/#currency/edit?id=1b178e47-1198-11ed-0a80-0929003359fc",
            }
        },
    },
    "salePrices": [
        {
            "value": 288000.0,
            "currency": {
                "meta": {
                    "href": "https://online.moysklad.ru/api/remap/1.2/entity/currency/1b178e47-1198-11ed-0a80-0929003359fc",
                    "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/currency/metadata",
                    "type": "currency",
                    "mediaType": "application/json",
                    "uuidHref": "https://online.moysklad.ru/app/#currency/edit?id=1b178e47-1198-11ed-0a80-0929003359fc",
                }
            },
            "priceType": {
                "meta": {
                    "href": "https://online.moysklad.ru/api/remap/1.2/context/companysettings/pricetype/1b184737-1198-11ed-0a80-0929003359fd",
                    "type": "pricetype",
                    "mediaType": "application/json",
                },
                "id": "1b184737-1198-11ed-0a80-0929003359fd",
                "name": "Цена продажи",
                "externalCode": "cbcf493b-55bc-11d9-848a-00112f43529a",
            },
        }
    ],
    "buyPrice": {
        "value": 0.0,
        "currency": {
            "meta": {
                "href": "https://online.moysklad.ru/api/remap/1.2/entity/currency/1b178e47-1198-11ed-0a80-0929003359fc",
                "metadataHref": "https://online.moysklad.ru/api/remap/1.2/entity/currency/metadata",
                "type": "currency",
                "mediaType": "application/json",
                "uuidHref": "https://online.moysklad.ru/app/#currency/edit?id=1b178e47-1198-11ed-0a80-0929003359fc",
            }
        },
    },
    "barcodes": [{"ean13": "2000000000114"}],
    "paymentItemType": "GOOD",
    "discountProhibited": False,
    "article": "12268",
    "weight": 0.0,
    "volume": 0.0,
    "variantsCount": 0,
    "isSerialTrackable": False,
    "trackingType": "NOT_TRACKED",
    "files": {
        "meta": {
            "href": "https://online.moysklad.ru/api/remap/1.2/entity/product/6b06f83a-59b8-11ed-0a80-03d4000d2a98/files",
            "type": "files",
            "mediaType": "application/json",
            "size": 0,
            "limit": 1000,
            "offset": 0,
        }
    },
}
```