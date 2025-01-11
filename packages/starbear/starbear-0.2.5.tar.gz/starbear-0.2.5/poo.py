from hrepr import H

from starbear.core.app import bear
from starbear.core.live import AutoRefresh

# class Watchable:
#     def notify(self, event):
#         for q in getattr(self, "queues", ()):
#             q.put_nowait(event)

#     @asynccontextmanager
#     async def watch_context(self):
#         q = Queue()
#         if not hasattr(self, "queues"):
#             self.queues = set()
#         self.queues.add(q)
#         try:
#             yield q
#         finally:
#             self.queues.discard(q)

#     async def watch(self):
#         async with self.watch_context() as q:
#             async for event in q:
#                 yield event


# @dataclass
# class Toot(Watchable):
#     x: int
#     y: int

#     def set_x(self, x):
#         self.x = x
#         self.notify(("x", x))

#     def set_y(self, y):
#         self.y = y
#         self.notify(("y", y))

#     async def __live__(self, element):
#         i = 0
#         async for event in self.watch():
#             i += 1
#             element.set([i, self.x, self.y])


# @dataclass
# class AutoRefresh:
#     value: object
#     refresh_rate: float = 0.05

#     async def __live__(self, element):
#         while True:
#             element.set(self.value)
#             await asyncio.sleep(self.refresh_rate)


# @bear
# async def __app__(page):
#     toot = Toot(1, 2)
#     page.print(H.div(toot))
#     page.print(H.div(toot))
#     page.print(H.div(toot))
#     while True:
#         await asyncio.sleep(0.1)
#         toot.set_x(3)


@bear
async def __app__(page):
    def inca(_):
        dico["a"] += 1

    def incb(_):
        dico["b"] += 1

    dico = {"a": 1, "b": 1}
    page.print(AutoRefresh(dico, refresh_rate=0.5))
    page.print(H.button("a+", onclick=inca))
    page.print(H.button("b+", onclick=incb))
    await page.wait()
