from hrepr import J

from starbear import bear, here
from starbear.core.constructors import register_constructor


@register_constructor("Quacko")
def _(page, id, value=None, delta=None):
    if value is not None:
        page.representer.store["Quacko", id] = value
    else:
        page.representer.store["Quacko", id] += delta
    return page.representer.store["Quacko", id]


@bear  # (strongrefs=True)
async def __app__(page):
    def fn(event):
        page.print(event)

    md = J(module=here() / "coup.js")
    page.print(md(fn))
    page.print(md(fn))

    await page.wait()
