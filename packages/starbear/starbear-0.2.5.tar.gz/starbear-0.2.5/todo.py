from dataclasses import dataclass

from starbear import H, Queue, bear, here


@dataclass
class Todo:
    done: bool
    text: str


todos = [
    Todo(True, "Wake up"),
    Todo(False, "Clean the house"),
    Todo(False, "Create this example"),
]


@bear
async def __app__(page):
    page.add_resources(here / "todo.css")
    q = Queue()
    table = H.table(
        H.tr(
            H.td(H.input(type="checkbox", checked=todo.done)),
            H.td(todo.text),
        )
        for todo in todos
    )
    page.print(table)
