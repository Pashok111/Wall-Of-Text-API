# Main imports
from fastapi import APIRouter, Response, status, Query
from fastapi.responses import RedirectResponse

# Other imports
from typing import Annotated, Dict, List
import tomllib

# Imports from main project
from api_versions.v1.pydantic_models_v1 import (
    Error,
    TextCreate, TextResponse,
    GetTextsQueryParams)
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


@main_router_v1.get("/docs", status_code=status.HTTP_301_MOVED_PERMANENTLY)
async def docs(response: Response) -> RedirectResponse:
    response.status_code = status.HTTP_301_MOVED_PERMANENTLY
    return RedirectResponse(f"{main_api_address}/docs")


@main_router_v1.post("/texts",
                     status_code=status.HTTP_201_CREATED,
                     responses={201: {"model": TextResponse},
                                400: {"model": Error},
                                500: {"model": Error}})
async def create_text(response: Response,
                      text_create: TextCreate
                      ) -> TextResponse | Error:
    parent_id = text_create.parent_id
    username = text_create.username
    text = text_create.text

    if parent_id != -1:
        db = SessionLocal()
        try:
            db_text = db.query(Text).get(parent_id)
        except Exception as e:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return Error(error=str(e))
        finally:
            db.close()
        if not db_text:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return Error(error="No text with this parent_id")

    db = SessionLocal()
    try:
        db_text = Text(parent_id=parent_id, username=username, text=text)
        db.add(db_text)
        db.commit()
        db.refresh(db_text)
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Error(error=str(e))
    finally:
        db.close()

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
    parent_id = filter_query.parent_id or -1
    include_comments = filter_query.include_comments

    db = SessionLocal()
    try:
        texts = db.query(Text).filter(Text.parent_id == parent_id).limit(
            limit).offset(limit * offset).all()
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Error(error=str(e))
    finally:
        db.close()

    if len(texts) == 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return Error(error="End of texts")

    response.status_code = status.HTTP_200_OK
    _response = [TextResponse(**t.__dict__) for t in texts]
    if not include_comments:
        return _response

    return [grab_comments(i) for i in _response]


@main_router_v1.get("/texts/{text_id}",
                    responses={200: {"model": TextResponse},
                               400: {"model": Error},
                               500: {"model": Error}})
async def get_text_by_id(response: Response,
                         text_id: int,
                         include_comments: bool = True
                         ) -> TextResponse | Error:
    db = SessionLocal()
    try:
        db_text = db.query(Text).get(text_id)
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return Error(error=str(e))
    finally:
        db.close()

    if not db_text:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return Error(error="No text with this ID")

    response.status_code = status.HTTP_200_OK
    _response = TextResponse(**db_text.__dict__)
    if not include_comments:
        return _response
    return grab_comments(_response)


def grab_comments(text_response: TextResponse) -> TextResponse:
    db = SessionLocal()
    try:
        comments = db.query(Text).filter(
            Text.parent_id == text_response.id).all()
    finally:
        db.close()

    if not comments:
        return text_response

    text_response.comments = [grab_comments(TextResponse(**comment.__dict__))
                              for comment in comments]
    return text_response
