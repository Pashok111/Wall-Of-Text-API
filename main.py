"""
Tested on Python 3.11.1

# noqa lines because of PyCharm bug, see here:
https://youtrack.jetbrains.com/issue/PY-63306/False-positive-for-unresolved-reference-of-state-instance-field-in-FastAPI-app

You can find more information about the project on GitHub:
https://github.com/Pashok111/wall-of-text-api
"""

# Other imports
import os

# Main imports
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_redoc_html,
    get_swagger_ui_oauth2_redirect_html
)
from fastapi.staticfiles import StaticFiles

# Imports from project
from api_versions import main_router_v1

# Config loading
load_dotenv()
main_api_address = os.getenv("MAIN_API_ADDRESS", "/api")
if not main_api_address.startswith("/"):
    main_api_address = f"/{main_api_address}"
main_address = os.getenv("MAIN_ADDRESS")
main_address = f"\nMain address: {main_address}." if main_address else ""

static_dir = os.getenv("STATIC_DIR", "static")
favicon = os.path.join(
    static_dir, os.getenv("FAVICON", "favicon.png")
)
redoc_js = os.path.join(
    static_dir, os.getenv("REDOC_JS", "redoc.standalone.js")
)
swagger_js = os.path.join(
    static_dir, os.getenv("SWAGGER_JS", "swagger-ui-bundle.js")
)
swagger_css = os.path.join(
    static_dir, os.getenv("SWAGGER_CSS", "swagger-ui.css")
)

DESCRIPTION = ("Wall Of Text API\n"
               f"You can check the docs at {main_api_address}/docs "
               f"and {main_api_address}/redoc.{main_address}")

app = FastAPI(
    title="Wall Of Text API",
    description=DESCRIPTION,
    version="1.0.0",
    openapi_url=f"{main_api_address}/openapi.json",
    docs_url=None,
    redoc_url=None,
    swagger_ui_oauth2_redirect_url=f"{main_api_address}/docs/oauth2-redirect"
)
app.mount(
    path=f"{main_api_address}/{static_dir}",
    app=StaticFiles(directory=static_dir),
    name="static"
)


@app.get("/", include_in_schema=False)
async def root(request: Request):
    return {"welcome_text":
            "This is the Wall Of Text API. "
            f"Check {request.url}{main_api_address[1:]} for more info."}


@app.get(f"{main_api_address}/docs", include_in_schema=False)
async def custom_docs():
    """Redefined docs endpoint"""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,  # noqa
        title=app.title + " - Swagger Docs",  # noqa
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,  # noqa
        swagger_js_url=swagger_js,
        swagger_css_url=swagger_css,
        swagger_favicon_url=favicon
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)  # noqa
async def custom_oauth2():
    """Redefined oauth2 redirect endpoint"""
    return get_swagger_ui_oauth2_redirect_html()


@app.get(f"{main_api_address}/redoc", include_in_schema=False)
async def custom_redoc():
    """Redefined redoc endpoint"""
    return get_redoc_html(
        openapi_url=app.openapi_url,  # noqa
        title=app.title + " - ReDoc",  # noqa
        redoc_js_url=redoc_js,
        redoc_favicon_url=favicon
    )


app.include_router(
    main_router_v1,
    prefix=main_api_address,
    tags=["default"],
    include_in_schema=False
)
app.include_router(
    main_router_v1,
    prefix=main_api_address + "/latest",
    tags=["latest"]
)

app.include_router(
    main_router_v1, prefix=main_api_address + "/v1", tags=["v1"]
)
