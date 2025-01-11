import time

import uvicorn
from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.routing import Route, WebSocketRoute


async def homepage(request):
    if request.query_params:
        raise Exception("fuck this")
    with open("template.html") as tpf:
        return HTMLResponse(tpf.read())


async def about(request):
    return HTMLResponse("<b>BOUHOUHOU!</b>")


async def feves(websocket):
    await websocket.accept()
    while True:
        resp = await websocket.receive_json()
        txt = resp["chat_message"]
        print(txt)
        time.sleep(1)
        await websocket.send_text(f'<div id="gourgane">Huh? What is {txt}?</div>')
    await websocket.close()


routes = [
    Route("/", endpoint=homepage),
    Route("/about", endpoint=about),
    WebSocketRoute("/feves", endpoint=feves),
]

app = Starlette(routes=routes)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="info")
