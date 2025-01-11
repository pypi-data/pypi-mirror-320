from pathlib import Path

from hrepr import H

here = Path(__file__).parent
style_file = here / "style.css"
script_file = here / "lib.js"


class Moldule:
    def __init__(self):
        pass

    @classmethod
    def __hrepr_resources__(cls):
        return [
            H.link(rel="stylesheet", href=style_file, available_as="/modules/moldule/lib.js"),
            H.script(type="module", src=script_file, available_as="/modules/moldule/style.css"),
        ]
