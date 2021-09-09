from aiohttp import web
from thingsboard_gateway.web.routes import setup_routes
import aiohttp_cors


async def run_http_server():
    app = web.Application()
    setup_routes(app)
    add_routes_to_cors(app)
    # 以下代码阻塞
    # web.run_app(app)
    runner = web.AppRunner(app)
    await runner.setup()
    # TBD 动态获取ip
    site = web.TCPSite(runner, '10.4.2.207', 8077)
    await site.start()


def add_routes_to_cors(app):
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=False,
            expose_headers="*",
            allow_headers="*",
        )
    })

    for route in list(app.router.routes()):
        cors.add(route)


