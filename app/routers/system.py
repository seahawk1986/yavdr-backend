# Module for system information (and possible operations)
import pydbus
from typing import Mapping
from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter()
bus = pydbus.SystemBus()


class Playbook(BaseModel):
    playbook: str
    options: Mapping


@router.put("/system/playbooks")
def run_playbook(playbook: str):
    """
    Run an ansible playbook with parameters.
    """
    pass
