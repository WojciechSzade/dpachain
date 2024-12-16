from typing import Annotated
import datetime

from fastapi import APIRouter, Depends, File, UploadFile

from src.core.models import BlockchainService, Block
from src.utils.dependencies import get_blockchain

router = APIRouter()

@router.post("/create_new_block")
def generate_next_block(pdf_file: Annotated[bytes, File()], author: str, date_of_defense: datetime.date, university: str, faculty: str, supervisor: str, blockchain: BlockchainService = Depends(get_blockchain)):
    pdf_hash = Block.calculate_pdf_hash(pdf_file)
    blockchain.create_new_block(pdf_hash, author, date_of_defense, university, faculty, supervisor)
    return {"message": "Block has been generated!"}

@router.get("/get_latest_block")
def get_latest_block(blockchain: BlockchainService = Depends(get_blockchain)):
    return blockchain.get_latest_block()
