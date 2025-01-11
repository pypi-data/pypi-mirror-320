from starbear import H, Queue, bear
from starbear.utils import ClientWrap, VirtualFile

stylish = """
.wow {
    color: blue;
}
"""


@bear
async def app(page):
    events = ClientWrap(Queue(), debounce=0.3, form=True)

    page["head"].print(H.link(rel="stylesheet", href=VirtualFile(stylish)))
    page.print(
        H.div["wow"](
            "hello!",
            style={
                "color": "yellow",
                "background": "cyan",
            },
        ),
        H.form(
            H.input(name="wow", oninput=events),
            H.input(name="crackpot", oninput=events),
            H.button(
                "Click!",
                onclick=ClientWrap(
                    page.print,
                    form=True,
                ),
            ),
        ),
    )

    async for x in events:
        page.print(x)
        1 / 0
