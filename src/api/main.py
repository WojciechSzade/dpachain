from typing import Annotated
import logging
import datetime

from fastapi import APIRouter, Depends, File, UploadFile

from src.core.main import BlockchainManager
from src.utils.dependencies import get_blockchain

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/get_latest_block")
def get_latest_block(blockchain: BlockchainManager = Depends(get_blockchain)):
    return blockchain.get_latest_block()


@router.get("/list_all_blocks")
def list_all_blocks(blockchain: BlockchainManager = Depends(get_blockchain)):
    return blockchain.get_all_blocks()