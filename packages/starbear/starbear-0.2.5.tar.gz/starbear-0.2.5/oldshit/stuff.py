import webbrowser
from pathlib import Path

import uvicorn
from hrepr import H
from hrepr.resource import JSFunction, Resource
from starlette.applications import Starlette

from starbear import Queue, bear

here = Path(__file__).parent


@bear("/demo1")
async def app1(page):
    page.print(
        H.form(
            H.span("", id="prompt"),
            " ",
            H.input(name="val", autocomplete="off"),
            hx_ws="send",
            id="the_form",
        )
    )

    page["#prompt"].set("What is your name?")
    name = (await page.recv())["val"]

    page["#prompt"].set("What is your favorite color?")
    color = (await page.recv())["val"]

    page["#the_form"].clear()
    page.print(H.b(name, style=f"color:{color}"))


@bear("/demo2")
async def app2(page):
    def click(evt):
        page["#box"].set(evt)

    page["head"].print(H.link(rel="stylesheet", href=Path("moldule/style.css")))
    page.print(H.div["moldy"](H.div("Hello"), H.button("Click me", onclick=click)))
    page.print(H.div(id="box"))
    page.print(
        H.button(
            "Click me too!",
            id="coolbeans",
            __constructor={
                "module": here / "moldule" / "indirect.js",
                "options": {"increment": 5, "callback": lambda x: print(x)},
            },
        )
    )


@bear("/demo3")
async def app3(page):
    page["head"].print(
        H.link(rel="stylesheet", href=here / "tip" / "light.css"),
    )
    page["head"].print(
        H.link(rel="stylesheet", href=here / "tip" / "tippy.css"),
    )
    page.print(
        H.span(
            "Helloes!",
            __constructor={
                # "module": here / "tip" / "tippy.js",
                # "module": "https://unpkg.com/tippy.js@5.2.1/dist/tippy.esm.js",
                "module": "https://esm.sh/tippy.js",
                "options": {"content": "stuff"},
            },
        )
    )


@bear("/txt")
async def app4(page):
    page.print(
        H.div(
            H.div(
                style="width:800px;height:500px;border:3px solid red;",
                contenteditable=True,
                __constructor={
                    "module": here / "mon" / "main.js",
                    "options": {
                        "value": "def f(x):\n    return x * x",
                        "language": "python",
                    },
                },
            )
        )
    )


@bear("/spl")
async def app5(page):
    page.print(
        H.div(
            H.div(
                __constructor={
                    "module": here / "spl" / "main.js",
                    "arguments": {
                        "columnGutters": [
                            {
                                "track": 1,
                                "element": gutter_left,
                            },
                            {
                                "track": 3,
                                "element": gutter_right,
                            },
                        ]
                    },
                }
            )
        )
    )


@bear("/edit")
async def app6(page):
    result_box = H.div.autoid()

    def save(value):
        print(value)
        g = {}
        exec(value, g, g)
        result = g["f"](10)
        print(result)
        page[result_box].set(H.div(result))
        return True

    def commit(value):
        pass

    def update(value):
        return save(value)

    page.print(
        H.div(
            H.div(
                __constructor={
                    "module": here / "mon" / "main.js",
                    "options": {
                        "filename": "<live>",
                        "content": {
                            "live": "def f(x):\n    return x * x",
                            "saved": "def f(x):\n    return x * x",
                        },
                        "callbacks": {
                            "save": save,
                            "commit": commit,
                            "update": update,
                        },
                    },
                }
            ),
            result_box,
        )
    )


@bear("/wack")
async def app7(page):
    async def clicky(evt):
        result = await page[thing].call.wooper(10)
        page[thing].print(result)

    button = H.button(
        "Clicky!",
        onclick=clicky,
    )

    thing = H.div(
        "hello", __constructor={"module": here / "moldule" / "wack.js", "options": {"x": 1}}
    ).autoid()

    page.print(
        H.div(
            button,
            thing,
        )
    )


@bear("/plotly")
async def app8(page):
    plot = H.div(
        __constructor={
            "script": "https://cdn.plot.ly/plotly-2.16.1.min.js",
            "symbol": "Plotly.newPlot",
            "arguments": [
                H.self(),
                [{"x": [1, 2, 3, 4, 5], "y": [1, 2, 4, 8, 16]}],
                {"margin": {"t": 0}},
            ],
        }
    )
    page.print(H.div["#thing"](style="border:1px solid red"))
    page["#thing"].print(plot)
    # await page[plot].do.on("plotly_click", lambda *args: print(args))

    async def dostuff(x, y):
        page.print((x, y))

    await page[plot].do.on(
        "plotly_click",
        # dostuff,
        JSFunction(
            argnames=["value"],
            code=f"console.log(value);data=value.points[0];x=data.x;y=data.y;{Resource(dostuff)}(x, y);",
        ),
    )


@bear("/rogue")
async def app9(page):
    q = Queue()
    page.print(H.div(H.button("Heyox!", onclick=q.tag("button")), H.input(oninput=q.tag("input"))))

    value = await q.get()
    page.print(H.div("AYE"))
    page.print(value)

    value = await q.get()
    page.print(H.div("COOL BEANS"))
    page.print(value)

    value = await q.get()
    page.print(H.div("grog"))
    page.print(value)

    value = await q.get()
    page.print(H.div("more!"))
    page.print(value)


@bear
async def zapp(page):
    page.print(H.b("hello!"))


app = Starlette(
    routes=[app2, app4, app5, app6, app7, app8, app9],
)
if __name__ == "__main__":
    host = "127.0.0.1"
    port = 5001
    appname = "rogue"
    webbrowser.open(f"http://{host}:{port}/{appname}")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")

    # require(["scripts/repl", "lib/split-grid.min"], (repl, Split) => {
    #     // Set up split screen
    #     let main = document.getElementById("main");
    #     let width = Math.min(800, main.offsetWidth - 40);
    #     main.style["grid-template-columns"] = `1fr 10px ${width}px 10px 1fr`;
    #     Split({
    #         columnGutters: [
    #             {
    #                 track: 1,
    #                 element: document.querySelector("#snek-gutter-left"),
    #             },
    #             {
    #                 track: 3,
    #                 element: document.querySelector("#snek-gutter-right"),
    #             }
    #         ]
    #     })

    #     let the_repl = new repl.Repl(main);
    #     the_repl.connect();
    #     the_repl.editor.focus();
    # });

    # <div id="main">
    #     <div id="snek-pin-pane-left" class="snek-pin-pane"></div>
    #     <div id="snek-gutter-left" class="gutter gutter-horizontal"></div>
    #     <div id="snek-interactor" class="snek-interactor">
    #         <div class="snek-outer-pane">
    #             <div class="snek-pane"></div>
    #         </div>
    #         <div class="snek-input-box">
    #             <div class="snek-input-mode"></div>
    #             <div class="snek-input"></div>
    #         </div>
    #         <div class="snek-nav">
    #         </div>
    #         <div class="snek-status-bar">
    #         </div>
    #     </div>
    #     <div id="snek-gutter-right" class="gutter gutter-horizontal"></div>
    #     <div id="snek-pin-pane-right" class="snek-pin-pane"></div>
    # </div>

# """
# a b c
# a d c
# """

# Grid(
#     template="""
#         a|bbbb|c
#         a|bbbb|c
#         a|bbbb|c
#         a|xxxx|c
#     """,
#     a=sidebar_left,
#     b=main,
#     c=sidebar_right,
#     x=repl,
# )

# """
# a|b|c
# a|b|c
# a|x|c
# """
