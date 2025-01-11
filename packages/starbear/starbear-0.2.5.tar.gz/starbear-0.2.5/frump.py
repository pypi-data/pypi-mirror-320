import asyncio

from hrepr import H

from starbear.core.app import bear


def f(i):
    return H.div(i)


def g(event):
    print("Z")


@bear
async def __app__(page):
    i = 0
    page.print(H.button("hello", onclick=g))
    while True:
        page.print(f(i))
        await asyncio.sleep(1)
        i += 1
