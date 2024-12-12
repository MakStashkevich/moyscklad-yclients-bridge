# Мост между сервисами Moyscklad и YClients

Задача бизнеса: синхронизировать товары из Moysclad с YClients

Решение: небольшой скрипт для автоматической синхронизации товаров на Python используя API обоих сервисов

## Как использовать?

1. Скачайте скрипт командой

`git clone git@github.com:MakStashkevich/moyscklad-yclients-bridge.git`

2. Откройте папку со скриптом

`cd moyscklad-yclients-bridge`

3. Запустите установочник Docker

`chmod +x ./scripts/init_docker_engine.sh && ./scripts/init_docker_engine.sh`

4. Скопируйте файл настроек

`cp .env.example .env`

... и введите настройки своих аккаунтов и айпи адрес сервера в новом файле `.env`

5. Запустите скрипт

`chmod +x push.sh && ./push.sh`

<b>Вот и все.</b> Хорошая работа!

<b>P.S.</b> По адресу указанному в настройках WEBSERVER_HOST можно открыть страницу для ручной синхронизации данных

---

## Есть вопросы или задача, которую нужно решить?

Пишите мне любым из возможных способов, везде отвечу.

Почта: makstashkevich@gmail.com

VK: [@makstashkevich](https://vk.me/makstashkevich)

![small-filled-telegram](https://raw.githubusercontent.com/CLorant/readme-social-icons/main/small/filled/telegram.svg) Telegram: [@stashkevich](https://t.me/stashkevich)

![small-filled-instagram](https://raw.githubusercontent.com/CLorant/readme-social-icons/main/small/filled/instagram.svg) Instagram: [@makstashkevich](https://instagram.com/makstashkevich)