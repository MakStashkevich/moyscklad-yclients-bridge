from .yclients_hook import routes as yclients_routes
from .moyscklad_hook import routes as moyscklad_routes

routes = [
    *yclients_routes,
    *moyscklad_routes,
]