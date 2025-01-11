from starbear import H, bear


@bear
async def mapbox(page):
    page.print(
        H.div(
            __constructor={
                "script": "https://api.mapbox.com/mapbox-gl-js/v2.1.1/mapbox-gl.js",
                "stylesheet": "https://api.mapbox.com/mapbox-gl-js/v2.1.1/mapbox-gl.css",
                "symbol": "mapboxgl.Map",
                "arguments": {
                    "container": H.self(),
                    "style": "mapbox://styles/mapbox/streets-v11",
                    "center": [0.1218, 52.2053],
                    "zoom": 11,
                },
            }
        )
    )
