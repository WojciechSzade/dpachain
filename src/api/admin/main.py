import logging

from fastapi import APIRouter, Depends
from typing import Annotated
import datetime
from fastapi import File


from src.core.main import BlockchainManager
from src.peer.nodes import NodeService
from src.utils.dependencies import get_blockchain, get_node_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/admin/drop_all_blocks")
def drop_all_blocks(blockchain: BlockchainManager = Depends(get_blockchain)):
    blockchain.blocks.delete_many({})
    return {"message": "All blocks have been dropped!"}


@router.get("/admin/generate_genesis_block")
def generate_genesis_block(blockchain: BlockchainManager = Depends(get_blockchain)):
    blockchain.generate_genesis_block()
    return {"message": "Genesis block has been generated!"}


@router.post("/create_new_block")
def generate_next_block(diploma_type: str, pdf_file: Annotated[bytes, File()], authors: (list[str] | str), title: str, language: str, discipline: str, is_defended: int, date_of_defense: datetime.date, university: str, faculty: str, supervisor: (list[str] | str), reviewer: (list[str] | str), additional_info: (str | None) = None, blockchain: BlockchainManager = Depends(get_blockchain)):
    pdf_hash = BlockchainManager.calculate_pdf_hash(pdf_file)
    try:
        blockchain.create_new_block(diploma_type, pdf_hash, authors, title, language, discipline,
                                    is_defended, date_of_defense, university, faculty, supervisor, reviewer, additional_info)
    except Exception as e:
        return {"message": f"Failed to create block: {e}"}
    return {"message": "Block has been generated!"}
