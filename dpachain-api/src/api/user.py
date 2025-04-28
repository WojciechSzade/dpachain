import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File

from src.block.interfaces import IBlockService
from src.block.errors import BlockError, BlockNotFoundError
from src.utils.dependencies import get_block_service
from src.api.utils import handle_error


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/user/get_block_by_hash")
def get_block_by_hash(block_hash, block_service: IBlockService = Depends(get_block_service)):
    try:
        return {"block": block_service.get_block_by_hash(block_hash)}
    except Exception as e:
        return handle_error(e)


@router.post("/user/calculate_pdf_hash")
def calculate_pdf_hash(pdf_file: Annotated[bytes, File()], block_service: IBlockService = Depends(get_block_service)):
    try:
        return {"calculated_pdf_hash": block_service.calculate_pdf_hash(pdf_file=pdf_file)}
    except Exception as e:
        return handle_error(e)
