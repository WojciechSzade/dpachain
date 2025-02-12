from typing import Annotated
import logging
import datetime

from fastapi import APIRouter, Depends, File, UploadFile

from src.block.main import BlockService
from src.utils.dependencies import get_block_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/get_latest_block")
def get_latest_block(block_service: BlockService = Depends(get_block_service)):
    return block_service.get_latest_block()


@router.get("/list_all_blocks")
def list_all_blocks(block_service: BlockService = Depends(get_block_service)):
    return block_service.get_all_blocks()
