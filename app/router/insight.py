from typing import Union

from fastapi import APIRouter, Query, Body

from app.settings import *
from app.storage.interferer import *
from app.storage.querier import *

router = APIRouter()


@router.get("/search", response_description="Search images by keywords")
async def search(keywords: Union[List[Any], None] = Query(default=None)):
    if keywords is None:
        return {"message": "You have entered nothing!"}
    ripple_querier = RippleQuerier(MongodbHandler(mongodb_client, "imageRipples", "collage"), Oss2Handler(oss2_bucket),
                                   RedisHandler(redis_client))
    return ripple_querier.fuzzy_search(keywords)


@router.get("/find/similar", response_description="Find similar images on ripples")
async def get_ripples(img_id: Union[str | None] = Query(default=None)):
    if img_id is None:
        return {"message": "You have entered nothing!"}
    ripple_querier = RippleQuerier(MongodbHandler(mongodb_client, "imageRipples", "collage"), Oss2Handler(oss2_bucket),
                                   RedisHandler(redis_client))
    return ripple_querier.get_similar_img(img_id, text_embedder, image_embedder)


@router.post("/interference/collapse", response_description="Do some interference")
async def get_ripples(img_id_1: Union[str | None] = Body(None, embed=True),
                      img_id_2: Union[str | None] = Body(None, embed=True)):
    if img_id_1 is None or img_id_2 is None:
        return {"message": "You have entered nothing!"}
    ripple_interferer = RippleInterferer(MongodbHandler(mongodb_client, "imageRipples", "collage"),
                                         Oss2Handler(oss2_bucket))
    return ripple_interferer.wave_collapse(img_id_1, img_id_2, image_interferer)
