import aiohttp
from aiohttp import web, WSCloseCode
import asyncio
import multidict

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    
    await ws.prepare(request)
    await ws.send_str('hi joey') 

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == 'close':
                await ws.close()
            else:
                await ws.send_str('some websocket message payload')
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print('ws connection closed with exception %s' % ws.exception())
            return ws
        
async def start_server(host="", port=8888):
    ## xx - path
    f = open('display.js', 'r')
    bridge = f.read()
    f.close()
    
    async def http_handler(request):
        return web.Response(text=bridge,
                            headers=multidict.MultiDict(
                                {'Content-Type': 'text/html'}))
    
    app = web.Application()
    app.add_routes([
        web.get('/',   http_handler),
        web.get('/ws', websocket_handler),
    ])
    runner = web.AppRunner(app)

    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
            
            
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server())
    loop.run_forever()
    
