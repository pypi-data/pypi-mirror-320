from hrepr import H

from starbear import bear


@bear
def app(page):
    tree = H.div(
        H.div(
            H.input(
                placeholder="say something",
                autocomplete="off",
            ),
            when_state="idle",
        ),
        H.div(
            "Waiting...",
            when_state="processing",
        ),
        H.div["results"](),
        anchor_state=["idle", "processing"],
    )

    page.print(tree)
