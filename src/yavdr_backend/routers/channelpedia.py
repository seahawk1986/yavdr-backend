from fastapi import APIRouter, Depends
from pydantic import BaseModel

from yavdr_backend.routers.auth import User, get_current_active_user
from yavdr_backend.tools.channelpedia import get_categories, get_channel_group


router = APIRouter()


class SourcesResponse(BaseModel): ...


@router.get("/channelpedia/get_categories")
async def get_sources(current_user: User = Depends(get_current_active_user)):
    return await get_categories()


@router.get("/channelpedia/get_group_channels/{source}/{position}/{group}")
async def get_group_channels(
    source: str,
    position: str,
    group: str,
    current_user: User = Depends(get_current_active_user),
):
    return await get_channel_group(source, position, group)
