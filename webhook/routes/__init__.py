from .default_hook import routes as default_routes
from .moyscklad_hook import routes as moyscklad_routes
from .yclients_hook import routes as yclients_routes

routes = [
    *default_routes,
    *yclients_routes,
    *moyscklad_routes,
]
