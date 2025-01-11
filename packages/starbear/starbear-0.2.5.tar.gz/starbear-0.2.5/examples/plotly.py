import asyncio
import math

from starbear import ClientWrap, H, Queue, bear


@bear
async def simple(page):
    plot = H.div(
        __constructor={
            "script": "https://cdn.plot.ly/plotly-2.16.1.min.js",
            "symbol": "Plotly.newPlot",
            "arguments": [
                H.self(),
                [
                    {
                        "x": [],
                        "y": [],
                    }
                ],
                {"margin": {"t": 0}},
            ],
        }
    )
    page.print(plot)
    await page[plot].js

    for i in range(100):
        await asyncio.sleep(0.1)
        await page.js.Plotly.extendTraces(plot, {"x": [[i]], "y": [[math.sin(i / 10)]]}, [0])


@bear
async def prompt(page):
    q = ClientWrap(Queue(), debounce=0.5, form=True)

    xs = list(range(100))

    def refresh(params):
        code = params["code"]
        if not isinstance(code, str):
            code = code["value"]

        xs = list(range(int(params["xmin"]), int(params["xmax"])))
        ys = [eval(code, {"x": x, "math": math}) for x in xs]

        plot = H.div(
            __constructor={
                "script": "https://cdn.plot.ly/plotly-2.16.1.min.js",
                "symbol": "Plotly.newPlot",
                "arguments": [
                    H.self(),
                    [
                        {
                            "x": xs,
                            "y": ys,
                        }
                    ],
                    {"margin": {"t": 0}},
                ],
            }
        )
        page[plotarea].set(plot)

    initial_params = {
        "xmin": page.query_params.get("xmin", 0),
        "xmax": 100,
        "step": 0.1,
        "code": "math.sin(x / 10)",
    }
    page.print(
        H.form(
            H.h2("Parameters"),
            H.div(
                "xmin",
                H.input(name="xmin", value=initial_params["xmin"], type="number", oninput=q),
                "xmax",
                H.input(name="xmax", value=initial_params["xmax"], type="number", oninput=q),
                "step",
                H.input(
                    name="step", value=initial_params["step"], type="number", step="0.1", oninput=q
                ),
            ),
            H.h2("Code"),
            H.textarea(initial_params["code"], name="code", oninput=q),
        ),
        H.h2("Plot"),
        plotarea := H.div().autoid(),
        errors := H.div().autoid(),
    )

    refresh(initial_params)
    async for x in q:
        try:
            refresh(x)
            page[errors].set("")
        except Exception as e:
            page[errors].set(e)

    # refresh(initial_code)

    # page["#thing"].print(plot)
    # await page[plot].do.on("plotly_click", lambda *args: print(args))

    # async def dostuff(x, y):
    #     page.print((x, y))

    # await page[plot].do.on(
    #     "plotly_click",
    #     # dostuff,
    #     JSFunction(
    #         argnames=["value"],
    #         code=f"console.log(value);data=value.points[0];x=data.x;y=data.y;{Resource(dostuff)}(x, y);"
    #     )
    # )
