import asyncio
from dataclasses import dataclass

from hrepr import H

from starbear.core.app import bear
from starbear.core.utils import FeedbackEvent as Event, Queue

# class Borborygm:
#     async def __live__(self, element):
#         for i in range(10):
#             yield i


# live(Borborygm(), onproduce=q)


class StateProxy:
    async def __listen__(self):
        q = Queue()
        self.register(q)


@dataclass
class Monster:
    size: int
    fearsomeness: int

    def __hrepr__(self, H, hrepr):
        return H.b("RARRRR")

    def __live_element__(self, H, hrepr):
        return H.live_element()

    async def __live__(self, element):
        element.print("wow")
        for i in range(100):
            await asyncio.sleep(0.5)
            # print("=>", await (yield i))
            print("=>", (yield i))

    # async def __live__(self, element):
    #     q = Queue()
    #     element.print(H.button("NICE", onclick=q))
    #     element.print(target := H.div(0).ensure_id())
    #     i = 0
    #     async for evt in q:
    #         i += 1
    #         element[target].set(i)


@bear
async def __app__(page):
    async def woof(element):
        element.print("wawww")
        for i in range(100):
            await asyncio.sleep(1)
            result = yield Event(type="odd" if i % 2 == 1 else "even", value=i)
            print(await result)

    q = Queue()
    page.print(container := H.div(id=True))
    page[container].set(H.div(Monster(size=10, fearsomeness=100)))
    # # await asyncio.sleep(1)
    # page[container].set(H.div(live(Monster(size=10, fearsomeness=100), on_produce=q)))
    page[container].print(H.live_element(runner=woof, on_produce_even=q, id=True))
    # for i in range(100):
    #     await asyncio.sleep(1)
    #     print("MAIN", i)
    async for event in q:
        match event:
            case Event("odd", x):
                page.print("odd", x)
                event.resolve(12345)
            case Event("even", x):
                page.print("even", x)
                event.resolve(1234)
            case x:
                page.print("other", x)
