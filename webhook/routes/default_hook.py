import logging
from json import JSONDecodeError

from aiohttp import web
from aiohttp.abc import BaseRequest

_logger = logging.getLogger(__name__)

routes = web.RouteTableDef()


@routes.get('/')
async def handle_default(request: BaseRequest):
    title = "Sync Bridge Moyscklad & YClients"
    button_handler = """
    const title = document.getElementById('sync_title');
    const button = document.getElementById('sync_button');
    button.addEventListener('click', async _ => {
        button.hidden = true;
        button.style.display = 'none';
        try {
            title.style = "color: blue";
            title.textContent = "Синхронизация... Подождите минутку...";
            const response = await fetch('/yclients/sync/', {
                method: 'post',
                body: {}
            });
            console.log('Completed!', response);
            data = await response.json()
            if (data && data.color && data.text) {
                title.style = `color: ${data.color}`;
                title.textContent = data.text;
            } else {
                title.style = "color: red";
                title.textContent = "Ошибка! Данные не были получены...";
            }
        } catch(err) {
            console.error(`Error: ${err}`);
            title.style = "color: red";
            title.textContent = err;
        }
    });
    """
    button_style = """
    button {
        background-color: #4CAF50;
        border: none;
        color: white;
        padding: 15px 32px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
    }
    """

    return html_response(text=f"""
    <html>
        <head>
            <title>{title}</title>
            <style>{button_style}</style>
        </head>
        <body>
            <h1>{title}</h1>
            <div id="sync">
                <h3 id="sync_title">Нажав на кнопку ниже вы принудительно запустите процесс синхронизации товаров YClients с МойСклад.</h3>
                <button id="sync_button">Запустить синхронизацию</button>
                <p>По поводу любых проблем пишите разработчику в <a href='https://t.me/makstashkevich'>Telegram</a> или на прямой адрес электронной почты <a href='mailto:makstashkevich@gmail.com'>makstashkevich@gmail.com</a></p>
            </div>
            <script>{button_handler}</script>
        </body>
    </html>
    """)


def html_response(text):
    return web.Response(text=text, content_type='text/html')


async def get_json_response(request: BaseRequest) -> dict:
    try:
        response = await request.json()
    except JSONDecodeError:
        response = {}

    return response
