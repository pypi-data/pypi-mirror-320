from starbear import ClientWrap, H, Queue, bear


@bear
async def app(page):
    queue = ClientWrap(Queue(), debounce=0.3, form=True)

    page.print(
        H.form(
            "What is your name?",
            H.input(name="name", oninput=queue),
            "What is your quest?",
            H.input(name="quest", oninput=queue),
            "What is your favourite color?",
            H.input(name="color", oninput=queue),
            H.button("Submit", style={"grid-column": "span 2"}),
            onsubmit=queue.wrap(debounce=None),
            style={
                "display": "grid",
                "grid-template-columns": "200px 1fr",
                "max-width": "600px",
            },
        ),
        target := H.div().autoid(),
    )

    async for answers in queue:
        name = answers["name"] or "???"
        quest = answers["quest"] or "???"
        color = answers["color"] or "???"
        mark = "!" if answers["$submit"] else "?"
        page[target].set(f"Hi {name}{mark} You seek {quest} and you like {color}{mark}")
