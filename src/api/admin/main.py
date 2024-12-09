from fastapi import APIRouter, Depends

from src.core.models import Blockchain
from src.utils.dependencies import get_blockchain

router = APIRouter()

@router.get("/admin/list_all_blocks")
def list_all_blocks(blockchain: Blockchain = Depends(get_blockchain)):
    return blockchain.get_all_blocks()

@router.post("/admin/drop_all_blocks")
def drop_all_blocks(blockchain: Blockchain = Depends(get_blockchain)):
    blockchain.blocks.delete_many({})
    return {"message": "All blocks have been dropped!"}

@router.post("/admin/generate_next_block")
def generate_next_block(pdf_hash: str, author: str, date_of_defense: str, university: str, faculty: str, supervisor: str, blockchain: Blockchain = Depends(get_blockchain)):
    blockchain.generate_next_block(pdf_hash, author, date_of_defense, university, faculty, supervisor)
    return {"message": "Block has been generated!"}

@router.get("/admin/get_latest_block")
def get_latest_block(blockchain: Blockchain = Depends(get_blockchain)):
    return blockchain.get_latest_block()
