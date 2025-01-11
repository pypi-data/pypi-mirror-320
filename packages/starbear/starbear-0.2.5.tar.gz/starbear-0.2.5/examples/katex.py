from hrepr import H

from starbear import H, bear


def math(x):
    return H.div(
        __constructor={
            "module": "https://cdn.jsdelivr.net/npm/katex@0.16.4/dist/katex.mjs",
            "symbol": "default.render",
            "arguments": [x, H.self()],
            "stylesheet": "https://cdn.jsdelivr.net/npm/katex@0.16.4/dist/katex.css",
        }
    )


@bear
async def simple(page):
    page.print(math("c = \\pm\\sqrt{a^2 + b^2}"))
    page.print(math("ab^5c^6"))
