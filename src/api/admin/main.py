from fastapi import APIRouter, Depends

from src.core.models import BlockchainService
from src.utils.dependencies import get_blockchain

router = APIRouter()

@router.post("/admin/drop_all_blocks")
def drop_all_blocks(blockchain: BlockchainService = Depends(get_blockchain)):
    blockchain.blocks.delete_many({})
    return {"message": "All blocks have been dropped!"}

@router.get("/admin/generate_genesis_block")
def generate_genesis_block(blockchain: BlockchainService = Depends(get_blockchain)):
    blockchain.generate_genesis_block()
    return {"message": "Genesis block has been generated!"}