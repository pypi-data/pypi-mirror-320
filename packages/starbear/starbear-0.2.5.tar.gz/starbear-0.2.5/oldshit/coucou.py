from hrepr import H

from starbear.reactive import reactive
from starbear.serve import bear


@reactive
def berry(state):
    return H.div(state["text"], style={"color": state["color"]})


@reactive
def thing(state):
    return H.div(
        berry(state["one"]),
        berry(state["two"]),
    )


@bear
async def main(page):
    state = {
        "one": {
            "text": "strawberry",
            "color": "red",
        },
        "two": {
            "text": "blueberry",
            "color": "blue",
        },
    }
    page.print(thing(state))
    state["one"]["text"] = "tomato"
    state["two"]["color"] = "violet"
