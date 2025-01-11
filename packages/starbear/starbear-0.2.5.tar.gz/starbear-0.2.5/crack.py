import asyncio

from aiostream import pipe, stream

from starbear.core.utils import Queue


class Event:
    __match_args__ = ("name", "value", "resolve")

    def __init__(self, name, value, resolve=None):
        self.name = name
        self.value = value
        self.resolve = resolve


class MultiQueue:
    def __init__(self, **generators):
        self.generators = {}
        for name, queue in generators.items():
            self.register(name, queue)

    def register(self, name, queue):
        # self.generators[name] = stream.iterate(queue) | pipe.map(lambda x: [name, x])
        self.generators[name] = stream.iterate(queue) | pipe.map(
            lambda x: Event(name=name, value=x)
        )
        return queue

    def queue(self, name):
        return self.register(name, Queue())

    def __aiter__(self):
        it = aiter(stream.merge(*self.generators.values()))
        return it._aiterator


async def testie(n, t, v):
    for _ in range(n):
        await asyncio.sleep(t)
        yield v


async def main():
    mq = MultiQueue(
        apple=testie(15, 0.1, "A"),
        banana=testie(10, 0.2, "BB"),
        cherry=testie(5, 0.5, "CC"),
    )
    async for item in mq:
        # print(item)
        match item:
            # case ["apple", x]:
            #     print(x)
            case Event("apple", x):
                print(x)


asyncio.run(main())
