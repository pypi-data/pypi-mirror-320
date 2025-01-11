import asyncio
from pathlib import Path

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
#bouh {
    background: #8ff;
}
""")


# h3>
#   Search Contacts
#   <span class="htmx-indicator">
#     <img src="/img/bars.svg"/> Searching...
#    </span>
# </h3>
# <input class="form-control" type="search"
#        name="search" placeholder="Begin Typing To Search Users..."
#        hx-get="/search"
#        hx-trigger="keyup changed delay:500ms, search"
#        hx-target="#search-results"
#        hx-indicator=".htmx-indicator">

# <table class="table">
#     <thead>
#     <tr>
#       <th>First Name</th>
#       <th>Last Name</th>
#       <th>Email</th>
#     </tr>
#     </thead>
#     <tbody id="search-results">
#     </tbody>
# </table>


# @bear("/search")
# async def sch(page):
#     def searchit(*args):
#         print(args)

#     page.print(
#         H.div(
#             H.h3(
#                 "Search contacts",
#                 H.span["htmx-indicator"]("Searching...")
#             ),
#             H.input["form-control"](
#                 type="search",
#                 name="search",
#                 placeholder="Begin typing...",
#                 hx_get=searchit,
#                 hx_trigger="keyup changed delay:500ms, search",
#                 hx_target="#search-results",
#                 hx_indicator=".htmx-indicator",
#             ),
#             H.table["table"](
#                 H.thead(
#                     H.tr(
#                         H.th("Name"),
#                         H.th("Job"),
#                     )
#                 ),
#                 H.tbody(id="search-results")
#             )
#         )
#     )


@bear("/bowwow0")
async def app(page):
    page["head"].print(style)

    page.print(H.a("hello", z="wow"))

    page.print(H.div["box"]("hello!", id="response"))

    # page.print(H.button("Click me one", hx_ws="send", hx_trigger="click", name="babanix"))

    # # for i in range(100):
    # #     await asyncio.sleep(1)
    # #     page.print(H.div["box"](i))

    # page.print(
    #     H.form(
    #         H.button("Click me too", name="bobino"),
    #         H.input(name="crackpipe"),
    #         hx_ws="send"
    #     )
    # )

    # # def quackers():
    # #     page.print(H.div["red"]("quack"))

    # page.print(
    #     H.button("Radical", onclick=lambda event: page.print(event))
    # )

    async def ticktock(_):
        for i in range(5):
            await asyncio.sleep(0.5)
            page.print(H.div["box"](i))

    page.print(H.button("Radical", onclick=ticktock))

    while True:
        msg = await page.recv()
        page["#response"].set(msg)


entries = [
    ("Alice", "Baker"),
    ("Bernard", "Banker"),
    ("Charlotte", "Engineer"),
]


# @bear("/bowwow")
# async def app(page):
#     async def searchit(*args, search):
#         # await asyncio.sleep(1)
#         # return H.b("Hey hey, ", search)
#         results = H.raw()
#         for name, prof in entries:
#             if search in name:
#                 results = results(H.tr(H.td(name), H.td(prof)))
#         return results

#     page.print(
#         H.div(
#             H.h3(
#                 "Search contacts",
#                 H.span["htmx-indicator"]("Searching...")
#             ),
#             H.input["form-control"](
#                 type="search",
#                 name="search",
#                 placeholder="Begin typing...",
#                 hx_get=searchit,
#                 hx_trigger="keyup changed delay:500ms, search",
#                 hx_target="#search-results",
#                 hx_indicator=".htmx-indicator",
#             ),
#             H.table["table"](
#                 H.thead(
#                     H.tr(
#                         H.th("Name"),
#                         H.th("Job"),
#                     )
#                 ),
#                 H.tbody(id="search-results")
#             )
#         )
#     )


@bear("/bowwow")
async def app(page):
    page.print(H.link(rel="stylesheet", href=Path("moldule/style.css")))
    page.print(H.div["moldy"]("testotron"))


if __name__ == "__main__":
    app = Starlette(routes=[app])
    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="info")
