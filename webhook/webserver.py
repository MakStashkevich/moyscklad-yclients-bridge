import logging
from hashlib import sha256

from aiohttp import web
from aiohttp_session import setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from settings import get_webserver_settings
from webhook.routes import routes

_logger = logging.getLogger(__name__)


def get_web_app():
    app = web.Application()
    setup_web_session(app)
    app.add_routes(routes)
    return app


def setup_web_session(app):
    session_secret_hash = sha256(get_webserver_settings().webserver_session_secret.encode()).digest()
    storage = EncryptedCookieStorage(session_secret_hash)
    setup(app, storage)


async def connect():
    settings = get_webserver_settings()
    host = settings.webserver_host
    port = settings.webserver_port
    app = get_web_app()

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, host="127.0.0.1", port=port)
    await site.start()

    _logger.info(f'Webhook server loaded on http://{host}:{port}')
