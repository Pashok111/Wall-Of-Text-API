# Main imports
from fastapi import APIRouter, Response, status, Query

# Other imports
from typing import Annotated, Dict, List
import tomllib

# Imports from main project
from api_versions.v1.pydantic_models_v1 import Error, TextCreate, TextResponse, GetTextsQueryParams
from api_versions.v1.database_v1 import SessionLocal, Text

with open("config.toml", "rb") as f:
    config = tomllib.load(f)
main_api_address = config["main_api_address"]
main_address = config["main_address"]
main_router_v1 = APIRouter()


@main_router_v1.get("")
async def root(response: Response) -> Dict[str, str]:
    response.status_code = status.HTTP_200_OK
    return {"welcome_text":
            "This is the Wall Of Text API. "
            f"You can check the docs at {main_api_address}/docs "
            f"and {main_api_address}/redoc. "
            f"Main address: {main_address}."}


@main_router_v1.post("/texts",
                     responses={201: {"model": TextResponse},
                                500: {"model": Error}})
async def create_text(response: Response,
                      text: TextCreate
                      ) -> TextResponse | Error:
    try:
        db = SessionLocal()
        db_text = Text(username=text.username, text=text.text)
        db.add(db_text)
        db.commit()
        db.refresh(db_text)
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Error(error={"error": str(e)})
    response.status_code = status.HTTP_201_CREATED
    return db_text


@main_router_v1.get("/texts",
                    responses={200: {"model": List[TextResponse]},
                               400: {"model": Error},
                               500: {"model": Error}})
async def get_texts(response: Response,
                    filter_query: Annotated[GetTextsQueryParams, Query()]
                    ) -> List[TextResponse] | Error:
    limit = filter_query.limit
    offset = filter_query.offset
    try:
        db = SessionLocal()
        texts = db.query(Text).limit(limit).offset(limit * offset).all()
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Error(error={"error": str(e)})
    if len(texts) == 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return Error(error={"error": "End of texts"})
    response.status_code = status.HTTP_200_OK
    return [
        TextResponse(id=text.id,
                     username=text.username,
                     text=text.text,
                     created_at_utc=text.created_at_utc)
        for text in texts
    ]
