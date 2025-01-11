import uvicorn
from starlette.applications import Starlette
from starlette.routing import Route


class Cub:
    def __init__(self, session):
        self.session = session
        self.methods = {}
        self.page = Page()

    async def process_main(self, args, scope, receive, send):
        with open(here / "base-template.html") as tpf:
            return HTMLResponse(tpf.read().replace("{{{route}}}", self.path))

    async def process_socket(self, args, scope, receive, send):
        pass

    async def process_method(self, args, scope, receive, send):
        (method_id,) = args


class MotherBear:
    def __init__(self):
        self.cubs = {}

    async def __call__(self, scope, receive, send):
        sess = scope["path_params"]["session"]
        route, *args = scope["path_params"]["object"].split("/")
        if sess not in self.cubs:
            self.cubs[sess] = Cub(self, sess)
        cub = self.cubs[sess]
        method = getattr(cub, f"process_{route or 'main'}")
        return await method(args=args, scope=scope, receive=receive, send=send)


if __name__ == "__main__":
    r = Route("/clunk/{session:int}/{object:path}", MotherBear())
    app = Starlette(routes=[r])
    uvicorn.run(app, host="127.0.0.1", port=5001, log_level="info")
