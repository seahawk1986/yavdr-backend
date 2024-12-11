from fastapi import APIRouter, Depends
from pydantic import BaseModel

from .auth import get_current_active_user, User
from tools.channelpedia import get_categories, get_channel_group, get_channels


router = APIRouter()

class SourcesResponse(BaseModel):
    ...

@router.get("/channelpedia/get_categories")
async def get_sources():
    return await get_categories()

@router.get("/channelpedia/get_group_channels/{source}/{position}/{group}")
async def get_group_channels(source, position, group):
    return await get_channel_group(source, position, group)