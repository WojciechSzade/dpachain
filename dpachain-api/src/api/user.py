import logging

from fastapi import APIRouter, Depends

from src.block.service import BlockService
from src.utils.dependencies import get_block_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/user/get_block_by_hash")
def get_block_by_hash(block_hash, block_service: BlockService = Depends(get_block_service)):
    return block_service.get_block_by_hash(block_hash)

