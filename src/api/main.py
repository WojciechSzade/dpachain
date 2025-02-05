from typing import Annotated
import logging
import datetime

from fastapi import APIRouter, Depends, File, UploadFile

from src.core.models import BlockchainService, Block
from src.utils.dependencies import get_blockchain

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/create_new_block")
def generate_next_block(diploma_type: str, pdf_file: Annotated[bytes, File()], authors: (list[str] | str), title: str, language: str, discipline: str, is_defended: int, date_of_defense: datetime.date, university: str, faculty: str, supervisor: (list[str] | str), reviewer: (list[str] | str), additional_info: (str | None) = None, blockchain: BlockchainService = Depends(get_blockchain)):
    logger.info(blockchain)
    pdf_hash = Block.calculate_pdf_hash(pdf_file)
    try:
        blockchain.create_new_block(diploma_type, pdf_hash, authors, title, language, discipline, is_defended, date_of_defense, university, faculty, supervisor, reviewer, additional_info)
    except Exception as e:
        return {"message": f"Failed to create block: {e}"}
    return {"message": "Block has been generated!"}

@router.get("/get_latest_block")
def get_latest_block(blockchain: BlockchainService = Depends(get_blockchain)):
    return blockchain.get_latest_block()
