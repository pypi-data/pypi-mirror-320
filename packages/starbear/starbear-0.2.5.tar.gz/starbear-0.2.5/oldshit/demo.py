from dataclasses import dataclass

from ovld import ovld


@dataclass
class B:
    pass


@ovld
def f(x: int, y: object):
    return "A"


@ovld
def f(x: int, y: int):
    return "B"


print(f(5, 6))
