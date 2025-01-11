from starlette.applications import Starlette
from starlette.responses import (
    HTMLResponse,
)
from starlette.routing import Mount, Route, WebSocketRoute
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocket

page = """
<html>
<head>
    <title>TEST</title>
</head>

<body>
    <b>hello</b>
    <div style="background:cyan;padding:10px;">
        <div id="wooper" style="background:yellow;">
            existing
        </div>
    </div>
    <script type="module">
        import { quack } from "/assets/bearlib.js";
        quack();
    </script>
</body>

</html>
"""


async def main(request):
    return HTMLResponse(page)


# <b><script>console.log('hello!!')</script>B</b><script>console.log('corbol.')</script>


async def sock(ws: WebSocket):
    await ws.accept()
    await ws.send_json(
        {
            "command": "put",
            "selector": "#wooper",
            "method": "beforeend",
            "content": "<div>wow that's cool!</div>",
        }
    )
    await ws.send_json(
        {
            "command": "put",
            "selector": "#wooper",
            "method": "beforeend",
            "content": """<b>0</b>
            <b>1</b>
            2
            <b>3</b>
        """,
        }
    )
    await ws.send_json(
        {
            "command": "eval",
            "selector": "#wooper",
            "code": """
            console.log("wow!", this)
        """,
        }
    )
    print(await ws.receive_json())
    print(await ws.receive_json())
    # await ws.close(code=3001, reason="Done")

    # async def recv():
    #     while True:
    #         try:
    #             data = await ws.receive_json()
    #             self.iq.put_nowait(data)
    #         except WebSocketDisconnect:
    #             break

    # async def send():
    #     while True:
    #         txt, in_history = await self.oq.get()
    #         try:
    #             await ws.send_text(txt)
    #             if in_history:
    #                 self.history.append(txt)
    #         except RuntimeError:
    #             # Put the unsent element back into the queue
    #             self.oq.putleft((txt, in_history))
    #             break

    # if self.ws:
    #     try:
    #         await self.ws.close()
    #     except RuntimeError:
    #         pass

    # await ws.accept()
    # self.ws = ws

    # if self.reset:
    #     for entry in self.history:
    #         await ws.send_text(entry)
    #     self.reset = False

    # await aio.wait(
    #     [aio.create_task(recv()), aio.create_task(send())],
    #     return_when=aio.FIRST_COMPLETED,
    # )


app = Starlette(
    debug=True,
    routes=[
        Route("/", main),
        WebSocketRoute("/socket", sock),
        Mount("/assets", app=StaticFiles(directory="."), name="static"),
    ],
)
