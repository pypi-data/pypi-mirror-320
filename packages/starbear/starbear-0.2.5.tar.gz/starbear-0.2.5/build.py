from dataclasses import dataclass

from hrepr import H, J

from starbear import here
from starbear.core.app import bear
from starbear.core.reg import Reference
from starbear.core.utils import Queue


@dataclass
class TodoEntry:
    done: bool
    text: str


@bear
async def __app__(page):
    q = Queue()
    Form = J(module=here / "build.js")

    td = TodoEntry(False, "Gape")

    todos = H.div(
        H.div(
            H.input(represents="done", type="checkbox", checked=True),
            H.input(represents="text", value="Do laundry"),
            H.button("x"),
            represents="0",
            __ref=Reference(td),
        ),
        H.div(
            H.input(represents="1.done", type="checkbox", checked=False),
            H.input(represents="1.text", value="Create this list"),
            H.button("x"),
        ),
        H.button("+"),
    )

    page.print(
        f := Form(
            todos,
            oninput=q,
        ),
        # todos,
    )
    async for event in q:
        page.print(event)
