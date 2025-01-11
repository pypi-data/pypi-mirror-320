import asyncio

from starbear import H, bear


@bear
async def __app__(page):
    page.print(H.h1("HELLO"))
    page.print(H.h2("HELLO"))
    page.print(H.h3("HELLO"))
    for i in range(10):
        await asyncio.sleep(0.4)
        page.print("wow")
