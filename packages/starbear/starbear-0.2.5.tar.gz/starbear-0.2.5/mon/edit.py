import asyncio
from pathlib import Path

from hrepr import H

from starbear import FeedbackQueue, bear

here = Path(__file__).parent


@bear
async def edit(page):
    queue = FeedbackQueue()

    progfile = Path("program.py")
    prog = progfile.read_text()

    page.add_resource(here / "editor-style.css")

    def poop(_):
        page.log("💩")
        1 / 0

    editor = H.div(
        __constructor={
            "module": Path(here / "main.js"),
            "options": {
                "content": {
                    "live": prog,
                    "saved": prog,
                },
                "callbacks": {
                    # "update": queue.tag("update"),
                    "update": poop,
                    "save": queue.tag("save"),
                    "commit": queue.tag("commit"),
                },
                "filename": "hey.py",
                "autofocus": True,
            },
        }
    )
    structure = H.div["panes"](
        H.div["editor"](editor),
        H.div["output"](
            error := H.div["error"](style="color:red;").autoid(),
            target := H.div["target"]().autoid(),
        ),
    )
    page.print(structure)

    task = None

    async def run(fn):
        try:
            await fn(page[target])
        except Exception as exc:
            page[error].set(str(exc))

    async def refresh(content):
        nonlocal task
        glb = {}
        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        page[error].clear()
        page[target].clear()
        exec(content, glb)
        task = asyncio.create_task(run(glb["main"]))

    await refresh(prog)

    async for (tag, content), resolve in queue:
        if tag == "update":
            await resolve(False)
        elif tag == "save":
            await refresh(content)
            await resolve(True)
        elif tag == "commit":
            await refresh(content)
            progfile.write_text(content)
            await resolve(True)
