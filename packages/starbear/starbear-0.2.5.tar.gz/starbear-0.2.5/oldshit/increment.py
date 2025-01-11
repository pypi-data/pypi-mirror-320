from hrepr import H

from starbear import Queue, bear

# @bear
# async def app(page):
#     page["head"].print(
#         H.link(rel="stylesheet", href=Path("path/to/style.css"))
#     )

#     n = 0
#     def increment(event):
#         nonlocal n
#         n += 1
#         page[target].set(str(n))

#     page.print(
#         H.button("Click me!", onclick=increment),
#         H.div(
#             target := H.span("0").autoid(),
#             " clicks"
#         )
#     )


@bear
async def app(page):
    q = Queue()
    page.print(H.button("Click me!", onclick=q), H.div(target := H.span("0").autoid(), " clicks"))
    i = 0
    async for event in q:
        i += 1
        page[target].set(str(i))


@bear
async def todo(page):
    q = Queue()
    tasks = [
        "hello",
        "world",
    ]
    page.print(
        H.div(
            "New task: ",
            H.input(oninput=q.tag("newtask"), onsubmit=q.tag("add")),
            H.button("Add", onclick=q.tag("add")),
        ),
        taskelem := H.div().autoid(),
    )

    def showtasks():
        page[taskelem].clear()
        for i, task in enumerate(tasks):
            page[taskelem].print(H.div(H.input(type="checkbox", onclick=q.tag(str(i))), task))

    showtasks()

    newtask = ""
    async for event in q:
        if event.tag == "newtask":
            newtask = event.arg["value"]
        elif event.tag == "add":
            tasks.append(newtask)
            showtasks()
        else:
            idx = int(event.tag)
            del tasks[idx]
            showtasks()


@bear
async def form(page):
    q = Queue()
    page.print(
        H.form(
            H.input(name="wow"),
            H.input(type="checkbox", name="rocking"),
            H.input(type="date", name="moment"),
            H.input(type="file", name="neat"),
            H.input(type="radio", name="radical", value="A!"),
            H.input(type="radio", name="radical", value="B!"),
            H.select(
                H.option("Volvo", value="volvo"),
                H.option("Saab", value="saab"),
                H.option("Mercedes", value="mercedes"),
                H.option("Audi", value="audi"),
                name="cars",
            ),
            H.button("go", hidden=True),
            onsubmit=page.print,
        )
    )
