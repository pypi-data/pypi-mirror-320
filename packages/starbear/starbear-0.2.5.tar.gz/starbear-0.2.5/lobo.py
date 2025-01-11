import asyncio
from contextlib import asynccontextmanager

from hrepr import H

from starbear.core.app import bear
from starbear.stream.functions import Multiplexer, count, repeat, take


async def wow():
    yield "w"
    yield "o"
    yield "w"


# class Multiplexer:
#     def __init__(self, source):
#         self.source = source
#         self.queues = set()
#         self.running = asyncio.create_task(self.run())

#     def notify(self, event):
#         for q in self.queues:
#             q.put_nowait(event)

#     @asynccontextmanager
#     async def stream_context(self):
#         q = Queue()
#         self.queues.add(q)
#         try:
#             yield q
#         finally:
#             self.queues.discard(q)

#     async def stream(self):
#         async with self.stream_context() as q:
#             async for event in q:
#                 yield event

#     async def run(self):
#         async for event in self.source:
#             self.notify(event)

#     def __hrepr__(self, H, hrepr):
#         return hrepr(self.stream())


async def merge(*streams):
    work = {asyncio.create_task(anext(s)): s for s in streams}
    while True:
        done, _ = await asyncio.wait(work.keys(), return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            s = work[task]
            del work[task]
            try:
                yield task.result()
            except StopAsyncIteration:
                continue
            work[asyncio.create_task(anext(s))] = s


class MergedStreams:
    def __init__(self, *streams):
        self.streams = streams

    async def __aiter__(self):
        work = {asyncio.create_task(anext(s)): s for s in self.streams}
        while True:
            done, _ = await asyncio.wait(work.keys(), return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                s = work[task]
                del work[task]
                try:
                    yield task.result()
                except StopAsyncIteration:
                    continue
                work[asyncio.create_task(anext(s))] = s


@asynccontextmanager
async def foo():
    print("A")
    try:
        yield
    finally:
        print("B")


async def blergh():
    async with foo():
        for i in range(100):
            asyncio.sleep(0.1)
            yield i


@bear
async def __app__(page):
    q1 = repeat("A", count=3, interval=0.5)
    q2 = repeat("B", interval=0.55)
    q2 = count(interval=0.5)
    mx = Multiplexer(take(q2, 10))
    # async for x in debounce(merge(mx.stream(), mx.stream(), mx.stream()), delay=0, max_wait=2):
    # async for x in debounce(merge(q1, q2), delay=1, max_wait=2):

    # async for x in merge(q1, q2):
    #     page.print(H.div(x))

    dico = {"a": 1, "b": 2}

    page.print(1234)
    page.print(H.div(q1))

    await asyncio.sleep(1)
    page.print(H.div(mx))

    await asyncio.sleep(1)
    page.print(H.div(mx))

    page.print(H.div(repeat(dico, interval=0.1)))

    dico["a"] = 31
    dico["c"] = 3

    # async for x in debounce(merge(q1, q2), delay=0.3):
    #     page.print(H.div(x))

    # async for x in blergh():
    #     page.print(x)
    #     break
