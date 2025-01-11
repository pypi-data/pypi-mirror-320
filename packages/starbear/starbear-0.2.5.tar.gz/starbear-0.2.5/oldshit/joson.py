import json

construct = {}


def register_constructor(key):
    def deco(fn):
        construct[key] = fn
        return fn

    return deco


@register_constructor("HTMLElement")
def _(page, selector):
    return page[selector]


def object_hook(dct):
    if "%" in dct:
        args = dict(dct)
        args.pop("%")
        return construct[dct["%"]](None, **args)
    else:
        return dct


class SpecialJSONDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=object_hook, *args, **kwargs)


data = '{"A": {"%": "HTMLElement", "selector": "wow"}}'
decoded = json.loads(data, object_hook=object_hook)
print(decoded)
