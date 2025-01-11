from pathlib import Path

import uvicorn
from hrepr import H
from starlette.applications import Starlette
from starlette.routing import Mount

from starbear import bear


@bear
async def allo(page):
    page.print(H.link(rel="stylesheet", href=Path("moldule/style.css")))
    page.print(H.div["moldy"](H.b("allo")))


@bear
async def boop(page):
    page.print(H.link(rel="stylesheet", href=Path("moldule/style.css")))
    page.print(H.div["moldy"](H.b("boop!")))


if __name__ == "__main__":
    app = Starlette(
        routes=[
            Mount("/allo", allo),
            Mount("/boop", boop),
        ]
    )
    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="info")


# @bear("/allo")
# async def allo(page):
#     page.print(
#         H.link(rel="stylesheet", href=Path("moldule/style.css"))
#     )
#     page.print(
#         H.div["moldy"](
#             H.b("allo")
#         )
#     )

# @bear("/boop")
# async def boop(page):
#     page.print(
#         H.link(rel="stylesheet", href=Path("moldule/style.css"))
#     )
#     page.print(
#         H.div["moldy"](
#             H.b("boop!")
#         )
#     )


# if __name__ == "__main__":
#     app = Starlette(routes=[allo, boop])
#     uvicorn.run(app, host="127.0.0.1", port=5000, log_level="info")
