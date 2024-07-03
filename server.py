from aiohttp import web
from auth import fetch_token, user_flows

async def handle_callback(request):
    params = request.rel_url.query
    state = params.get('state')
    code = params.get('code')

    if not state or not code:
        return web.Response(text="Missing state or code", status=400)

    for user_id, (flow, stored_state) in user_flows.items():
        if stored_state == state:
            if fetch_token(user_id, state, code):
                bot = request.app['bot']
                await bot.send_message(user_id, "Авторизация прошла успешно!")
                break

    return web.Response(text="Авторизация прошла успешно, вернитесь в Telegram.")

async def start_webhook(dp, bot):
    app = web.Application()
    app['bot'] = bot
    app.router.add_get('/callback', handle_callback)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8000)
    await site.start()
