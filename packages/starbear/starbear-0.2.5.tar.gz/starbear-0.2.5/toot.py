import asyncio
from dataclasses import dataclass
from pathlib import Path

from hrepr import H

from starbear import Reference
from starbear.serve import bear
from starbear.utils import FeedbackQueue

here = Path(__file__).parent


@dataclass
class Point:
    x: int
    y: int


def zo(evt):
    return 1 / 0


@bear(template_params={"title": "toot"})
async def app(page):
    # q = FeedbackQueue().wrap(toggles="loading", form=True)
    q = FeedbackQueue()

    # for i in range(100):
    #     await asyncio.sleep(0.5)
    #     page.log(H.div(i, style="border:1px solid green;margin:10px;padding:10px;"))

    # return

    page.add_resources(
        Path("style.css"),
        "mila.ico",
    )

    # for i in range(10):
    #     page.print(H.button(i, __ref=Reference([i])))
    #     # page.print(H.button(i, onclick=zo))

    page["body"].template(here / "templatou.html", q=q)

    async for event in q:
        page["#boxy"].print(event)

    return

    # async def wait(_):
    #     await asyncio.sleep(2)
    #     page.print("done.")

    # async def wait2(_):
    #     await page.window.console.log("hello!")
    #     await page[thing].toggle("loading", True)
    #     await asyncio.sleep(2)
    #     page.print("donezo!")
    #     await page[thing].toggle("loading", False)

    # page.print("hiya?")

    # thing = H.div["not-loading"](
    #     H.div("yes", visible_on_loading=1),
    #     H.div("no", visible_on_loading=0),
    #     H.form(
    #         H.button(
    #             "Hello",
    #             onclick=q,
    #         ),
    #         H.button(
    #             "World",
    #             onclick=ClientWrap(
    #                 wait,
    #                 toggles="loading",
    #                 pre="this.setAttribute('disabled', '')",
    #                 post="this.removeAttribute('disabled')",
    #             ),
    #         ),
    #         # onsubmit=q,
    #         H.button(
    #             "OI",
    #             onclick=wait2,
    #         )
    #     ),
    #     has_loading=True,
    # ).autoid()
    # page.print(thing)

    pt = Point(10, 25)

    thing = H.div(
        H.form(
            H.input(name="one"),
            __ref="one",
        ),
        H.form(
            H.input(name="two"),
            __ref="two",
        ),
        H.div(
            nested := H.div(
                "nested",
            ).autoid(),
        ),
        __ref=Reference(pt),
        oninput=q.wrap(refs=True),
    ).autoid()

    page.print(thing)
    page[nested].print(
        H.form(
            H.input(name="three"),
            __ref="three",
        ),
    )

    async for entry, resolve in q:
        page.print(entry)
        page.print(entry.target)
        page.print(entry.refs)
        page.print(entry.ref)


@bear  # (strongrefs=True)
async def app(page):
    nclicks = 0

    def increment(event):
        nonlocal nclicks
        nclicks += 1
        page[clickspan].set(str(nclicks))

    page.print(
        H.div(
            H.button("Click me!"),
            onclick=increment,
        ),
        H.div("You clicked ", clickspan := H.span(nclicks).autoid(), " times."),
    )

    await asyncio.Future()


from dataclasses import dataclass

from starbear import Queue


@dataclass
class Person:
    name: str
    age: int


@bear
async def app(page):
    q = Queue()
    alice = Person("Alice", 29)
    barbara = Person("Barbara", 34)
    persons = [alice, barbara]
    page.print(
        H.div(
            [H.div(H.button(person.name), __ref=Reference(person)) for person in persons],
            onclick=q.wrap(refs=True).tag("ah."),
        )
    )
    async for event in q:
        ref = event.ref
        person = ref.datum
        page.print(H.div(event.tag, " is ", person.age, " years old."))
        page[ref, "button"].set("X")
