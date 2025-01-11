from dataclasses import dataclass

from hrepr import H

from starbear import Queue


@dataclass
class CardInfo:
    name: str
    hp: int
    initiative: int
    star: int


def make_card(info):
    ratio = 3.5 / 2.5
    h = 650
    w = h / ratio
    normh = 100 * ratio
    return H.svg(
        H.rect(
            x=0,
            y=0,
            width=100,
            height=10,
            fill="blue",
        ),
        H.text("★" * info.star, x=10, y=8, fill="yellow", style="font-size:10"),
        H.rect(
            x=73.8,
            y=66,
            width=20,
            height=60,
            fill="white",
            stroke="red",
            rx=3,
        ),
        H.line(
            x1=73.8,
            y1=101,
            x2=93.8,
            y2=101,
            stroke="red",
        ),
        H.line(
            x1=73.8,
            y1=76,
            x2=93.8,
            y2=76,
            stroke="red",
        ),
        H.text(info.name, x="3", y="21", fill="black", style="font-size:12"),
        H.path(
            d="M14 20.408c-.492.308-.903.546-1.192.709-.153.086-.308.17-.463.252h-.002a.75.75 0 01-.686 0 16.709 16.709 0 01-.465-.252 31.147 31.147 0 01-4.803-3.34C3.8 15.572 1 12.331 1 8.513 1 5.052 3.829 2.5 6.736 2.5 9.03 2.5 10.881 3.726 12 5.605 13.12 3.726 14.97 2.5 17.264 2.5 20.17 2.5 23 5.052 23 8.514c0 3.818-2.801 7.06-5.389 9.262A31.146 31.146 0 0114 20.408z",
            fill="red",
            transform="translate(72,45),scale(1)",
        ),
        style="background:white;border:3px solid black;",
        height=f"{h}px",
        width=f"{w}px",
        viewbox=f"0 0 100 {normh}",
    )


async def main(page):
    q = Queue()
    qf = q.wrap(form=True)
    info = CardInfo(name="???", hp=10, star=5, initiative=100)
    form = H.form(
        H.input(value=info.name, name="name", oninput=qf, autocomplete="off"),
        H.input(value=info.hp, name="hp", oninput=qf, autocomplete="off"),
        H.input(value=info.star, name="star", oninput=qf, autocomplete="off"),
    )
    page.print(H.div(form, card_div := H.div().autoid()))

    def show():
        card = make_card(info)
        page[card_div].set(card)

    show()
    async for entry in q:
        try:
            info.name = entry["name"]
            info.hp = int(entry["hp"])
            info.star = int(entry["star"])
            show()
        except Exception as exc:
            page[card_div].set(exc)
