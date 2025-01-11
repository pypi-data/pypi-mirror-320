import uvicorn
from hrepr import H
from spacebear.serve import bear
from starlette.applications import Starlette

style = H.style("""
.red {
    color: red;
}
.box {
    border: 1px solid black;
    padding: 5px;
    margin: 5px;
}
#response {
    background: #ff8;
}
#sky {
    background: #8ff;
}
""")


@bear("/thing")
async def app(page):
    page["head"].print(style)
    page.print(H.div["box"]("hello!", id="sky"))
    page.print(H.div["box"](id="response"))

    page.print(H.div(H.button("One", onclick=page["#response"].print)))

    page.print(H.div(H.button("Two", onclick=lambda event: page.print(H.b("x")))))

    page.print(H.div(H.form(H.input(name="value"), hx_ws="send")))

    i = 0
    while True:
        i += 1
        msg = await page.recv()
        page["#response"].set(msg["value"] * i)


if __name__ == "__main__":
    app = Starlette(routes=[app])
    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="info")
