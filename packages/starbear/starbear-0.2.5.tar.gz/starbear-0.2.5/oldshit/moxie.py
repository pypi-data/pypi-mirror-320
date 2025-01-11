import asyncio
from pathlib import Path

from hrepr import H

from starbear.serve import bear
from starbear.utils import ClientWrap, FeedbackQueue


@bear
async def app(page):
    q = FeedbackQueue().wrap(toggles="loading", form=True)

    async def wait(_):
        await asyncio.sleep(2)
        page.print("done.")

    async def wait2(_):
        await page.window.console.log("hello!")
        await page[thing].toggle("loading", True)
        await asyncio.sleep(2)
        page.print("donezo!")
        await page[thing].toggle("loading", False)

    # page["head"].print(
    #     H.style(
    #         """
    #         .loading button {
    #             opacity: 0.5;
    #             pointer-events: none;
    #         }
    #         """
    #     )
    # )

    page["head"].print(
        H.link(
            rel="stylesheet",
            href=Path("style.css"),
        )
    )
    page.print("hi?")

    # await asyncio.sleep(5)

    thing = H.div["not-loading"](
        H.div("yes", visible_on_loading=1),
        H.div("no", visible_on_loading=0),
        H.form(
            H.button(
                "Hello",
                onclick=q,
            ),
            H.button(
                "World",
                onclick=ClientWrap(
                    wait,
                    toggles="loading",
                    pre="this.setAttribute('disabled', '')",
                    post="this.removeAttribute('disabled')",
                ),
            ),
            # onsubmit=q,
            H.button(
                "OI",
                onclick=wait2,
            ),
        ),
        has_loading=True,
    ).autoid()
    page.print(thing)

    async for entry, resolve in q:
        await asyncio.sleep(1)
        page.print(entry)
        await resolve(4)


# @bear
# async def app(page):
#     async def wait(_):
#         await asyncio.sleep(2)
#         page.print("done.")

#     thing = H.div(
#         H.div(
#             "Peek",
#             __active_on="init",
#         ),
#         H.div(
#             "BOO!",
#             __active_on="boo",
#         ),
#         H.button(
#             "-A-",
#             onclick=wait
#             # onclick=Pipeline(
#             #     Switch("boo"),
#             #     wait,
#             #     Switch("init"),
#             # )
#         ),
#         __state_holder=True,
#     )
#     page.print(thing)


# @bear
# async def app(page):
#     q = FeedbackQueue().wrap(toggles="loading", form=True)

#     loader, loading, normal = create_toggle()

#     thing = loader.div(
#         loading.div("loading..."),
#         normal.div("normal!"),
#         H.form(
#             H.button(
#                 "Hello",
#                 onclick=q,
#             ),
#             H.button(
#                 "World",
#                 onclick=ClientWrap(wait, toggles="loading"),
#             ),
#         ),
#     )
#     page.print(thing)

#     async for entry, resolve in q:
#         await asyncio.sleep(1)
#         page.print(entry)
#         await resolve(4)
