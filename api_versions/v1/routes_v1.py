# Other imports
import sys
from typing import Annotated, Dict, List

# Main imports
from fastapi import APIRouter, Request, Response, status, Query
from fastapi.responses import RedirectResponse

# Imports from project
from .database_v1 import SessionLocal, Text
from .pydantic_models_v1 import (
    Error,
    TextCreate,
    TextResponse,
    GetTextsQueryParams
)

# TOML import
if sys.version_info < (3, 11):
    try:
        import tomli as tomllib  # noqa
    except ImportError as ex:
        raise ImportError("tomli is required for Python < 3.11") from ex # noqa
else:
    import tomllib

# Config loading
try:
    with open("config.toml", "rb") as f:
        config = tomllib.load(f)
except FileNotFoundError:
    raise FileNotFoundError("config.toml not found")

main_api_address = config["main_api_address"]
main_api_address = main_api_address if main_api_address else "/api"
main_address = config["main_address"]
main_address = f" Main address: {main_address}." if main_address else ""
main_router_v1 = APIRouter()


@main_router_v1.get("")
async def root(response: Response, request: Request) -> Dict[str, str]:
    response.status_code = status.HTTP_200_OK
    return {"welcome_text":
            "This is the Wall Of Text API. "
            f"You can check the docs at {request.url}/docs "
            f"and {request.url}/redoc.{main_address}"}


@main_router_v1.get("/docs", status_code=301, include_in_schema=False)
async def docs_redirect() -> RedirectResponse:
    return RedirectResponse(f"{main_api_address}/docs", status_code=301)


@main_router_v1.get("/redoc", status_code=301, include_in_schema=False)
async def redoc_redirect() -> RedirectResponse:
    return RedirectResponse(f"{main_api_address}/redoc", status_code=301)


@main_router_v1.get("/openapi.json", status_code=301, include_in_schema=False)
async def openapi_json_redirect() -> RedirectResponse:
    return RedirectResponse(f"{main_api_address}/openapi.json", status_code=301)


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
            db_text = db.get(Text, parent_id)
        except Exception as e:  # pylint: disable=broad-exception-caught
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
    except Exception as e:  # pylint: disable=broad-exception-caught
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
    except Exception as e:  # pylint: disable=broad-exception-caught
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
        db_text = db.get(Text, text_id)
    except Exception as e:  # pylint: disable=broad-exception-caught
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

    for comment in comments:
        comment.comment_depth = text_response.comment_depth + 1
        text_response.comments.append(
            grab_comments(TextResponse(**comment.__dict__))
        )
    return text_response
