"""Tested on Python 3.12.4"""

# Main imports
from fastapi import FastAPI

# Other imports
import tomllib

# Imports from main project
from api_versions.v1.routes_v1 import main_router_v1

with open("config.toml", "rb") as f:
    config = tomllib.load(f)
main_api_address = config["main_api_address"]
main_address = config["main_address"]
description = ("Wall Of Text API\n"
               f"You can check the docs at {main_api_address}/docs "
               f"and {main_api_address}/redoc. "
               f"Main address: {main_address}.")

app = FastAPI(
    title="Wall Of Text API",
    description=description,
    version="1.0.0",
    openapi_url=f"{main_api_address}/openapi.json",
    docs_url=f"{main_api_address}/docs",
    redoc_url=f"{main_api_address}/redoc",
    swagger_ui_oauth2_redirect_url=f"{main_api_address}/docs/oauth2-redirect",
)

app.include_router(main_router_v1, prefix=main_api_address)
app.include_router(main_router_v1,
                   prefix=main_api_address + "/latest",
                   tags=["latest"])

app.include_router(main_router_v1,
                   prefix=main_api_address + "/v1",
                   tags=["v1"])
