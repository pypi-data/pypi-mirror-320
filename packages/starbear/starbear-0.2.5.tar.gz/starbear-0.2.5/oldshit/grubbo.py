from pathlib import Path

from hrepr import H

from starbear.serve import staticbear

here = Path(__file__).parent


@staticbear
async def app(request):
    return H.div(
        H.link(rel="stylesheet", href=Path(here / "style.css")),
        H.b("hello!", onclick=lambda x: print(x)),
    )


# @bear
# async def app2(page):
#     page.print(
#         H.link(rel="stylesheet", href=Path(here / "style.css")),
#         H.b("hello2!")
#     )
