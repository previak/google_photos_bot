from aiohttp import web
from app.service import fetch_token
from app.database.requests import get_tg_id_by_state


async def handle_callback(request):
    params = request.rel_url.query
    state = params.get('state')
    code = params.get('code')

    if not state or not code:
        return web.Response(text="Missing state or code", status=400)

    tg_id = await get_tg_id_by_state(state)

    if await fetch_token(tg_id, state, code):
        bot = request.app['bot']
        await bot.send_message(tg_id, "Авторизация прошла успешно!")

    return web.Response(text="Авторизация прошла успешно, вернитесь в Telegram.")


async def start_webhook(dp, bot):
    app = web.Application()
    app['bot'] = bot
    app.router.add_get('/callback', handle_callback)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8000)
    await site.start()
